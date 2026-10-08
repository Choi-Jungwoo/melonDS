# 对照验证、完成标准与已知限制

[返回总路由](README.md)。本章给新模拟器定义验收，不是已执行的 ROM 兼容性报告。

## 区分证据层次

| 证据 | 能说明什么 | 不能说明什么 |
|---|---|---|
| 文档链接/覆盖检查 | 页面可达、源码有归属 | 描述一定正确、设备已实现 |
| core 构建 | 当前编译配置可生成库 | Platform 已链接、ROM 能运行 |
| 单设备/指令输入 | 指定边界有正确结果 | 整机所有时序正确 |
| 固定 ROM 场景 | 该资源/配置/输入路径可运行 | 所有游戏、所有模式兼容 |
| 与 melonDS 差分 | 是否匹配该基线实现 | 该基线没有硬件误差 |
| 独立实机 trace | 对测试条件下硬件行为的更强证据 | 未覆盖的边界也正确 |

参考程序也可能有 TODO 或缺陷。出现差异时先决定是在复现实现还是校准硬件；如果改进某个源码近似，应记录输入和新证据，而不是悄悄让两种语义混在一起。

## 固定对照条件

每次对照保存 manifest：源码提交、新实现版本、console、BIOS/firmware/ROM/save/NAND/SD 的本地摘要、启动方式、JIT/renderer/HLE、音频设置、RTC 初态、输入序列与资源副本位置。关闭或固定实时 RTC 同步、随机 MAC、现实摄像头/Mic 和网络来源。

不把 ROM 或个人存储内容随测试报告发布。报告需要的是可识别的本地资源摘要、生成自制输入的方法和可重放步骤。

建议保留的最小 trace：

```text
system_cycle, console, cpu_or_device, pc_or_event,
operation, address, width, value, irq_state, stop_state
```

日志中的 PC 要注明是否已去掉流水线偏移；时间必须统一成系统周期。先比较最早差异，而不是直到崩溃才看最后一屏日志。

## 逐模块验收矩阵

| 模块 | 代表输入 | 比较对象 |
|---|---|---|
| ARM/Thumb | 手工构造边界指令、模式切换、异常返回 | R/CPSR/SPSR、PC、访存和周期 |
| CP15/总线 | TCM/PU/cache 改配置，别名访问、8/16/32 位 MMIO | 数据、abort、权限、取指和时序 |
| 调度 | 相同时间事件、新事件缩短 target、HALT/睡眠 | 执行顺序、时间不倒退、唤醒与剩余事件 |
| Timer/IRQ | 多次溢出、级联、使能/清除顺序 | counter、IF/IRQ、异常进入点 |
| DMA/NDMA | count=0、地址重装、FIFO 阻塞、跨 target | 写序、剩余量、CPUStop、IRQ 时间 |
| IPC | 空满、溢出、IRQ enable 时已满足条件 | 返回值、队列位置、双方 IRQ |
| 卡带/SPI | 分段命令、chip select、读写 ready、保存页 | 每字节/字响应、busy、DMA、落盘内容 |
| LCD/VRAM | VCOUNT 改写、重叠映射、捕获后立即读取 | 标志/事件、银行数据、捕获内存 |
| 2D/3D 视觉 | 固定图层/几何/纹理/窗口/混色场景 | 参考图、结果图、差分图人工检查 |
| SPU/Mic | 已知 PCM/ADPCM、循环、noise、FIFO 捕获 | 样本、长度、写 RAM 时间与内容 |
| RTC/输入 | BCD 跨日/闹钟、AND/OR 按键、触摸协议 | 返回寄存器、IRQ、ADC 序列 |
| NAND/SD/AES | 可丢弃镜像、已知 crypto 向量、块读写 | 扇区内容、FIFO、水位、MAC、错误 |
| DSP/媒体 | 已知 microcode、mailbox、固定相机帧 | 共享 RAM、回复/IRQ、音频/图像数据 |
| 网络 | 固定帧回放、双实例 CMD/reply/ACK | 包顺序/模拟时间、设备 RX RAM、超时 |
| 快照 | 在每类事务进行中保存/恢复 | 同样输入后的机器状态与介质策略 |
| JIT/GL/HLE | 与基准相同输入，含失效/切后端 | 客体状态与输出；性能另记 |

