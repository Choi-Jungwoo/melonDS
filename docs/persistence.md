# 即时存档、游戏保存与外部存储

[返回总路由](README.md)。本章适用于快照恢复、文件迁移、无界面平台实现和确定性验证。

## 源码入口

[Savestate.h](../src/Savestate.h)、[Savestate.cpp](../src/Savestate.cpp)：缓冲区格式与读写；[NDS.cpp](../src/NDS.cpp)：`GetSavestateConfig/DoSavestate`；[DSi.cpp](../src/DSi.cpp)：`DoSavestateExtra`；各设备的 `DoSavestate`；[SaveManager.cpp](../src/frontend/qt_sdl/SaveManager.cpp)；[FATStorage.cpp](../src/FATStorage.cpp)、[FATIO.cpp](../src/FATIO.cpp)；[DSi_NAND.cpp](../src/DSi_NAND.cpp)；[EmuInstance.cpp](../src/frontend/qt_sdl/EmuInstance.cpp)：`loadState/saveState/undoStateLoad`。

## 四种“保存”

| 类型 | 内容 | 生命周期 |
|---|---|---|
| 游戏 save | 卡带非易失芯片的字节 | 客体协议写入，经平台回调落盘 |
| firmware/RTC 配置 | 用户设置、校准、时间偏移等 | 客体/前端改动后持久化 |
| 即时存档 | CPU、RAM、设备内部状态、时间和待执行事件 | 任意模拟时刻冻结/恢复 |
| NAND/SD/FAT 目录 | 系统或客体文件系统的存储内容 | 块写、挂载、导入/导出 |

即时存档不会天然回滚另三类已写到磁盘的内容。新实现必须明确外部介质是否纳入快照或使用另行维护的副本，不能向使用者承诺“读档后磁盘也回到过去”。

## 即时存档格式与入口

当前 `SAVESTATE_MAJOR=14`、`MINOR=0`。头部包含 `MELN` magic、major/minor、总长度与保留字段；每段有四字节 magic、长度和保留字段。`Section` 按段查找，`Var8/16/32/64`、`Bool32`、`VarArray` 按既定格式读写；`Finish` 完成段/总长度。

加载检查 magic、主版本、未来 minor 和总长度。配置字还约束当前整机/选项，具体位看 `GetSavestateConfig` 的 DS/DSi 实现。该格式是 melonDS 的内部兼容契约，独立新实现可定义自己的格式；若要兼容 `.ml*`，必须逐段匹配版本、字段顺序、数组布局、布尔宽度和字节序。

`NDS::DoSavestate` 保存主 RAM（最大容量）、共享和 ARM7 WRAM、总线控制、IRQ、IPC、Timer、DMA、事件时间、两 CPU、各设备，再调用 DSi 扩展。事件仅保存时间/函数编号/参数；函数指针与实例指针在运行时已注册，不能序列化主机地址。

## 必须保存与必须重建的状态

| 状态 | 恢复要求 |
|---|---|
| CPU 寄存器/模式/流水线/CP15 | 保留下一条指令的语义和取指状态 |
| Timer 分频余量、DMA 当前地址/剩余量 | 从暂停点继续，不能只恢复控制寄存器 |
| 事件槽、两个 CPU/设备时间戳 | 保持相对时间与到期顺序 |
| FIFO 内容/指针、SPI 命令阶段 | 恢复半条事务，而不是强制回空闲 |
| 显存/几何 RAM/寄存器锁存 | 保存逻辑内容；宿主 GPU 结果先回写 |
| bank 映射、快速指针、时序表 | 根据状态重建，不能持久化地址 |
| JIT 块、宿主 GL/线程句柄 | 丢弃/重新初始化或明确同步 |
| 麦克风/网络/摄像头现实输入 | 保存协议状态不等于重现未来输入，需要额外输入日志 |

`GPU::DoSavestate` 和 renderer 的 Pre/Post 钩子负责渲染同步；恢复后核心重建时序/映射和电源，JIT reset。`Mic::DoSavestate` 重新打开或关闭采集并清缓冲。`NDS::DoSavestate` 对 `KeyInput` 仍有 TODO，`DSi.h` 也注明部分 GPIO 未入存档，不能据此宣称现有快照包含所有确定性输入。

## 前端读档与失败语义

`EmuInstance::loadState` 先保存当前状态到 backup，读入目标文件并调用核心加载；成功后保留 backup 供 `undoStateLoad`。注意：当前失败分支直接返回，不能从“有 backup”推断加载失败时已经自动回滚。

`saveState` 先以写模式打开目标，再生成内存快照并写入。因此当前代码也不是先完整生成、再原子替换旧文件的事务实现。新实现建议先验证/构建完整新状态，成功后切换；落盘使用完整临时结果替换，并验证短读、短写与损坏长度。这是新实现要求，不是对现有代码的保证。

## SaveManager

核心回调提供整个保存缓冲和变化区间。`RequestFlush` 更新主缓冲，处理跨尾回绕；帧末 `CheckFlush` 复制到加锁的 secondary buffer 并提高版本号。后台线程每 100 ms 检查，最近请求稳定约两秒后写文件；析构会等待线程并尝试最终 flush。

新前端可采用更简单的同步写入，但应保存这些契约：设备的内存内容立即可读、文件写不借用随时失效的指针、切游戏前处理旧保存、每实例路径隔离、错误向调用者可见。当前 SaveManager 的写结果处理不能视为已经证明断电安全。

## FATStorage 和 NAND

`FATStorage` 用块镜像承载 FAT，可选把宿主目录导入并按 index 导出改动。`LoadIndex/SaveIndex`、`ImportDirectory/CleanupDirectory/ExportChanges` 涉及新增、修改与删除；只读位、文件时间和大小用于同步。该功能可能影响宿主文件，复现时使用隔离副本，按真实错误返回处理失败。

`FATIO` 将 FatFs 的磁盘读写桥接到回调；FatFs 是文件系统实现，不负责模拟 CPU 或 SD 控制器。DSi NAND 的原始块、加密 FAT 内容及标题管理是另一层，见 [DSi 存储](dsi-storage.md)。`DSi_MMCStorage::DoSavestate` 明确保留“文件内容怎么办”的 TODO，外部介质不能因为设备状态已存档就被认为一起保存。

## 复刻检查

固定全部外部输入和介质副本，运行到 DMA/SPI/FIFO 非空时保存；继续 N 帧记录状态，再恢复并重放同样输入，比较 CPU、RAM、事件与设备轨迹。另测坏 magic/版本/长度/截断段、短写、无写权限、存储已变化、切游戏和退出前 flush。验收时分别报告“核心恢复一致”和“外部持久化一致”。
