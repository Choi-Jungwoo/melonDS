# 地址空间、总线与 MMIO

[返回总路由](README.md)。本章用于实现访存或追踪寄存器效果；VRAM 的银行规则在 [视频内存](video-memory.md)，DSi 扩展在 [DSi 核心](dsi-core.md)。

## 源码入口与访问层次

[NDS.cpp](../src/NDS.cpp) 的 `ARM9Read8/16/32`、`ARM9Write8/16/32` 与 ARM7 对应方法处理总线；`ARM9IORead*`/`ARM9IOWrite*` 与 ARM7 对应方法处理 MMIO。[CP15.cpp](../src/CP15.cpp) 的 `DataRead*/DataWrite*` 位于 ARM9 指令与总线之间；[ARM.cpp](../src/ARM.cpp) 包含 ARM7 数据访问和 CPU 的 `Bus*` 方法。

```text
CPU 指令 → CPU Data/Code 访问（TCM、权限、取指 cache、计时）
         → NDS/DSi 的 CPU 专属总线 → RAM / MMIO / VRAM / 卡槽
DMA      → 总线访问 + DMA 自己的时序与仲裁
调试器   → 调试读写入口（检查是否遵循相同副作用和 TCM 可见性）
```

直接返回指针的 `ARM9GetMemRegion/ARM7GetMemRegion`、[MemRegion.h](../src/MemRegion.h) 是取指或快速路径；带副作用的 IO 不应因优化而变成可随意 memcpy 的内存。

## DS 地址域索引

下表给出路由边界，不代表整个范围每个字节都存在。确切镜像、保护、宽度和空洞行为由各 `Read/Write` 分支决定。

| 地址域 | ARM9 | ARM7 |
|---|---|---|
| `00000000` 附近 | ITCM 由 CP15 决定 | BIOS，16 KiB 物理存储并有读取保护 |
| `02000000–02FFFFFF` | 主 RAM 镜像 | 同一物理主 RAM |
| `03000000–03FFFFFF` | 共享 WRAM 的分配视图 | 共享 WRAM/内部 64 KiB WRAM 按地址与分配解码 |
| `04000000` 起 | ARM9 MMIO | ARM7 MMIO；同地址可代表不同设备 |
| `04100000` | IPC 接收 FIFO | IPC 接收 FIFO |
| `04100010` | 卡带数据端口 | 卡带数据端口，受所有权限制 |
| `04800000` 附近 | 不按 ARM7 Wi-Fi 设备解码 | Wi-Fi RAM/寄存器，有电源和宽度限制 |
| `05000000` | 2D palette RAM | 无相同的普通 palette 视图 |
| `06000000–06FFFFFF` | GPU 的 BG/OBJ/LCDC 视图 | 分配给 ARM7 的 VRAM 银行 |
| `07000000` | OAM | 无相同的普通 OAM 视图 |
| `08000000–09FFFFFF` | Slot-2 ROM，受 EXMEMCNT 限制 | 同一 Slot-2 的另一 CPU 视图 |
| `0A000000` 域 | Slot-2 save/扩展 | 同一总线的另一 CPU 视图 |
| `FFFF0000` 附近 | ARM9 BIOS 的高地址视图 | 无相同映射 |

物理大小见 [MemConstants.h](../src/MemConstants.h)：DS 主 RAM 有效掩码为 `0x3FFFFF`；核心为 DSi 预留最大 16 MiB。共享 WRAM 32 KiB、ARM7 WRAM 64 KiB、ARM9 BIOS 4 KiB、ARM7 BIOS 16 KiB。DTCM 通过 CP15 可定位到其他地址，不能仅按上表高位判断。

## 共享 WRAM 与外部总线所有权

`MapSharedWRAM` 的 `WRAMCNT & 3`：

| 值 | ARM9 | ARM7 共享视图 |
|---|---|---|
| 0 | 全 32 KiB | 无分配 |
| 1 | 后 16 KiB | 前 16 KiB |
| 2 | 前 16 KiB | 后 16 KiB |
| 3 | 无分配 | 全 32 KiB |

