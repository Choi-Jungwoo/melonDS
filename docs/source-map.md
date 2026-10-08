# 源码覆盖与反向路由

[返回总路由](README.md)。按文件查找阅读主题；按功能选文档请使用总路由。

本表对基线中 `src` 的第一方文件逐项给出入口，声明/实现/同名 UI 合并在一行。第三方随库源码按目录归组，并指向集成契约；辅助构建、固件源和资源也按目录路由。目录链接表示覆盖该目录全部内容，不能据文件覆盖推断每行算法都已重述或验证。

新增第一方源码时补对应文件链接与主题，修改行为时更新主题正文。`mise run docs-check` 将 Git 已跟踪和未忽略的新文件与本表核对，避免新文件没有入口。

## 整体架构

| 源码文件 | 阅读主题 |
|---|---|
| [Args.h](../src/Args.h) | [整体架构](architecture.md) |
| [NDS.cpp](../src/NDS.cpp)、[NDS.h](../src/NDS.h) | [整体架构](architecture.md) |

## 启动

| 源码文件 | 阅读主题 |
|---|---|
| [FreeBIOS.cpp](../src/FreeBIOS.cpp)、[FreeBIOS.h](../src/FreeBIOS.h) | [启动](boot.md) |
| [FreeBIOS_Data.h](../src/FreeBIOS_Data.h) | [启动](boot.md) |

## CPU

| 源码文件 | 阅读主题 |
|---|---|
| [ARM.cpp](../src/ARM.cpp)、[ARM.h](../src/ARM.h) | [CPU](cpu.md) |
| [ARMInterpreter.cpp](../src/ARMInterpreter.cpp)、[ARMInterpreter.h](../src/ARMInterpreter.h) | [CPU](cpu.md) |
| [ARMInterpreter_ALU.cpp](../src/ARMInterpreter_ALU.cpp)、[ARMInterpreter_ALU.h](../src/ARMInterpreter_ALU.h) | [CPU](cpu.md) |
| [ARMInterpreter_Branch.cpp](../src/ARMInterpreter_Branch.cpp)、[ARMInterpreter_Branch.h](../src/ARMInterpreter_Branch.h) | [CPU](cpu.md) |
| [ARMInterpreter_LoadStore.cpp](../src/ARMInterpreter_LoadStore.cpp)、[ARMInterpreter_LoadStore.h](../src/ARMInterpreter_LoadStore.h) | [CPU](cpu.md) |
| [ARM_InstrTable.h](../src/ARM_InstrTable.h) | [CPU](cpu.md) |
| [CP15.cpp](../src/CP15.cpp) | [CPU](cpu.md) |

## 内存

| 源码文件 | 阅读主题 |
|---|---|
| [MemConstants.h](../src/MemConstants.h) | [内存](memory.md) |
| [MemRegion.h](../src/MemRegion.h) | [内存](memory.md) |

## 系统控制

| 源码文件 | 阅读主题 |
|---|---|
| [DMA.cpp](../src/DMA.cpp)、[DMA.h](../src/DMA.h) | [系统控制](system-control.md) |
| [DMA_Timings.cpp](../src/DMA_Timings.cpp)、[DMA_Timings.h](../src/DMA_Timings.h) | [系统控制](system-control.md) |

## LCD 与显存

| 源码文件 | 阅读主题 |
|---|---|
| [GPU.cpp](../src/GPU.cpp)、[GPU.h](../src/GPU.h) | [LCD 与显存](video-memory.md) |
| [GPU_OpenGL.cpp](../src/GPU_OpenGL.cpp)、[GPU_OpenGL.h](../src/GPU_OpenGL.h) | [LCD 与显存](video-memory.md) |
| [GPU_Soft.cpp](../src/GPU_Soft.cpp)、[GPU_Soft.h](../src/GPU_Soft.h) | [LCD 与显存](video-memory.md) |
| [OpenGLSupport.cpp](../src/OpenGLSupport.cpp)、[OpenGLSupport.h](../src/OpenGLSupport.h) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/CaptureDownscaleFS.glsl](../src/OpenGL_shaders/CaptureDownscaleFS.glsl) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/CaptureDownscaleVS.glsl](../src/OpenGL_shaders/CaptureDownscaleVS.glsl) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/CaptureFS.glsl](../src/OpenGL_shaders/CaptureFS.glsl) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/CaptureVS.glsl](../src/OpenGL_shaders/CaptureVS.glsl) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/FinalPassFS.glsl](../src/OpenGL_shaders/FinalPassFS.glsl) | [LCD 与显存](video-memory.md) |
| [OpenGL_shaders/FinalPassVS.glsl](../src/OpenGL_shaders/FinalPassVS.glsl) | [LCD 与显存](video-memory.md) |

## 2D

