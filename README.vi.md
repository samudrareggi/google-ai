# ePlus AI Toolkit — Tiếng Việt

<!-- Source README.md git-blob: 2b8488a21c25e7b771f7a4014f8b945e182fe285 -->

[English](README.md) · **Tiếng Việt** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md)


> **Tài liệu gốc:** [README tiếng Anh](README.md). Nội dung bên dưới được diễn đạt bằng tiếng Việt để dễ theo dõi, đồng thời giữ nguyên các lệnh, điều kiện và lưu ý an toàn. Khi thông tin khác với chương trình thực tế, hãy ưu tiên kiểm tra mã nguồn và tài liệu gốc.

**ePlus AI Toolkit** giúp bạn kiểm tra các ưu đãi Google AI Pro được hiển thị qua Google One và Google Play trên thiết bị Android. Công cụ chạy trên **Windows và macOS**: Windows sử dụng PowerShell, còn macOS sử dụng Terminal (zsh/bash). Cả giao diện Textual lẫn chế độ dòng lệnh đều dùng chung bộ xử lý Python, ADB và Frida.

![Giao diện ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Đây không phải công cụ chính thức của Google và có thể phát sinh chi phí.** Ở các bước **2–5**, công cụ có thể mở trang thanh toán Google Play và tự nhấn **Subscribe**. Ưu đãi xuất hiện trong danh sách, mức giá đầu tiên bằng 0 hoặc thông báo đã gửi yêu cầu thanh toán **không có nghĩa là** bạn đủ điều kiện, được dùng miễn phí hay đã gia hạn thành công. Trước khi thực hiện, hãy kiểm tra đúng tài khoản, khoản tiền phải trả ngay, mức phí những kỳ sau và ngày gia hạn trong **Google Play**. Dừng công cụ không hủy được giao dịch đã gửi.

> [!NOTE]
> **Cần có tối thiểu 3 USD khả dụng cho 3 giao dịch riêng biệt, mỗi giao dịch 1 USD — không phải một lần trừ 3 USD.** Theo quy trình **24 tháng** đã được người dùng báo cáo, Step 2 (dùng thử 12 tháng), Step 3 (gia hạn thêm 6 tháng) và Step 4 (gia hạn thêm 6 tháng) tương ứng với **ba lần xác minh thẻ/thanh toán, mỗi lần 1 USD**: **3 × US$1 = US$3**. Tùy trạng thái ngân hàng và Google Play, khoản 1 USD có thể chỉ là **tạm giữ để xác thực**, không phải phí đã trừ chính thức; số tiền thực tế cũng có thể khác. **3 USD là mức số dư tối thiểu cho ví dụ này, không phải mức phí cố định hoặc bảo đảm mọi tài khoản đều đủ điều kiện.** Khoản tạm giữ có thể làm giảm số dư khả dụng và thường được giải tỏa trong **1–14 ngày làm việc**, tùy ngân hàng. Sau từng bước, hãy tự kiểm tra trạng thái giao dịch và ngày gia hạn tại Google Play. Step 5 là tùy chọn, **không tính trong ba giao dịch trên**. [Giải thích chính thức của Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Tuyên bố miễn trừ trách nhiệm

ePlus AI Toolkit là dự án độc lập, **không thuộc và không được Google, Google One, Google Play, NetEase hay MuMuPlayer tài trợ hoặc xác nhận**. Phần mềm được cung cấp theo hiện trạng, không bảo đảm bạn sẽ nhận được ưu đãi, đăng ký thành công hoặc chạy được trên mọi thiết bị. Việc chuẩn bị môi trường có thể thay đổi cấu hình Android, Frida hoặc mạng. Chỉ dùng với tài khoản và thiết bị bạn sở hữu hoặc được phép sử dụng, đồng thời tuân thủ điều khoản liên quan. Đọc thêm [tuyên bố miễn trừ trách nhiệm](DISCLAIMER.md) và [hướng dẫn an toàn](SECURITY.md).

## 1. Chuẩn bị

**Chọn hướng dẫn phù hợp với hệ điều hành đang dùng.** Trên Mac, bạn không cần cài hay chạy PowerShell.

| Thành phần | Windows | macOS |
| --- | --- | --- |
| Terminal | **PowerShell 5.1 trở lên** | **Terminal** với zsh hoặc bash |
| Python | **3.10 trở lên**, dùng lệnh `python` | **3.10 trở lên**, dùng `python3`; công cụ tự tạo môi trường `.venv` |
| Git | Git for Windows | Git từ Xcode Command Line Tools hoặc Homebrew |
| Android | Thiết bị hoặc máy ảo đã bật root và ADB; hướng dẫn của dự án hỗ trợ **MuMuPlayer cho Windows** | Thiết bị Android có root hoặc máy ảo tương thích; **MuMuPlayer Pro cho Mac** chỉ phù hợp với Apple Silicon, không hỗ trợ Intel Mac |
| Ứng dụng Android | Google Play Store và Google One, đã đăng nhập đúng tài khoản | Tương tự trên thiết bị Android bạn sử dụng |
| ADB | Công cụ có thể tìm hoặc tải Android SDK Platform-Tools | Cần cài riêng, chẳng hạn `brew install android-platform-tools`; kiểm tra bằng `adb devices` |
| Frida | **16.5.9**; trình thiết lập Windows có thể chuẩn bị khi cần | **16.5.9** trong `.venv`; vẫn phải kiểm tra khả năng tương thích với Android |
| Lệnh khởi chạy | `.\run-all.ps1` | `sh run-macos.sh` hoặc `ePlus-AI-Toolkit.command` |

Dù dùng Windows hay macOS, bạn vẫn cần một môi trường Android đã thiết lập đúng và có quyền truy cập. Mã nguồn hỗ trợ các bước 0–5 trên macOS, nhưng **chưa xác minh được quy trình thanh toán trên Mac/MuMu thực tế**. Xem hướng dẫn riêng cho [Windows](docs/INSTALLATION.md) và [macOS](docs/MACOS-PREVIEW.md).

### Yêu cầu trên Windows

- Cài Windows, PowerShell **5.1 trở lên** và Python **3.10 trở lên**.
- Tự cài MuMuPlayer, khởi động máy ảo Android và bật root cùng ADB.
- Cài Google Play Store và Google One trong Android, rồi đăng nhập tài khoản cần kiểm tra.
- Chuẩn bị kết nối ADB và Frida **16.5.9** tương thích. Công cụ có thể hỗ trợ tìm và cài các thành phần này, **nhưng không tự cài MuMuPlayer**.

### Bước 1 — Cài MuMuPlayer

Tải MuMuPlayer từ [trang chính thức của NetEase](https://www.mumuplayer.com/download/) và chọn phiên bản Windows. Không nên tải từ các trang chia sẻ không rõ nguồn gốc.

Sau khi cài đặt, hãy bật quyền root và ADB cho máy ảo. Kiểm tra Google Play Store và Google One đã có sẵn, sau đó đăng nhập đúng tài khoản bạn muốn kiểm tra ưu đãi.

Bạn có thể xem thêm [hướng dẫn cài đặt kèm hình ảnh trên GitHub Wiki](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Cài và khởi động

**Bước 2 — Tải và chạy công cụ trên Windows.** Mở PowerShell trong thư mục dự định lưu mã nguồn.

Mở PowerShell:

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Nếu bạn đã tải mã nguồn về máy từ trước:

```powershell
git pull --ff-only
.\run-all.ps1
```

Chạy lệnh **không kèm tham số** sẽ mở giao diện **Textual** thay vì tự bắt đầu thanh toán. Khi bắt đầu kiểm tra, chương trình có thể tự chuẩn bị Textual, ADB và Frida. Thường **không cần** chạy `setup_env.py` trước. Bước chuẩn bị có thể thay đổi công cụ, proxy/mạng và cấu hình máy ảo.

Nếu ADB có trong PATH, kiểm tra kết nối:

```powershell
adb devices
```

Thiết bị phải ở trạng thái `device`, không phải `offline` hoặc `unauthorized`. Nếu không tìm thấy ADB, xem [hướng dẫn xử lý lỗi](docs/DETAILED-GUIDE.md).

### Phương án thay thế: sử dụng bản phát hành khi gặp lỗi

Nếu phiên bản mới nhất chạy từ source gặp lỗi, bạn có thể thử **bản phát hành đã công bố** tại [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Chọn một phiên bản, đọc ghi chú phát hành và tải gói Windows **nếu có file đính kèm**. Nếu chỉ có **Source code (zip)** do GitHub cung cấp, hãy tải ZIP, giải nén, mở PowerShell ngay trong thư mục đã giải nén rồi chạy:

```powershell
.\run-all.ps1
```

**Source code (zip) chỉ là mã nguồn, không phải tệp `.exe` hoặc bộ cài đã dựng sẵn.** Nên giữ bản phát hành trong **thư mục riêng**, không chép đè lên bản source đang dùng. Bản phát hành cũ có thể chưa chứa những bản sửa lỗi mới và vẫn cần Windows, Python, MuMuPlayer, ADB/Frida cùng các lưu ý về thanh toán. Nếu lỗi vẫn xảy ra, xem [hướng dẫn khắc phục](docs/DETAILED-GUIDE.md) hoặc [tạo Issue](https://github.com/hoangsvit/google-ai/issues).

## macOS — Cài đặt và khởi chạy

Trên **macOS**, cài **Git**, **Python 3.10+** và **Android SDK Platform-Tools (ADB)** (Homebrew: `brew install android-platform-tools`). Kết nối thiết bị Android có root và Google Play Store/Google One, hoặc máy ảo Android tương thích. **MuMuPlayer Pro trên Mac hỗ trợ Apple Silicon**; Mac Intel cần thiết bị hoặc máy ảo khác.

Mở **Terminal** và chạy:

```sh
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
adb devices
sh run-macos.sh
```

Lệnh `sh run-macos.sh` mở cùng giao diện Textual với **Steps 0–5**. `--check` kiểm tra môi trường (có thể thay đổi cấu hình), `--list` chỉ liệt kê ưu đãi, và `--step 2` chỉ mở TUI với Step 2 được chọn — **không tự thanh toán**. Các Steps 2–5 có thể phát sinh phí thật và yêu cầu xác nhận riêng. **Chưa kiểm thử giao dịch trên Mac/MuMu thực tế.** Xem [hướng dẫn Mac chi tiết](docs/MACOS-PREVIEW.md).

## Kiểm tra kết nối Android và xem ưu đãi (Windows + macOS)

Trên bảng điều khiển có hai chức năng kiểm tra được phát triển từ hướng dẫn cấu hình Android và danh sách ưu đãi của dự án gốc:

- **Diagnose Android connection — Kiểm tra kết nối Android:** Xác định ADB đã có trên máy hay chưa, liệt kê thiết bị Android đã cấp quyền kết nối, đọc kiến trúc ABI, kiểm tra ứng dụng Google One và phiên bản Frida trên máy tính. Tùy hệ điều hành, công cụ sẽ hướng dẫn thiết lập bằng PowerShell/MuMu trên Windows hoặc Terminal/Homebrew trên macOS. Chức năng này **không tự cài phần mềm, kết nối hay khởi động lại máy ảo, chạy Frida hoặc thực hiện thanh toán**. Tuy nhiên, lệnh `adb devices` có thể khởi động ADB server trên máy.
- **Check Device & Offers (Step 1) — Kiểm tra thiết bị và ưu đãi:** Dùng quy trình Android/Frida hiện có để lấy danh sách ưu đãi rồi hiển thị trong **Offer Explorer** bên dưới Live Status. Màn hình chỉ cho biết mã sản phẩm, mã ưu đãi, kỳ thanh toán đầu tiên và việc giá kỳ đầu có bằng 0 hay không. Công cụ **không hiển thị** offer token, purchase token, thông tin tài khoản đầy đủ hoặc dữ liệu thẻ. Khác với tính năng chẩn đoán kết nối, bước này có thể thiết lập lại một số thành phần Android nên **không hoàn toàn chỉ đọc**.

**Giá kỳ đầu bằng 0 không đồng nghĩa với việc được dùng miễn phí hoặc gia hạn thành công.** Step 1 chỉ truy vấn danh sách của ba mã sản phẩm `g1.2tb.ai.subs_variant`, `g1.play.2tb.ai` và `g1.2tb.ai`; các bước 2–5 vẫn truy vấn đúng ưu đãi dành cho từng bước. Vì báo cáo Android chưa có đủ thông tin về những kỳ thanh toán tiếp theo, Offer Explorer đánh dấu giá tương lai là **chưa được xác minh**. Hãy đối chiếu các điều khoản và số tiền thực tế ngay trong Google Play.

## 3. Sử dụng giao diện

Nhấn **Check Device & Offers** để chạy **Step 1 — Available offers** và kiểm tra ưu đãi mà **không bắt đầu thanh toán**. Bạn có thể theo dõi tiến trình tại **Live Status**, chọn **Show technical details** để xem thông tin kỹ thuật và kiểm tra đúng tài khoản trong Google Play. Nếu 30 giây không có thông báo mới, công cụ sẽ cảnh báo; điều đó **chưa có nghĩa là chương trình đã bị treo**.

Trên Windows, hãy đăng nhập đúng tài khoản trong Google Play trước khi kiểm tra. Khi công cụ xác minh được tài khoản và tìm thấy ưu đãi 12 tháng có giá kỳ đầu bằng 0, chọn **Review 12-month checkout** để xem và xác nhận riêng Step 2. Nếu được yêu cầu, hãy nhập thông tin thanh toán trực tiếp trong Google Play. Sau khi hoàn tất, kiểm tra gói đăng ký thực tế và ngày gia hạn tại đó.

Trên Windows, **Prepare MuMu** có thể tạo và mở một máy ảo Android 15 mới ở chế độ dọc. Nhập địa chỉ email Google Play cần nhận diện, rồi đăng nhập và xác minh trong MuMu. Khi công cụ nhận diện được tài khoản, chọn **Check Device & Offers** để chạy Step 1 trên máy ảo mới.

Step 1 không mua hàng, nhưng quá trình chuẩn bị vẫn có thể tải hoặc sửa ADB/Frida và thay đổi cấu hình máy ảo hoặc mạng. **Step 0 — Environment cũng có thể thay đổi môi trường trên máy**, nên không được xem là thao tác hoàn toàn chỉ đọc. Thanh bên hiển thị sáu bước; thông tin trong Android Device và Google Account được lấy từ kết quả thực tế, đồng thời che bớt dữ liệu nhận dạng tài khoản. Những terminal có hỗ trợ liên kết sẽ cho phép mở trang của tác giả gốc và người duy trì.

Mục **Advanced: Run by step** gồm:

| Chế độ | Chức năng |
| --- | --- |
| **One step only** | Chỉ chạy một bước được chọn từ 0 đến 5 |
| **From selected step** | Bắt đầu chuỗi có hướng dẫn từ Step 2–5 |
| **All: Steps 2–5** | Bắt đầu chuỗi từ Step 2; Step 5 là tùy chọn |

| Bước | Vai trò | Rủi ro |
| --- | --- | --- |
| **0 — Environment** | Kiểm tra/chuẩn bị Android, ADB và Frida | Không checkout, nhưng có thể đổi cấu hình |
| **1 — Available offers** | Truy vấn ưu đãi | Không checkout, nhưng preflight có thể đổi môi trường |
| **2 — Pro 12 months** | Thử ưu đãi gốc 12 tháng | **Có thể thanh toán thật** |
| **3 — Pro +6 months** | Thử cập nhật gói | **Có thể thanh toán thật** |
| **4 — Pro +6 months (second)** | Thử cập nhật lần tiếp | **Có thể thanh toán thật** |
| **5 — Optional +6 months** | Thử ưu đãi tùy chọn | **Có thể thanh toán thật** |

**Ví dụ đã được báo cáo: 24 tháng qua ba giao dịch riêng (cần xác minh trên Google Play):**

| Bước | Thời hạn nếu áp dụng thành công | Giao dịch riêng biệt |
| --- | --- | --- |
| **2 — Pro 12 months** | **12 tháng** đầu tiên | **1 USD** (lần 1) |
| **3 — Pro +6 months** | Tổng cộng **18 tháng** | **1 USD** (lần 2) |
| **4 — Pro +6 months (second)** | Tổng cộng **24 tháng** | **1 USD** (lần 3) |
| **Tổng đến Step 4** | **24 tháng nếu đã xác minh** | **3 × US$1 = US$3**; không phải một lần trừ 3 USD |

**Step 5 là tùy chọn, không thuộc ba giao dịch trên.** Thời hạn hiển thị và việc xác minh thẻ không tự chứng minh gia hạn thành công; cần kiểm tra gói đăng ký và ngày gia hạn trong Google Play sau từng bước.

Tên 12/6 tháng là **tên lịch sử của các bước**, không phải cam kết được cộng thêm thời hạn. Nếu đã có gói đang hoạt động, **không chạy lại Step 2**.

Trước **mỗi bước thanh toán trên giao diện**, bạn phải xác nhận riêng. Nếu công cụ báo đã thử gửi yêu cầu thanh toán, hãy tự kiểm tra gói đang sử dụng, khoản tiền phải trả và ngày gia hạn tại [Google Play Subscriptions](https://play.google.com/store/account/subscriptions). Chỉ chọn **Verified in Google Play → Next** sau khi bạn đã tự xác minh trong Google Play. **Công cụ không thể tự xác nhận giao dịch đã thành công.**

Khi một bước đang chạy, các nút **Check Device & Offers**, **Run** và các tùy chọn chế độ hoặc bước sẽ tạm khóa để tránh chạy nhiều thao tác cùng lúc. Bạn vẫn có thể xem trợ giúp và nhật ký kỹ thuật. Nút **Next** chỉ xuất hiện khi kết quả thanh toán có thể được kiểm tra trước khi tiếp tục; nếu xảy ra lỗi hoặc chưa rõ kết quả, công cụ không cho chuyển sang bước kế tiếp.

**Dừng hoặc thoát:** Với Steps 0–1, bạn có thể yêu cầu dừng tiến trình trên máy. Với Steps 2–5, **Stop after this step** chỉ ngăn công cụ chạy tiếp bước sau, **không buộc dừng giao dịch đang xử lý**. Nếu nhấn **Q / Exit** trong lúc thanh toán, công cụ sẽ đợi bước hiện tại kết thúc rồi mới thoát. Phím **D** bật/tắt nhật ký kỹ thuật, còn **R** chạy theo chế độ đã chọn.

## 4. PowerShell CLI (nâng cao)

**Chỉ dành cho Windows.** Các lệnh PowerShell không áp dụng cho macOS; Mac dùng `run-macos.sh` và [hướng dẫn riêng](docs/MACOS-PREVIEW.md). Khi truyền tham số cụ thể, lệnh sẽ chạy ở chế độ CLI thay vì mở giao diện Textual.

**Kiểm tra, không mua hàng:**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

Log kỹ thuật nằm trong `logs/`, còn báo cáo phiên chạy mới nhất nằm ở `ultra0-report/`. **Không công khai log hoặc báo cáo thô** chứa email, token và thông tin thanh toán. `setup_env.py` và [`tools/windows/setup-environment.bat`](tools/windows/setup-environment.bat) chỉ là công cụ khắc phục lỗi hoặc sửa môi trường, không phải bước cài đặt bắt buộc trước dashboard.

**Các lệnh sau có thể kích hoạt thanh toán thật:**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

Khác với giao diện Textual, khi chạy riêng từng bước bằng `-Step 2..5`, PowerShell **không yêu cầu xác nhận thêm lần nữa**. Chỉ dùng các lệnh này nếu bạn chủ động muốn thực hiện giao dịch có thể phát sinh phí và đã đọc kỹ điều khoản.

Chạy nhiều bước theo hướng dẫn, có xác nhận ở từng giai đoạn:

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

Khi chương trình yêu cầu lựa chọn, nhập **1 = Continue (tiếp tục), 2 = End run (kết thúc), 0 = Stop (dừng)**. Hãy tự xác minh kết quả trên Google Play trước khi chuyển sang bước tiếp theo. `-StartStep 3` không xác minh các bước trước đã thành công.

Chọn thiết bị hoặc tài khoản dự kiến:

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Chỉ nhập mã thiết bị (serial) thực sự xuất hiện trong danh sách ADB. Tránh `-Force` vì nó bỏ qua bước kiểm tra khớp tài khoản, **không** vượt qua điều kiện ưu đãi hay giới hạn thanh toán của Google.

## 5. Kết quả và xử lý lỗi

- **Không tìm thấy MuMu/ADB:** kiểm tra máy ảo, root, ADB và trạng thái kết nối.
- **Lỗi Frida:** mở log và kiểm tra phiên bản **16.5.9**/khả năng tương thích Android.
- **Không có ưu đãi:** mở Google One/Play Store, rồi chạy lại **Step 1**.
- **Sai tài khoản:** xác nhận đúng hồ sơ Google Play, không bỏ qua xác minh.
- **Checkout đã gửi nhưng chưa xác nhận:** không coi là gia hạn; kiểm tra trực tiếp Google Play trước khi thử lại.
- **`already_subscribed` hoặc `ineligible`:** dừng lại, không thử các bước thanh toán khác khi chưa xác minh.
- **Lỗi hiển thị ký tự trên Windows:** cập nhật mã nguồn mới nhất; trình khởi chạy đã được cấu hình dùng UTF-8 khi chuyển dữ liệu đầu ra.
- **Đã gửi yêu cầu checkout:** đó chỉ là thao tác cố gắng gửi, **không phải xác nhận đã kích hoạt hoặc gia hạn**.
- **Lỗi bảo mật thanh toán (ví dụ OR-REH-04):** dừng các bước thanh toán, kiểm tra thông báo bảo mật chính thức.

Nhật ký chạy được lưu trong `logs/`, còn báo cáo nằm trong `ultra0-report/`. **Không chia sẻ nhật ký hoặc báo cáo khi chưa che email, token và thông tin thanh toán**. CI chỉ thực hiện kiểm thử tĩnh và mô phỏng; không xác minh giao dịch mua hàng thật. **Quy trình thanh toán trên Mac/MuMu thực tế vẫn chưa được kiểm chứng**.

## Hỗ trợ cộng đồng và dự án liên quan

Nếu gặp vấn đề khi cài đặt hoặc sử dụng ePlus AI Toolkit, hãy truy cập [bài đăng hỗ trợ trên Telegram ePlus](https://t.me/eplus_news/29) để liên lạc, trao đổi kinh nghiệm và nhờ cộng đồng hỗ trợ. Với lỗi kỹ thuật có thể tái hiện, bạn cũng có thể [tạo GitHub Issue](https://github.com/hoangsvit/google-ai/issues). **Không chia sẻ mật khẩu, mã OTP/2FA, offer/purchase token, log chưa che thông tin cá nhân hoặc dữ liệu thẻ thanh toán.** Đây là hỗ trợ cộng đồng, không phải kênh hỗ trợ chính thức của Google.

**Không tham gia được chương trình Google AI Pro?** Bạn có thể tham khảo [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), một dự án khác của ePlus.DEV để [tìm kiếm hoặc chia sẻ mã mời Muse](https://muse.eplus.dev/). **Muse là dịch vụ riêng**, mã mời Muse **không kích hoạt và không thay thế** quyền đăng ký Google AI Pro. Mã mời có thể hết lượt hoặc bị giới hạn theo khu vực/tài khoản.

## Cấu trúc mã nguồn

Các tệp khởi chạy và mô-đun Python chính vẫn nằm tại thư mục gốc để bảo đảm tương thích với các hướng dẫn hiện có. Trên Windows dùng `run-all.ps1`, còn trên macOS dùng `run-macos.sh`.

| Đường dẫn | Vai trò |
| --- | --- |
| `run-all.ps1` | Khởi chạy giao diện Textual và chế độ CLI trên Windows |
| `run-macos.sh`, `ePlus-AI-Toolkit.command`, `macos_runner.py` | Khởi chạy và điều phối các bước 0–5 trên Mac; chưa xác minh thanh toán trên thiết bị thật |
| `tui.py`, `tui_core.py`, `ultra0.py`, `setup_env.py`, `device_selector.py`, `query_sku.py` | Các mô-đun Python đang được sử dụng |
| [`tools/windows/`](tools/windows/README.md) | Công cụ thiết lập Windows thủ công, chỉ dùng khi cần |
| [`legacy/windows/`](legacy/windows/README.md) | Các tệp .bat cũ; một số sử dụng `--force` để bỏ qua bước đối chiếu tài khoản, có thể **phát sinh phí thật**. Nên dùng launcher được duy trì |
| `scripts/`, `assets/` | Tiện ích hỗ trợ và tài nguyên Android/Frida |
| `tests/`, `.github/workflows/`, `docs/` | Bộ kiểm thử, GitHub Actions và tài liệu |

## Tài liệu và đóng góp

[README tiếng Anh](README.md) · [Wiki Install](https://github.com/hoangsvit/google-ai/wiki/Install) · [Hướng dẫn kỹ thuật](docs/DETAILED-GUIDE.md) · [Các bước gốc](docs/ORIGINAL-STEPS.md) · [Disclaimer](DISCLAIMER.md) · [Bảo mật](SECURITY.md) · [Đóng góp](CONTRIBUTING.md) · [Thông báo bản quyền](THIRD_PARTY_NOTICES.md)

Bạn cũng có thể tham khảo [cấu trúc dự án](docs/PROJECT.md), [cách dùng dashboard và CLI](docs/USAGE.md), [an toàn thanh toán](docs/SAFETY.md), [lưu ý tác giả](docs/AUTHOR-NOTES.md) và [hướng dẫn AI agent](AGENTS.md). GitHub Actions kiểm tra Python, PowerShell, Textual và các tình huống mô phỏng Frida/Billing; **không thực hiện giao dịch Google Play thật**. CI thành công không chứng minh thiết bị tương thích hoặc tài khoản đủ điều kiện.

## Ghi công

**Tác giả gốc:** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Người duy trì:** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). Giữ nguyên thông báo MIT của tác giả gốc trong [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md); giấy phép này không mặc nhiên áp dụng cho các đóng góp mới không liên quan. [Danh sách người đóng góp](https://github.com/hoangsvit/google-ai/graphs/contributors).

[Trung tâm tài liệu](docs/README.md) · [Tài liệu tham khảo cũ (tiếng Việt)](docs/i18n/README.vi.md) · [An toàn thanh toán](docs/SAFETY.md)
