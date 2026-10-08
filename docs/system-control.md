# IRQ、Timer、DMA、IPC 与数学单元

[返回总路由](README.md)。这些单元共同决定 CPU 何时能继续运行；依赖 [主调度](architecture.md) 和 [MMIO](memory.md)。

## 源码入口

[NDS.h](../src/NDS.h) 定义 IRQ 编号、CPUStop 位、Timer、事件槽与 IPC FIFO；[NDS.cpp](../src/NDS.cpp) 实现 `UpdateIRQ`、`HaltInterrupted`、`RunTimers`、`TimerStart`、`CheckDMAs`、IPC 的两 CPU IO 分支、`StartDiv/DivDone/StartSqrt/SqrtDone`。[DMA.cpp](../src/DMA.cpp)、[DMA.h](../src/DMA.h) 为通道状态机；[DMA_Timings.cpp](../src/DMA_Timings.cpp) 和 [DMA_Timings.h](../src/DMA_Timings.h) 为主 RAM burst 时序；[FIFO.h](../src/FIFO.h) 为固定容量队列。

## IRQ 与唤醒

每个 CPU 独立保存 `IME`、`IE`、`IF`；外设 `SetIRQ(cpu, irq)` 置 IF，`UpdateIRQ` 计算输入线。基本表达式为 `IME.bit0 && (IE & IF)`；DSi ARM7 还并入 `IE2 & IF2`。进入异常还受 CPSR I 位控制。

软件写 IF 使用写一清零语义。ARM9 清 IF 后会再调用 `GPU3D.CheckFIFOIRQ`，所以仍满足条件的几何 FIFO IRQ 可以立刻回来。把 IF 当普通可任意覆盖的寄存器会破坏中断状态。

`HaltInterrupted` 对 ARM9 要求 IME 已开，对 ARM7 则可由已使能的待处理中断唤醒，即便 IME 未开而暂不进入 IRQ。睡眠唤醒另走 ARM7 `SetIRQ` 的逻辑，并设置 `CPUStop_Wakeup`、重启 3D 帧。这三层要分开：设备置标志 → CPU 离开 HALT/睡眠 → CPU 实际进入异常。

## Timer

每 CPU 四个 Timer，保存 `Reload`、`Cnt`、`Counter`、`CycleShift`。计数器内部把 16 位客体计数左移 10 位，以统一处理除以 1/64/256/1024 的预分频。`TimerTimestamp[cpu]` 记录上次已结算的系统时间；ARM9 计时先换算为系统周期。

`RunTimers` 只推进启用且不为级联模式的 Timer；溢出由 `HandleTimerOverflow` 加 reload、产生 IRQ，并向后续启用级联的 Timer 传播一次增量。一次推进可跨多次溢出，所以 `RunTimer` 使用循环消耗溢出量。

`TimerGetCounter` 读前结算，`TimerStart` 改控制前也结算；只有 enable 从 0 到 1 才把 reload 装入计数。写 reload 与写当前 counter 不可混为一谈。级联到每 CPU 的第四个 Timer 即停止，不能串到另一 CPU。

## 传统 DMA 状态机

两个 CPU 各四通道。寄存器为源地址、目标地址、控制字；内部另存当前地址、剩余量、当前批量、增量、启动模式、运行/进行中/被阻塞状态，以及主 RAM burst 位置。

```text
禁用 → 写 CNT 使能沿 → 锁存地址与模式
    → 立即模式：Start；事件模式：等待 CheckDMAs
Start → 设置 RemCount/IterCount、重装地址 → StopCPU
Run9/Run7 → 逐单元总线读写、记周期、更新地址与剩余量
    → 达到 CPU target：保留中间状态，下次继续
    → 本批结束：重复模式等待下次触发，或清 enable
    → 如允许则置完成 IRQ，ResumeCPU
```

| 内部 StartMode | 触发者 |
|---|---|
| ARM9 `0x00` / ARM7 `0x10` | 立即 |
| ARM9 `0x01` / ARM7 `0x11` | VBlank |
| ARM9 `0x02` | 可见行 HBlank |
| ARM9 `0x03` | 显示相关逐行触发，见 `GPU::StartScanline` 的 2–193 行范围 |
| ARM9 `0x04` | 显示 FIFO 请求 |
| ARM9 `0x05` / ARM7 `0x12` | 卡带数据就绪 |
| ARM9 `0x07` | GX FIFO 低于阈值 |
| ARM9 `0x06` / ARM7 `0x13` | 当前 `WriteCnt` 报未实现的启动模式 |

32 位/16 位控制决定传送粒度；count=0 代表掩码范围加一，而非零次。ARM9 计数掩码为 21 位，ARM7 通道 0–2 为 14 位，通道 3 为 16 位。地址可递增、递减、固定或按模式重装；重复与重装必须保留寄存器地址和当前地址的区别。

GX FIFO DMA 每批最多 112 单元。FIFO 满还会让正在传送的 DMA 暂停；不能把整次 DMA 替换为 memcpy。主循环以通道顺序运行并共享 CPU 时间目标，传送消耗了 CPU 的可用时间。

### DMA 时序

`UnitTimings9_16/32` 与 ARM7 对应函数区分源/目标区域、总线宽度、顺序/非顺序和 burst 开始；主 RAM 到主 RAM 不等同普通线性拷贝。`DMA_Timings` 包含测得/特化的主 RAM burst 表。源码仍保留固定/递减地址、初始 nonseq 延迟等 TODO，复刻时应先保持当前对照行为，再单独验证硬件差异。

DSi 的 NDMA 是独立状态机，见 [DSi 核心](dsi-core.md)，不是放大传统 DMA 计数器。

## IPC

`IPCSync9/7` 传递双方的低位状态，并能请求对方同步 IRQ。FIFO 有两个方向，每个 16 个 32 位元素：`IPCFIFO9` 表示 ARM9 写、ARM7 读，反向同理。

`IPCFIFOCnt` 的空/满状态由队列动态合成；enable、发送空 IRQ、接收非空 IRQ 和 error 是不同位。写满会置 error；读空会置 error 并使用 `Peek` 行为。FIFO 未启用的读取也与出队不同。清发送 FIFO、清 error、首次使能已满足条件的 IRQ、从空变非空、从非空变空，都有专门分支。

复刻时把双方控制字与两个队列一起视为状态机。仅在 enqueue/dequeue 时触发 IRQ，会遗漏软件打开 IRQ 使能时队列已经符合条件的情形。

## 除法与整数平方根

数学单元在 ARM9 MMIO。`StartDiv` 取消旧完成事件、置 busy，并安排 18（32/32）或 34（其他模式）系统周期后的完成。支持 32/32、64/32、64/64 有符号除法；除零和最小负数除以 -1 都有显式分支，商和余数不能直接依赖宿主未定义行为。

`StartSqrt` 安排 13 周期，完成函数按 32/64 位无符号输入作整数开方。结果向下取整，不能用浮点 sqrt 后随意转换。当前完成函数读取当时的寄存器字段；操作数重写导致的重调度必须按 IO 分支实现。

## 复刻检查

用 MMIO 驱动可观测的小程序：IME 关闭时 ARM7 HALT 唤醒、IF 清后 GX 重触发、Timer 级联多次溢出、DMA 零 count/重装/抢占、IPC 的空满错误与开 IRQ 即触发、数学单元 busy 中改操作数。比对的是 IRQ 时间、内存写序和剩余状态；最终数据相同但时序不同也应记为差异。
