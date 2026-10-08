# 声道、混音、声音捕获与麦克风

[返回总路由](README.md)。DSi 的 DSP/I²S 接入见 [DSi 媒体](dsi-media.md)，宿主输出见 [前端](frontend.md)。

## 源码入口

[SPU.h](../src/SPU.h)、[SPU.cpp](../src/SPU.cpp)：`SPUChannel`、`SPUCaptureUnit`、`SPU::Mix`、`BufferAudio`、`ReadOutput`、`SetSampleRate`；[Mic.h](../src/Mic.h)、[Mic.cpp](../src/Mic.cpp)：`Start/Stop/Advance/ReadSample`；[blip-buf](../src/blip-buf)：输出重采样；[EmuInstanceAudio.cpp](../src/frontend/qt_sdl/EmuInstanceAudio.cpp)：宿主音频回调与节流。

## 三种时钟不能混用

系统调度的基准频率在相关设备中使用 33513982 Hz；SPU 的内部基准是其一半 `16756991.f`。普通 `MixInterval=1024` 系统周期，每次传给声道 512 个 SPU 周期；DSi 的另一速率使用 704/352。`Reset` 安排首个 SPU 事件，`Mix` 从上一事件时间继续安排下一次。

声道采样频率由其 Timer reload 决定，混音输出更新频率由 MixInterval 决定，最终宿主采样率由 `SetOutputSampleRate`/blip-buf 决定。将它们统一为“每秒 48000 次声道读取”会改变播放音高、FIFO 读取时间和捕获。

## 16 个声道

每个声道保存 CNT、源地址、Timer reload、loop position、length、音量、音量移位、pan、key-on、当前位置/采样、历史采样、ADPCM 解码器/循环状态、噪声状态和读取 FIFO。寄存器地址和长度单位的换算在 `SPU.h` 的 setter 中；例如 loop/length 转为字节，源地址按字对齐。

`SetCnt` 检测 enable 上升沿，`Start` 初始化实际播放；参数寄存器与播放中状态分开。`Run<type>` 按经过的 SPU 周期更新 Timer，可能一次推进多个源采样。FIFO 经 ARM7 总线补数据，不能让采样器直接借用永不更新的主 RAM 指针。

| 格式 | 核心状态/算法 | 边界 |
|---|---|---|
| PCM8 | 有符号 8 位读取并扩展 | 结束/循环、FIFO 边界 |
| PCM16 | 有符号 16 位读取 | 小端、地址/长度粒度 |
| ADPCM | 头部 predictor/index；每 nibble 更新差值和 step index | index 0–88，采样钳位，循环点恢复 predictor/index |
| PSG | 占空比表与相位 | 仅相应声道支持；8–13 为 PSG 路径 |
| Noise | 移位寄存器生成噪声 | 14–15 走 noise，保留相位/寄存器 |

ADPCM 代码使用特定饱和边界与高低 nibble 顺序，须逐步核对 `NextSample_ADPCM`，不要直接替换为任意同名音频库。单次/循环/保持模式决定停止和最后样本的处理。

## 混音与输出

`Mix` 推进声道，再按音量、pan 和控制字合成左右声道。声道 1/3 可被路由为专用输出，并可从普通 mixer 排除。声音捕获在相应混音阶段取值；最后才应用 master volume、bias、静音和钳位。

DS/DS Lite 的可选硬件位深退化到 10 位；DSi 不应用同样的 SOUNDBIAS，且 POWCNT 的静音只控制 NITRO 混音部分，DSP 仍可经 I²S 加入。插值选项是提升音质的宿主增强，原始路径默认不插值。

左右样本变化作为 delta 写入 blip-buf，`BufferAudio` 把它们转换为宿主速率并放入受锁保护的环形输出。`RunFrame` 末尾主动 flush，使本帧尾部声音可立即读取。`ReadOutput` 由 SDL 回调消费；`Sync/TrimOutput/DrainOutput` 处理生产消费速率差，宿主卡顿不应改变客体 Timer。

## 两路声音捕获

`SPUCaptureUnit` 持有目标、长度、Timer、写 FIFO、位置；它把混音样本写回客体内存。启动、buffer wrap、8/16 位打包和停止行为必须保持。当前 `Mix` 明确留有其他捕获源和相关硬件异常行为的 TODO，所以已实现的左右 mixer 捕获不能当作全部捕获模式。

## 麦克风

`Mic` 集中管理三类使用者：DS TSC 的 AUX 输入、DSi 麦克风 MMIO、DSP。`OpenMask` 避免某一路关闭时停掉其他使用者；延迟停止计数避免 DS 间歇采样频繁开关宿主设备。

`Platform::Mic_ReadInput` 契约为 signed 16-bit mono、约 47.6 kHz，并返回实际采样数。`FeedBuffer/Advance` 在模拟时间推进时消费；DS TSC 转为无符号 12 位 ADC 结果。输入不足、停止再启动和存档恢复都要有明确行为；恢复 Mic 状态时当前实现重新建立宿主采集并清输入缓冲，不保存未来的现实音频。

## 复刻检查

用已知短 PCM、固定 ADPCM 块、固定噪声初态对照逐样本输出与循环点；比较声音捕获写入 RAM 的字节和时间。检查快进/暂停/恢复后的环形缓冲、声道结束位和多路 Mic 引用。听感验证包含爆音、失真、左右声道与音高，但不能仅靠“听起来相同”验证 Timer 和 DMA。
