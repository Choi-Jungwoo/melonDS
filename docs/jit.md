# JIT、块缓存与 fastmem

[返回总路由](README.md)。先完成 [CPU 解释器](cpu.md) 与 [内存](memory.md) 的行为基准；本章的机制用于提速，不改变客体 ISA。

## 源码入口

- [ARMJIT.cpp](../src/ARMJIT.cpp)、[ARMJIT.h](../src/ARMJIT.h)、[ARMJIT_Internal.h](../src/ARMJIT_Internal.h)：块构建/查找/失效及慢速访存。
- [ARM_InstrInfo.cpp](../src/ARM_InstrInfo.cpp)、[ARM_InstrInfo.h](../src/ARM_InstrInfo.h)：解码元信息、寄存器/标志读写与分支分析。
- [JitBlock.h](../src/JitBlock.h)、[ARMJIT_RegisterCache.h](../src/ARMJIT_RegisterCache.h)：块元数据、寄存器缓存。
- [ARMJIT_x64](../src/ARMJIT_x64)、[ARMJIT_A64](../src/ARMJIT_A64)：Compiler、ALU、LoadStore、Branch 和宿主汇编 linkage。
- [ARMJIT_Memory.cpp](../src/ARMJIT_Memory.cpp)、[ARMJIT_Memory.h](../src/ARMJIT_Memory.h)：地址分类/镜像、fastmem、页保护与故障处理。
- [ARMJIT_Global.cpp](../src/ARMJIT_Global.cpp)、[ARMJIT_Global.h](../src/ARMJIT_Global.h)、[dolphin](../src/dolphin)：全局平台能力、宿主代码 emitter/ABI 支持。

## 从 PC 到宿主代码

CPU 的 JIT 分支从流水线 PC 推算实际指令地址，通过 `SetupExecutableRegion/LookUpBlock` 查询；命中则 `ARM_Dispatch`，否则 `CompileBlock`。

`CompileBlock` 确定 CPU/ARM-Thumb 模式，归一化代码物理地址，检查已有块是否因重映射失效，取指并收集 `FetchedInstr`、地址范围/掩码、literal、分支和寄存器/标志信息。根据 MaxBlockSize 和分支边界结束，使用 x64/A64 compiler 生成代码，登记范围索引、保护页及 fast lookup。

优化包括 literal 和 branch；它们把“代码和常量目前是什么”变成缓存假设，必须参与失效。未直接翻译的行为可走解释/辅助函数；辅助调用前后还需兑现宿主 ABI 与客体状态一致性。

## 执行边界

生成代码需更新周期、PC/CPSR 和内存副作用，并在目标时间、IRQ、HALT、idle loop 或其他 stop 条件处返回调度。把多条 ARM 指令合并成块不能让新事件等到任意晚的块末尾。

汇编 linkage 和 offsets 对 CPU 结构布局有依赖：`ARMJIT_x64/ARMJIT_Offsets.h`、`ARMJIT_GenOffsets.cpp` 以及 C++ static_assert 防止偏移漂移。修改 ARM 字段、类型宽度或 register cache 后要同时核对两宿主后端。

## 失效不是只有写当前 PC

`LocaliseCodeAddress/LocaliseAddress` 把客体镜像归一到物理区域；同一物理内容可能从不同虚拟地址或 CPU 视图执行。`InvalidateByAddr` 查找关联块，撤下 fast lookup、处理 literal 依赖和其他范围记录，再回收或缓存块。

需要触发失效或重映射的来源：CPU store、DMA 写、共享内存另一 CPU 写、ITCM 内容/配置变化、VRAM/NWRAM/WRAM 改映射、存档恢复及客体 code-cache 操作。JIT 的代码失效与客体 ICache 可见性又不是同一层，必须按源路径保持先后关系。

## fastmem

fastmem 为两 CPU 预留宿主虚拟地址范围，把安全的客体内存页映射进去，直接执行宿主 load/store；不能直接映射的区域通过 slow path 访问。页面首次访问、代码页写入和 MMIO 可由异常/信号 handler 处理。

`FaultHandler` 确认故障来自 JIT，再尝试 `MapAtAddress` 或让 compiler 的 `RewriteMemAccess` 改写为慢路径；真实宿主错误不能全部吞掉。页大小、镜像、读写保护和宿主可执行内存策略分别处理，`JitEnableWrite/JitEnableExecute` 管理代码写/执行阶段。

慢路径负责访问宽度、对齐/旋转、TCM 与设备副作用；快路径与慢路径应得到相同客体结果。平台 ABI、页大小、信号上下文和 macOS JIT 权限不能照搬到别的系统。调试时关闭 fastmem 可避免预期故障信号干扰调试器。

## 分阶段复刻与检查

先实现不优化的 block translator，逐块与解释器比较寄存器、flags、内存和时间；随后启用 literal/branch，再引入 fastmem。特别验证自修改代码、不同镜像执行同一物理页、DMA 覆写块、TCM/MBK/VRAM 切换、块内 MMIO 提前产生事件、IRQ/HALT 和读档后缓存。

当前 CMake 仅对指定宿主架构/平台允许 JIT，具体条件见 [构建](build.md)。本次文档验证使用关闭 JIT 的最小核心，没有据此验证任何 JIT 宿主后端的运行正确性。
