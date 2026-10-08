# melonDS 逻辑与复刻文档：总路由

本套文档面向要阅读、移植或重新实现 DS/DSi 模拟器的 agent。输入是本目录和这份 melonDS 源码；输出目标是一个能够执行相同客体程序、保留设备可观察行为的新模拟器。先建立能对照的解释器与软件渲染版本，再实现 DSi、联网和优化路径。

源码基线：`906e9ebb27da8c6a715cd7abab4abfe8a8d29427`，整理日期：2026-10-08。后续源码变化应同时更新相关章节及 [源码覆盖表](source-map.md)。本文档描述该提交的实现，不把源码中的 TODO、HACK 或近似时序当作已经证实的硬件规格。

## 阅读协议

1. 首次进入，读 [整体架构](architecture.md)，确认状态所有者、时钟单位、核心与宿主边界。
2. 从下面路由选择当前任务；阅读主题中的“源码入口”“行为与状态”“复刻检查”。在源码中以列出的符号定位完整函数，连同调用者和存档函数一起读。
3. 实施新模拟器时，按 [复刻路线](reimplementation.md) 的阶段推进，以 [验证方案](validation.md) 的可观察结果判定完成。
4. 改变寄存器、映射、时序或缓存时，沿 [跨模块变更表](architecture.md#跨模块变更表) 补齐受影响的模块。

文档提供算法、状态与依赖的阅读路线；逐条指令分支、所有寄存器位掩码、像素舍入和协议字节布局仍以链接的源码为精确查表来源。复刻 agent 必须把这些源码分支落实为行为，不能用“已读文档”代替实现与验证。

## 按任务路由

| 正在处理的问题 | 主文档 | 连带阅读 |
|---|---|---|
| 实例组成、运行一帧、时钟和暂停 | [整体架构](architecture.md) | [系统控制与 DMA](system-control.md) |
| ROM 装载、BIOS、固件、直接启动 | [启动流程](boot.md) | [卡带](cartridge.md)、[DSi 核心](dsi-core.md) |
| ARM/Thumb、异常、CP15、缓存 | [CPU](cpu.md) | [内存与 MMIO](memory.md)、[JIT](jit.md) |
| 地址解码、映射、权限、访问宽度 | [内存与 MMIO](memory.md) | [视频时序与 VRAM](video-memory.md)、[DSi 核心](dsi-core.md) |
| IRQ、Timer、DMA、IPC、除法与开方 | [系统控制与 DMA](system-control.md) | [整体架构](architecture.md) |
| 扫描线、VBlank、显存银行、显示捕获 | [视频时序与 VRAM](video-memory.md) | [2D](video-2d.md)、[3D](video-3d.md) |
| 背景、精灵、窗口、混色、双屏 | [2D 渲染](video-2d.md) | [视频时序与 VRAM](video-memory.md) |
| 几何命令、矩阵、光栅化、纹理、GL | [3D 渲染](video-3d.md) | [视频时序与 VRAM](video-memory.md) |
| 声道、ADPCM、声音捕获、麦克风 | [声音](audio.md) | [DSi 媒体设备](dsi-media.md) |
| ROM 协议、卡带存档、DLDI、GBA 扩展 | [卡带](cartridge.md) | [持久化](persistence.md) |
| SPI、固件闪存、触摸、电源、RTC | [基础外设](peripherals.md) | [声音](audio.md)、[启动流程](boot.md) |
| 无线寄存器、本地联机、网络、Netplay | [无线与网络](wireless.md) | [前端与平台](frontend.md)、[DSi 存储与网络](dsi-storage.md) |
| DSi 启动、SCFG、MBK、NDMA | [DSi 核心](dsi-core.md) | [DSi 存储与网络](dsi-storage.md)、[DSi 媒体设备](dsi-media.md) |
| NAND、SD/MMC、AES、SDIO Wi-Fi | [DSi 存储与网络](dsi-storage.md) | [持久化](persistence.md) |
| DSP/Teakra/HLE、摄像头、I²C/I²S | [DSi 媒体设备](dsi-media.md) | [声音](audio.md)、[前端与平台](frontend.md) |
| 快照、游戏存档、目录同步、恢复 | [即时存档与持久化](persistence.md) | 所有设备的 `DoSavestate` |
| Qt/SDL、线程、输入、音频输出、配置 | [前端与平台](frontend.md) | [构建与依赖](build.md) |
| 动态翻译、代码失效、fastmem | [JIT](jit.md) | [CPU](cpu.md)、[内存与 MMIO](memory.md) |
| GDB、作弊、日志、调试入口 | [调试与作弊](debugging.md) | [验证方案](validation.md) |
| 选择复用范围、建立新工程 | [复刻路线](reimplementation.md) | [构建与依赖](build.md) |
| 检查模块是否漏读、找未知文件 | [源码覆盖表](source-map.md) | 对应主题文档 |

## 文档的证据边界

- “当前实现”：可在所列函数、字段或构建文件核对的事实。
- “建议”：为新模拟器安排的实现步骤和验证方法，未声称本仓库已有这些测试或接口。
- “限制”：已见于源码的未完成行为，或此次没有运行验证的部分。各章保留具体入口，供下一位 agent 接续。

覆盖核心、DSi 扩展、前端、平台实现、网络、调试、生成资源和第三方库的接入点。第三方 CPU/DSP、密码、压缩、文件系统实现仍由其随库源码解释；接入时需要保存的数据和时钟语义在本套文档说明。源码授权与各子目录声明见 [构建与依赖](build.md)。

## 维护与检查

`mise run docs-check` 检查本目录的本地 Markdown 链接、总路由可达性和源码覆盖表；它不证明模拟结果正确。`mise run build-core` 验证最小核心可构建。运行行为的验收标准单独定义在 [验证方案](validation.md)。
