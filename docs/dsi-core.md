# DSi 整机扩展、SCFG、MBK 与 NDMA

[返回总路由](README.md)。DSi 复用 [DS 调度](architecture.md)、[CPU](cpu.md)、[基础总线](memory.md)，再增加本章与 [存储](dsi-storage.md)、[媒体](dsi-media.md) 所述行为。

## 源码入口

[DSi.h](../src/DSi.h)、[DSi.cpp](../src/DSi.cpp)：构造、`Reset`、`LoadNAND`、`SetupDirectBoot`、`SoftReset`、`SetScfgClock9`、`ApplyNewRAMSize`、`MapNWRAM_*`、`CheckIO9Access/CheckIO7Access`、CPU 总线覆写；[DSi_NDMA.h](../src/DSi_NDMA.h)、[DSi_NDMA.cpp](../src/DSi_NDMA.cpp)：扩展 DMA。

## 与 DS 的差异清单

| 领域 | DSi 增加或改变的内容 |
|---|---|
| CPU/时间 | 仍是 ARM9/ARM7 架构，ARM9 时钟倍率可切换 |
| 主 RAM | 最大 16 MiB，当前可见大小由配置/模式决定 |
| BIOS | ARM9i/ARM7i 各 64 KiB，SCFG 控制可见性/兼容路径 |
| WRAM | A/B/C 三块各 256 KiB NWRAM，可映射 CPU/DSP 视图 |
| 总线/IRQ | SCFG 访问控制、ARM7 IE2/IF2、GPIO 和新设备区 |
| DMA | 每 CPU 再加四 NDMA 通道，传统 DMA 仍存在 |
| 存储 | SDMMC 接 NAND/SD，SDIO 接新 Wi-Fi，第二卡带控制器 |
| 媒体 | DSP、I²C 电源/相机、I²S、扩展 TSC、摄像头数据通路 |

`ConsoleType==1` 也会改变基类中的 RAM 掩码、时钟、电源和设备行为，不能只复制 DSi.cpp 而跳过 NDS 的条件分支。

## 启动与模式切换

`DSi::Reset` 根据 BIOS 镜像校验结果判断是否走完整 BIOS 引导。接着执行基类复位，再设置 DSi 的声音、共享 WRAM、新设备、NAND 与 SCFG 初态。`LoadNAND` 同时负责 NWRAM 初始化与启动资源准备。

完整 BIOS 路径让 BIOS 继续启动；不完整 BIOS 路径读取 NAND 的 bootparams 和 MBK 设置，解密/装入 boot2、设置启动 RAM，并把两 CPU 跳到相应入口。该路径包含已知兼容初值和 TODO，应作为当前实现快照读取。

`SetupDirectBoot` 根据 ROM 头的 `UnitCode` 判断 DS 兼容或 DSi 模式。DS 兼容分支关闭 NWRAM 映射/窗口、使用旧 TSC 模式、降低 ARM9 倍率并调整可见 RAM；DSi 分支用扩展头的 MBK/权限、ARM9i/ARM7i 程序与 modcrypt 信息建立启动环境。随后仍需基类的通用寄存器/栈/入口设置。

`SoftReset`、`SCFG_DSiLoaderHack` 和 `CheckDSiLoaderHack` 是另需追踪的兼容路径；不要把 loader hack 当成硬件寄存器新增的真实功能。

## SCFG 与 MMIO 路由

SCFG_BIOS、CLOCK、EXT、MC、RST 控制 BIOS、时钟、设备访问与卡槽电源。`CheckIO9Access/CheckIO7Access` 在访问 DSi MMIO 和第二卡槽前检查门控。保留不同 CPU 的位定义，关闭访问后的结果和副作用以对应读写函数为准。

| 地址域/寄存器 | 行为入口 |
|---|---|
| `04004000` 一组 SCFG | BIOS/CLOCK/EXT/MC/RST，CPU 权限和锁定条件 |
| `04004040` 起 MBK 区 | NWRAM 银行槽、范围及写保护 |
| `04004100` 起 | NDMA 全局控制与通道 |
| `04004200` 起（ARM9） | 摄像头控制/数据 |
| `04004300` 域 | DSP MMIO，按 CPU 路由和门控判断 |
| `04004400` 起（ARM7） | AES 控制、FIFO、IV、MAC 和 key slot |
| `04004500` 域（ARM7） | I²C |
| `04004600/4604`（ARM7） | 麦克风控制/数据 |
| `04004700`（ARM7） | 扩展声音控制 |
| `04004800–040049FF`（ARM7） | SDMMC |
| `04004A00–04004BFF`（ARM7） | SDIO |
| `04004C00` 域（ARM7） | GPIO |
| `040021A0` 起、`04102010` | 第二卡带控制和数据 |
| `04000218/21C`（ARM7） | IE2/IF2 |

本表是导航范围。每一种位宽仍走独立 IO switch；某些寄存器仅实现特定位宽或 alias，不能据范围自动生成全可读写设备。

`SetScfgClock9` 先把 ARM9 timestamp/target 还原系统单位，再切 shift 后转回，并更新 ARM9 区域时序。只修改频率常数会让设备看到时间跳跃。

## MBK 与 NWRAM

MBK1–5 分配物理槽，MBK6–8 给每 CPU 配置可见窗口，MBK9 写保护。A 分四个槽，B/C 分八个槽；两 CPU 和 DSP 的消费者并非对称。`MapNWRAM_A/B/C` 更新银行映射，`MapNWRAMRange` 更新窗口起止/掩码，JIT 重映射随之发生。

实现至少区分三件事：物理银行字节、银行槽归属、某 CPU 的地址窗口。改窗口不搬数据，映射空洞不自动等同主 RAM。相同银行从 CPU 与 DSP 访问必须看到相同内容。重叠槽规则在 DSi 源码仍有待确认注释，不能自行概括成普通 WRAM 的单指针模型。

## NDMA

每通道保存源/目标、总长度、块长度、subblock timer、fill data、控制及当前/剩余状态。NDMA 以 32 位单元传送，支持 fill、地址固定/递增/递减、块间重装和事件/立即模式。

`WriteCnt` 在使能沿锁存状态，模式大于 `0x10` 被归到立即模式；ARM7 内部模式编号带 `0x20`。`Start` 将零 block length 解释为 `0x1000000`，根据总剩余量限制单批，并用独立 CPUStop 位暂停 CPU。`Run9/Run7` 负责按 CPU target 分批推进。

`DSi::CheckDMAs` 通过 `NDMAModes` 将传统触发源映射到 NDMA，再由新设备直接发特定模式请求：例如第一/第二卡槽、GX FIFO、相机、SD、AES、麦克风。触发条件在设备消费/生产 FIFO 时重算，不能只在写 enable 时查一次。

当前 `RunNDMAs` 明确未实现 round-robin，`StallNDMAs` 为 TODO，部分 Timer/旧 Wi-Fi 等启动模式不支持；subblock delay 也不能视为完整实现。独立复刻需要把“与当前实现一致”和“补完硬件模式”作为两项验收。

## 复刻检查

在 DS 模式已稳定后测试 DSi：切 CLOCK 前后系统时间连续，SCFG 关闭设备时访问受限，MBK 的跨 CPU/DSP 共享与写保护成立；传统 DMA 和 NDMA 并存时 IRQ/CPUStop 不相互清错。对完整 BIOS、boot2 补载、DS 兼容直接启动、DSi 直接启动分别记录初态与首段执行轨迹。
