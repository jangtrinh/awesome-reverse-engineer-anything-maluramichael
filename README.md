# Awesome Reverse Engineer Anything [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

<!-- links:start -->
[![Support me on Ko-fi](https://malura.de/assets/badge/kofi.svg)](https://malura.de/go/kofi?ref=awesome-reverse-engineer-anything)
[![Check out my page](https://malura.de/assets/badge/malura.svg)](https://malura.de/go/site?ref=awesome-reverse-engineer-anything)
<!-- links:end -->

> Reverse engineering turns a closed program, protocol or device into something you can read, rebuild and run yourself. These are the open projects that did it and the tools they used, with star trends refreshed every day. Only what is hot makes it: at least 500 stars and a commit in the last year to get in, and once a project is in, it stays.

## Contents

- [Trending](#trending)
- [Apps](#apps)
- [Games](#games)
- [Emulators](#emulators)
- [Protocols, APIs and Formats](#protocols-apis-and-formats)
- [Hardware and Firmware](#hardware-and-firmware)
- [Tools](#tools)
- [Related Lists](#related-lists)
- [Growth](#growth)

## Trending

Most stars gained per day over the last 7 days, excluding related lists.

| Project | Category | Stars | Stars per day |
| --- | --- | ---: | ---: |
| [Clean Your TV](https://github.com/Gathin23/cleanyourtv) | [Hardware and Firmware](#hardware-and-firmware) | 49.7k | ~3,107 |
| [PhotoCraft](https://github.com/storytold/photocraft) | [Apps](#apps) | 76k | ~2,304 |
| [REA](https://github.com/morluto/rea) | [Tools](#tools) | 420.6k | ~2,082 |
| [Craft Anything](https://github.com/storytold/craft-anything) | [Tools](#tools) | 2.2k | ~1,099 |
| [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp) | [Games](#games) | 3.5k | ~874 |
| [Aerial TV](https://github.com/pengchujin/aerial-tv) | [Hardware and Firmware](#hardware-and-firmware) | 8.9k | ~685 |
| [WordCraft](https://github.com/storytold/wordcraft) | [Apps](#apps) | 17k | ~654 |
| [PdfCraft](https://github.com/storytold/pdfcraft) | [Apps](#apps) | 19.1k | ~580 |
| [nxnative](https://github.com/seedds/nxnative) | [Games](#games) | 11.2k | ~559 |
| [FilmCraft](https://github.com/storytold/filmcraft) | [Apps](#apps) | 17.3k | ~523 |
| [SolidCraft](https://github.com/tangency-labs/solidcraft) | [Apps](#apps) | 13k | ~501 |
| [LightCraft](https://github.com/storytold/lightcraft) | [Apps](#apps) | 15.3k | ~463 |
| [DroidDeck](https://github.com/Droid-Deck/DroidDeck) | [Emulators](#emulators) | 17.3k | ~444 |
| [MacNativeGames](https://github.com/ly05010419/MacNativeGames) | [Games](#games) | 6.8k | ~427 |
| [Free My TV](https://github.com/simbasjungles/free-my-tv) | [Hardware and Firmware](#hardware-and-firmware) | 5.7k | ~408 |

`~` is the lifetime average, used until a project has daily snapshots.

## Apps

Desktop software and operating systems rebuilt without the original source code.

### Crafting Apps

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [PhotoCraft](https://github.com/storytold/photocraft) | Adobe Photoshop | Image editor in pure Rust with layers, masks, type and real PSD files. | 76k | 2026-11-02 |
| [ArtCraft](https://github.com/storytold/artcraft) |  | AI image and video studio for artists, and the home of the Crafting Apps. | 38.3k | 2026-10-31 |
| [PdfCraft](https://github.com/storytold/pdfcraft) |  | PDF reader and editor in pure Rust. | 19.1k | 2026-11-02 |
| [FilmCraft](https://github.com/storytold/filmcraft) |  | Nonlinear video editor in pure Rust with color and sound. | 17.3k | 2026-11-02 |
| [WordCraft](https://github.com/storytold/wordcraft) | Microsoft Word | Clean-room word processor in pure Rust that reads and writes .docx files. | 17k | 2026-11-02 |
| [LightCraft](https://github.com/storytold/lightcraft) |  | Non-destructive photo library and raw developer in pure Rust. | 15.3k | 2026-11-02 |
| [SolidCraft](https://github.com/tangency-labs/solidcraft) |  | Parametric 3D CAD in pure Rust by Tangency Labs, a community Crafting App. | 13k | 2026-11-02 |
| [VectorCraft](https://github.com/storytold/vectorcraft) |  | Vector illustration tool in pure Rust. | 11.2k | 2026-11-02 |
| [EffectCraft](https://github.com/storytold/effectcraft) |  | Motion graphics and compositing tool in pure Rust. | 8.3k | 2026-11-02 |
| [CADCraft](https://github.com/storytold/cadcraft) | AutoCAD | Clean-room computer-aided design and drafting app in pure Rust. | 7.4k | 2026-11-02 |
| [GridCraft](https://github.com/storytold/gridcraft) | Microsoft Excel | Clean-room spreadsheet in pure Rust. | 7k | 2026-11-02 |
| [DesignCraft](https://github.com/storytold/designcraft) |  | Page layout and publishing editor in pure Rust. | 5k | 2026-11-02 |
| [Craft Launcher](https://github.com/storytold/craft-launcher) |  | App launcher for the Crafting Apps. | 4.7k | 2026-11-01 |
| [DeckCraft](https://github.com/storytold/deckcraft) | Microsoft PowerPoint | Clean-room presentation app in pure Rust. | 4.5k | 2026-11-02 |
| [FigCraft](https://github.com/storytold/figcraft) |  | Clean-room interface design and prototyping tool in pure Rust. | 4.1k | 2026-11-02 |
| [SoundCraft](https://github.com/storytold/soundcraft) | Avid Pro Tools | Clean-room audio recording and editing app in pure Rust. | 4k | 2026-11-02 |
| [TextureCraft](https://github.com/storytold/texturecraft) |  | 3D texture painting workflow in pure Rust. | 179 | 2026-11-02 |

### Clean-Room Rebuilds

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [OpenIDEA](https://github.com/l0ng-ai/openidea) | IntelliJ IDEA | Native IDE with a Rust core that keeps the IDEA keymap and tool windows, with a debugger, Git, terminal and database client. | 4.4k | 2026-11-02 |
| [BIMCraft](https://github.com/IPedrax/BIMCraft) | Autodesk Revit | Clean-room building information modeling in pure Rust, built to be driven by agents. | 850 | 2026-10-29 |

### Compatibility Layers

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [ReactOS](https://github.com/reactos/reactos) | Windows | Free Windows-compatible operating system. | 18.4k | 2026-11-02 |
| [Darling](https://github.com/darlinghq/darling) | macOS | Darwin and macOS emulation layer for Linux. | 13.7k | 2026-10-28 |
| [Wine](https://github.com/wine-mirror/wine) | Windows API | Runs Windows applications on Linux and macOS. GitHub mirror of the official repository. | 4.3k | 2026-10-30 |

## Games

Commercial games turned back into source code or native ports. None of these should ship game data.

### Decompilations

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [oot](https://github.com/zeldaret/oot) | The Legend of Zelda: Ocarina of Time | Decompilation of the N64 game. | 5.6k | 2026-10-18 |
| [pokeemerald](https://github.com/pret/pokeemerald) | Pokémon Emerald | Decompilation of the Game Boy Advance game. | 3.7k | 2026-10-01 |
| [melee](https://github.com/doldecomp/melee) | Super Smash Bros. Melee | Decompilation of the GameCube game. | 2.5k | 2026-10-28 |

### Static Recompilations

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) | The Legend of Zelda: Majora's Mask | Static recompilation for Windows, Linux and macOS. | 7.6k | 2026-09-25 |
| [Unleashed Recompiled](https://github.com/hedge-dev/UnleashedRecomp) | Sonic Unleashed | Unofficial PC port of the Xbox 360 version through static recompilation. | 5.3k | 2026-06-29 |
| [totk-pc-recomp](https://github.com/valentderah/totk-pc-recomp) | The Legend of Zelda: Tears of the Kingdom | Static recompilation to native Windows with a Vulkan renderer. Game files not included. | 3.5k | 2026-11-02 |
| [SavageWindRecomp](https://github.com/Revivedx/SavageWindRecomp) | The Legend of Zelda: Breath of the Wild | Work-in-progress static recompilation of the Switch version for Windows and Linux. Bring your own dump. | 2.8k | 2026-11-01 |
| [LASRecomp](https://github.com/peiikai/LASRecomp) | The Legend of Zelda: Link's Awakening | Static recompilation of the Switch game to native macOS, Windows and Linux. | 2.1k | 2026-11-02 |
| [skate3recomp](https://github.com/mchughalex/skate3recomp) | Skate 3 | Native recompilation for Windows, Linux and macOS. | 1.8k | 2026-07-24 |
| [SymphonyRecomp](https://github.com/BlackLabelHQ/SymphonyRecomp) | Castlevania: Symphony of the Night | Static recompilation of the PlayStation classic. | 1k | 2026-11-01 |

### Source Ports and Engine Rebuilds

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [OpenRA](https://github.com/OpenRA/OpenRA) | Command & Conquer: Red Alert | Real-time strategy engine in C# for early Westwood games. | 17.7k | 2026-10-28 |
| [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2) | RollerCoaster Tycoon 2 | Open source reimplementation of the game. | 16.5k | 2026-11-02 |
| [nxnative](https://github.com/seedds/nxnative) | Nintendo Switch games | Runs Switch games natively on iPhone, iPad and Mac by rewriting them, with a Horizon HLE host. | 11.2k | 2026-11-02 |
| [MacNativeGames](https://github.com/ly05010419/MacNativeGames) | The Legend of Zelda: Tears of the Kingdom, Breath of the Wild | Plays your own copies natively on Apple silicon Mac, iPhone and iPad without an emulator. | 6.8k | 2026-11-02 |
| [OpenMW](https://github.com/OpenMW/openmw) | The Elder Scrolls III: Morrowind | Open-world RPG engine that plays Morrowind. | 6.7k | 2026-11-01 |
| [Ship of Harkinian](https://github.com/HarbourMasters/Shipwright) | The Legend of Zelda: Ocarina of Time | PC port built from the decompilation. | 5.8k | 2026-11-01 |
| [Horizon](https://github.com/horizon-rust/horizon) | Minecraft: Java Edition | Rewrite from scratch in Rust, checked against vanilla with differential test harnesses. | 5.8k | 2026-11-02 |
| [NBlood](https://github.com/NBlood/NBlood) | Blood, Redneck Rampage, Powerslave | Reverse engineered ports of Build engine games. | 820 | 2026-10-02 |
| [MetroidPrimePort](https://github.com/Odrannnn/MetroidPrimePort) | Metroid Prime | Native port for Linux, Windows and Android built from the PrimeDecomp decompilation. No game assets included. | 621 | 2026-11-02 |

## Emulators

Consoles reimplemented in software.

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [shadPS4](https://github.com/shadps4-emu/shadPS4) | PlayStation 4 | Emulator for Windows, Linux, macOS and FreeBSD. | 34k | 2026-11-02 |
| [RPCS3](https://github.com/RPCS3/rpcs3) | PlayStation 3 | Emulator and debugger. | 20.3k | 2026-11-02 |
| [DroidDeck](https://github.com/Droid-Deck/DroidDeck) | SteamOS | Brings the SteamOS experience to Android. | 17.3k | 2026-11-02 |
| [PCSX2](https://github.com/PCSX2/pcsx2) | PlayStation 2 | Emulator. | 16k | 2026-11-02 |
| [Dolphin](https://github.com/dolphin-emu/dolphin) | GameCube, Wii | Emulator that plays both consoles on PC with improvements. | 15.8k | 2026-11-02 |
| [xemu](https://github.com/xemu-project/xemu) | Original Xbox | Emulator for Windows, macOS and Linux. | 4.2k | 2026-11-02 |
| [Xenia Canary](https://github.com/xenia-canary/xenia-canary) | Xbox 360 | Emulator research project. | 2.7k | 2026-11-01 |
| [ares](https://github.com/ares-emulator/ares) | Many consoles | Multi-system emulator focused on accuracy and preservation. | 1.9k | 2026-11-01 |

## Protocols, APIs and Formats

Open clients and libraries for closed protocols, private APIs and undocumented file formats.

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [OpenHaystack](https://github.com/seemoo-lab/openhaystack) | Apple Find My | Framework for tracking your own Bluetooth devices through the Find My network. | 13.9k | 2026-08-17 |
| [DiPlay](https://github.com/shihabal3amri/DiPlay) | Apple CarPlay | Independent CarPlay receiver for compatible Android head units. | 13.1k | 2026-10-28 |
| [Baileys](https://github.com/WhiskeySockets/Baileys) | WhatsApp Web | Socket-based TypeScript and JavaScript API. | 11.5k | 2026-11-01 |
| [OpenDrop](https://github.com/seemoo-lab/opendrop) | Apple AirDrop | Open AirDrop implementation in Python. | 9.9k | 2026-08-17 |
| [libimobiledevice](https://github.com/libimobiledevice/libimobiledevice) | iOS device protocols | Cross-platform library to communicate with iOS devices. | 8.3k | 2026-06-10 |
| [whatsmeow](https://github.com/tulir/whatsmeow) | WhatsApp Web | Go library for the multidevice API. | 7.7k | 2026-10-31 |
| [librespot](https://github.com/librespot-org/librespot) | Spotify | Open source client library. | 7.4k | 2026-10-21 |
| [YouTube.js](https://github.com/LuanRT/YouTube.js) | YouTube InnerTube API | JavaScript client for YouTube's internal API. | 5.4k | 2026-10-31 |
| [pypush](https://github.com/JJTech0130/pypush) | APNs, iMessage | Python client for Apple's push service and iMessage. | 3.8k | 2026-03-15 |
| [Samba](https://github.com/samba-team/samba) | SMB | File and print services for Windows clients. GitHub mirror of the official repository. | 1.1k | 2026-11-02 |
| [ShazamIO](https://github.com/shazamio/ShazamIO) | Shazam API | Asynchronous Python library. | 998 | 2026-11-02 |

## Hardware and Firmware

Devices, chips and cloud-locked gadgets opened up for local use.

### Smart TVs

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [Clean Your TV](https://github.com/Gathin23/cleanyourtv) | Android TV, Google TV | Strips ads and bloat from any Android or Google TV over Wi-Fi and adds an Apple TV-style home screen. | 49.7k | 2026-11-02 |
| [Aerial TV](https://github.com/pengchujin/aerial-tv) | Xiaomi, TCL home screens | Ad-free tvOS-style launcher for Xiaomi, TCL and other China-market TVs. | 8.9k | 2026-11-02 |
| [Free My TV](https://github.com/simbasjungles/free-my-tv) | Google TV, webOS, Tizen | Fast, ad-free home screen for Google TV, LG webOS and Samsung Tizen, with one button to undo. | 5.7k | 2026-10-31 |
| [dumbtv](https://github.com/humblemuzzu/dumbtv) | Fire TV | Takes ads, tracking and clutter out of a Fire TV over ADB without root, and every step can be undone. | 1.9k | 2026-10-27 |
| [Clean Your TV App](https://github.com/udhaykumarbala/cleanyourtv-app) | Android TV | Community phone app that runs Clean Your TV without a laptop or coding agent. | 1.4k | 2026-10-31 |
| [Tellyscope](https://github.com/man15h/tellyscope) | Android TV | Debloats an Android TV, installs apps and transfers files from your phone, without root. | 1.2k | 2026-11-02 |

### Devices and Firmware

| Project | Rebuilds | What it is | Stars | Last commit |
| --- | --- | --- | ---: | --- |
| [Valetudo](https://github.com/Hypfer/Valetudo) | Robot vacuum clouds | Cloud replacement for vacuum robots that enables local-only operation. | 9.9k | 2026-11-01 |
| [rtl_433](https://github.com/merbanan/rtl_433) | ISM band devices | Decodes radio transmissions from devices on the ISM bands. | 7.9k | 2026-10-27 |
| [m1n1](https://github.com/AsahiLinux/m1n1) | Apple Silicon | Bootloader and experimentation playground. | 4.3k | 2026-11-01 |
| [opendbc](https://github.com/commaai/opendbc) | Car CAN buses | Python API for your car. | 3.5k | 2026-10-31 |
| [dji-firmware-tools](https://github.com/o-gs/dji-firmware-tools) | DJI firmware | Tools for handling firmware of DJI products, with a focus on quadcopters. | 2.3k | 2026-10-25 |
| [python-kasa](https://github.com/python-kasa/python-kasa) | TP-Link smart home | Python API for TP-Link smart home products. | 1.8k | 2026-11-01 |
| [facetimehd](https://github.com/patjak/facetimehd) | FacetimeHD webcam | Reverse engineered Linux driver for the Broadcom 1570 PCIe webcam. | 1.5k | 2026-10-14 |
| [apple-knowledge](https://github.com/hack-different/apple-knowledge) | Apple hardware | Collection of reverse engineered Apple things and a machine-readable hardware database. | 1.4k | 2026-10-13 |
| [Project IceStorm](https://github.com/YosysHQ/icestorm) | Lattice iCE40 FPGAs | Reverse engineered bitstream documentation. | 1.2k | 2026-11-02 |
| [HomeKey-ESP32](https://github.com/rednblkx/HomeKey-ESP32) | Apple Home Key | ESP32 HomeKit lock with Home Key support. | 1.1k | 2026-10-17 |
| [open_oura](https://github.com/Th0rgal/open_oura) | Oura Ring | Rust toolkit with the reverse engineered BLE protocol, event decoders and reimplemented data processing. | 666 | 2026-10-07 |

## Tools

What people use to take things apart.

### AI Agents and MCP

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [REA](https://github.com/morluto/rea) | Reverse Engineer Anything: one MCP that lets agents analyze app behavior down to native binaries. | 420.6k | 2026-11-02 |
| [ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) | Bridges IDA Pro with language models through MCP. | 13.3k | 2026-09-26 |
| [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) | MCP server for Ghidra. | 11.7k | 2026-10-10 |
| [Universal Modder](https://github.com/rehan-remade/universal-modder) | Skills and tools that let Claude Code mod almost any PC game you own. | 9.3k | 2026-11-02 |
| [reverse-api-engineer](https://github.com/kalil0321/reverse-api-engineer) | Turns any website into a typed API client, with Claude Code, Codex, Cursor or OpenCode. | 2.4k | 2026-10-29 |
| [Craft Anything](https://github.com/storytold/craft-anything) | Crafting App that shows how any software works, then rebuilds it in clean-room or deep mode. | 2.2k | 2026-11-02 |
| [Co-op Anything](https://github.com/cranebeaker/coop-anything) | MCP server and playbook for adding co-op to single-player games with an AI agent. | 1.8k | 2026-11-02 |
| [Open ReverseLab](https://github.com/LING71671/open-reverselab) | Agent platform and MCP server for Ghidra, Frida, x64dbg and Rizin. | 1.3k | 2026-10-21 |
| [reverify](https://github.com/2akouwu/reverify) | Keeps AI reverse engineering honest: the model proposes, deterministic tools check every claim. | 1.3k | 2026-11-01 |
| [Eleven](https://github.com/Zfinix/eleven) | Agent-first reverse engineering for macOS, Windows and Linux. | 954 | 2026-10-31 |
| [Unbrowse](https://github.com/unbrowse-ai/unbrowse) | Finds the APIs behind a website so agents can call them directly. | 842 | 2026-10-30 |

### Decompilers and Disassemblers

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | Software reverse engineering framework. | 97k | 2026-11-02 |
| [jadx](https://github.com/skylot/jadx) | DEX to Java decompiler. | 51.5k | 2026-10-30 |
| [Apktool](https://github.com/iBotPeaches/Apktool) | Reverse engineers Android APK files. | 26.9k | 2026-11-02 |
| [ILSpy](https://github.com/icsharpcode/ILSpy) | Decompiler for .NET with PDB generation and ReadyToRun support. | 26.9k | 2026-11-01 |
| [radare2](https://github.com/radareorg/radare2) | UNIX-like reverse engineering framework and command-line toolset. | 25.2k | 2026-11-02 |
| [dnSpyEx](https://github.com/dnSpyEx/dnSpy) | Unofficial revival of the .NET debugger and assembly editor. | 11.4k | 2026-11-01 |
| [Rizin](https://github.com/rizinorg/rizin) | UNIX-like reverse engineering framework and command-line toolset. | 4.1k | 2026-11-01 |
| [ASC](https://github.com/MG1937/ASC) | Fast, lightweight Android decompiler for agents and mobile researchers. | 2.6k | 2026-10-30 |
| [Kuna](https://github.com/Noelo-Lab/kuna) | Agent-first decompiler in Rust, originally ported from Ghidra. | 780 | 2026-11-02 |

### Debuggers and Dynamic Analysis

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [x64dbg](https://github.com/x64dbg/x64dbg) | User mode debugger for Windows. | 50.2k | 2026-10-28 |
| [Frida](https://github.com/frida/frida) | Dynamic instrumentation toolkit. | 22.6k | 2026-11-01 |
| [capa](https://github.com/mandiant/capa) | Identifies capabilities in executable files. | 6.3k | 2026-11-02 |

### Binary and Firmware Inspection

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [ImHex](https://github.com/WerWolv/ImHex) | Hex editor for reverse engineers. | 55.7k | 2026-10-09 |
| [binwalk](https://github.com/ReFirmLabs/binwalk) | Firmware analysis tool. | 14.6k | 2026-08-11 |

### Network and API Capture

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [mitmproxy](https://github.com/mitmproxy/mitmproxy) | Interactive TLS-capable intercepting HTTP proxy. | 46.6k | 2026-11-01 |
| [mitmproxy2swagger](https://github.com/alufers/mitmproxy2swagger) | Reverse engineers REST APIs from captured traffic. | 9.7k | 2026-10-26 |

### Recompilers and Decomp Toolchains

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [N64Recomp](https://github.com/N64Recomp/N64Recomp) | Statically recompiles N64 games into native executables. | 8.3k | 2026-05-27 |
| [ps2-web-recomp](https://github.com/snuri00/ps2-web-recomp) | Static recompilation of PS2 games to WebAssembly with a native runtime. | 1.4k | 2026-10-29 |
| [decomp.me](https://github.com/decompme/decomp.me) | Collaborative decompilation and reverse engineering website. | 653 | 2026-11-01 |

## Related Lists

Other lists and directories on the same subject.

| Project | What it is | Stars | Last commit |
| --- | --- | ---: | --- |
| [Awesome Decomp Games](https://github.com/SubmitGame/awesome-decomp-games) | Rated, auto-refreshed list of decompiled, recompiled and reverse engineered games. | 2.8k | 2026-11-01 |
| [Awesome Reverse Engineering](https://github.com/morluto/awesome-reverse-engineering) | Curated tools and learning resources, by the creators of REA. | 1.5k | 2026-10-30 |
| [Awesome Reverse-Engineered](https://github.com/alexgaoth/awesome-reverse-engineered) | Searchable index of more than 17,000 projects built by reverse engineering. | 1.1k | 2026-11-01 |
| [Awesome REA by reacher-z](https://github.com/reacher-z/Awesome-REA) | Tools, case studies and research papers across six reverse engineering domains. | 805 | 2026-11-02 |

## Growth

Projects never leave the list, so it only gets bigger.

| Month | New | Total | |
| --- | ---: | ---: | --- |
| 2026-11 | 111 | 111 | ██████████████████████████████ |

## Contributing

New entries are welcome. [Open an issue](https://github.com/maluramichael/awesome-reverse-engineer-anything/issues/new?template=add-project.yml) and a bot prepares the pull request, or read the [contribution guidelines](contributing.md).

## Footnotes

111 projects. Stars last fetched on 2026-11-02. This file is generated from [`data/projects`](data/projects), please do not edit it by hand.