| 源码文件 | 阅读主题 |
|---|---|
| [GPU2D.cpp](../src/GPU2D.cpp)、[GPU2D.h](../src/GPU2D.h) | [2D](video-2d.md) |
| [GPU2D_OpenGL.cpp](../src/GPU2D_OpenGL.cpp)、[GPU2D_OpenGL.h](../src/GPU2D_OpenGL.h) | [2D](video-2d.md) |
| [GPU2D_Soft.cpp](../src/GPU2D_Soft.cpp)、[GPU2D_Soft.h](../src/GPU2D_Soft.h) | [2D](video-2d.md) |
| [GPU_ColorOp.h](../src/GPU_ColorOp.h) | [2D](video-2d.md) |
| [OpenGL_shaders/2DCompositorFS.glsl](../src/OpenGL_shaders/2DCompositorFS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DCompositorVS.glsl](../src/OpenGL_shaders/2DCompositorVS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DLayerPreFS.glsl](../src/OpenGL_shaders/2DLayerPreFS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DLayerPreVS.glsl](../src/OpenGL_shaders/2DLayerPreVS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DSpriteFS.glsl](../src/OpenGL_shaders/2DSpriteFS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DSpritePreFS.glsl](../src/OpenGL_shaders/2DSpritePreFS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DSpritePreVS.glsl](../src/OpenGL_shaders/2DSpritePreVS.glsl) | [2D](video-2d.md) |
| [OpenGL_shaders/2DSpriteVS.glsl](../src/OpenGL_shaders/2DSpriteVS.glsl) | [2D](video-2d.md) |

## 3D

| 源码文件 | 阅读主题 |
|---|---|
| [GPU3D.cpp](../src/GPU3D.cpp)、[GPU3D.h](../src/GPU3D.h) | [3D](video-3d.md) |
| [GPU3D_Compute.cpp](../src/GPU3D_Compute.cpp)、[GPU3D_Compute.h](../src/GPU3D_Compute.h) | [3D](video-3d.md) |
| [GPU3D_Compute_shaders.h](../src/GPU3D_Compute_shaders.h) | [3D](video-3d.md) |
| [GPU3D_OpenGL.cpp](../src/GPU3D_OpenGL.cpp)、[GPU3D_OpenGL.h](../src/GPU3D_OpenGL.h) | [3D](video-3d.md) |
| [GPU3D_Soft.cpp](../src/GPU3D_Soft.cpp)、[GPU3D_Soft.h](../src/GPU3D_Soft.h) | [3D](video-3d.md) |
| [GPU3D_Texcache.cpp](../src/GPU3D_Texcache.cpp)、[GPU3D_Texcache.h](../src/GPU3D_Texcache.h) | [3D](video-3d.md) |
| [GPU3D_TexcacheOpenGL.cpp](../src/GPU3D_TexcacheOpenGL.cpp)、[GPU3D_TexcacheOpenGL.h](../src/GPU3D_TexcacheOpenGL.h) | [3D](video-3d.md) |
| [OpenGL_shaders/3DClearBitmapFS.glsl](../src/OpenGL_shaders/3DClearBitmapFS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DClearBitmapVS.glsl](../src/OpenGL_shaders/3DClearBitmapVS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DClearFS.glsl](../src/OpenGL_shaders/3DClearFS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DClearVS.glsl](../src/OpenGL_shaders/3DClearVS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DFinalPassEdgeFS.glsl](../src/OpenGL_shaders/3DFinalPassEdgeFS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DFinalPassFogFS.glsl](../src/OpenGL_shaders/3DFinalPassFogFS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DFinalPassVS.glsl](../src/OpenGL_shaders/3DFinalPassVS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DRenderFS.glsl](../src/OpenGL_shaders/3DRenderFS.glsl) | [3D](video-3d.md) |
| [OpenGL_shaders/3DRenderVS.glsl](../src/OpenGL_shaders/3DRenderVS.glsl) | [3D](video-3d.md) |

## 声音

| 源码文件 | 阅读主题 |
|---|---|
| [Mic.cpp](../src/Mic.cpp)、[Mic.h](../src/Mic.h) | [声音](audio.md) |
| [SPU.cpp](../src/SPU.cpp)、[SPU.h](../src/SPU.h) | [声音](audio.md) |

## 卡带

