# DSi DSP、I²S、I²C、触摸与摄像头

[返回总路由](README.md)。本章依赖 [DSi 核心](dsi-core.md)、[声音](audio.md) 和 [平台接口](frontend.md)。

## 源码入口

| 设备 | 源码 |
|---|---|
| DSP 桥接 | [DSi_DSP.cpp](../src/DSi_DSP.cpp)、[DSi_DSP.h](../src/DSi_DSP.h) |
| DSP 低层执行 | [teakra](../src/teakra)、[teakra/src/README.md](../src/teakra/src/README.md) |
| 已知 microcode 高层实现 | [DSP_HLE](../src/DSP_HLE)：UcodeBase、AACUcode、G711Ucode、GraphicsUcode |
| I²S | [DSi_I2S.cpp](../src/DSi_I2S.cpp)、[DSi_I2S.h](../src/DSi_I2S.h) |
| I²C/BPTWL | [DSi_I2C.cpp](../src/DSi_I2C.cpp)、[DSi_I2C.h](../src/DSi_I2C.h) |
| DSi TSC | [DSi_SPI_TSC.cpp](../src/DSi_SPI_TSC.cpp)、[DSi_SPI_TSC.h](../src/DSi_SPI_TSC.h) |
| 摄像头/采集模块 | [DSi_Camera.cpp](../src/DSi_Camera.cpp)、[DSi_Camera.h](../src/DSi_Camera.h) |

## DSP 是第三个执行系统

Teak DSP 有自身寄存器、指令、程序/数据存储、MMIO、DMA、mailbox/semaphore 和音频串行部件。`DSi_DSP` 负责 ARM 侧控制、reset/enable、PData 传送、共享 NWRAM 和中断桥接，Teakra 负责 DSP 指令及其内部设备。

`StartDSPLLE` 注册三路 reply handler 与 semaphore handler；共享内存 read16/write16 连接 `DSPRead16/DSPWrite16`；AHBM 访问连接 DSi ARM9 总线。源码注明 AHBM 目前即时完成、未精细模拟总线仲裁。

`DSPCatchUp` 以 ARM9Timestamp 为追赶目标，按差值调用 `Run`；关闭 DSP 时也前移其时间基准，避免释放 reset 后补跑错误积压。ARM9 系统时钟换算、DSP 时间和 SPU sample clock 不是同一个接口，移植时逐调用点保持单位。

ARM 对 DSP 寄存器和程序/数据 RAM 的访问要处理 PDATA FIFO、地址递增、传输宽度与状态；命令/回复寄存器、semaphore mask 和 IRQ 都是客体可见协议。只运行 Teakra 的 `Run` 而遗漏这些桥接，DSi 驱动仍无法启动 DSP。

## Teakra 的继续阅读路线

从 [teakra.cpp](../src/teakra/src/teakra.cpp) 和 [processor.cpp](../src/teakra/src/processor.cpp) 进入，读 [interpreter.h](../src/teakra/src/interpreter.h)、[decoder.h](../src/teakra/src/decoder.h)、[register.h](../src/teakra/src/register.h)、[memory_interface.h](../src/teakra/src/memory_interface.h)。寄存器/指令与设备说明在该目录的 `register.md`、`decoder.md`、`mmio.md`、`dma.md`、`ahbm.md`、`apbp.md`、`btdmp.md`、`timer.md` 等随库资料；具体存在的文件以目录为准。

复用 Teakra 时保持回调、时钟、状态序列化和共享映射即可；重写 DSP 时必须继续覆盖其整个解码器、算术/地址寄存器、异常及各内部设备，不能以“已有 ARM9”替代 DSP 指令执行。

## DSP HLE

`StartDSPHLE` 计算 microcode CRC，选择已知版本的 AAC、G711 或 Graphics 实现；未知 CRC 回退 Teakra。`UcodeBase` 保持三路命令/回复、semaphore、共享 pipe、音频和 Mic FIFO，派生类实现相应命令。

