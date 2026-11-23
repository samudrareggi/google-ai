# ePlus AI Toolkit — 한국어

<!-- Source README.md git-blob: a68087fe5b1794e92832f5ff1bfd41dca32f3d53 -->

[English](README.md) · [Tiếng Việt](README.vi.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · **한국어** · [Español](README.es.md) · [Français](README.fr.md)


> **원본 문서:** [영어 README](README.md). 한국어로 쉽게 읽을 수 있도록 설명을 다듬었으며, 명령어와 기술적 조건, 안전 경고는 원본에 맞추었습니다. 설명과 실제 동작이 다를 경우 소스 코드와 영어 문서를 확인하세요.

**ePlus AI Toolkit**은 Android 기기의 Google One과 Google Play에 표시되는 Google AI Pro 혜택을 확인하는 도구입니다. **Windows**에서는 PowerShell로, **macOS**에서는 Terminal(zsh/bash)로 실행합니다. Textual 화면과 명령줄 방식은 모두 Python·ADB·Frida 기반의 동일한 실행 엔진을 사용합니다.

![ePlus AI Toolkit 화면](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **비공식 도구이며 실제 요금이 청구될 수 있습니다.** **Step 2–5**는 실제 Google Play 결제 화면을 열고 상황에 따라 **Subscribe(구독)**를 자동으로 누를 수 있습니다. 프로모션이 표시되거나 첫 결제 금액이 0이거나 결제 요청 메시지가 나타나더라도 **프로모션 적용, 무료 구독, 구독 활성화, 기간 연장이 확인된 것은 아닙니다**. 실행 전에 Google Play에서 계정, 오늘의 결제 금액, 이후 요금과 갱신일을 확인해야 합니다. 도구를 중지해도 이미 제출한 거래는 취소되지 않습니다.

> [!NOTE]
> **미화 3달러가 한 번에 결제되는 것이 아니라, 1달러씩 세 번의 별도 거래가 진행되므로 최소 3달러의 사용 가능 잔액을 준비하세요.** 보고된 **24개월** 이용 사례는 Step 2(최초 12개월), Step 3(+6개월), Step 4(추가 +6개월)에서 **각각 1달러의 카드 확인 또는 결제 거래**가 발생한 흐름입니다. 합계는 **3 × US$1 = US$3**입니다. 다만 1달러는 실제 확정 청구가 아닌 임시 승인 보류일 수도 있으며, 은행·계정·Google Play에 따라 금액이 달라질 수 있습니다. **3달러는 이 사례의 최소 준비 잔액일 뿐 고정 수수료나 24개월 이용 보장이 아닙니다.** 임시 승인 금액은 사용 가능 잔액을 줄일 수 있으며 은행에 따라 보통 **영업일 기준 1~14일** 내 해제됩니다. 각 단계가 끝나면 Google Play에서 거래 상태와 갱신일을 직접 확인하세요. 선택 사항인 Step 5는 **이 세 거래에 포함되지 않습니다**. [Google Play 공식 안내](https://support.google.com/googleplay/answer/6224192?hl=en).

## 면책 고지

이 프로젝트는 Google, Google One, Google Play, NetEase, MuMuPlayer와 **제휴·후원·승인 관계가 없는 독립 비공식 도구**입니다. 소프트웨어는 **있는 그대로** 제공되며 프로모션 자격, 결제 결과, 에뮬레이터 호환성을 보장하지 않습니다. 본인이 소유하거나 사용 권한이 있는 장치 및 계정에서만 사용하고, 법률과 플랫폼 약관을 준수하세요. [전체 면책 고지(영어)](DISCLAIMER.md)와 [보안 안내](SECURITY.md)를 참고하세요.

## 1. 사용 전 준비

**사용하는 운영체제에 맞춰 준비하세요.** macOS에서는 PowerShell을 설치할 필요가 없습니다.

| 항목 | Windows | macOS |
| --- | --- | --- |
| 터미널 | **PowerShell 5.1 이상** | 기본 **Terminal**(zsh/bash) |
| Python | **3.10 이상**(`python` 명령어) | **3.10 이상**(`python3`). 실행 시 로컬 `.venv` 생성 |
| Git | Git for Windows | Xcode Command Line Tools 또는 Homebrew |
| Android 환경 | 루팅 및 ADB를 활성화한 기기나 에뮬레이터. **Windows용 MuMuPlayer** 사용 절차 지원 | 루팅된 Android 기기 또는 호환 에뮬레이터. **Mac용 MuMuPlayer Pro**는 Apple Silicon 기종용이며 Intel Mac에서는 사용할 수 없음 |
| Android 앱 | 확인할 계정으로 로그인한 Google Play Store 및 Google One | 연결할 Android 기기에 같은 앱 필요 |
| ADB | 필요한 경우 Android SDK Platform-Tools 검색·다운로드 가능 | 별도로 설치(예: `brew install android-platform-tools`). `adb devices`로 확인 |
| Frida | **16.5.9**. Windows 설정 도구가 준비할 수 있음 | 로컬 `.venv`에 **16.5.9** 설치. Android 기기와의 호환성 확인 필요 |
| 실행 | `.\run-all.ps1` | `sh run-macos.sh` 또는 `ePlus-AI-Toolkit.command` |

두 운영체제 모두 사용할 권한이 있고 올바르게 설정된 Android 환경이 필요합니다. macOS용 코드에는 Steps 0–5가 포함되어 있지만, **실제 Mac/MuMu 환경에서 결제가 정상 동작하는지는 검증되지 않았습니다**. [Windows 안내](docs/INSTALLATION.md)와 [macOS 안내](docs/MACOS-PREVIEW.md)를 함께 확인하세요.

### Windows 요구 사항

- **PowerShell 5.1 이상**과 **Python 3.10 이상**이 설치된 Windows.
- 별도로 설치한 MuMuPlayer. Android 인스턴스에서 루팅과 ADB 디버깅을 켜야 합니다.
- 확인할 Google 계정으로 로그인한 Google Play Store와 Google One.
- 연결 가능한 ADB 및 호환되는 **Frida 16.5.9**. 도구가 설정을 도울 수 있지만 **MuMuPlayer 자체를 설치하지는 않습니다**.

### 1단계 — MuMuPlayer 설치

[MuMuPlayer 공식 웹사이트(NetEase)](https://www.mumuplayer.com/download/)에서 Windows 버전을 내려받으세요. 출처가 불분명한 다운로드 사이트는 사용하지 않는 것이 좋습니다.

에뮬레이터를 실행한 뒤 루팅과 ADB 디버깅을 활성화합니다. Google Play Store와 Google One을 사용할 수 있는지 확인하고, 혜택을 조회할 Google 계정으로 로그인하세요.

그림과 함께 설명한 [GitHub Wiki 설치 가이드](https://github.com/hoangsvit/google-ai/wiki/Install)도 참고할 수 있습니다.

## 2. 설치 및 실행

PowerShell에서 실행:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

이미 저장소를 다운로드했다면:

```powershell
git pull --ff-only
.\run-all.ps1
```

**인자 없이 실행**하면 Textual 대시보드가 열리고 결제는 자동으로 시작되지 않습니다. 필요한 경우 Textual, ADB, Frida를 준비합니다. 일반적으로 `setup_env.py`를 미리 실행할 필요가 없습니다. 초기 준비 과정은 에뮬레이터, 프록시 또는 네트워크 설정을 변경할 수 있습니다.

ADB가 PATH에 있다면 연결 확인:

```powershell
adb devices
```

장치 상태가 `device`여야 하며 `offline`이나 `unauthorized`이면 안 됩니다. 문제 해결은 [상세 가이드](docs/DETAILED-GUIDE.md)를 참고하세요.

### 최신 버전이 작동하지 않으면 기존 릴리스 사용

최신 소스 코드 실행 중 오류가 발생한다면 [GitHub Releases](https://github.com/hoangsvit/google-ai/releases)에서 **공개된 릴리스 버전**을 사용해 볼 수 있습니다. 릴리스 노트를 확인하고 Windows용 첨부 파일이 있는 경우 해당 파일을 받으세요. GitHub에서 자동 제공하는 **Source code (zip)**만 있다면 ZIP을 다운로드하고 압축을 푼 다음, 해당 폴더에서 PowerShell을 열어 실행하세요.

```powershell
.\run-all.ps1
```

**Source code (zip)은 미리 빌드된 `.exe`나 설치 프로그램이 아닙니다.** 기존 소스 폴더를 덮어쓰지 말고 **별도 폴더**에 보관하세요. 이전 릴리스에는 최신 버그 수정이 빠져 있을 수 있습니다. Windows, Python, MuMuPlayer, ADB/Frida와 결제 관련 주의사항은 여전히 필요합니다. 문제가 계속되면 [문제 해결 가이드](docs/DETAILED-GUIDE.md) 또는 [Issues](https://github.com/hoangsvit/google-ai/issues)를 확인하세요.

## macOS — 설치 및 실행

macOS에서는 **Git**, **Python 3.10+**, **Android SDK Platform-Tools (ADB)**를 설치하세요(Homebrew: `brew install android-platform-tools`). Google Play Store/Google One이 있는 루팅 Android 기기 또는 호환 에뮬레이터가 필요합니다. Mac용 **MuMuPlayer Pro는 Apple Silicon 지원**, Intel Mac은 다른 Android 환경이 필요합니다.

**Terminal**에서 실행:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

`sh run-macos.sh`는 **0–5단계**가 포함된 Textual 대시보드를 엽니다. `--check`는 환경을 확인하며 설정을 바꿀 수 있고, `--list`는 혜택 조회만 수행합니다. `--step 2`는 화면에서 단계를 선택할 뿐 **자동 결제하지 않습니다**. 2–5단계는 실제 요금이 발생할 수 있어 단계별 승인이 필요합니다. **실제 Mac/MuMu에서 결제는 아직 검증되지 않았습니다.** [Mac 상세 안내](docs/MACOS-PREVIEW.md)를 참고하세요.

## Android 연결 확인 및 혜택 조회 (Windows + macOS)

대시보드에는 원본 프로젝트의 Android 설정 안내와 혜택 목록을 바탕으로 만든 두 가지 확인 기능이 있습니다.

- **Diagnose Android connection — Android 연결 진단:** ADB 설치 여부와 연결이 승인된 Android 기기를 확인하고, 기기의 ABI 아키텍처, Google One 설치 상태, 컴퓨터의 Frida 버전을 표시합니다. Windows에서는 PowerShell·MuMu·Platform-Tools, macOS에서는 Terminal·Homebrew를 이용한 안내를 제공합니다. **소프트웨어 설치, 에뮬레이터 연결·재시작, Frida 실행, 결제는 수행하지 않습니다.** 단, `adb devices` 명령으로 로컬 ADB 서버가 시작될 수 있습니다.
- **Check Device & Offers (Step 1) — 기기 및 혜택 확인:** 기존 Android/Frida 조회 기능으로 혜택을 가져와 Live Status 아래의 **Offer Explorer**에 표시합니다. 상품 ID, 혜택 ID, 첫 결제 기간, 첫 기간의 요금이 0인지 여부만 보여 줍니다. 혜택·구매 토큰이나 원본 계정 식별 정보, 카드 정보는 표시하지 않습니다. 이 단계는 Android 환경을 준비하면서 **일부 설정을 변경할 수 있으므로**, 연결 진단과 달리 완전히 읽기 전용은 아닙니다.

**첫 기간의 요금이 0이라고 해서 무료 이용이나 구독 기간 연장이 보장되지는 않습니다.** Step 1에서는 목록 조회 용도로만 `g1.2tb.ai.subs_variant`, `g1.play.2tb.ai`, `g1.2tb.ai`를 확인합니다. Steps 2–5는 각 단계에 맞는 조회를 그대로 사용합니다. Android 보고서에는 이후 결제 기간의 요금이 모두 포함되지 않으므로, Offer Explorer에서는 미래 요금을 **미확인**으로 표시합니다. 실제 청구 금액과 갱신 조건은 Google Play에서 직접 확인하세요.

## 3. 대시보드 사용법

단계가 실행되는 동안에는 **Check Device & Offers**, **Run**, 실행 모드와 단계 선택을 잠가 다른 작업이 동시에 시작되지 않도록 합니다. Step 0은 컴퓨터의 설정을 변경할 수 있습니다. Step 1은 결제를 시작하지 않지만 사전 준비 과정에서 ADB/Frida 설정이 바뀔 수 있습니다. 다음 단계로 진행하기 전에 반드시 Google Play에서 결과를 확인하세요. **Stop이나 Exit를 눌러도 이미 제출한 결제는 취소되지 않습니다.**


**Check Device & Offers**는 **Step 1 — Available offers**를 실행하여 프로모션을 조회합니다. **구독 결제를 시작하지 않습니다**. **Live Status**와 **Show technical details**에서 진행 상황을 확인하세요. 30초 동안 로그가 없다는 경고는 반드시 프로그램이 멈췄다는 뜻이 아닙니다.

Windows에서는 혜택을 확인하기 전에 사용할 계정으로 Google Play에 로그인하세요. 계정이 확인되고 첫 기간 요금이 0인 12개월 혜택이 표시되면 **Review 12-month checkout**을 눌러 내용을 검토한 뒤 Step 2만 별도로 승인하세요. 결제 정보가 필요하면 Google Play에서 직접 입력하세요. 절차가 끝나면 Google Play에서 실제 구독 상태와 갱신 날짜를 확인하세요.

**Advanced: Run by step** 모드:

| 모드 | 기능 |
| --- | --- |
| **One step only** | 선택한 Step 0–5 하나만 실행 |
| **From selected step** | 선택한 Step(2–5)부터 안내에 따라 여러 단계를 진행 |
| **All: Steps 2–5** | Step 2부터 순서대로 진행하며, Step 5는 선택할 수 있음 |

| Step | 기능 | 위험 |
| --- | --- | --- |
| **0 — Environment** | Android / ADB / Frida 점검과 준비 | 결제 없음. 환경 설정은 변경될 수 있음 |
| **1 — Available offers** | Google Play 프로모션 조회 | 결제 없음. 사전 점검 중 환경 변경 가능 |
| **2 — Pro 12 months** | 기존 12개월 프로모션 단계 | **실제 결제 가능** |
| **3 — Pro +6 months** | 구독 변경 시도 | **실제 결제 가능** |
| **4 — Pro +6 months (second)** | 두 번째 구독 변경 시도 | **실제 결제 가능** |
| **5 — Optional +6 months** | 선택적 변경 시도 | **실제 결제 가능** |

**보고된 24개월 사례(Google Play에서 확인 필요):**

| Step | 정상 적용 시 누적 기간 | 별도 카드 거래 |
| --- | --- | --- |
| **2 — Pro 12 months** | 최초 **12개월** | **1달러**(첫 번째) |
| **3 — Pro +6 months** | 총 **18개월** | **1달러**(두 번째) |
| **4 — Pro +6 months (second)** | 총 **24개월** | **1달러**(세 번째) |
| **Step 4까지 합계** | 확인된 경우 **24개월** | **3 × US$1 = US$3**, 3달러 단일 결제가 아님 |

**선택 사항인 Step 5는 이 세 거래에 포함되지 않습니다.** 표시된 기간이나 카드 승인만으로 구독 연장 성공을 확인할 수 없으므로, 각 단계 후 Google Play에서 구독 상태와 갱신일을 확인하세요.

표시된 개월 수는 **이전 워크플로의 단계 이름**이며 실제 구독 기간 연장을 보장하지 않습니다. 이미 활성 구독이 있다면 **Step 2를 다시 실행하지 마세요**.

TUI에서 **각 결제 단계는 별도 승인이 필요합니다**. 도구가 결제 제출을 시도했다고 표시해도 [Google Play 구독 관리](https://play.google.com/store/account/subscriptions)에서 실제 구독, 요금과 갱신일을 확인하세요. 직접 변경 사항을 확인한 경우에만 **Verified in Google Play → Next**를 선택하세요. 도구는 구독 성공을 독립적으로 증명할 수 없습니다.

**중지/종료:** Step 0–1에서는 Stop이 로컬 검사를 종료하도록 요청합니다. Step 2–5의 **Stop after this step**은 이후 단계를 막을 뿐 **진행 중인 결제를 강제 종료하지 않습니다**. 결제 중 **Q / Exit**는 현재 단계 종료 후 종료합니다. **D**는 기술 로그, **R**은 선택한 모드 실행입니다.

## 4. PowerShell 명령어 (고급)

**Windows 전용 명령어입니다.** Mac에서는 PowerShell 대신 `run-macos.sh`와 [macOS 안내](docs/MACOS-PREVIEW.md)를 사용하세요. 실행할 때 매개변수를 지정하면 Textual 화면 대신 CLI 모드가 열립니다.

**조회/진단(구독 결제 없음):**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**다음 명령은 실제 결제를 시작할 수 있습니다:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

TUI와 달리 단독 `-Step 2..5` 명령은 **PowerShell에서 별도의 승인 질문을 표시하지 않습니다**. 실제 결제를 의도하고 조건을 확인한 경우에만 실행하세요.

단계마다 확인을 받는 CLI 실행 방법:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

CLI 선택: **1 = Continue(계속), 2 = End run(종료), 0 = Stop(중지)**. 각 단계마다 Google Play에서 직접 결과를 검증하세요. `-StartStep 3`은 이전 단계가 성공했다는 증거가 아닙니다.

장치/계정 선택:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

ADB에서 실제로 표시되는 시리얼만 사용하세요. `-Force`는 계정 일치 확인을 건너뛰므로 **권장하지 않습니다**. 프로모션 자격이나 Google 결제 제한을 우회하지는 못합니다.

## 5. 결과와 문제 해결

- **MuMu/ADB가 감지되지 않음:** 에뮬레이터 실행, root/ADB 권한 및 장치 상태를 확인하세요.
- **Frida 오류:** 로그와 **16.5.9** / Android 호환성을 확인하세요.
- **프로모션이 없음:** Google One / Play Store를 열고 **Step 1**을 다시 실행하세요.
- **계정 불일치:** Play Store 프로필을 확인하고 검증을 우회하지 마세요.
- **결제 제출 시도:** 구독 성공과 다릅니다. 재시도 전에 Google Play에서 상태를 확인하세요.
- **결제 보안 오류(예: OR-REH-04):** 결제 단계를 중단하고 공식 보안 절차를 확인하세요.

로그는 `logs/`, 보고서는 `ultra0-report/`에 저장됩니다. **계정 정보, 토큰, 결제 정보를 포함한 원본 파일을 공유하지 마세요.** CI는 정적/모의 테스트만 수행하며 실제 결제 성공을 검증하지 않습니다. 

## 커뮤니티 지원 및 관련 프로젝트

ePlus AI Toolkit 설치나 사용에 문제가 있다면 [ePlus Telegram 지원·토론 게시물](https://t.me/eplus_news/29)에서 커뮤니티와 연락하고 해결 방법을 공유할 수 있습니다. 재현 가능한 버그는 [GitHub Issue](https://github.com/hoangsvit/google-ai/issues)로도 제보해 주세요. **비밀번호, OTP/2FA 코드, 오퍼/구매 토큰, 개인정보가 포함된 원본 로그, 카드 정보를 공개하지 마세요.** Google 공식 지원 채널은 아닙니다.

**Google AI Pro 프로모션에 참여할 수 없나요?** 별도의 ePlus.DEV 커뮤니티 프로젝트인 [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub)에서 [Muse 초대 코드를 찾거나 공유](https://muse.eplus.dev/)할 수 있습니다. **Muse는 별도 서비스**이며 초대 코드로 **Google AI Pro 구독을 활성화하거나 대신할 수 없습니다**. 코드 이용 가능 여부 및 지역·계정 자격은 보장되지 않습니다.

## 저장소 구성

기존 설치 안내와의 호환성을 유지하기 위해 실행 스크립트와 주요 Python 모듈은 저장소 최상위 폴더에 있습니다. Windows에서는 `run-all.ps1`, Mac에서는 `run-macos.sh`를 사용하세요.

| 파일 또는 폴더 | 역할 |
| --- | --- |
| `run-all.ps1` | Windows에서 Textual 대시보드 또는 CLI 실행 |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | Mac에서 Steps 0–5 실행 및 제어. 실기기 결제는 미검증 |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | 현재 사용하는 Python 모듈과 보조 도구 |
| [`tools/windows/`](tools/windows/README.md) | 필요한 경우 사용하는 Windows 수동 설정 |
| [`legacy/windows/`](legacy/windows/README.md) | 이전 .bat 파일. 일부는 `--force`로 계정 확인을 건너뛰므로 **실제 요금이 발생할 수 있음** |
| `scripts/`, `assets/` | 보조 스크립트 및 Android/Frida 리소스 |
| `tests/`, `.github/workflows/`, `docs/` | 자동 테스트, GitHub Actions, 문서 |

## 문서 및 개발 참여

[영어 README](README.md) · [설치 Wiki](https://github.com/hoangsvit/google-ai/wiki/Install) · [상세 가이드](docs/DETAILED-GUIDE.md) · [원본 단계](docs/ORIGINAL-STEPS.md) · [면책 고지](DISCLAIMER.md) · [보안](SECURITY.md) · [기여](CONTRIBUTING.md) · [저작권 고지](THIRD_PARTY_NOTICES.md)

[프로젝트 구조](docs/PROJECT.md), [대시보드/CLI 사용법](docs/USAGE.md), [결제 안전](docs/SAFETY.md), [기존 작성자 참고](docs/AUTHOR-NOTES.md), [AI 에이전트 지침](AGENTS.md)도 확인하세요. GitHub Actions는 Python/PowerShell/Textual 및 모의 Frida/Billing을 검사하지만 **실제 Google Play 결제는 실행하지 않습니다**. CI 검사를 통과하더라도 실제 기기에서 정상 동작하거나 구독 혜택을 받을 수 있다는 뜻은 아닙니다.

## 제작 및 기여

**원저자:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **관리자:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). 원본 MIT 저작권 고지는 `THIRD_PARTY_NOTICES.md`에 보존되어 있습니다.

[문서 모음](docs/README.md) · [이전 한국어 참고 안내](docs/i18n/README.ko.md) · [결제 안전](docs/SAFETY.md)