这是视图变化，不是复制数据。ARM7 对未分配共享区的回退和内部 WRAM 镜像继续看 ARM7 总线函数。映射变化还要更新 JIT/fastmem。

`SetExMemCnt` 把部分位同步到另一 CPU；位 7 控制 Slot-2 所有权，位 11 控制第一 DS 卡槽 CPU 选择，DSi 另有第二卡槽控制位。`SetGBASlotTimings` 调整只有获权 CPU 使用的等待周期与 Slot-2 空总线衰减值；另一 CPU 并不获得同等设备访问。

## MMIO 分发目录

| 主要寄存器地址 | 所属行为 | 下一入口 |
|---|---|---|
| `04000000–0400006F`、`04001000` 起 | 显示控制、2D、捕获/FIFO | `GPU::Read/Write*`、`GPU2D::Write*` |
| `040000B0` 起、每通道 12 字节 | 传统 DMA；ARM9 还有填充值 | `DMA::WriteCnt`、`Run*` |
| `04000100–0400010F` | 四个 Timer 的计数/reload 和 control | `TimerGetCounter`、`TimerStart` |
| `04000130/132/136/138` | 按键、KEYCNT、扩展输入与 RTC 等 CPU 特定寄存器 | `NDS` IO switch、`RTC::Read/Write` |
| `04000180/184/188`、`04100000` | IPCSYNC、FIFO 控制、发送、接收 | `NDS` 的两套 IPC 分支 |
| `040001A0` 起、`04100010` | 卡带 SPI、ROM 控制/命令/数据 | `NDSCartSlot` |
| `040001C0/1C2`（ARM7） | 系统 SPI | `SPIHost` |
| `04000204/208/210/214` | EXMEMCNT、IME、IE、IF | `SetExMemCnt`、`UpdateIRQ` |
| `04000240` 起 | VRAMCNT、WRAMCNT/状态 | `MapVRAM_*`、`MapSharedWRAM` |
| `04000280–040002BF`（ARM9） | 除法、开方 | `StartDiv/DivDone/StartSqrt/SqrtDone` |
| `04000300` 起 | POSTFLG、HALTCNT、POWCNT 等 | 启动、电源、HALT/睡眠 |
| `04000400` 起（ARM9） | 几何 FIFO/命令及 3D 状态 | `GPU3D` |
| `04000400–0400051F`（ARM7） | 声道、混音和捕获 | `SPU` |

不能做一张仅以地址为键的全局寄存器字典：例如 `04000400` 在两个 CPU 上用途完全不同。每条 MMIO 规则至少含 `(console, cpu, address, width, direction)`。

## 需要逐分支保留的语义

- 写只读位、写一清零、保留位、byte lane 掩码；16/32 位访问不一定等同若干个 8 位访问。
- FIFO 读会出队，空读可能返回前值并置错误；普通“读寄存器”不能把队列状态漏掉。
- Timer 读前先追赶时间；数学单元写入可能取消并重排完成事件；卡带读会释放下一次传输。
- BIOS 读取与执行地址/保护有关；未映射值由具体区域决定，不统一承诺零或 `0xFFFFFFFF`。
- Palette/VRAM 的 byte 写规则、重叠银行读 OR/写广播、OAM 的宽度语义属于总线行为。
- RAM 镜像或 CP15/MBK 切换后，取指指针、块缓存和硬件可见映射必须一致。

## 复刻检查

以“地址域 × CPU × 8/16/32 位 × 读写 × 当前映射/电源”列覆盖表，先测试普通 RAM 的镜像，再测共享 WRAM 分配、同址异设备、FIFO 出队和写一清零。检查 DMA 对 MMIO 的写入能产生与 CPU 同样的设备效果，同时保持不同的访存时间。新增映射需再走一遍 [JIT](jit.md) 和 [持久化](persistence.md) 的失效/恢复清单。
