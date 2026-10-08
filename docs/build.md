# 构建边界、依赖与生成资源

[返回总路由](README.md)。目的：获得可对照的源码构建，并知道新模拟器需要复用哪些组件。

## 源码入口

[根 CMakeLists.txt](../CMakeLists.txt)、[src/CMakeLists.txt](../src/CMakeLists.txt)、[前端 CMakeLists.txt](../src/frontend/qt_sdl/CMakeLists.txt)、[net/CMakeLists.txt](../src/net/CMakeLists.txt)、[BUILD.md](../BUILD.md)、[CMakePresets.json](../CMakePresets.json)、[vcpkg.json](../vcpkg.json)、[flake.nix](../flake.nix)、[cmake](../cmake)、[CI 工作流](../.github/workflows)。

## 分层构建

根项目为 C11/C++17。`core` 静态库包含 DS、DSi、软件渲染、存档、设备和基础第三方库；JIT、OpenGL 和 GDB 按选项加入。DSi/Teakra 并非由 `BUILD_QT_SDL` 关闭：关闭 UI 仍构建 DSi 核心和 Teakra。

`BUILD_QT_SDL` 增加 Qt/SDL 可执行程序、Platform 实现、宿主图形和网络；`net-utils` 是前端引入的独立静态库。新前端可以链接 core 并实现 Platform，不必把 Qt 类型移入核心。

| 开关 | 本基线作用 |
|---|---|
| `BUILD_QT_SDL` | 是否构建桌面前端，默认开 |
| `ENABLE_JIT` | x86_64/ARM64 的条件选项；当前排除 Apple x86_64 |
| `ENABLE_OGLRENDERER` | 是否加入 GL/compute renderer 与 shader 生成 |
| `ENABLE_GDBSTUB` | 是否编译 GDB stub |
| `USE_QT6` | Qt6/Qt5，默认 Qt6 |
| `USE_VCPKG` | 引入 vcpkg 依赖配置 |
| `USE_SYSTEM_LIBSLIRP` | 使用系统 slirp 或内置源码 |
| `ENABLE_LTO/ENABLE_LTO_RELEASE` | 链接时优化，受工具链能力约束 |

## 本仓库 task

[mise.toml](../mise.toml) 管理本次文档与核心对照所需工具：CMake 3.31.12、uv 0.12.7。选版本前已查询 mise 的已安装版本；uv 复用已装版本，CMake 无已装版本后选择 3.31 系列。宿主 C/C++ 编译器和 SDK 由系统提供，本次为 Xcode AppleClang。

```sh
mise run docs-check
mise run build-core
```

`docs-check` 使用 uv 管理的 Python 3.13 和标准库，检查文档路由、链接与源码覆盖；`configure-core`/`build-core` 建立 `build/core`，关闭 Qt/SDL、JIT、GL 和 GDB，输出 `core` 静态库。这是最小参考构建，不是可运行的 headless emulator，也不生成游戏运行结果。

需要完整桌面构建时，先按 BUILD.md 准备当前平台的 Qt、SDL2、libarchive、zstd、faad2、ENet 和相关图形/网络依赖，再在 mise 中增加对应 configure/build task。新增命令行工具先查 `mise ls --installed <tool>` 并放入 `[tools]`；Python 通过 uv，只有实际引入 Rust 时才声明 `rust = "latest"`。

不要在同一 build 目录来回混用不同配置；前端、JIT/GL 对照构建各用独立目录。既有 presets/vcpkg/flake 是平台配置参考，不应让自动 agent 顺带重写这些上游路径。

## 依赖接入地图

| 依赖/目录 | 用途 | 复刻时必须保留的边界 |
|---|---|---|
| [teakra](../src/teakra) | DSi DSP 指令和内部设备 | memory/AHBM/mailbox/sample callbacks、时钟与状态 |
| [fatfs](../src/fatfs) | FAT 文件系统 | sector 回调、挂载寿命、错误码 |
| [tiny-AES-c](../src/tiny-AES-c)、[sha1](../src/sha1) | AES/NAND 等密码计算 | 字节序、key/IV/counter、精确输入布局 |
| [xxhash](../src/xxhash) | JIT/缓存等散列 | 缓存键/失效逻辑，非硬件哈希功能 |
| [blip-buf](../src/blip-buf) | 音频 delta 重采样 | 内部时钟、输出率、缓冲与 flush |
| [dolphin](../src/dolphin) | JIT emitter、CPU 能力、ABI | 宿主指令/寄存器/代码缓存维护 |
| [net/libslirp](../src/net/libslirp)、[net/pcap](../src/net/pcap) | 用户态网络栈和抓包接口声明 | Ethernet 帧、轮询/回调与线程 |
| ENet | LAN/部分 Netplay 宿主传输 | 可靠通道、连接/断开与包所有权 |
| [frontend/duckstation](../src/frontend/duckstation)、[frontend/glad](../src/frontend/glad) | GL context 与函数加载 | current context、线程与释放 |
| [qt_sdl/toml](../src/frontend/qt_sdl/toml) | 配置解析 | 类型、默认值、迁移和写入 |
| [qt_sdl/gif-h](../src/frontend/qt_sdl/gif-h) | GIF 输出辅助 | 前端媒体功能，不影响 CPU 模拟 |
| Qt、SDL2、libarchive、zstd、faad2 | UI/输入音频、资源装载、压缩/AAC | [前端](frontend.md) 的平台契约 |

以上“复用”是工程边界描述，不意味着将整库内部算法逐行重写。若新实现替换依赖，需要先验证相同接口和数据格式，而不是只换同名函数。

## 生成物与打包

`OpenGL_shaders/CMakeLists.txt` 通过 `cmake/MakeEmbed.cmake` 把 GLSL 生成嵌入头。改 shader 源时要重新生成，不直接只改构建目录中的头。compute shader 另在源头文件中。

[freebios](../freebios) 生成内置 BIOS 数据，core 使用 `FreeBIOS_Data.h`；[melonDLDI](../melonDLDI) 生成 homebrew 驱动，嵌入头由卡带模块使用。生成这些客体二进制需要对应交叉工具链，应单独按原 Makefile 分析，不因构建宿主 core 成功就宣称生成链已验证。

[res](../res) 与 `.qrc/.ui` 负责图标、窗口和平台打包资源；[tools](../tools) 的 mac 库收集、universal 合并、MSYS 分发是打包辅助。版本头由 CMake 从 `version.h.in` 生成；构建信息选项在 src/CMakeLists.txt。

源码授权声明在 [LICENSE](../LICENSE) 与各第三方目录/文件头；FreeBIOS 的随附说明和输入配置图像的 LICENSE 也须随复用范围核对。本文档没有改变这些声明。

## 已执行的验证

2026-10-08 在当前 macOS 工作区执行 `mise run build-core` 成功，使用 CMake 3.31.12、AppleClang 21.0.0。出现上游 Teakra CMake 旧兼容策略和 macOS 最低部署目标相关警告；未改动上游构建逻辑处理这些警告。没有运行 ROM、完整桌面、JIT/GL 或跨平台构建；这些仍是 [验证方案](validation.md) 的后续项目。
