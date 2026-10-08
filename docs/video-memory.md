# LCD 时序、VRAM 银行与显示捕获

[返回总路由](README.md)。像素生成继续读 [2D](video-2d.md) 与 [3D](video-3d.md)。

## 源码入口

[GPU.h](../src/GPU.h)、[GPU.cpp](../src/GPU.cpp)：`StartFrame`、`StartScanline`、`StartHBlank`、`FinishFrame`、`MapVRAM_*`、`ReadVRAM_*`/`WriteVRAM_*`、`MakeVRAMFlat_*Coherent`、`CheckCaptureStart/End`、`SyncVRAMCaptureBlock`。具体捕获实现由 [GPU_Soft.cpp](../src/GPU_Soft.cpp) 或 [GPU_OpenGL.cpp](../src/GPU_OpenGL.cpp) 承担。

## LCD 的两个坐标

普通一帧 263 行，每屏 256×192。源码 `LINE_CYCLES = 355*6 = 2130` 系统周期，`HBLANK_CYCLES = 48+256*6 = 1584` 是从行起点到 HBlank 的偏移，剩余 546 周期到下一行。普通帧为 560190 系统周期。

函数参数 `line` 是本次帧实际经过的行数；`VCount` 是软件可写、按 9 位回绕的硬件寄存器。两者可能不同。不得简单把帧结束写成固定执行 263 次：`VCount` 可延长或改变一帧，`RunFrame` 返回实际扫描线数供前端节流。

| 时点 | 当前调用链与可观察效果 |
|---|---|
| 帧开始 | 锁存屏幕启用、确定是否需要显示 FIFO；`StartScanline(0)` |
| 每行开始 | 清 HBlank、更新 VCount、窗口；检查逐行 DMA/FIFO；按自然 VCount 转移处理状态 |
| VCount=0 | 捕获 enable 满足时开始捕获 |
| VCount=192 | VBlank IRQ、结束捕获、清 FIFO 指针、等待 3D 完成、触发 VBlank DMA、几何交换、渲染器 VBlank |
| VCount=262 | 清 VBlank 标志 |
| 每行 HBlank | 锁存 2D 寄存器，绘制可见行，预绘下一行精灵，触发 HBlank DMA/IRQ |
| VCount=215 的 HBlank | 启动 3D 光栅化任务 |
| VCount=262 或 511 的 HBlank 后 | `FinishFrame` 换显示缓冲并记录行数 |

`StartScanline` 先按自然递增后的 VCount 处理关键转移，再应用上行的软件写入覆盖，最后比较 VMatch。跳过 261→262 会影响 VBlank 标志和下一次 IRQ。这个顺序比“寄存器是否支持写”更重要。

当前 2D 绘制集中在 HBlank；代码注明某些锁存/绘制实际应在行起点后 48 周期。它是明确的实现近似，不应写成逐像素精确扫描模型。

## VRAM 物理银行与视图

| 银行 | 物理容量 | 映射实现 |
|---|---|---|
| A、B、C、D | 各 128 KiB | `MapVRAM_AB`、`MapVRAM_CD` |
| E | 64 KiB | `MapVRAM_E` |
| F、G | 各 16 KiB | `MapVRAM_FG` |
| H | 32 KiB | `MapVRAM_H` |
| I | 16 KiB | `MapVRAM_I` |

合计 656 KiB。VRAMCNT 的 enable/MST/offset 决定银行连接到 LCDC、A/B 背景、A/B 精灵、扩展调色板、3D 纹理/调色板或 ARM7。每个银行支持的组合不同，逐一读对应 `MapVRAM_*` switch，不能给九银行共用一张无差别表。

`VRAMMap_*` 保存银行位集合而不是单指针。多个银行重叠时，相关读取按位 OR，写入广播到所有匹配银行；未映射和 byte 写的行为按访问模板实现。物理内容在改映射时保留。ARM7 只能看到已分配给它的银行。

Palette 和 OAM 是另两组物理存储，有自己的脏标志与访问约束；不要算进这 656 KiB，也不要混同普通主 RAM。

## 平坦缓存和捕获一致性

为加速渲染，GPU 从银行化内存构建平坦 BG/OBJ/纹理视图，并按脏块更新。`MakeVRAMFlat_*Coherent` 的任务是使指定消费者看到最新视图；银行改用途、内容写入和映射重叠都可能使缓存失效。

显示捕获的输入可以来自 2D/3D 画面、VRAM 或显示 FIFO，按控制字选择大小、源、目标和混合。捕获写回 VRAM，之后游戏可将结果当纹理或背景读取，所以它是客体数据路径，不只是截图功能。

OpenGL 渲染可让最新捕获结果暂留在宿主 GPU；`VRAMCaptureBlockFlags`、`AllocCapture`、`SyncVRAMCapture` 与 `SyncAllVRAMCaptures` 追踪这件事。CPU、DMA、纹理消费者和即时存档读取前必须完成相应回写；切银行用途或覆盖旧结果也要处理这一状态。

显示 FIFO 由 `DisplayFIFO/SampleDisplayFIFO` 分批消费，按需要安排事件并产生 DMA 请求。不能把整行输入视为在行末才一次读入，DMA 与读取时间之间存在客体可见反馈。

## Renderer 边界

`Renderer` 统一提供逐行绘制、精灵预处理、3D 开始/等待、VBlank、捕获同步、取帧缓冲和存档钩子。软件渲染的输出为每屏 256×192、32 位 BGRA；加速渲染可能交付其他类型的资源，调用者必须检查接口结果。

`ScreenSwap` 决定哪个引擎输出送哪块 LCD，前端横竖排列/缩放则属于 [前端](frontend.md)。切换 renderer 时需考虑旧任务结束、VRAM 内容同步和新缓存初始化。

## 复刻检查

先验证 LCD 标志和 IRQ/DMA 时间，再验证像素：记录一帧事件轨迹，并专测 VCOUNT 覆盖；把两个银行映射到同一视图验证 OR/广播；捕获后立即由 CPU、DMA 和 3D 各读一次。视觉结果通过确定输入的截图和差分图人工核对，UI 布局无需写代码测试。捕获产生的内存数据则可按硬件协议记录作比较。