HLE 的成功不仅是输出音频/图像正确，还包括命令字、回复时机、共享内存布局与 microcode 版本。AAC 通过 `Platform::AAC_*` 使用宿主解码器，Qt 实现位于 [Platform_AAC.cpp](../src/frontend/qt_sdl/Platform_AAC.cpp)。新平台须处理初始化/配置/解码失败，保留未知 microcode 的低层执行路径。

## I²S 与麦克风 FIFO

`SPU::Mix` 最后调用 `DSi_I2S::SampleClock`，它把 DS 混音与 DSP 输出按扩展声音控制结合，并推进麦克风路径。MICCNT 的格式/采样率/清 FIFO 位只能在特定关闭状态下改写；`ReadMicData` 无论总线宽度都拉取一个 FIFO word，空时重复最后 word，这会影响 8/16 位读行为。

状态包含采样分频、临时打包值/数量、FIFO 与溢出/请求标志。NDMA 由 FIFO 水位触发。与 DS TSC、DSP 同时使用 Mic 时，共享 [Mic](audio.md) 的引用计数语义。

## I²C 与 BPTWL

`DSi_I2CHost` 选择设备并维护当前地址、方向和 acquire/last 事务边界；从设备包括 BPTWL 电源管理与两颗摄像头。BPTWL 保存电池、充电、音量、背光、boot flag 和 IRQ 状态，提供复位/关机、按键持续时间等行为。

宿主电源/音量热键在 EmuThread 转换为 BPTWL 输入；游戏通过 I²C 读到这些状态。前端暂停不能代替关机命令，宿主音量滑块也不应无条件覆盖客体寄存器。`DoHardwareReset/DoShutdown` 连接整机生命周期。

DSi TSC 仍挂在系统 SPI，增加页式寄存器及音频配置/触摸读数；模式切回 DS 时要遵循 `SetMode` 逻辑。读取屏幕坐标只是上层输入，底层寄存器序列继续读 `DSi_SPI_TSC`。

## 摄像头的控制面与数据面

每个 `DSi_Camera` 经 I²C 接收传感器配置，保存 reset/standby、时钟、MCU 寄存器、格式/分辨率及帧进度；`DSi_CamModule` 是 ARM9 MMIO 的采集控制器，负责裁剪、双像素缓冲、IRQ、NDMA 和数据端口。

```text
游戏 I²C 配置传感器 → 激活摄像头
    → Platform::Camera_Start/CaptureFrame
    → Camera::StartTransfer / TransferScanline
    → CamModule 裁剪/格式处理、双缓冲
    → 数据可用 → NDMA 或 CPU 读端口 → 客体 RAM
```

平台编号 0 为外摄、1 为内摄。内部 FrameBuffer 使用 640×480 YUYV、每 word 两像素，采集模块每个 pixel buffer 最多 512 words；计数单位需逐接口区分。`Event_DSi_CamIRQ` 与 `Event_DSi_CamTransfer` 分别驱动帧信号和逐行传输。不能让宿主摄像头回调直接写客体 RAM 而跳过设备时序。

前端 [CameraManager.cpp](../src/frontend/qt_sdl/CameraManager.cpp) 管理实际摄像头/图像来源和格式转换。确定性对照使用固定图像输入；宿主设备帧率不可作为客体扫描线时钟。

## 复刻检查与限制

先用 Teakra 跑已知 DSP 程序并比较 mailbox、共享 RAM、IRQ、采样；再比较 HLE 和 LLE 的相同已支持 microcode。I²C 测事务拆分、last/read/write、reset 和关机；摄像头以固定图像比较裁剪后的 RAM 数据、FIFO 读序与 NDMA 时间，界面预览人工核对。DSP 的 FIFO IRQ/总线仲裁、部分地址步进在源码仍有 TODO，不能省略差异记录。
