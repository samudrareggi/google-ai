# ePlus AI Toolkit — 简体中文

<!-- Source README.md git-blob: 2b8488a21c25e7b771f7a4014f8b945e182fe285 -->

[English](README.md) · [Tiếng Việt](README.vi.md) · **简体中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)


> **原始文档：**[英文 README](README.md)。中文版采用更易理解的表述，同时保留原文中的命令、技术要求和安全警告。如文档与实际运行情况不一致，请以源代码及英文原文为准。

**ePlus AI Toolkit** 用于查看 Android 设备上的 Google One 和 Google Play 提供的 Google AI Pro 优惠。它支持 **Windows 和 macOS**：Windows 用户通过 PowerShell 启动，Mac 用户则使用 Terminal（zsh/bash）。Textual 图形化终端界面与命令行模式共用 Python、ADB 和 Frida 执行引擎。

![ePlus AI Toolkit 界面](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **非官方工具，可能产生真实费用。** **Step 2–5** 可能打开 Google Play 的真实结账页面，并自动点击 **Subscribe（订阅）**。发现优惠、看到首期价格为 0，或收到“已提交结账”的消息，**均不代表**账户有资格、订阅免费、已激活或续期成功。每次操作前，请在 Google Play 上核实账户、本次收费、后续价格和续订日期。停止工具不能撤销已经提交的交易。

> [!NOTE]
> **至少准备 3 美元可用余额，用于三笔各 1 美元的独立交易，并非一次扣除 3 美元。** 在用户报告的 **24 个月**流程中，Step 2（最初 12 个月）、Step 3（延长 6 个月）和 Step 4（再延长 6 个月）各涉及**一笔 1 美元的银行卡验证或支付交易**：**3 × US$1 = US$3**。其中的 1 美元可能只是临时预授权冻结，并非已入账的实际扣款；金额也可能因银行、账户或 Google Play 的要求而不同。**3 美元只是这一案例的最低备用余额，不是固定手续费，也不保证所有账户都能获得 24 个月。** 预授权会暂时占用可用余额，通常依据银行处理情况在 **1–14 个工作日**内解除。每完成一步，请到 Google Play 核实交易状态和订阅续订日期。可选的 Step 5 **不计入上述三笔交易**。[Google Play 官方说明](https://support.google.com/googleplay/answer/6224192?hl=en)。

## 免责声明

本项目与 **Google、Google One、Google Play、NetEase、MuMuPlayer 没有从属或官方合作关系**。软件按**现状**提供，不保证优惠可用、订阅结果或设备兼容性。仅在您拥有或获授权使用的设备、账户上运行，并遵守法律及平台条款。详情参见[完整免责声明（英文）](DISCLAIMER.md)和[安全说明](SECURITY.md)。

## 1. 使用前的准备工作

**请按照自己的操作系统进行设置。** Mac 用户无需安装 PowerShell。

| 项目 | Windows | macOS |
| --- | --- | --- |
| 终端 | **PowerShell 5.1 或更高版本** | 系统自带的 **Terminal**（zsh/bash） |
| Python | **3.10 或更高版本**，使用 `python` 命令 | **3.10 或更高版本**，使用 `python3`；启动时创建本地 `.venv` 环境 |
| Git | Git for Windows | 通过 Xcode Command Line Tools 或 Homebrew 安装 |
| Android 环境 | 已开启 root 和 ADB 的设备或模拟器；项目提供 **Windows 版 MuMuPlayer** 的操作流程 | 已 root 的 Android 设备或兼容模拟器；**Mac 版 MuMuPlayer Pro** 适用于 Apple Silicon，不支持 Intel Mac |
| Android 应用 | Google Play Store 和 Google One，并登录要检查的账户 | 所选 Android 设备上同样需要安装这两个应用 |
| ADB | 工具可按需查找或下载 Android SDK Platform-Tools | 需单独安装，例如 `brew install android-platform-tools`；使用 `adb devices` 检查连接 |
| Frida | **16.5.9**，可由 Windows 配置程序准备 | 在 `.venv` 中安装 **16.5.9**，仍需核实与 Android 的兼容性 |
| 启动命令 | `.\run-all.ps1` | `sh run-macos.sh` 或 `ePlus-AI-Toolkit.command` |

无论使用哪种系统，都需要一个已经正确配置、且你有权访问的 Android 环境。虽然 macOS 版本已实现 Steps 0–5，**但尚未在真实 Mac/MuMu 环境中验证支付流程**。另请参考 [Windows 指南](docs/INSTALLATION.md)和 [macOS 指南](docs/MACOS-PREVIEW.md)。

### Windows 环境要求

- Windows，已安装 **PowerShell 5.1 或更高版本**及 **Python 3.10 或更高版本**。
- 自行安装 MuMuPlayer，并为 Android 实例启用 root 和 ADB 调试。
- 在 Android 中安装 Google Play Store 和 Google One，使用要检查优惠的 Google 账户登录。
- 准备可连接的 ADB 和兼容的 **Frida 16.5.9**。本工具可协助配置，但**不会代为安装 MuMuPlayer**。

### 第一步 — 安装 MuMuPlayer

从 [MuMuPlayer 官方网站（NetEase）](https://www.mumuplayer.com/download/)下载 Windows 版本。请勿使用来源不明的下载站点。

启动模拟器后，启用 root 权限和 ADB 调试。确保 Google Play Store 和 Google One 可用，并登录正确的 Google 账户。

需要图文步骤时，可参阅 [GitHub Wiki 安装指南](https://github.com/hoangsvit/google-ai/wiki/Install)。

## 2. 获取并启动

在 PowerShell 中运行：

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

已克隆仓库时：

```powershell
git pull --ff-only
.\run-all.ps1
```

**不带参数**会打开 Textual 交互界面，而非立即执行结账。首次启动或检查时可能自动配置 Textual、ADB、Frida；通常不需要预先执行 `setup_env.py`。环境准备可能修改模拟器、代理或网络配置。

如 ADB 已在 PATH 中，检查设备：

```powershell
adb devices
```

设备应显示为 `device`，不能是 `offline` 或 `unauthorized`。有问题请参考[详细故障排查](docs/DETAILED-GUIDE.md)。

### 最新版本无法使用时，尝试已发布版本

如果运行仓库最新代码遇到错误，可以尝试 [GitHub Releases](https://github.com/hoangsvit/google-ai/releases) 中**已发布的版本**。先阅读版本说明；若附带 Windows 安装包，可下载相应文件。若页面只有 GitHub 自动提供的 **Source code (zip)**，请下载 ZIP 并解压，在解压后的文件夹打开 PowerShell，然后运行：

```powershell
.\run-all.ps1
```

**Source code (zip) 不是预编译的 `.exe` 或安装程序。** 建议将发布版本放在**独立文件夹**，不要覆盖当前仓库。旧版本可能缺少最新修复；仍需 Windows、Python、MuMuPlayer、ADB/Frida，并遵守相同的支付安全注意事项。如果问题仍在，请参考[故障排查](docs/DETAILED-GUIDE.md)或[提交 Issue](https://github.com/hoangsvit/google-ai/issues)。

## macOS — 安装和启动

macOS 需安装 **Git**、**Python 3.10+** 与 **Android SDK Platform-Tools (ADB)**（Homebrew：`brew install android-platform-tools`）。连接已 root、具有 Google Play Store 和 Google One 的 Android 设备或兼容模拟器。Mac 版 **MuMuPlayer Pro 支持 Apple Silicon**，Intel Mac 需要其他兼容 Android 环境。

在 **Terminal** 中执行：

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh` 打开包含 **步骤 0–5** 的 Textual 界面。`--check` 检查环境（可能改变配置）；`--list` 仅查询优惠；`--step 2` 只预选该步骤，**不会自动付款**。步骤 2–5 可能产生真实费用，必须逐步确认。**真实 Mac/MuMu 上的支付尚未验证。** 参阅 [Mac 详细指南](docs/MACOS-PREVIEW.md)。

## 检查 Android 连接并查看优惠（Windows + macOS）

控制台提供两项检查功能，分别参考了原项目的 Android 配置流程和优惠列表：

- **Diagnose Android connection（连接诊断）：** 检查电脑是否安装 ADB、列出已授权的 Android 设备，并读取设备 ABI、Google One 安装状态及电脑端 Frida 的版本。Windows 用户会看到 PowerShell、MuMu、Platform-Tools 的操作建议；macOS 用户则会看到 Terminal 和 Homebrew 的说明。此功能**不会安装软件、连接或重启模拟器、启动 Frida，也不会进行支付**。不过，执行 `adb devices` 可能会启动本地 ADB 服务。
- **Check Device & Offers (Step 1)（检查设备与优惠）：** 使用现有 Android/Frida 流程查询优惠，并在 Live Status 下方的 **Offer Explorer** 中展示结果。页面只显示产品 ID、优惠 ID、首个计费周期以及首期价格是否为零，**不会展示**优惠或购买 token、未经脱敏的账户标识和银行卡信息。与连接诊断不同，该步骤可能会准备 Android 环境，**因此并非完全没有副作用**。

**首期价格为零，不等于一定可以免费使用或成功延长订阅。** Step 1 只在列表查询模式下检查 `g1.2tb.ai.subs_variant`、`g1.play.2tb.ai` 和 `g1.2tb.ai`，而 Steps 2–5 继续使用各自的查询流程。由于 Android 报告未提供后续各期的完整费用信息，Offer Explorer 会把未来价格标记为**尚未验证**。实际收费与续费条款请在 Google Play 中确认。

## 3. Textual 界面

在某个步骤运行期间，**Check Device & Offers**、**Run** 以及模式和步骤选择功能会暂时锁定，避免重复执行。Step 0 可能修改电脑上的设置；Step 1 虽不会主动付款，但在准备过程中可能调整 ADB/Frida。请先到 Google Play 核实结果，再进入下一步。**点击 Stop 或 Exit 并不能撤销已提交的交易。**


点击 **Check Device & Offers** 执行 **Step 1 — Available offers**：查询优惠，**不会发起订阅结账**。可通过 **Live Status** 和 **Show technical details** 查看进度。如果 30 秒内没有新日志，程序会给出提醒，但这**不一定表示程序卡住了**。

在 Windows 上，请先在 Google Play 中登录要使用的账号，再查询优惠。如果工具核实了账号，并找到首期价格为零的 12 个月优惠，请选择 **Review 12-month checkout** 查看详情并单独确认 Step 2。若有提示，请直接在 Google Play 中填写付款信息。结账后，请在那里核实实际订阅状态和续订日期。

在 Windows 上，**Prepare MuMu** 可创建并打开新的竖屏 Android 15 实例。请输入要检测的 Google Play 邮箱，然后在 MuMu 中登录并完成所需验证。检测到账户后，选择 **Check Device & Offers**，在新实例上运行 Step 1。

在 **Advanced: Run by step** 中，可选择：

| 模式 | 行为 |
| --- | --- |
| **One step only** | 只执行所选的 Step 0–5 |
| **From selected step** | 从所选 Step 2–5 启动引导式流程 |
| **All: Steps 2–5** | 从 Step 2 启动引导式流程；Step 5 可选 |

| 步骤 | 用途 | 风险 |
| --- | --- | --- |
| **0 — Environment** | 准备/诊断 Android、ADB、Frida | 不结账，但可能修改本地/模拟器设置 |
| **1 — Available offers** | 查询 Google Play 优惠 | 不结账，但预检查可能修改环境 |
| **2 — Pro 12 months** | 原始 12 个月优惠流程 | **可能扣费** |
| **3 — Pro +6 months** | 原始订阅更新流程 | **可能扣费** |
| **4 — Pro +6 months (second)** | 第二次订阅更新流程 | **可能扣费** |
| **5 — Optional +6 months** | 可选更新流程 | **可能扣费** |

**用户报告的 24 个月示例（需要在 Google Play 核实）：**

| 步骤 | 成功生效后的累计时长 | 独立交易 |
| --- | --- | --- |
| **2 — Pro 12 months** | 最初 **12 个月** | **1 美元**（第 1 笔） |
| **3 — Pro +6 months** | 合计 **18 个月** | **1 美元**（第 2 笔） |
| **4 — Pro +6 months (second)** | 合计 **24 个月** | **1 美元**（第 3 笔） |
| **截至 Step 4** | 核实后合计 **24 个月** | **3 × US$1 = US$3**，不是一次支付 3 美元 |

**可选的 Step 5 不计入这三笔交易。** 页面上显示的时长或银行卡预授权并不能证明续期成功；每一步完成后都应在 Google Play 中确认订阅和续订日期。

以上月数只是**历史流程名称**，不保证真正延长订阅。如果已有有效订阅，**不要重复 Step 2**。

TUI 中**每个结账步骤均需单独批准**。当工具提示已尝试提交结账时，请到 [Google Play Subscriptions](https://play.google.com/store/account/subscriptions) 亲自确认实际套餐、收费与续订日期。只有确认订阅确实改变后才能选择 **Verified in Google Play → Next**；工具本身**无法独立证明激活成功**。

**停止与退出：**Step 0–1 的 Stop 会请求终止本地检查。Step 2–5 的 **Stop after this step** 只阻止后续步骤，**不会强制中断正在进行的支付**。**Q / Exit** 在结账期间会等当前步骤结束；**D** 切换技术日志，**R** 执行当前选择。

## 4. PowerShell 命令行操作（高级）

**仅适用于 Windows。** 以下命令在 PowerShell 中使用。Mac 用户请改用 `run-macos.sh`，并参考 [macOS 使用指南](docs/MACOS-PREVIEW.md)。启动时指定参数会直接进入 CLI 模式，而不是打开 Textual 界面。

**查询/诊断：不发起结账**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**以下命令可能发起真实交易：**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

与 TUI 不同，独立执行 `-Step 2..5` 时 **PowerShell 不会再次弹出批准提示**。请确认自己确实希望发起结账并已核实条款。

引导式 CLI：

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

CLI 确认选项为 **1 = Continue（继续）、2 = End run（结束）、0 = Stop（停止）**。每步后必须自行检查 Google Play。使用 `-StartStep 3` **不代表**前面的订阅更新已成功。

可指定设备或预期账号：

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

仅使用 ADB 实际显示的序列号。请避免 `-Force`：它会绕过账号匹配检查，但**不能**绕过优惠资格或 Google 支付限制。

## 5. 查看结果与排查问题

- **检测不到 MuMu/ADB：**检查模拟器运行状态、root、ADB 授权及设备连接。
- **Frida 错误：**查看技术日志，核对 **16.5.9** 及 Android 兼容性。
- **没有优惠：**启动 Google One/Play Store，重新执行 **Step 1**。
- **账户不匹配：**在 Play Store 检查登录账号，不要跳过验证。
- **已尝试提交结账：**不等于成功续订；重新操作前必须在 Google Play 上确认。
- **支付安全错误（如 OR-REH-04）：**停止付费步骤，按官方流程处理账号安全问题。

日志位于 `logs/`，报告位于 `ultra0-report/`。**不要公开包含账户、token 或支付信息的原始文件。** CI 仅执行静态检查和模拟测试，**不会进行或验证真实的 Google Play 交易**。

## 社区支持及相关项目

安装或使用 ePlus AI Toolkit 时遇到问题，可通过 [ePlus Telegram 支持/讨论帖](https://t.me/eplus_news/29) 与社区联系、交流排错经验。可复现的软件问题也可以[提交 GitHub Issue](https://github.com/hoangsvit/google-ai/issues)。**请勿公开密码、OTP/2FA 验证码、优惠或购买 token、未经脱敏的日志以及银行卡信息。** 此渠道是社区交流，不属于 Google 官方支持。

**无法参与 Google AI Pro 优惠？** 可另行了解 ePlus.DEV 的 [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub)，在[网站上查找或分享 Muse 邀请码](https://muse.eplus.dev/)。**Muse 是独立服务**，Muse 邀请码**不能激活或替代** Google AI Pro 订阅，也不保证邀请码可用；资格可能受地区或账户限制。

## 项目文件结构

为保证现有使用说明仍然有效，启动脚本和主要 Python 模块保留在仓库根目录。Windows 使用 `run-all.ps1`，macOS 使用 `run-macos.sh`。

| 文件或目录 | 用途 |
| --- | --- |
| `run-all.ps1` | 在 Windows 上打开 Textual 界面或命令行模式 |
| `run-macos.sh`、`ePlus-AI-Toolkit.command`、`macos_runner.py` | 在 Mac 上启动、运行 Steps 0–5；尚未验证真实支付 |
| `tui.py`、`tui_core.py`、`ultra0.py`、`setup_env.py`、`device_selector.py`、`query_sku.py` | 工具当前使用的 Python 组件 |
| [`tools/windows/`](tools/windows/README.md) | 按需使用的 Windows 手动配置工具 |
| [`legacy/windows/`](legacy/windows/README.md) | 旧版 .bat 脚本；部分脚本使用 `--force` 跳过账户检查，**可能产生实际费用** |
| `scripts/`、`assets/` | 辅助脚本及 Android/Frida 资源 |
| `tests/`、`.github/workflows/`、`docs/` | 自动测试、GitHub Actions 与文档 |

## 文档与参与贡献

[英文 README](README.md) · [安装 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [详细指南](docs/DETAILED-GUIDE.md) · [原始步骤说明](docs/ORIGINAL-STEPS.md) · [免责声明](DISCLAIMER.md) · [安全说明](SECURITY.md) · [贡献](CONTRIBUTING.md) · [第三方版权声明](THIRD_PARTY_NOTICES.md)

另请参阅[项目结构](docs/PROJECT.md)、[控制台/CLI 用法](docs/USAGE.md)、[支付安全](docs/SAFETY.md)、[原作者备注](docs/AUTHOR-NOTES.md)及 [AI 代理规则](AGENTS.md)。GitHub Actions 仅测试 Python、PowerShell、Textual 及模拟的 Frida/Billing 行为，**不会执行真实 Google Play 交易**。CI 测试通过并不代表工具一定能在你的设备上运行，也不能证明账户符合优惠条件。

## 致谢

**原作者：**[@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra)。**维护者：**[David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev)。原始 MIT 版权声明保留在 `THIRD_PARTY_NOTICES.md`。

[文档主页](docs/README.md) · [历史中文参考指南](docs/i18n/README.zh-CN.md) · [付款安全](docs/SAFETY.md)