测试期望来自手工可推导的小输入、独立硬件记录或固定的参考执行。不要从被测实现复制同一段运算再充当 oracle；“生成后能自己读回来”只能是格式自洽检查，不能单独证明正确。UI、视觉布局以人工场景核对，不为它们添加代码测试。

## 集成验收顺序

1. 自制两 CPU ROM：各写 RAM 标志、通过 IPC 交换、等待 Timer IRQ、触发 DMA；输出检查与渲染无关。
2. DS 直接启动与固件启动分别验证；随后扩充 2D/3D/声音、保存、外设的固定场景。
3. 快照重放：在 DMA、SPI、GX FIFO、音频循环和 SD 传输中途分别保存；复原相同介质副本并继续同样输入。
4. DSi 兼容/原生模式、DSP、存储和媒体分别加入；再增加本地 MP 和 LAN。
5. 最后开启 JIT、fastmem、GL、DSP HLE，逐项比较基准，避免同时引入多种差异来源。

每项完成要有明确配置、输入、比较字段和结果。停止条件是目标范围的矩阵全部具备证据或明确列出未支持项，而不是运行时间长、截图漂亮或日志没有报错。

## 源码已明确的限制索引

| 位置 | 当前限制/待验证点 | 影响 |
|---|---|---|
| `NDS::InitTimings` | VRAM 空洞/银行划分、DSi 时序 TODO | 总线周期不能当作完整硬件规格 |
| `DMA.cpp` 顶部说明 | nonseq、地址模式等时序 TODO | 最终数据相同仍可能时序不同 |
| `GPU::StartHBlank/BlankFrame` | 部分绘制/锁存时点近似，BlankFrame 渲染处理 TODO | 行中效果和睡眠显示 |
| `GPU3D.cpp` 开头 | hang/test result/锁存待研究 | 极端命令与状态读取 |
| `SPU::Mix` | 其他声音捕获源未完成 | 特殊录音/反馈 |
| `DSi::RunNDMAs/StallNDMAs` | round-robin/subblock/stall 等未完整实现 | DSi DMA 仲裁 |
| `DSi_AES/DSi_SD` | 延迟与部分协议状态 TODO | DMA/IRQ 时间、边界命令 |
| `DSi_DSP` | AHBM 仲裁、部分 FIFO IRQ/地址步进待确认 | DSP 同步与传输 |
| `DSi_NWifi` | 协议 HLE、硬编码/未实现命令 | 固件/联网范围 |
| `Netplay.cpp/MPInterface::Set` | 输入/镜像同步多处禁用，未接入 Netplay 后端 | 不等于完整在线同步 |
| `NDS::DoSavestate/DSi.h` | KeyInput 与部分 GPIO 保存缺口 | 确定性恢复的范围 |
| `EmuInstance::loadState/saveState` | 无加载失败自动回滚、非原子覆盖写路径 | 损坏/失败时恢复策略 |
| `Platform::GBAModeNotSupported` | 不执行整台 GBA 模式 | Slot-2 支持不等于 GBA 模拟器 |

对应源码链接可从主题章节及 [覆盖表](source-map.md) 进入；这张表记录复刻边界，不是本次修复清单。

## 本次文档工作的验证范围

已阅读主调度、模块接口与关键实现分支，建立文件路由；已实际构建关闭 Qt/JIT/GL/GDB 的 core。文档检查任务只做本地结构检查。没有运行 BIOS/ROM、网络会话、截图对照、音频对照或实机测试；各章节的“复刻检查”是留给新实现的验收步骤。
