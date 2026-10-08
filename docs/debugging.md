# 调试、作弊与辅助设施

[返回总路由](README.md)。诊断具体模块继续读主题文档；跨模块差异定位见 [验证](validation.md)。

## GDB

[debug/GdbStub.cpp](../src/debug/GdbStub.cpp)、[GdbProto.cpp](../src/debug/GdbProto.cpp)、[GdbCmds.cpp](../src/debug/GdbCmds.cpp) 分别处理连接/状态、远程协议封包、命令分发；[GdbArch.h](../src/debug/GdbArch.h)、[GdbStub.h](../src/debug/GdbStub.h)、[GdbCmds.h](../src/debug/GdbCmds.h)、[hexutil.h](../src/debug/hexutil.h) 定义寄存器映射和编码。

`GDBArgs` 分别给 ARM7/ARM9 配置端口和启动断点。ARM 实现 StubCallbacks 的寄存器/内存读写、reset 和 remote command；`GdbCheckA/B/C` 插入解释执行边界处理连接、单步与断点。写 PC/PSR 会涉及流水线和模式，不是任意写寄存器数组。

编译时 `ENABLE_GDBSTUB` 决定是否包含，运行时 `RunFrame` 选择对应解释器。JIT 路径在当前分派中优先，因此调试基准应显式关闭 JIT，确认端口和单步确实生效。`debug/gdb_test` 是单独的协议测试程序，不是整个模拟器的正确性测试套件。

## 日志与客体调试输出

`Platform::Log` 是宿主日志入口；`NDS::NocashPrint` 等提供 guest 调试输出。`NDS.h` 的 `DEBUG_CHECK_DESYNC` 可用于主循环同步诊断。调试 CPU 时先记录实际指令地址与体系结构 PC 的转换，避免日志看起来一直偏移一条指令。

建议新增诊断只记录有用事件：首个异常、未知 MMIO、IRQ 转换、DMA 开始/结束、映射变更和第一次 trace 差异。高频日志会拖慢宿主，真实性判断仍依据模拟周期而不是日志的墙钟间隔。

## Action Replay

[AREngine.cpp](../src/AREngine.cpp)、[AREngine.h](../src/AREngine.h) 解释 ARCode 的双 word 指令流。状态包括 offset、data register、条件栈、循环位置/次数及特殊计数；支持按宽度写内存、比较/条件、循环、数据搬运等。具体 opcode 完整覆盖以 `RunCheat` switch 为准。

作弊写入经 `NDS.ARM7Write*` 总线，可能触发 MMIO 或 JIT 失效；不能简单视作“帧末改 RAM”。实际运行钩子在 `ARM::TriggerIRQ`：ARM7 进入 IRQ 且 `IF & IE` 中 VBlank 位为真时运行。`RunCheats` 仅运行 Enabled 项。

[ARCodeFile.cpp](../src/ARCodeFile.cpp) 负责文本列表的解析、保存、导入和分类；[ARDatabaseDAT.cpp](../src/ARDatabaseDAT.cpp) 读取游戏码索引/数据库代码；Qt 的 CheatsDialog/CheatImportDialog 管理 UI。导入时应验证指令对完整、长度与数据块边界；不能让损坏文件成为越界内存访问。新核心准确性对照时默认关闭作弊，并在对照 manifest 标明是否启用。

## 支撑文件

| 文件/目录 | 用途与阅读边界 |
|---|---|
| [types.h](../src/types.h)、[Utils.cpp](../src/Utils.cpp)、[Utils.h](../src/Utils.h) | 固定宽度类型、字节序/内存辅助；移植前核对整数与对齐假设 |
| [FIFO.h](../src/FIFO.h) | 固定容量 FIFO/RingBuffer；空读、满写、指针和存档行为影响多设备 |
| [CRC32.cpp](../src/CRC32.cpp)、[CRC32.h](../src/CRC32.h) | ROM/BIOS/microcode 等识别和校验 |
| [NonStupidBitfield.h](../src/NonStupidBitfield.h) | VRAM 等脏块跟踪 |
| [TinyVector.h](../src/TinyVector.h) | JIT 等内部小型集合，不是客体可见对象 |
| [version.h.in](../src/version.h.in) | CMake 生成版本信息 |

这些辅助模块可以在新语言中使用已有标准容器/位操作替代，但必须保留队列溢出/空读、整数回绕和字节序语义。替换容器不能顺带改变设备容量。

## 复刻检查

GDB 单步验证分支/Thumb/异常后 PC，读取 TCM 与普通 MMIO 区别，关闭连接后执行可继续。作弊用手工可判定的短序列验证条件、循环与写入时间，坏输入拒绝行为单独验证。真实 bug 排查先固定配置和输入，再沿设备事件到 CPU 的因果链定位，不靠增加通用日志掩盖首个差异。
