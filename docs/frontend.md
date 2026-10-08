# 前端、线程和 Platform 接口

[返回总路由](README.md)。本章用于将核心接到新 UI、无界面 runner 或不同宿主；核心时间不由 UI 帧率决定。

## 源码入口

| 层 | 入口 |
|---|---|
| 进程、参数、多实例 | [main.cpp](../src/frontend/qt_sdl/main.cpp)、[main.h](../src/frontend/qt_sdl/main.h)、[CLI.cpp](../src/frontend/qt_sdl/CLI.cpp) |
| 实例/资源 | [EmuInstance.h](../src/frontend/qt_sdl/EmuInstance.h)、[EmuInstance.cpp](../src/frontend/qt_sdl/EmuInstance.cpp) |
| 模拟线程 | [EmuThread.h](../src/frontend/qt_sdl/EmuThread.h)、[EmuThread.cpp](../src/frontend/qt_sdl/EmuThread.cpp) |
| 输入/声音 | [EmuInstanceInput.cpp](../src/frontend/qt_sdl/EmuInstanceInput.cpp)、[EmuInstanceAudio.cpp](../src/frontend/qt_sdl/EmuInstanceAudio.cpp) |
| 窗口/屏幕 | [Window.cpp](../src/frontend/qt_sdl/Window.cpp)、[Screen.cpp](../src/frontend/qt_sdl/Screen.cpp)、[ScreenLayout.cpp](../src/frontend/ScreenLayout.cpp) |
| 宿主桥接 | [Platform.h](../src/Platform.h)、[Platform.cpp](../src/frontend/qt_sdl/Platform.cpp)、[PlatformOGL.h](../src/PlatformOGL.h) |
| 配置/资源辅助 | [Config.cpp](../src/frontend/qt_sdl/Config.cpp)、[ArchiveUtil.cpp](../src/frontend/qt_sdl/ArchiveUtil.cpp)、[CameraManager.cpp](../src/frontend/qt_sdl/CameraManager.cpp) |

## 生命周期与线程

`main` 初始化 Qt/SDL、配置、网络/实例并建立窗口。`EmuInstance` 聚合核心指针、资源路径、保存管理、输入/音频、摄像头和多个窗口。`EmuThread` 持有运行/暂停/单步状态，接收消息并执行核心。

UI 的 boot、reset、插拔卡、读写状态、切换 GL 等操作由 `sendMessage/handleMessages` 汇入模拟线程。部分调用等待 semaphore 获得结果；嵌套暂停使用计数栈，不能以一个随意覆盖的 bool 替换。真实修改核心状态之前必须与运行帧串行化。

宿主还可能有软件光栅线程、SDL 音频回调、SaveManager、网络及摄像头回调。核心接口不等于全部线程安全。声音输出用自己的锁，图像显示/renderer 切换用 renderLock/GL context 协议；销毁时停止生产者、等待工作线程，再释放实例和资源。

## 前端一帧

`EmuThread::run` 处理运行状态、热键/DSi 电源输入、渲染设置；将 `inputMask`、触摸、盖状态交给核心，同步 RTC，然后执行 `RunFrame`。如果 renderer 仍需 shader 编译，先分步编译。

帧后检查 NDS/GBA/firmware 保存请求，绘制屏幕，处理 fast-forward/slowmo/静音和 DSi 音量同步，再按音频队列与 FPS 策略节流。`nlines` 进入帧间隔计算，支持 VCOUNT 改动产生非标准帧。最后处理消息队列。

墙钟只用于播放/显示速率和外部输入策略；核心必须保留自己的周期。快进是减少宿主等待，不是让 Timer/DMA 每帧少运行。

## 输入与屏幕坐标

键盘/手柄映射产生 DS 的低电平按键 mask，热键是另一组前端动作。`ScreenLayout::Setup/GetScreenTransforms` 计算双屏/旋转/缩放/间距/混合布局；`GetTouchCoords` 逆变换到下屏 256×192 坐标并处理 clamp。点击上屏或屏外不能直接当作触摸下屏。

核心 `ScreenSwap` 是硬件引擎到 LCD 的选择，UI swap 是两个物理屏幕在宿主窗口的位置。旋转、DPI、整数缩放和多窗口改变后，显示矩阵与触摸逆矩阵应一起更新。麦克风和扩展控制器的单位/采样契约见 Platform，输入模拟来源也要走相同接口。

## Platform 最小实现清单

| 接口组 | 新宿主需要兑现的契约 |
|---|---|
| 文件 | UTF-8 路径、打开标志、保留/截断/禁止创建、seek/tell/length、实际读写数量、关闭 |
| 停止/日志 | `SignalStop(reason, userdata)` 回到正确实例；日志不改变模拟时钟 |
| 线程/锁/信号量 | 创建、等待、唤醒和释放配对；停止时不遗留阻塞线程 |
| 时间 | `GetMSCount/GetUSCount/Sleep` 是宿主时间；不得代替 SysTimestamp |
| 保存 | `WriteNDSSave/WriteGBASave/WriteFirmware/WriteDateTime` 保存变化或明确报告处理策略 |
| 无线/网络 | `MP_*` 的 DS 帧与时间戳、`Net_*` 的 Ethernet 帧各守自己的格式 |
| Mic/Camera | 启停配对、实际采样数量、确定格式、实例 userdata；缺设备时给定义好的输入 |
| AAC | 初始化、配置、解码和错误返回，供 DSP HLE 使用 |
| 扩展与动态库 | guitar/rumble/motion 单位、动态加载符号和释放 |

静态库 `core` 可以构建而未链接这些平台实现。新 runner 的最终可执行程序仍须提供所需符号；“core 编译成功”不等于已经能启动 ROM。最小 runner 可以明确禁用现实设备并提供可重复输入，但文件写入/停止/错误不能悄悄假成功。

## 配置、资源与功能窗口

Config 使用 TOML，区分全局和实例设置；默认值、迁移和存储路径以 `Config.cpp/h` 为准。EmuInstance 把配置转成 Args/设备调用，核心不直接依赖 Qt 对话框。

各 `*SettingsDialog` 编辑输入、视频、音频、路径、固件、摄像头、Wi-Fi/MP、界面与电源；ROMInfo/RAMInfo 展示信息，Cheats/CheatImport 管理代码，TitleManager 操作 DSi NAND。对应 `.ui` 为界面结构、`.qrc`/`res` 为资源，不能仅阅读 C++ 就忽略打包和可访问的交互。

归档与压缩由 ArchiveUtil 和 EmuInstance 处理；GL 上下文复用 [frontend/duckstation](../src/frontend/duckstation)，函数加载器为 [frontend/glad](../src/frontend/glad)。UI 前端可替换，核心设备行为仍按 [总路由](README.md) 保留。

## 复刻检查

手动跑启动、暂停嵌套、单帧、reset、插拔卡、读档、切 renderer、开关窗口、退出等操作，观察是否死锁或残留输出。人工验证旋转/DPI/布局后的触摸落点、音频设备断开、摄像头缺失和配置持久化。另以无界面固定输入 runner 对照核心行为，使 UI 问题与模拟问题可分离定位。
