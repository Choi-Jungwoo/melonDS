# 双 2D 引擎与像素合成

[返回总路由](README.md)。先读 [LCD/VRAM](video-memory.md)，其中定义何时锁存寄存器、绘制行和回写捕获。

## 源码入口

- [GPU2D.h](../src/GPU2D.h)、[GPU2D.cpp](../src/GPU2D.cpp)：A/B 引擎寄存器、`UpdateRegistersPreDraw/PostDraw`、窗口与坐标状态。
- [GPU2D_Soft.cpp](../src/GPU2D_Soft.cpp)、[GPU2D_Soft.h](../src/GPU2D_Soft.h)：`DrawScanline`、`DrawScanlineBGMode`、`DrawBG_*`、`DrawSprites`、`InterleaveSprites`、`DrawPixel`。
- [GPU_Soft.cpp](../src/GPU_Soft.cpp)：显示模式选择、主亮度、双屏输出及捕获；[GPU_ColorOp.h](../src/GPU_ColorOp.h)：颜色运算。
- [GPU2D_OpenGL.cpp](../src/GPU2D_OpenGL.cpp)、[GPU2D_OpenGL.h](../src/GPU2D_OpenGL.h)、[OpenGL_shaders](../src/OpenGL_shaders)：对应加速实现。

## 状态分层

两引擎各有四背景、精灵、窗口、mosaic、混色和主亮度相关状态；A 引擎还可以把 3D 作为 BG0，并参与主显示/捕获路径。`DispCnt`、`BGCnt`、滚动、仿射矩阵与参考点、窗口边界/掩码、blend 控制属于客体寄存器。

内部状态另有 `DispCntLatch`、仿射参考点的 internal/reload 值、mosaic 行位置和启用锁存。寄存器写入、当前行生效、下一行递增不是同一时刻。新渲染器应先复制这些时序状态，再考虑像素缓存。

## 一行的合成流程

```text
扫描线状态/窗口更新
    → 读取锁存后的 DISPCNT 与图层使能
    → 准备精灵行及 backdrop，计算每像素的窗口图层/效果掩码
    → 按窗口许可和优先级合入 BG 与 OBJ（保留最上层和第二层）
    → 半透明 OBJ / 3D alpha / BLDCNT 效果
    → 显示模式和主亮度
    → LCD 输出；如启用则生成 VRAM 捕获数据
```

实际调用分散在 `SoftRenderer2D` 与外层 `SoftRenderer`。`BGOBJLine` 为每个像素保留最上层与第二层，供 `ColorComposite` 选择混色目标；窗口在图层插入时就参与判断。必须保留像素的层标识与优先级直到效果阶段，过早变成 RGB 会丢失目标层选择、窗口和 alpha 条件。

## 背景模式

`DrawScanlineBGMode<bgmode>` 是模式组合的权威入口：BG0/BG1 通常为 text；BG2 在 mode 2/4 为 affine、mode 5 为 extended；BG3 在 mode 1/2 为 affine、mode 3–5 为 extended。mode 6/7 有独立路径，不从常用模式推断。A 的 DISPCNT 3D 位可替换 BG0。

| 路径 | 输入到像素的步骤 | 易错点 |
|---|---|---|
| `DrawBG_Text` | 滚动坐标 → tile map → tile index/flip/palette → 4/8 bpp 像素 | 屏块布局、调色板 0 透明、扩展 palette、镜像 |
| `DrawBG_Affine` | 固定点参考坐标 + PA/PC 按列推进 → tile/palette | 越界 wrap、符号扩展、每行参考点更新 |
| `DrawBG_Extended` | 控制位选择扩展 tile 或 bitmap → 像素 | indexed/direct color、尺寸、透明位和地址粒度 |
| `DrawBG_Large` | 大位图坐标与窗口 | A/B 能力与模式限制 |
| `DrawBG_3D` | 几何光栅行 → BG0 插入 | 3D alpha 与普通 BG 透明并不等价 |

仿射和颜色使用固定点/整数运算。用浮点“近似相同”可能在边界像素和负坐标处改变取整结果。mosaic 既有横向复用也有跨行锁存，不能只对最终画面做马赛克滤镜。

## 精灵

OAM 的 128 条对象记录给出形状/尺寸、位置、tile、优先级、palette、仿射矩阵索引和模式。`DrawSprites` 先选出当前行相关对象，再由 `DrawSprite_Normal` 或 `DrawSprite_Rotscale` 生成行数据。

需要覆盖：坐标回绕、禁用对象、仿射 double-size 边界、翻转、1D/2D tile 映射、bitmap OBJ、半透明 OBJ、OBJ window、mosaic、同优先级按 OAM 顺序竞争。精灵提前一行预渲染，寄存器/OAM 在行间更改时必须按源码锁存点观察结果。

## 优先级、窗口和颜色

软件路径从低到高覆盖各优先级，背景同级有固定顺序，OBJ 在对应层间插入。不能仅对所有像素按一个 depth 数排序。`CalculateWindowMask` 合并 WIN0、WIN1、OBJ window 和外部区域，各区域可独立启用 BG/OBJ 与颜色效果。

BLDCNT 决定第一/第二目标层和效果，BLDALPHA/BLDY 给出系数。半透明 OBJ、3D alpha、透明 backdrop 的处理条件不同。保持源码的内部颜色精度、系数钳位和舍入；最终 BGRA 转换在输出侧。主亮度与 layer blend 是两次不同操作。

外层显示控制可以选择常规图层、VRAM 显示、主存 FIFO 或关闭显示；捕获源和 LCD 输出也可能不同，因此“最终屏幕像素”不能通用于所有捕获输入。

## 加速路径与复刻检查

OpenGL 2D 使用图层/精灵预处理和 compositor shader，仍须服从同一锁存、窗口与显存一致性。先以软件路径和原分辨率建立对照，再增加放大与硬件后端。

准备一组可重复视觉场景：每类 BG 模式、同优先级 BG/OBJ、窗口交叠、半透明精灵、负仿射坐标、mosaic、上下屏交换、逐行改寄存器及捕获。保存参考截图、结果截图、差分图和使用的寄存器配置；人工核对透明边缘与优先级，不为 UI 或视觉布局添加代码测试。