| 源码文件 | 阅读主题 |
|---|---|
| [GBACart.cpp](../src/GBACart.cpp)、[GBACart.h](../src/GBACart.h) | [卡带](cartridge.md) |
| [GBACartMotionPak.cpp](../src/GBACartMotionPak.cpp) | [卡带](cartridge.md) |
| [NDSCart.cpp](../src/NDSCart.cpp)、[NDSCart.h](../src/NDSCart.h) | [卡带](cartridge.md) |
| [NDSCart/CartCommon.cpp](../src/NDSCart/CartCommon.cpp)、[NDSCart/CartCommon.h](../src/NDSCart/CartCommon.h) | [卡带](cartridge.md) |
| [NDSCart/CartHomebrew.cpp](../src/NDSCart/CartHomebrew.cpp)、[NDSCart/CartHomebrew.h](../src/NDSCart/CartHomebrew.h) | [卡带](cartridge.md) |
| [NDSCart/CartR4.cpp](../src/NDSCart/CartR4.cpp)、[NDSCart/CartR4.h](../src/NDSCart/CartR4.h) | [卡带](cartridge.md) |
| [NDSCart/CartRetail.cpp](../src/NDSCart/CartRetail.cpp)、[NDSCart/CartRetail.h](../src/NDSCart/CartRetail.h) | [卡带](cartridge.md) |
| [NDSCart/CartRetailBT.cpp](../src/NDSCart/CartRetailBT.cpp)、[NDSCart/CartRetailBT.h](../src/NDSCart/CartRetailBT.h) | [卡带](cartridge.md) |
| [NDSCart/CartRetailIR.cpp](../src/NDSCart/CartRetailIR.cpp)、[NDSCart/CartRetailIR.h](../src/NDSCart/CartRetailIR.h) | [卡带](cartridge.md) |
| [NDSCart/CartRetailNAND.cpp](../src/NDSCart/CartRetailNAND.cpp)、[NDSCart/CartRetailNAND.h](../src/NDSCart/CartRetailNAND.h) | [卡带](cartridge.md) |
| [NDSCart/CartSD.cpp](../src/NDSCart/CartSD.cpp)、[NDSCart/CartSD.h](../src/NDSCart/CartSD.h) | [卡带](cartridge.md) |
| [NDSCart/melonDLDI.h](../src/NDSCart/melonDLDI.h) | [卡带](cartridge.md) |
| [NDS_Header.h](../src/NDS_Header.h) | [卡带](cartridge.md) |
| [ROMList.cpp](../src/ROMList.cpp)、[ROMList.h](../src/ROMList.h) | [卡带](cartridge.md) |

## 基础外设

| 源码文件 | 阅读主题 |
|---|---|
| [RTC.cpp](../src/RTC.cpp)、[RTC.h](../src/RTC.h) | [基础外设](peripherals.md) |
| [SPI.cpp](../src/SPI.cpp)、[SPI.h](../src/SPI.h) | [基础外设](peripherals.md) |
| [SPI_Firmware.cpp](../src/SPI_Firmware.cpp)、[SPI_Firmware.h](../src/SPI_Firmware.h) | [基础外设](peripherals.md) |

## DSi 核心

| 源码文件 | 阅读主题 |
|---|---|
| [DSi.cpp](../src/DSi.cpp)、[DSi.h](../src/DSi.h) | [DSi 核心](dsi-core.md) |
| [DSi_NDMA.cpp](../src/DSi_NDMA.cpp)、[DSi_NDMA.h](../src/DSi_NDMA.h) | [DSi 核心](dsi-core.md) |

## DSi 存储

| 源码文件 | 阅读主题 |
|---|---|
| [DSi_AES.cpp](../src/DSi_AES.cpp)、[DSi_AES.h](../src/DSi_AES.h) | [DSi 存储](dsi-storage.md) |
| [DSi_NAND.cpp](../src/DSi_NAND.cpp)、[DSi_NAND.h](../src/DSi_NAND.h) | [DSi 存储](dsi-storage.md) |
| [DSi_NWifi.cpp](../src/DSi_NWifi.cpp)、[DSi_NWifi.h](../src/DSi_NWifi.h) | [DSi 存储](dsi-storage.md) |
| [DSi_SD.cpp](../src/DSi_SD.cpp)、[DSi_SD.h](../src/DSi_SD.h) | [DSi 存储](dsi-storage.md) |
| [DSi_TMD.h](../src/DSi_TMD.h) | [DSi 存储](dsi-storage.md) |

## DSi 媒体

| 源码文件 | 阅读主题 |
|---|---|
| [DSP_HLE/AACUcode.cpp](../src/DSP_HLE/AACUcode.cpp)、[DSP_HLE/AACUcode.h](../src/DSP_HLE/AACUcode.h) | [DSi 媒体](dsi-media.md) |
| [DSP_HLE/G711Ucode.cpp](../src/DSP_HLE/G711Ucode.cpp)、[DSP_HLE/G711Ucode.h](../src/DSP_HLE/G711Ucode.h) | [DSi 媒体](dsi-media.md) |
| [DSP_HLE/GraphicsUcode.cpp](../src/DSP_HLE/GraphicsUcode.cpp)、[DSP_HLE/GraphicsUcode.h](../src/DSP_HLE/GraphicsUcode.h) | [DSi 媒体](dsi-media.md) |
| [DSP_HLE/UcodeBase.cpp](../src/DSP_HLE/UcodeBase.cpp)、[DSP_HLE/UcodeBase.h](../src/DSP_HLE/UcodeBase.h) | [DSi 媒体](dsi-media.md) |
| [DSi_Camera.cpp](../src/DSi_Camera.cpp)、[DSi_Camera.h](../src/DSi_Camera.h) | [DSi 媒体](dsi-media.md) |
| [DSi_DSP.cpp](../src/DSi_DSP.cpp)、[DSi_DSP.h](../src/DSi_DSP.h) | [DSi 媒体](dsi-media.md) |
| [DSi_I2C.cpp](../src/DSi_I2C.cpp)、[DSi_I2C.h](../src/DSi_I2C.h) | [DSi 媒体](dsi-media.md) |
| [DSi_I2S.cpp](../src/DSi_I2S.cpp)、[DSi_I2S.h](../src/DSi_I2S.h) | [DSi 媒体](dsi-media.md) |
| [DSi_SPI_TSC.cpp](../src/DSi_SPI_TSC.cpp)、[DSi_SPI_TSC.h](../src/DSi_SPI_TSC.h) | [DSi 媒体](dsi-media.md) |

