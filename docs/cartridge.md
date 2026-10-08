# DS 卡带、保存芯片、DLDI 与 Slot-2

[返回总路由](README.md)。启动装载见 [启动](boot.md)，落盘见 [持久化](persistence.md)。

## 源码入口与分层

- [NDSCart.cpp](../src/NDSCart.cpp)、[NDSCart.h](../src/NDSCart.h)：`ParseROM`、`ReadROMParams`、`NDSCartSlot` 与其每 CPU `Interface`，加密、时钟和传输。
- [NDSCart/CartCommon.cpp](../src/NDSCart/CartCommon.cpp)：`ROMCommandStart/Receive`、ROM 协议基础；[NDS_Header.h](../src/NDS_Header.h)：ROM/banner/DSi 头。
- [NDSCart](../src/NDSCart)：各卡带类型；[ROMList.cpp](../src/ROMList.cpp)、[ROMList.h](../src/ROMList.h)：游戏码与 ROM/save 参数。
- [GBACart.cpp](../src/GBACart.cpp)、[GBACart.h](../src/GBACart.h)、[GBACartMotionPak.cpp](../src/GBACartMotionPak.cpp)：Slot-2 存储与外设。

核心区分“总线插槽”“CPU 访问接口”“卡带设备”。插槽处理所有权、复位、加密种子和事件；接口保存各 CPU 侧 ROM/SPI 控制、命令与数据位置；`CartCommon` 派生类解释设备命令和存储。不能把读 `04100010` 简化成 `rom[address++]`。

## ROM 解析与卡带选择

`ParseROM` 接受拥有或复制的镜像，检查基本长度，建立 ROM 大小/镜像参数，读 header、homebrew 标识和 ROMList，选择设备类型并接入保存数据。库中的参数影响 ROM 容量、芯片 ID、保存芯片类型，不能仅按文件扩展名推断。

| 实现 | 行为范围 |
|---|---|
| [CartRetail.cpp](../src/NDSCart/CartRetail.cpp) | 常规零售 ROM 与 SPI EEPROM/FLASH |
| [CartRetailNAND.cpp](../src/NDSCart/CartRetailNAND.cpp) | 卡带自身 NAND 型存储/读写命令，与 DSi 系统 NAND 不同 |
| [CartRetailIR.cpp](../src/NDSCart/CartRetailIR.cpp) | IR 扩展与 SPI 命令转发；支持范围按命令分支判断 |
| [CartRetailBT.cpp](../src/NDSCart/CartRetailBT.cpp) | BT 卡带专门 SPI 行为，不能由类名推断已完整模拟真实蓝牙链路 |
| [CartSD.cpp](../src/NDSCart/CartSD.cpp) | SD 存储与 DLDI 补丁公共行为 |
| [CartHomebrew.cpp](../src/NDSCart/CartHomebrew.cpp) | homebrew 启动、argv、读写 SD 命令 |
| [CartR4.cpp](../src/NDSCart/CartR4.cpp) | R4 变体、加密和 SD/FAT 访问协议 |

## ROM 传输状态机

1. 客体写命令字节、ROMCNT 和种子；检查 CPU 选择、复位/电源、busy 和启动位。
2. 按当前加密阶段解释命令，向 Cart 请求响应或建立写事务。
3. 接口计算传输长度与命令/数据延迟，安排 `Event_CartROMTransfer9/7`（DSi 第二槽有独立事件）。
4. `ROMReceiveData/ROMSendData` 推进卡侧数据、双缓冲位置和 ready 状态；数据就绪时触发对应 DMA 请求。
5. CPU/DMA 读写数据端口消耗一字并更新 ready，解除等待并继续下一段。
6. `ROMEndTransfer` 清 busy，必要时置 transfer-done IRQ，并结束设备事务。

传输周期由 ROMCNT 决定；当前实现区分每位传输速度和跨 `0x200` 字节边界的额外延迟。SPI 是另一通道，保留 chip select、传输中状态和完成事件。不能让 SPI 与 ROM 数据端口共享一套位置计数。

KEY1 使用 BIOS 中的 key material 和游戏码初始化表，处理 secure-area/命令阶段；KEY2 保存移位状态和种子。保留 `Key1_*`、`Key2_*` 的字节序、初始化时机和阶段迁移，并逐调用点检查哪些传输实际使用它们。直接启动的 secure-area 解密在 [启动](boot.md) 中另有路径。

## 保存芯片

`CartRetail::SPITransmitReceive` 分发到 EEPROMTiny、EEPROM、FLASH 协议。需要状态：选中/释放、当前命令、地址阶段、写使能/状态、页面/擦除规则及 SRAM 内容。一次 select 下的多字节命令和中途 release 决定事务边界。

写入后通过 `Platform::WriteNDSSave` 上报整个 save buffer 和本次变化范围，前端再合并落盘。保存容量来自类型/参数与已有镜像；扩大、镜像、页回绕和越界行为要对照相应设备分支，不统一为任意长度数组。

## Homebrew SD 与 DLDI

`CartSD::ApplyDLDIPatch/ApplyDLDIPatchAt` 在 ROM 中定位并重定位 DLDI 驱动，驱动生成源见 [melonDLDI](../melonDLDI)，嵌入数据见 [melonDLDI.h](../src/NDSCart/melonDLDI.h)。homebrew 的 SD 扇区访问由卡带命令转向 `FATStorage`；它不是 DS 原生 SD 控制器。

argv、驱动内存区、重定位指针和只读标志都是 ABI。移植时可重新实现宿主存储，但必须让客体驱动看到一致的扇区、返回值和边界；不能把宿主路径直接塞给客体程序。FATStorage 可与宿主目录同步，具体副作用见 [持久化](persistence.md)。

## Slot-2

`GBACartSlot` 经 NDS 总线暴露 GBA ROM/save、RAM expansion、rumble、solar sensor、motion pak、guitar grip 等设备。控制权与等待周期由 EXMEMCNT 决定。`GBACartMotionPak` 还把平台输入转换为设备坐标/校准表示；[Platform.h](../src/Platform.h) 规定加速度/陀螺仪等单位。

这是 DS 对 GBA 卡槽和扩展的访问模拟；当前整机进入 GBA 模式会以 `GBAModeNotSupported` 停止，不提供完整 GBA 主机执行模式。空卡槽值也有等待周期相关的衰减模型。

## 复刻检查

用协议序列验证 command→busy→ready→读取→IRQ/DMA，覆盖中途复位、切 CPU 所有权、SPI select 保持/释放、保存芯片页回绕及擦除。重开实例验证磁盘保存可读回；用 homebrew 读写已知 SD 扇区校验 DLDI。扩展输入须在对应寄存器/串行响应中验证，不能以 UI 显示开关已打开作为完成标准。
