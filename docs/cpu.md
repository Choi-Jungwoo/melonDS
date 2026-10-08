# ARM9、ARM7、解释器与 CP15

[返回总路由](README.md)。数据总线在 [内存](memory.md)，调度与 IRQ 在 [系统控制](system-control.md)，动态翻译在 [JIT](jit.md)。

## 源码入口

| 文件 | 读什么 |
|---|---|
| [ARM.h](../src/ARM.h)、[ARM.cpp](../src/ARM.cpp) | `ARM`、`ARMv5`、`ARMv4`，寄存器、模式切换、`JumpTo`、`Execute`、异常、计时 |
| [ARMInterpreter.cpp](../src/ARMInterpreter.cpp)、[ARM_InstrTable.h](../src/ARM_InstrTable.h) | ARM/Thumb 分派表及各指令入口 |
| [ARMInterpreter_ALU.cpp](../src/ARMInterpreter_ALU.cpp) | 条件码、移位、算术、乘法、饱和及各架构差异 |
| [ARMInterpreter_LoadStore.cpp](../src/ARMInterpreter_LoadStore.cpp) | 单次/多次传送、未对齐、符号扩展、写回与时序 |
| [ARMInterpreter_Branch.cpp](../src/ARMInterpreter_Branch.cpp) | B/BL/BX/BLX、SWI、PSR 访问和异常返回 |
| [CP15.cpp](../src/CP15.cpp) | ARM9 控制、TCM、保护区域、指令缓存和数据访问 |

## 架构状态

ARM9 用 `ARMv5`，ARM7 用 `ARMv4`。它们共享接口，但不是同一套语义加一个频率参数。需要显式保存：R0–R15、CPSR、各异常模式 banked 寄存器/SPSR、当前与预取指令、周期累计、IRQ 输入、HALT 状态，以及 ARM9 的 CP15/TCM/cache 状态。

R15 是实现中的流水线 PC，不能在所有指令里当作“当前指令地址”。读 PC、存 PC、分支目标、LR 返回地址和异常返回均有偏移差异。`JumpTo`、`FillPipeline`、`RestoreCPSR` 是这些约定的集中入口；新解释器应先写出自己的 PC 不变量，再一一与源函数对照。

## 解释执行

`Execute` 首先处理 HALT 和中断，随后执行到对应 `Timestamp >= Target`。Thumb 由 CPSR T 位选择；ARM 条件码通过 `CheckCondition` 和 `ConditionTable` 判断。ARM 解码索引由指令 bit 4–7 与 bit 20–27 组合；Thumb 使用自己的表。v5 的无条件 BLX immediate 有专门分支，不能简单把条件 `0xF` 当作全部跳过。

每条指令先按当前流水线取出指令并预取后继，再运行处理器函数，然后处理 HALT/IRQ 和周期。分支或写 PC 通过 `JumpTo` 重建预取状态。周期来自取指、数据读写和内部周期的组合，使用 `AddCycles_*`；条件失败也有取指周期。

### 指令族的实现清单

| 指令族 | 需要保留的边界 | 源码对照 |
|---|---|---|
| 逻辑、加减、比较 | N/Z/C/V 各自更新条件；带进位的宽算术；写 PC+S 时恢复 SPSR | ALU、`RestoreCPSR` |
| barrel shifter | shift=0、32、>32，RRX，寄存器移位的低位与 carry | ALU 的各移位分支 |
| MUL/长乘/Q/CLZ | 有符号性、结果宽度、标志、v4/v5 支持及内部周期 | ALU、指令表 |
| LDR/STR 与半字/符号读 | 地址对齐、旋转/扩展、前后索引、写回与 PC 特例 | LoadStore |
| LDM/STM/PUSH/POP | 空列表、base 在列表中、用户寄存器视图、首笔 nonseq 与后续 seq | LoadStore |
| B/BL/BX/BLX | ARM/Thumb 切换、链接地址、对齐与流水线刷新 | Branch、`JumpTo` |
| SWI/未定义/abort/IRQ | 目标模式、SPSR、LR 偏移、向量基址、屏蔽位 | ARM、Branch、CP15 |
| MRS/MSR/MRC/MCR | 可写位、特权、banked 切换、CP15 寄存器副作用 | Branch、CP15 |

这张表是覆盖清单，不替代指令表。复刻时按 `ARM_InstrTable.h` 的所有有效分派补齐处理器，并记录架构不支持路径，避免只实现编译器常用指令。

## 模式和异常

`UpdateMode` 处理 banked 寄存器交换，包括 FIQ 的额外 R8–R12；`RestoreCPSR` 恢复异常前模式。`TriggerIRQ` 先检查 CPSR 的 IRQ 屏蔽，再保存返回状态并跳异常向量。`PrefetchAbort` 与 `DataAbort` 分开，因为返回地址和发生阶段不同。

CPU IRQ 输入由 `NDS::UpdateIRQ` 计算，但 HALT 的唤醒判断并不等价于“CPU 将立即进入 IRQ”。ARM7 与 ARM9 的 IME 参与条件不同，见 [系统控制](system-control.md)。`Halted==2` 是调度中断当前批次的实现状态，应与客体 HALT 区别保存和处理。

## ARM9 CP15、TCM 和缓存

`CP15Reset/Read/Write` 的寄存器 ID 是指令字段编码后的内部索引。实现应以 `CP15Write` 的 switch 为表，记录位掩码及触发的区域重建，不只保存一个寄存器数组。

- `UpdateDTCMSetting/UpdateITCMSetting`：计算启用、范围和镜像。物理 ITCM 32 KiB、DTCM 16 KiB，客体配置的窗口大小与物理容量不是同一件事。
- `UpdatePURegion/UpdatePURegions`：保护区域的覆盖优先级、读写/执行权限、cache 属性；由此生成快速访问表。
- `CodeRead32`：优先考虑 TCM、保护和取指 cache；`ICacheLookup`、按地址或整体失效影响取指内容与时序。
- `DataRead*/DataWrite*`：执行权限、TCM 与总线分派，并累计数据访问周期；`*32S` 为顺序访问路径。
- `UpdateRegionTimings`：当总线或 DSi 频率变化时更新 CPU 侧时间表。

当前实现不应被概括为“完整仿真所有 ARM9 cache 微架构”。读 CP15 注释，区分已模拟的指令 cache、数据访问时序模型和尚待验证的硬件细节。JIT/fastmem 是宿主优化，不能取代客体 cache 可观察行为。

## 复刻检查

从 RAM 执行小程序，比较寄存器、CPSR、异常 LR/SPSR、内存写轨迹及周期。测试须包含两架构的差异，而不是同一函数输出与自己重算的期望值比较。重点输入是移位边界、溢出、未对齐、base/writeback 冲突、Thumb 切换、IRQ 返回、TCM 重映射和写代码后 cache 失效。逐条 trace 用解释器作基准，JIT 应在解释器已稳定后加入。