## 无线与网络

| 源码文件 | 阅读主题 |
|---|---|
| [Wifi.cpp](../src/Wifi.cpp)、[Wifi.h](../src/Wifi.h) | [无线与网络](wireless.md) |
| [WifiAP.cpp](../src/WifiAP.cpp)、[WifiAP.h](../src/WifiAP.h) | [无线与网络](wireless.md) |
| [net/LAN.cpp](../src/net/LAN.cpp)、[net/LAN.h](../src/net/LAN.h) | [无线与网络](wireless.md) |
| [net/LocalMP.cpp](../src/net/LocalMP.cpp)、[net/LocalMP.h](../src/net/LocalMP.h) | [无线与网络](wireless.md) |
| [net/MPInterface.cpp](../src/net/MPInterface.cpp)、[net/MPInterface.h](../src/net/MPInterface.h) | [无线与网络](wireless.md) |
| [net/Net.cpp](../src/net/Net.cpp)、[net/Net.h](../src/net/Net.h) | [无线与网络](wireless.md) |
| [net/NetDriver.h](../src/net/NetDriver.h) | [无线与网络](wireless.md) |
| [net/Net_PCap.cpp](../src/net/Net_PCap.cpp)、[net/Net_PCap.h](../src/net/Net_PCap.h) | [无线与网络](wireless.md) |
| [net/Net_Slirp.cpp](../src/net/Net_Slirp.cpp)、[net/Net_Slirp.h](../src/net/Net_Slirp.h) | [无线与网络](wireless.md) |
| [net/Netplay.cpp](../src/net/Netplay.cpp)、[net/Netplay.h](../src/net/Netplay.h) | [无线与网络](wireless.md) |
| [net/PacketDispatcher.cpp](../src/net/PacketDispatcher.cpp)、[net/PacketDispatcher.h](../src/net/PacketDispatcher.h) | [无线与网络](wireless.md) |

## 前端与平台

