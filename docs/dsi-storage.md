# DSi SD/MMC、NAND、AES 与新 Wi-Fi

[返回总路由](README.md)。先读 [DSi 核心](dsi-core.md) 的门控与 NDMA；外部存储寿命见 [持久化](persistence.md)。

## 源码入口

[DSi_SD.h](../src/DSi_SD.h)、[DSi_SD.cpp](../src/DSi_SD.cpp)：`DSi_SDHost`、`DSi_SDDevice`、`DSi_MMCStorage`；[DSi_NAND.h](../src/DSi_NAND.h)、[DSi_NAND.cpp](../src/DSi_NAND.cpp)：`NANDImage/NANDMount`；[DSi_TMD.h](../src/DSi_TMD.h)：标题元数据；[DSi_AES.cpp](../src/DSi_AES.cpp)、[DSi_AES.h](../src/DSi_AES.h)；[DSi_NWifi.cpp](../src/DSi_NWifi.cpp)、[DSi_NWifi.h](../src/DSi_NWifi.h)。

## 存储路径

```text
ARM7 MMIO / NDMA
    → SDMMC host：命令、响应、FIFO、IRQ、块计数
        → MMCStorage：MMC/SD 命令状态
            → NANDImage 的原始文件 或 FATStorage 的 SD 扇区
    → SDIO host：同类主机接口
        → NWifi：SDIO function/mailbox 与无线控制协议

宿主标题管理 → NANDMount → 加密 FAT 读写 → NANDImage
```

CPU 经硬件控制器访问 NAND，和宿主工具挂载 NAND 内 FAT 是两条路径。不能在原始 MMC 块读时总是返回解密 FAT 内容；客体可能通过 AES 自己解密。

## SD host 状态机

主机保存端口、时钟、软件复位、选项、命令/参数、响应缓冲、IRQ status/mask、card IRQ、16/32 位数据模式、块长度/数量、stop action 和双 FIFO。状态标志会由传输和 FIFO 水位更新；IRQ mask 的内部含义不是简单的正向 IE。

1. 寄存器写命令，设备 `SendCMD`/`SendACMD` 解释当前卡状态并用 `SendResponse` 回传。
2. 读块通过 `DataRX` 注入主机，安排 `FinishRX`；写块通过 `DataTX` 取出客体准备的数据，安排 `FinishTX`。
3. `CheckRX/CheckTX` 结合 FIFO、块计数和 NDMA 决定能否继续。
4. `ReadFIFO16/32`、`WriteFIFO16/32` 处理客体端口，`UpdateFIFO32/CheckSwapFIFO` 保持两种视图与缓冲交换。
5. 一块完成后设备 `ContinueTransfer` 更新地址；单块/多块/停止命令决定是否继续。

`DSi_MMCStorage` 保存 CID/CSD/OCR/CSR/RCA、块大小与当前读写地址。命令 enum 和 switch 是协议覆盖表：初始化、识别/选择卡、状态、块长、单/多块读写和 APP_CMD/ACMD。NAND 与 SD 的响应/寻址不完全一致。复刻时单独列出每个命令的状态前提、响应和数据阶段。

当前代码注明传输延迟、busy、SDHC/SDXC、部分 error/FIFO/status 命令仍未完整确认；不要把固定延迟或返回零写成通用 SD 规格。

## NANDImage、NANDMount 与标题

`NANDImage` 拥有宿主文件、长度、eMMC CID、ConsoleID 和派生出的 FAT/ES 加密状态；句柄不可复制。`NANDMount` 挂载解密后的 FAT，回调闭包依赖其稳定地址，因此不可移动。

`LoadNAND` 使用它读取 boot2 与设备/系统设置。宿主标题管理通过 `ListTitles/GetTitleInfo/ImportTitle/DeleteTitle`、public/private/banner save 导入导出及文件操作修改镜像；`DSi_TMD` 定义元数据布局，需与 NDSHeader、ticket 和目录结构对应。

`NANDMount::ApplyUserData` 更新两份 TWLCFG 系统设置；将某个文件写成功不等于全部标题结构完成。重实现应验证镜像长度、分区/文件偏移、资源匹配与写结果，并用副本验证失败恢复。

## AES 设备

AES 硬件接口包含控制、块计数、输入/输出 FIFO、IV、MAC、四组 key slot 和当前工作 key。设备 state machine 位于 `DSi_AES`，块算法复用 [tiny-AES-c](../src/tiny-AES-c)。

- `WriteKeyNormal/KeyX/KeyY` 和 `DeriveNormalKey` 处理 key slot 与派生，保留所有 128 位字节/字顺序变换。
- `WriteCnt` 处理 key 选择、模式、输入/输出 DMA 阈值和启动沿；锁存剩余数据块/附加块并初始化 crypto context。
- 模式 0/1 为 CCM 解密/加密，2/3 走 CTR；`ProcessBlock_CCM_*` 与 `ProcessBlock_CTR` 消耗四个输入 word、产生结果并推进计数/计数器。
- `Update` 在输入足够、输出有空间时处理；`CheckInputDMA/CheckOutputDMA` 分别请求 ARM7 NDMA 模式 `0x2A/0x2B`。
- 完成后更新 busy、MAC 校验/输出及 IRQ；输出 FIFO 在运算结束后仍可能有数据，需要继续允许排空。

当前 `WriteInputFIFO` 有添加处理延迟的 TODO，部分 CCM MAC 输入模式未完成。AES 的数学结果正确不代表其 FIFO、DMA 或耗时正确；标准库 AES 只能替换块算法部分。

## DSi_NWifi

这是连接 SDIO 的新无线设备，不是 [旧 DS Wi-Fi](wireless.md) 寄存器的另一地址映射。`SendCMD` 处理 SDIO 命令；F0/F1 维护 function 寄存器、IRQ、window 访问与 mailbox。mailbox 的 BMI→HTC→WMI 命令解析模拟固件初始化、端点、扫描/连接和包传递。

关键链：`SDIO_Read/Write` → `ReadBlock/WriteBlock` → `HandleCommand` → `BMI_Command/HTC_Command/WMI_Command`；网络数据经 `WMI_SendPacket`、`CheckRX/DrainRXBuffer` 转到 Platform 的 Ethernet 接口。`MSTimer` 更新扫描/连接等异步状态，产生 WMI events 和 SDIO IRQ。

当前实现含大量 HACK/TODO 和硬编码固件/端点行为，属于协议层模拟，并非执行实际无线芯片 CPU 固件。实现新版本时应逐命令建立响应表，保证 guest 初始化序列可继续；不能承诺未实现命令、所有固件版本和所有无线模式兼容。

## 复刻检查

用小型、可丢弃的块镜像比较单/多块读写、FIFO16/32 切换、停止和 NDMA；单独用已知 AES 向量验证字序/CTR/CCM，再用 MMIO 序列验证水位和完成 IRQ。NAND 挂载和客体原始读分别验证；NWifi 以初始化握手、扫描、连接、收发和断开协议 trace 为验收，而不是只看宿主网络 socket 成功创建。
