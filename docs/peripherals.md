# 系统 SPI、固件、触摸、按键、RTC 与电源

[返回总路由](README.md)。卡带 SPI 在 [卡带](cartridge.md)，DSi I²C/TSC 扩展在 [DSi 媒体](dsi-media.md)。

## 源码入口

[SPI.h](../src/SPI.h)、[SPI.cpp](../src/SPI.cpp)：`SPIHost`、`SPIDevice`、`FirmwareMem`、`PowerMan`、`TSC`；[SPI_Firmware.h](../src/SPI_Firmware.h)、[SPI_Firmware.cpp](../src/SPI_Firmware.cpp)：固件布局/生成/校验；[RTC.h](../src/RTC.h)、[RTC.cpp](../src/RTC.cpp)：串行 RTC 与时钟；[NDS.cpp](../src/NDS.cpp)：`SetKeyMask`、`TouchScreen`、`ReleaseScreen`、`SetLidClosed`、KEYCNT 与电源 MMIO。

## 系统 SPI 总线

SPIHost 在 ARM7 `040001C0/1C2`，可选电源管理、固件闪存、触摸控制器。CNT 含 enable、busy、IRQ、设备号、hold 和速度；Data 是串行事务接口，而非独立的普通寄存器。

`WriteData` 在 enable 且不 busy 时接收一字节，置 busy，把数据送给选中设备，按 hold 决定是否 `Release`，并安排 `8 * (8 << speed)` 系统周期后的完成。`TransferDone` 清 busy 并按需触发 ARM7 SPI IRQ；busy 时读取/再次写入有专门处理。

每个设备保存 `Hold`、`DataPos`、最近返回数据及命令状态。结束 chip select 会改变下一字节的解释。当前代码对 16 位 SPI、传输中更改速度和部分读值仍有警告/TODO，应保留范围说明。

## 固件闪存

`Firmware` 是带结构化字段与原始字节的镜像，包含启动相关区域、用户设置、触摸校准、无线配置与校验。DS/DSi/不同容量布局的区分以其访问器为准；[README](../README.md) 也说明不同固件容量与引导能力。

`FirmwareMem::Write` 解释闪存命令、状态与地址阶段；`Release` 完成写事务并通过 `Platform::WriteFirmware` 报告变化。`SetupDirectBoot` 选择用户设置并写入客体启动信息。新实现不能只提供一个固定用户名结构而丢掉游戏经 SPI 读写固件的路径。

前端的固件自定义和保存路径策略在 `EmuInstance::customizeFirmware`、`getEffectiveFirmwareSavePath` 等函数；核心镜像与实际落盘文件可能按实例分开，避免把生成配置误写到原始资源。

## 触摸与麦克风 ADC

`NDS::TouchScreen` 直接转交 `TSC::SetTouchCoords`，后者把坐标左移四位作为 ADC 输入并更新触摸按下位；DS 固件在 `FirmwareMem::Reset` 中统一校准点，DSi NAND 设置在前端装载时作对应处理。它不是每次触摸时运行通用校准公式。释放使用特殊值，不能把 `(0,0)` 当作无触摸。

`TSC::Write` 保存控制字、选择 X/Y/AUX，结果在后续串行字节中分段返回。DS AUX 从 `Mic::ReadSample` 取 signed16 样本并转换为 unsigned12。读命令和读取结果有流水关系，立即把完整坐标塞进同一个 Data 字节不符合协议。

DSi 使用派生 TSC，有扩展页式寄存器、音频控制和兼容模式；复用触摸上层接口，但设备字节协议需单独实现。

## 按键与合盖

`KeyInput` 包含普通及扩展输入，按下为低电平；`KEYCNT` 选择参与中断的键，并规定 AND/OR 条件。键盘/手柄映射属于宿主，核心只接收定义好的 mask。

合盖不是普通暂停按钮。盖状态进入客体输入与 IRQ/电源逻辑；游戏可选择进入睡眠，唤醒又由专门 IRQ 路径恢复。前端触摸应先从布局逆变换到下屏硬件坐标，见 [前端](frontend.md)。

## RTC

RTC 通过 GPIO 风格串行线读写。`RTC::Write` 处理片选/时钟边沿和传输方向，`ByteIn/CmdRead/CmdWrite` 处理命令、位序和 BCD 日期寄存器；`StateData` 保存日期、状态和闹钟/IRQ 配置。

`ScheduleTimer` 将 32768 Hz RTC 时钟转换为系统周期，用 `TimerError` 累积余数避免每次四舍五入造成长期漂移。`ClockTimer` 计数到一秒推进年月日与时分秒，并处理周期/闹钟中断。12/24 小时、月底、闰年、BCD 校正等逻辑在 `Count*`、`DaysInMonth` 和 `WriteDateTime`。

宿主初始时间及可选同步由 EmuInstance 设置；模拟中计时由 RTC 事件驱动。复现 trace 时要固定 RTC 初态并控制宿主同步，否则同一 ROM/输入也可能跑出不同结果。`Platform::WriteDateTime` 是客体改时间后的通知，不是每读一次 RTC 就取宿主墙钟。

## 电源与复刻检查

DS `PowerMan` 处理 SPI 电源寄存器；NDS 的 POWCNT 控制屏幕、2D/3D、SPU 与 Wi-Fi 等；HALTCNT 可请求 HALT、睡眠或不支持的 GBA 模式。设备掉电时还会改变访问值和等待周期，应看 `SetPowerCnt` 的调用链。

按字节重放 SPI 事务并比较每个返回值/busy/IRQ；验证片选中断、触摸按下/释放和 ADC 字节顺序。RTC 用跨日、跨月、闹钟、睡眠持续计时的固定序列验证；按键用 AND/OR 条件验证 IRQ。前端按钮和布局的视觉检查手动完成。