| 源码文件 | 阅读主题 |
|---|---|
| [Platform.h](../src/Platform.h) | [前端与平台](frontend.md) |
| [PlatformOGL.h](../src/PlatformOGL.h) | [前端与平台](frontend.md) |
| [frontend/ScreenLayout.cpp](../src/frontend/ScreenLayout.cpp)、[frontend/ScreenLayout.h](../src/frontend/ScreenLayout.h) | [前端与平台](frontend.md) |
| [frontend/mic_blow.h](../src/frontend/mic_blow.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/ARCodeQDecl.h](../src/frontend/qt_sdl/ARCodeQDecl.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/AboutDialog.cpp](../src/frontend/qt_sdl/AboutDialog.cpp)、[frontend/qt_sdl/AboutDialog.h](../src/frontend/qt_sdl/AboutDialog.h)、[frontend/qt_sdl/AboutDialog.ui](../src/frontend/qt_sdl/AboutDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/ArchiveUtil.cpp](../src/frontend/qt_sdl/ArchiveUtil.cpp)、[frontend/qt_sdl/ArchiveUtil.h](../src/frontend/qt_sdl/ArchiveUtil.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/AudioSettingsDialog.cpp](../src/frontend/qt_sdl/AudioSettingsDialog.cpp)、[frontend/qt_sdl/AudioSettingsDialog.h](../src/frontend/qt_sdl/AudioSettingsDialog.h)、[frontend/qt_sdl/AudioSettingsDialog.ui](../src/frontend/qt_sdl/AudioSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/CLI.cpp](../src/frontend/qt_sdl/CLI.cpp)、[frontend/qt_sdl/CLI.h](../src/frontend/qt_sdl/CLI.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/CameraManager.cpp](../src/frontend/qt_sdl/CameraManager.cpp)、[frontend/qt_sdl/CameraManager.h](../src/frontend/qt_sdl/CameraManager.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/CameraSettingsDialog.cpp](../src/frontend/qt_sdl/CameraSettingsDialog.cpp)、[frontend/qt_sdl/CameraSettingsDialog.h](../src/frontend/qt_sdl/CameraSettingsDialog.h)、[frontend/qt_sdl/CameraSettingsDialog.ui](../src/frontend/qt_sdl/CameraSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/CheatImportDialog.cpp](../src/frontend/qt_sdl/CheatImportDialog.cpp)、[frontend/qt_sdl/CheatImportDialog.h](../src/frontend/qt_sdl/CheatImportDialog.h)、[frontend/qt_sdl/CheatImportDialog.ui](../src/frontend/qt_sdl/CheatImportDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/CheatsDialog.cpp](../src/frontend/qt_sdl/CheatsDialog.cpp)、[frontend/qt_sdl/CheatsDialog.h](../src/frontend/qt_sdl/CheatsDialog.h)、[frontend/qt_sdl/CheatsDialog.ui](../src/frontend/qt_sdl/CheatsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/Config.cpp](../src/frontend/qt_sdl/Config.cpp)、[frontend/qt_sdl/Config.h](../src/frontend/qt_sdl/Config.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/DateTimeDialog.cpp](../src/frontend/qt_sdl/DateTimeDialog.cpp)、[frontend/qt_sdl/DateTimeDialog.h](../src/frontend/qt_sdl/DateTimeDialog.h)、[frontend/qt_sdl/DateTimeDialog.ui](../src/frontend/qt_sdl/DateTimeDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/EmuInstance.cpp](../src/frontend/qt_sdl/EmuInstance.cpp)、[frontend/qt_sdl/EmuInstance.h](../src/frontend/qt_sdl/EmuInstance.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/EmuInstanceAudio.cpp](../src/frontend/qt_sdl/EmuInstanceAudio.cpp) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/EmuInstanceInput.cpp](../src/frontend/qt_sdl/EmuInstanceInput.cpp) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/EmuSettingsDialog.cpp](../src/frontend/qt_sdl/EmuSettingsDialog.cpp)、[frontend/qt_sdl/EmuSettingsDialog.h](../src/frontend/qt_sdl/EmuSettingsDialog.h)、[frontend/qt_sdl/EmuSettingsDialog.ui](../src/frontend/qt_sdl/EmuSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/EmuThread.cpp](../src/frontend/qt_sdl/EmuThread.cpp)、[frontend/qt_sdl/EmuThread.h](../src/frontend/qt_sdl/EmuThread.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/FirmwareSettingsDialog.cpp](../src/frontend/qt_sdl/FirmwareSettingsDialog.cpp)、[frontend/qt_sdl/FirmwareSettingsDialog.h](../src/frontend/qt_sdl/FirmwareSettingsDialog.h)、[frontend/qt_sdl/FirmwareSettingsDialog.ui](../src/frontend/qt_sdl/FirmwareSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/InputConfigDialog.cpp](../src/frontend/qt_sdl/InputConfig/InputConfigDialog.cpp)、[frontend/qt_sdl/InputConfig/InputConfigDialog.h](../src/frontend/qt_sdl/InputConfig/InputConfigDialog.h)、[frontend/qt_sdl/InputConfig/InputConfigDialog.ui](../src/frontend/qt_sdl/InputConfig/InputConfigDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/MapButton.h](../src/frontend/qt_sdl/InputConfig/MapButton.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/resources/LICENSE.md](../src/frontend/qt_sdl/InputConfig/resources/LICENSE.md) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/resources/ds.qrc](../src/frontend/qt_sdl/InputConfig/resources/ds.qrc) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/resources/ds_back.svg](../src/frontend/qt_sdl/InputConfig/resources/ds_back.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InputConfig/resources/ds_open.svg](../src/frontend/qt_sdl/InputConfig/resources/ds_open.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/InterfaceSettingsDialog.cpp](../src/frontend/qt_sdl/InterfaceSettingsDialog.cpp)、[frontend/qt_sdl/InterfaceSettingsDialog.h](../src/frontend/qt_sdl/InterfaceSettingsDialog.h)、[frontend/qt_sdl/InterfaceSettingsDialog.ui](../src/frontend/qt_sdl/InterfaceSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/LANDialog.cpp](../src/frontend/qt_sdl/LANDialog.cpp)、[frontend/qt_sdl/LANDialog.h](../src/frontend/qt_sdl/LANDialog.h)、[frontend/qt_sdl/LANDialog.ui](../src/frontend/qt_sdl/LANDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/LANStartClientDialog.ui](../src/frontend/qt_sdl/LANStartClientDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/LANStartHostDialog.ui](../src/frontend/qt_sdl/LANStartHostDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/MPSettingsDialog.cpp](../src/frontend/qt_sdl/MPSettingsDialog.cpp)、[frontend/qt_sdl/MPSettingsDialog.h](../src/frontend/qt_sdl/MPSettingsDialog.h)、[frontend/qt_sdl/MPSettingsDialog.ui](../src/frontend/qt_sdl/MPSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/NetplayDialog.cpp](../src/frontend/qt_sdl/NetplayDialog.cpp)、[frontend/qt_sdl/NetplayDialog.h](../src/frontend/qt_sdl/NetplayDialog.h)、[frontend/qt_sdl/NetplayDialog.ui](../src/frontend/qt_sdl/NetplayDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/NetplayStartClientDialog.ui](../src/frontend/qt_sdl/NetplayStartClientDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/NetplayStartHostDialog.ui](../src/frontend/qt_sdl/NetplayStartHostDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/OSD_shaders.h](../src/frontend/qt_sdl/OSD_shaders.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PathSettingsDialog.cpp](../src/frontend/qt_sdl/PathSettingsDialog.cpp)、[frontend/qt_sdl/PathSettingsDialog.h](../src/frontend/qt_sdl/PathSettingsDialog.h)、[frontend/qt_sdl/PathSettingsDialog.ui](../src/frontend/qt_sdl/PathSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/Platform.cpp](../src/frontend/qt_sdl/Platform.cpp) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/Platform_AAC.cpp](../src/frontend/qt_sdl/Platform_AAC.cpp) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/PowerManagementDialog.cpp](../src/frontend/qt_sdl/PowerManagement/PowerManagementDialog.cpp)、[frontend/qt_sdl/PowerManagement/PowerManagementDialog.h](../src/frontend/qt_sdl/PowerManagement/PowerManagementDialog.h)、[frontend/qt_sdl/PowerManagement/PowerManagementDialog.ui](../src/frontend/qt_sdl/PowerManagement/PowerManagementDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/battery.qrc](../src/frontend/qt_sdl/PowerManagement/resources/battery.qrc) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/dsi_battery2.svg](../src/frontend/qt_sdl/PowerManagement/resources/dsi_battery2.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/dsi_battery3.svg](../src/frontend/qt_sdl/PowerManagement/resources/dsi_battery3.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/dsi_batteryalmostempty.svg](../src/frontend/qt_sdl/PowerManagement/resources/dsi_batteryalmostempty.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/dsi_batteryfull.svg](../src/frontend/qt_sdl/PowerManagement/resources/dsi_batteryfull.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/PowerManagement/resources/dsi_batterylow.svg](../src/frontend/qt_sdl/PowerManagement/resources/dsi_batterylow.svg) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/QPathInput.h](../src/frontend/qt_sdl/QPathInput.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/RAMInfoDialog.cpp](../src/frontend/qt_sdl/RAMInfoDialog.cpp)、[frontend/qt_sdl/RAMInfoDialog.h](../src/frontend/qt_sdl/RAMInfoDialog.h)、[frontend/qt_sdl/RAMInfoDialog.ui](../src/frontend/qt_sdl/RAMInfoDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/ROMInfoDialog.cpp](../src/frontend/qt_sdl/ROMInfoDialog.cpp)、[frontend/qt_sdl/ROMInfoDialog.h](../src/frontend/qt_sdl/ROMInfoDialog.h)、[frontend/qt_sdl/ROMInfoDialog.ui](../src/frontend/qt_sdl/ROMInfoDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/Screen.cpp](../src/frontend/qt_sdl/Screen.cpp)、[frontend/qt_sdl/Screen.h](../src/frontend/qt_sdl/Screen.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/TitleImportDialog.ui](../src/frontend/qt_sdl/TitleImportDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/TitleManagerDialog.cpp](../src/frontend/qt_sdl/TitleManagerDialog.cpp)、[frontend/qt_sdl/TitleManagerDialog.h](../src/frontend/qt_sdl/TitleManagerDialog.h)、[frontend/qt_sdl/TitleManagerDialog.ui](../src/frontend/qt_sdl/TitleManagerDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/VideoSettingsDialog.cpp](../src/frontend/qt_sdl/VideoSettingsDialog.cpp)、[frontend/qt_sdl/VideoSettingsDialog.h](../src/frontend/qt_sdl/VideoSettingsDialog.h)、[frontend/qt_sdl/VideoSettingsDialog.ui](../src/frontend/qt_sdl/VideoSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/WifiSettingsDialog.cpp](../src/frontend/qt_sdl/WifiSettingsDialog.cpp)、[frontend/qt_sdl/WifiSettingsDialog.h](../src/frontend/qt_sdl/WifiSettingsDialog.h)、[frontend/qt_sdl/WifiSettingsDialog.ui](../src/frontend/qt_sdl/WifiSettingsDialog.ui) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/Window.cpp](../src/frontend/qt_sdl/Window.cpp)、[frontend/qt_sdl/Window.h](../src/frontend/qt_sdl/Window.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/font.h](../src/frontend/qt_sdl/font.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/main.cpp](../src/frontend/qt_sdl/main.cpp)、[frontend/qt_sdl/main.h](../src/frontend/qt_sdl/main.h) | [前端与平台](frontend.md) |
| [frontend/qt_sdl/main_shaders.h](../src/frontend/qt_sdl/main_shaders.h) | [前端与平台](frontend.md) |

