# DS Wi-Fi、接入点、联机与宿主网络

[返回总路由](README.md)。DSi SDIO 无线见 [DSi 存储与网络](dsi-storage.md)。

## 源码入口

[Wifi.h](../src/Wifi.h)、[Wifi.cpp](../src/Wifi.cpp)：寄存器/RAM、RF/BB、微秒计时、TX/RX、多人协议；[WifiAP.cpp](../src/WifiAP.cpp)、[WifiAP.h](../src/WifiAP.h)：模拟 AP；[Platform.h](../src/Platform.h)：`MP_*` 与 `Net_*`；[net](../src/net)：宿主传输与分发。

## 四层边界

| 层 | 字节/时间契约 | 实现 |
|---|---|---|
| DS 无线硬件 | ARM7 MMIO、设备 RAM、IRQ 与模拟微秒时钟 | Wifi |
| 模拟接入点 | 802.11 管理/数据帧与 Ethernet 桥接 | WifiAP |
| DS 多人传输 | 12 字节 DS TX 头 + 原始 802.11 帧，带模拟时间戳 | Platform MP、MPInterface |
| 外部网络 | Ethernet 帧送宿主网络驱动 | Platform Net、Net/Slirp/PCap |

多人传输不是普通 Ethernet，模拟 AP 也不是所有联网方式的共同入口。新实现即使复用同一个 socket 库，仍需保留这些不同的帧格式和时间语义。

## 无线设备状态与运行

`Wifi::Read/Write` 处理设备 RAM、寄存器、镜像和副作用；电源状态经 `SetPowerCnt/UpdatePowerOn` 影响可用性。还需保存 RF/BB 串行传输、频道、MAC/BSSID、TX slot、RX 环形位置、IRQ enable/flags、微秒/毫秒/beacon 计数及联机状态。

`ScheduleTimer` 把微秒间隔转换到系统周期，并用 TimerError 累计舍入误差；`USTimer/MSTimer` 推进发送、接收、beacon、超时和电源状态。用宿主 sleep 模拟每个无线 tick 会引入负载相关行为，调度必须仍由核心时间驱动。

发送路径：客体准备 RAM/slot → `StartTX_LocN/StartTX_Cmd/StartTX_Beacon` → `FireTX/ProcessTX` → `TXSendFrame` → MP 或 AP。接收路径：平台返回帧 → `CheckRX/StartRX/FinishRX` → 写设备 RX ring、更新状态/计数与 IRQ。头部过滤、帧长度、对齐、ring wrap 和 busy 转换都需逐分支保留。

## DS 多人协议

多人模式含主机 CMD、客户端 reply、主机 ACK，使用专门 MAC 和客户端位掩码。`SendMPReply/SendMPAck/MPClientReplyRX`、`RecvHostPacket/RecvReplies` 保留事务阶段、回复窗口和模拟时间戳；不能把它们折叠为无序广播数据报。

[MPInterface.cpp](../src/net/MPInterface.cpp) 当前可建立 Dummy、LocalMP 或 LAN。`MPPacketHeader` 含 magic、sender、type、length、timestamp；[LocalMP.cpp](../src/net/LocalMP.cpp) 处理本地实例通信；[LAN.cpp](../src/net/LAN.cpp) 使用 ENet、发现/会话/玩家列表与包队列传送同样的模拟无线消息。

[PacketDispatcher.cpp](../src/net/PacketDispatcher.cpp) 按实例掩码复制包到各自队列并加锁；发送者、接收者位掩码、退出时注销和队列容量要一起处理。宿主到包时间与包中模拟时间戳分开，后者用于协调模拟中的接收窗口。

## AP 与网络驱动

`WifiAP` 处理认证/关联等管理交互和数据帧封装；`Platform::Net_SendPacket/RecvPacket` 传的是 Ethernet。[Net.cpp](../src/net/Net.cpp)、[NetDriver.h](../src/net/NetDriver.h) 选择驱动并把数据分发给实例。

[Net_Slirp.cpp](../src/net/Net_Slirp.cpp) 连接用户态 libslirp，处理回调、轮询和定时；[Net_PCap.cpp](../src/net/Net_PCap.cpp) 连接主机抓包/网卡接口。相同游戏 TCP/IP 栈由客体运行，模拟器提供的是无线硬件/AP 和帧转发，不是把游戏网络调用逐个替换成宿主 API。

移植时验证帧长度、队列边界、断连/超时、线程停止和驱动失败返回。无需联网的核心版本可以明确使用 DummyMP/空网络来源，但这不构成联机功能完成。

## Netplay 当前边界

[Netplay.cpp](../src/net/Netplay.cpp) 另有 ENet 玩家、镜像实例、ROM/save/state blob 和输入帧同步的设计；它与 LAN 的模拟无线传输不是同一功能。多段核心逻辑（包括 `ProcessInput` 主体）位于 `#if 0`；`MPInterface::Set` 也没有建立 Netplay 实例的分支。

因此它应作为未完成方案阅读，不能作为现成的 rollback/完整在线同步实现。新模拟器若要求 Netplay，需要另行定义初态、输入日志、外部介质一致性、延迟策略和失同步处理，再按完整功能验收。

## 复刻检查

依次验证离线 MMIO/RF 初始化、单机 AP 关联与收发、本地两实例 CMD/reply/ACK、LAN 的延迟/丢包/断开。记录包类型、模拟时间、水位与 IRQ；固定 MAC/RTC/输入和网络回放，定位首个差异。联网成功一次只证明该条路径，不证明时序、多人上限、所有频道或全部固件兼容。
