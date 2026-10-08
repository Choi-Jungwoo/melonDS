# 3D 命令、几何引擎与光栅化

[返回总路由](README.md)。几何引擎有独立的客体状态与耗时；输出通过 [2D](video-2d.md) 的 BG0 和 [视频捕获](video-memory.md) 进入屏幕/内存。

## 源码入口

| 部分 | 文件与符号 |
|---|---|
| 几何与命令 | [GPU3D.cpp](../src/GPU3D.cpp)、[GPU3D.h](../src/GPU3D.h)：`CmdNumParams`、`WriteToGXFIFO`、`CmdFIFOWrite/Read`、`ExecuteCommand`、`Run` |
| 顶点/多边形 | 同上：`SubmitVertex`、`SubmitPolygon`、`CalculateLighting`、矩阵和裁剪函数、`VBlank` |
| 软件光栅 | [GPU3D_Soft.cpp](../src/GPU3D_Soft.cpp)、[GPU3D_Soft.h](../src/GPU3D_Soft.h)：`RenderFrame`、`RenderPolygons`、`RenderScanline`、`RenderPolygonScanline`、`RenderPixel` |
| 普通 GL | [GPU3D_OpenGL.cpp](../src/GPU3D_OpenGL.cpp)、[GPU3D_OpenGL.h](../src/GPU3D_OpenGL.h) |
| Compute GL | [GPU3D_Compute.cpp](../src/GPU3D_Compute.cpp)、[GPU3D_Compute.h](../src/GPU3D_Compute.h)、[GPU3D_Compute_shaders.h](../src/GPU3D_Compute_shaders.h) |
| 纹理缓存 | [GPU3D_Texcache.cpp](../src/GPU3D_Texcache.cpp)、[GPU3D_TexcacheOpenGL.cpp](../src/GPU3D_TexcacheOpenGL.cpp) |

## 命令接收与反压

GXFIFO 接口允许一个 32 位字打包四个 8 位命令，随后按 `CmdNumParams[command]` 接收参数；也有直接写命令寄存器的路径。零参数命令的推进、全零命令字和跨多个写入的参数累积都在 `WriteToGXFIFO` 中处理。

当前实现包含 256 项命令 FIFO、4 项命令 pipeline、64 项 stall queue。最后一项是处理一次 STM 等多次写入越过 FIFO 容量的宿主实现缓冲：发生时设置 `GXFIFOStall`，不能把它解释为硬件多了 64 个普通可见 FIFO 项。

读取 pipeline 后从 FIFO 补充，消耗 stall queue，按条件解除阻塞，并重新检查 DMA/IRQ。FIFO 小于 128 时请求 GX DMA；IRQ 模式可以选择小于 128 或为空。读取 GXSTAT 会先推进 `Run`，因此忙/空/测试状态必须与当前时间一致。

## 几何状态和命令覆盖

| 命令族 | 必要状态与行为 |
|---|---|
| matrix mode/push/pop/store/restore/load/multiply/scale/translate | projection、position、vector、texture 矩阵及各栈、栈指针与错误标志 |
| color/normal/texcoord/material/light/shininess | 当前颜色、法线、材质、灯光向量/颜色、shininess 表，纹理坐标生成模式 |
| vertex 16/10/XY/XZ/YZ/diff | 部分坐标保留与符号扩展，当前顶点、矩阵变换，固定点截断 |
| begin/end | triangles/quads/strips 的装配、顶点复用与绕序 |
| polygon/texture/palette attributes | 属性锁存时点，剔除面、alpha、ID、阴影、纹理参数 |
| swap buffers | `FlushRequest`/`FlushAttributes`，在 VBlank 交换几何 RAM |
| viewport、box/position/vector test | 裁剪/透视后的结果寄存器与 busy 状态 |

完整 opcode、参数数量、执行延迟直接对照 `CmdNumParams` 和 `ExecuteCommand`。几何计时包含顶点流水线槽、polygon setup、阻塞与可并行命令；逐命令加一个固定耗时不足以保留 FIFO 反馈。

顶点保存齐次坐标、颜色、纹理坐标及裁剪状态。`SubmitPolygon` 完成裁剪/剔除、视口变换、深度/W、退化/线多边形标志和排序键；`Polygon` 保存其引用顶点和属性。几何 RAM 双银行，每银行 6144 顶点、2048 多边形，溢出处理要跟随源代码而非无限增长容器。

## 交换与排序

`VBlank` 在有 flush 时把不透明和半透明多边形分开，按排序属性用 stable sort。排序键主要包含 bottom Y、top Y，等键保留原顺序；是否对半透明多边形自动排序受 flush 属性控制。

随后锁存渲染参数、换几何 RAM 银行并清本轮计数。无新 flush 时可以复用先前几何，并比较渲染配置判断帧是否相同。`GPU::StartHBlank` 在 VCount 215 启动光栅，下一 VBlank 等待完成；这与“命令刚写完就立即画到屏幕”不同。

## 软件光栅算法路线

1. 按 clear color/depth/属性或 clear bitmap 初始化背景缓冲。
2. `SetupPolygon` 建左右边缘，逐行更新边缘插值；退化多边形和线走专门规则。
3. 每像素插值深度/W、颜色和纹理坐标，执行纹理寻址及格式解码。
4. 应用材质模式（调制、decal、toon/highlight 等）、alpha test、深度/多边形 ID 规则，更新颜色及属性缓冲。
5. 阴影 mask/阴影多边形、半透明重复覆盖规则与普通不透明路径分开处理。
6. 按属性处理边缘标记、抗锯齿覆盖和雾，交付 2D 合成需要的颜色/alpha。

软件源码有精确边缘覆盖、整数插值和深度比较特例；不能仅用宿主标准三角形光栅 API 保证一致。Z-buffer/W-buffer 选择、相等深度、top/bottom 边界以及半透明 polygon ID 都会改变结果。

### 纹理

覆盖 A3I5、2/4/8 位 indexed、4×4 压缩、A5I3 和 direct color；格式 0 的无纹理路径也有语义。地址生成包括尺寸、repeat/flip、透明 palette index 0 与调色板基址。4×4 压缩还读取模式/调色板信息并按模式生成中间色，须保持整数舍入。

纹理缓存的键不仅是 VRAM 地址，还包括格式、尺寸、palette 和内容版本。VRAM 银行重映射、palette 写、显示捕获产生的内容变化都要使缓存更新。先把银行和平坦视图做正确，后加缓存。

## OpenGL 后端

普通 OpenGL 与 compute renderer 都复用几何结果，但采用不同的宿主绘制/计算流程；[OpenGL_shaders](../src/OpenGL_shaders) 与 compute shader 头是执行逻辑的一部分。放大坐标、改进多边形等设置是宿主增强项，不应变成新核心的默认硬件定义。

shader 编译可能分步进行，前端在尚未完成时不跑正常帧。后台渲染线程、GL context、纹理缓存和捕获回读必须按 `FinishRendering`、存档钩子及 renderer 切换顺序同步。

## 复刻检查与限制

协议层记录 FIFO 水位、GXSTAT、DMA/IRQ 与 stall 时间；几何层比较命令输入后的矩阵、顶点和多边形。视觉层用固定 display list 生成各纹理格式、裁剪、W/Z、透明交叠、阴影、雾和边缘场景，人工检查原分辨率截图及差分图。

`GPU3D.cpp` 对 GPU hang、测试结果何时可见、某些锁存还保留 TODO。文档能引导复现当前实现，不把它提升为所有边界都已达到实机像素/周期精度的结论。