## 持久化

| 源码文件 | 阅读主题 |
|---|---|
| [FATIO.cpp](../src/FATIO.cpp)、[FATIO.h](../src/FATIO.h) | [持久化](persistence.md) |
| [FATStorage.cpp](../src/FATStorage.cpp)、[FATStorage.h](../src/FATStorage.h) | [持久化](persistence.md) |
| [Savestate.cpp](../src/Savestate.cpp)、[Savestate.h](../src/Savestate.h) | [持久化](persistence.md) |
| [frontend/qt_sdl/SaveManager.cpp](../src/frontend/qt_sdl/SaveManager.cpp)、[frontend/qt_sdl/SaveManager.h](../src/frontend/qt_sdl/SaveManager.h) | [持久化](persistence.md) |

## JIT

| 源码文件 | 阅读主题 |
|---|---|
| [ARMJIT.cpp](../src/ARMJIT.cpp)、[ARMJIT.h](../src/ARMJIT.h) | [JIT](jit.md) |
| [ARMJIT_A64/ARMJIT_ALU.cpp](../src/ARMJIT_A64/ARMJIT_ALU.cpp) | [JIT](jit.md) |
| [ARMJIT_A64/ARMJIT_Branch.cpp](../src/ARMJIT_A64/ARMJIT_Branch.cpp) | [JIT](jit.md) |
| [ARMJIT_A64/ARMJIT_Compiler.cpp](../src/ARMJIT_A64/ARMJIT_Compiler.cpp)、[ARMJIT_A64/ARMJIT_Compiler.h](../src/ARMJIT_A64/ARMJIT_Compiler.h) | [JIT](jit.md) |
| [ARMJIT_A64/ARMJIT_Linkage.S](../src/ARMJIT_A64/ARMJIT_Linkage.S) | [JIT](jit.md) |
| [ARMJIT_A64/ARMJIT_LoadStore.cpp](../src/ARMJIT_A64/ARMJIT_LoadStore.cpp) | [JIT](jit.md) |
| [ARMJIT_Compiler.h](../src/ARMJIT_Compiler.h) | [JIT](jit.md) |
| [ARMJIT_Global.cpp](../src/ARMJIT_Global.cpp)、[ARMJIT_Global.h](../src/ARMJIT_Global.h) | [JIT](jit.md) |
| [ARMJIT_Internal.h](../src/ARMJIT_Internal.h) | [JIT](jit.md) |
| [ARMJIT_Memory.cpp](../src/ARMJIT_Memory.cpp)、[ARMJIT_Memory.h](../src/ARMJIT_Memory.h) | [JIT](jit.md) |
| [ARMJIT_RegisterCache.h](../src/ARMJIT_RegisterCache.h) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_ALU.cpp](../src/ARMJIT_x64/ARMJIT_ALU.cpp) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_Branch.cpp](../src/ARMJIT_x64/ARMJIT_Branch.cpp) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_Compiler.cpp](../src/ARMJIT_x64/ARMJIT_Compiler.cpp)、[ARMJIT_x64/ARMJIT_Compiler.h](../src/ARMJIT_x64/ARMJIT_Compiler.h) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_GenOffsets.cpp](../src/ARMJIT_x64/ARMJIT_GenOffsets.cpp) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_Linkage.S](../src/ARMJIT_x64/ARMJIT_Linkage.S) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_LoadStore.cpp](../src/ARMJIT_x64/ARMJIT_LoadStore.cpp) | [JIT](jit.md) |
| [ARMJIT_x64/ARMJIT_Offsets.h](../src/ARMJIT_x64/ARMJIT_Offsets.h) | [JIT](jit.md) |
| [ARM_InstrInfo.cpp](../src/ARM_InstrInfo.cpp)、[ARM_InstrInfo.h](../src/ARM_InstrInfo.h) | [JIT](jit.md) |
| [JitBlock.h](../src/JitBlock.h) | [JIT](jit.md) |

