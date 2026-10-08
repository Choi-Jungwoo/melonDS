# 资源装载、复位与启动

[返回总路由](README.md)。先读 [整体架构](architecture.md)；DSi 的扩展初始化另见 [DSi 核心](dsi-core.md)。

## 源码入口

- [EmuInstance.cpp](../src/frontend/qt_sdl/EmuInstance.cpp)：`verifySetup`、`loadROMData`、`loadROM`、`updateConsole`、`reset`、`bootToMenu`、各 `load*BIOS`/`loadFirmware`/`loadNAND`。
- [NDS.cpp](../src/NDS.cpp)：构造函数、`Reset`、`Start`、`NeedsDirectBoot`、两个 `SetupDirectBoot` 重载。
- [NDSCart.cpp](../src/NDSCart.cpp)：`ParseROM`、卡槽装载、`DecryptSecureArea`；[NDS_Header.h](../src/NDS_Header.h)：ROM 头的确切字段布局。
- [FreeBIOS.cpp](../src/FreeBIOS.cpp)、[FreeBIOS.h](../src/FreeBIOS.h)、[freebios](../freebios)：内置 BIOS 的生成物和源代码。
- [SPI_Firmware.cpp](../src/SPI_Firmware.cpp)、[SPI.cpp](../src/SPI.cpp)：固件结构、校验和启动配置拷贝。

## 资源角色

| 资源 | 用途 | 缺失时的当前路径 |
|---|---|---|
| DS ARM9/ARM7 BIOS | 异常入口、软件中断、启动所需例程 | `NDSArgs` 默认提供 NTR FreeBIOS，走直接启动 |
| DS firmware | 引导程序、用户信息、触摸校准、无线设置 | 可生成配置固件；是否可启动由 `IsBootable` 判断 |
| ROM 镜像 | 两 CPU 程序、资源、overlay、卡带命令响应 | 解析后选择具体 Cart 实现 |
| 游戏存档镜像 | EEPROM/FLASH/NAND 等非易失内容 | 由卡带类型决定大小和初值，不与即时存档混用 |
| DSi BIOS/NAND/SD | TWL 启动、系统存储和可移除存储 | 由 DSi 和前端的专门分支处理 |

默认参数和前端策略是两层：`DSiArgs` 默认 `BrokenBIOS` 占位，不等于 Qt 前端的 DSi BIOS 回退选择。当前前端还有 `FreeBIOSGetTwlArm9/Arm7` 路径，具体条件应读 `loadDSiARM9BIOS/loadDSiARM7BIOS`。不要把 `NDSArgs` 关于 DS 默认资源的说明外推到所有 DSi 启动方式。

## 从文件到运行的顺序

1. 前端解释路径、归档和压缩，得到 ROM 字节；`loadROMData` 与 `decompressROM` 负责宿主文件形式。核心接收镜像而不是 Qt 文件对话框。
2. `NDSCart::ParseROM` 读取头、ROM 参数库并建立合适卡带；装载存档与可选 homebrew SD。ROM 的头偏移、大小和目标地址是客体输入，新实现应在拷贝前验证范围和整数溢出。
3. `updateConsole` 按 DS/DSi 配置构造或更新实例，把 BIOS、固件、渲染器、JIT/GDB/声音选项与存储句柄放入 Args。
4. 设置卡带，调用整机 `Reset`，安装 RTC、用户固件设置及前端设备状态。
5. 如果要求或必须直接启动，执行 `SetupDirectBoot(romname)`；否则保留 BIOS 复位入口。
6. `Start` 开始运行，随后 `EmuThread` 请求 `RunFrame`。插卡但不复位是另一操作，不能隐式等同启动新游戏。

## DS Reset 的依赖顺序

`NDS::Reset` 先清 JIT，选择 RAM 掩码与 ARM9 倍率，初始化 CP15，再建内存时序表。随后归零时间戳和 RAM，设置共享 WRAM、EXMEMCNT、IRQ、IPC、数学单元与电源状态；复位 CPU、Timer、DMA、事件槽；最后复位 GPU、卡槽、SPU、Mic、SPI、RTC、Wifi。

顺序有实际依赖：`CP15Reset` 要早于 `InitTimings`；事件表要在设备 Reset 安排周期事件之前清；映射更新必须指向已分配的物理内存。新实例、软复位、停止后重开不能复用未经复位的 FIFO、串行传输位置或主机回调对象。

## DS 直接启动做了什么

`NeedsDirectBoot` 检查固件是否可启动，以及两个 BIOS 是否为已知原生镜像。直接启动模拟的是 BIOS/固件已经完成装载后的整机状态，不是只把 PC 改为 ROM 入口。

`SetupDirectBoot()` 的关键动作：

- 将共享 WRAM 分给 ARM7；FreeBIOS 路径补 Nintendo logo。
- 把 ROM 头写入 RAM 的启动信息区，填入卡带 ID、头 CRC、secure-area CRC 和启动标志。
- 对需要的 ARM9 secure area 解密；按头给出的 ROM 偏移、RAM 地址与长度装入 ARM9/ARM7 程序。
- 设置 ARM7 BIOS 保护，拷贝固件用户配置。
- 逐项写 CP15：控制字、权限区域、cache 配置及 DTCM/ITCM 位置。必须保留这些写的顺序和副作用。

带 `romname` 的重载继续通知卡带（homebrew 可能安装 argv/DLDI），初始化两 CPU 的 R12/SP/LR、IRQ/SVC 模式栈，`JumpTo` 填流水线，然后设置 EXMEMCNT、POSTFLG、屏幕/SPU 电源、SPI、声音 bias 和 Wi-Fi 等待周期。

启动 RAM 常量、CP15 区域表和栈地址直接查上述两个函数；它们是一组相互匹配的启动快照。仅复制程序而遗漏这组状态，会让游戏在启动库、IRQ 或第一笔 DMA 时失败。

## DSi 分支

`DSi::Reset` 区分完整 BIOS 启动与从 NAND 手动装载 boot2；`DSi::SetupDirectBoot` 还处理 DSi 头、扩展二进制、MBK、modcrypt、权限和模式切换。必须结合 [DSi 核心](dsi-core.md) 与 [存储](dsi-storage.md) 实现。DS 直接启动的成功不能证明 DSi 菜单、DSiWare 或增强卡带启动正确。

## 复刻检查

建议为固件启动和直接启动分别保留启动后的状态记录：两 CPU 的寄存器和模式栈、TCM、WRAM 分配、RAM 头信息、POSTFLG、电源、第一批事件。先用自制的两 CPU 程序验证各自入口、栈和 IPC，再验证 secure-area、homebrew 参数与 DSi 分支。单个游戏出现画面只是启动链的一项证据。