## 调试与辅助

| 源码文件 | 阅读主题 |
|---|---|
| [ARCodeFile.cpp](../src/ARCodeFile.cpp)、[ARCodeFile.h](../src/ARCodeFile.h) | [调试与辅助](debugging.md) |
| [ARDatabaseDAT.cpp](../src/ARDatabaseDAT.cpp)、[ARDatabaseDAT.h](../src/ARDatabaseDAT.h) | [调试与辅助](debugging.md) |
| [AREngine.cpp](../src/AREngine.cpp)、[AREngine.h](../src/AREngine.h) | [调试与辅助](debugging.md) |
| [CRC32.cpp](../src/CRC32.cpp)、[CRC32.h](../src/CRC32.h) | [调试与辅助](debugging.md) |
| [FIFO.h](../src/FIFO.h) | [调试与辅助](debugging.md) |
| [NonStupidBitfield.h](../src/NonStupidBitfield.h) | [调试与辅助](debugging.md) |
| [TinyVector.h](../src/TinyVector.h) | [调试与辅助](debugging.md) |
| [Utils.cpp](../src/Utils.cpp)、[Utils.h](../src/Utils.h) | [调试与辅助](debugging.md) |
| [debug/GdbArch.h](../src/debug/GdbArch.h) | [调试与辅助](debugging.md) |
| [debug/GdbCmds.cpp](../src/debug/GdbCmds.cpp)、[debug/GdbCmds.h](../src/debug/GdbCmds.h) | [调试与辅助](debugging.md) |
| [debug/GdbProto.cpp](../src/debug/GdbProto.cpp) | [调试与辅助](debugging.md) |
| [debug/GdbStub.cpp](../src/debug/GdbStub.cpp)、[debug/GdbStub.h](../src/debug/GdbStub.h) | [调试与辅助](debugging.md) |
| [debug/gdb_test/.gitignore](../src/debug/gdb_test/.gitignore) | [调试与辅助](debugging.md) |
| [debug/gdb_test/Makefile](../src/debug/gdb_test/Makefile) | [调试与辅助](debugging.md) |
| [debug/gdb_test/main.cpp](../src/debug/gdb_test/main.cpp) | [调试与辅助](debugging.md) |
| [debug/hexutil.h](../src/debug/hexutil.h) | [调试与辅助](debugging.md) |
| [types.h](../src/types.h) | [调试与辅助](debugging.md) |

## 构建

| 源码文件 | 阅读主题 |
|---|---|
| [CMakeLists.txt](../src/CMakeLists.txt) | [构建](build.md) |
| [OpenGL_shaders/CMakeLists.txt](../src/OpenGL_shaders/CMakeLists.txt) | [构建](build.md) |
| [frontend/qt_sdl/CMakeLists.txt](../src/frontend/qt_sdl/CMakeLists.txt) | [构建](build.md) |
| [net/CMakeLists.txt](../src/net/CMakeLists.txt) | [构建](build.md) |
| [version.h.in](../src/version.h.in) | [构建](build.md) |

## 第三方与随库资料

| 目录 | 基线文件数 | 用途 | 集成主题 |
|---|---:|---|---|
| [src/teakra](../src/teakra) | 83 | DSP 指令、内部外设、随库说明与测试工具 | [DSi 媒体](dsi-media.md) |
| [src/dolphin](../src/dolphin) | 19 | 宿主代码生成、ABI 和 CPU 能力 | [JIT](jit.md) |
| [src/fatfs](../src/fatfs) | 9 | FAT 文件系统 | [持久化](persistence.md) |
| [src/tiny-AES-c](../src/tiny-AES-c) | 5 | AES 块算法 | [DSi 存储](dsi-storage.md) |
| [src/sha1](../src/sha1) | 3 | NAND 等所需 SHA1 | [DSi 存储](dsi-storage.md) |
| [src/xxhash](../src/xxhash) | 3 | 缓存/代码摘要 | [JIT](jit.md) |
| [src/blip-buf](../src/blip-buf) | 4 | 声音重采样 | [声音](audio.md) |
| [src/net/libslirp](../src/net/libslirp) | 151 | 用户态网络栈及随库工具 | [无线与网络](wireless.md) |
| [src/net/pcap](../src/net/pcap) | 14 | 抓包接口声明 | [无线与网络](wireless.md) |
| [src/frontend/duckstation](../src/frontend/duckstation) | 23 | 宿主 GL context | [前端与平台](frontend.md) |
| [src/frontend/glad](../src/frontend/glad) | 10 | GL 函数加载 | [前端与平台](frontend.md) |
| [src/frontend/qt_sdl/toml](../src/frontend/qt_sdl/toml) | 59 | TOML 配置解析 | [前端与平台](frontend.md) |
| [src/frontend/qt_sdl/gif-h](../src/frontend/qt_sdl/gif-h) | 1 | GIF 输出 | [前端与平台](frontend.md) |

## 客体生成源、构建、工具与资源

| 路径 | 作用 | 阅读主题 |
|---|---|---|
| [freebios](../freebios) | 内置 BIOS 汇编、生成规则和来源说明 | [启动](boot.md)、[构建](build.md) |
| [melonDLDI](../melonDLDI) | homebrew SD 驱动源与生成 | [卡带](cartridge.md)、[构建](build.md) |
| [cmake](../cmake) | 依赖发现、编译标志、shader 嵌入与打包 | [构建](build.md) |
| [.github](../.github) | CI、issue/贡献工作流 | [构建](build.md) |
| [tools](../tools) | mac 库收集/universal、MSYS 分发、文档校验 | [构建](build.md) |
| [res](../res) | 图标、资源清单、桌面/应用打包资产 | [前端](frontend.md)、[构建](build.md) |
| [CMakeLists.txt](../CMakeLists.txt)、[CMakePresets.json](../CMakePresets.json) | 根目标与平台 presets | [构建](build.md) |
| [vcpkg.json](../vcpkg.json)、[flake.nix](../flake.nix)、[flake.lock](../flake.lock) | 依赖声明与锁定 | [构建](build.md) |
| [mise.toml](../mise.toml)、[BUILD.md](../BUILD.md) | task 与平台构建说明 | [构建](build.md) |
| [README.md](../README.md)、[CONTRIBUTING.md](../CONTRIBUTING.md)、[LICENSE](../LICENSE) | 项目入口、贡献约定与授权文本 | [总路由](README.md)、[构建](build.md) |
| [.gitignore](../.gitignore)、[.gitattributes](../.gitattributes) | 生成目录与文件属性 | [构建](build.md) |
