# Quy Trình Vận Hành Chuẩn (SOP)
# Smart Factory Dashboard — Hướng Dẫn Vận Hành Hàng Ngày

| Trường | Chi tiết |
|---|---|
| **Mã tài liệu** | SOP-SFD-001-VI |
| **Phiên bản** | 1.0 |
| **Ngôn ngữ** | Tiếng Việt |
| **Ngày tạo** | 2026-04-02 |
| **Bộ phận** | Sản xuất / Nhà máy thông minh |
| **Áp dụng cho** | Toàn bộ vận hành viên và kỹ sư sử dụng Smart Factory Dashboard |
| **Chu kỳ xem xét** | Mỗi 6 tháng hoặc sau khi cập nhật hệ thống |

---

## Mục Lục

1. [Mục đích](#1-mục-đích)
2. [Phạm vi áp dụng](#2-phạm-vi-áp-dụng)
3. [Phân công trách nhiệm](#3-phân-công-trách-nhiệm)
4. [Yêu cầu hệ thống](#4-yêu-cầu-hệ-thống)
5. [Quy trình khởi động hàng ngày](#5-quy-trình-khởi-động-hàng-ngày)
6. [Nạp dữ liệu OEE](#6-nạp-dữ-liệu-oee)
7. [Nạp dữ liệu nhật ký AGV](#7-nạp-dữ-liệu-nhật-ký-agv)
8. [Nạp dữ liệu hình ảnh AOI](#8-nạp-dữ-liệu-hình-ảnh-aoi)
9. [Đọc và diễn giải Dashboard](#9-đọc-và-diễn-giải-dashboard)
10. [Sử dụng bộ lọc ngày](#10-sử-dụng-bộ-lọc-ngày)
11. [Sử dụng chức năng tooltip khi di chuột](#11-sử-dụng-chức-năng-tooltip-khi-di-chuột)
12. [Theo dõi log terminal](#12-theo-dõi-log-terminal)
13. [Lỗi thường gặp và khắc phục](#13-lỗi-thường-gặp-và-khắc-phục)
14. [Quy trình kết thúc ngày](#14-quy-trình-kết-thúc-ngày)
15. [Quy tắc quản lý file dữ liệu](#15-quy-tắc-quản-lý-file-dữ-liệu)
16. [Liên hệ khẩn cấp](#16-liên-hệ-khẩn-cấp)

---

## 1. Mục đích

Quy trình vận hành chuẩn (SOP) này quy định các bước thực hiện hàng ngày khi vận hành hệ thống **Smart Factory Dashboard**. Dashboard tổng hợp và hiển thị trực quan dữ liệu thực tế và lịch sử từ ba hệ thống cốt lõi của nhà máy:

- **OEE (Overall Equipment Effectiveness)** — Dữ liệu năng suất máy móc theo từng chuyền
- **AGV (Automated Guided Vehicle)** — Nhật ký nhiệm vụ vận chuyển vật liệu của xe tự động
- **AOI (Automated Optical Inspection)** — Kết quả kiểm tra hình ảnh lỗi sản phẩm

Mục đích là đảm bảo mọi vận hành viên đều tuân theo quy trình nhất quán, đáng tin cậy khi nạp, xem xét và báo cáo dữ liệu nhà máy, nhằm ngăn ngừa sai sót dữ liệu, sự cố hệ thống hoặc diễn giải kết quả sai.

---

## 2. Phạm vi áp dụng

SOP này áp dụng cho:

- Tất cả vận hành viên theo ca (Sáng / Chiều / Đêm)
- Kỹ sư sản xuất và giám sát viên
- Kỹ sư chất lượng theo dõi tỷ lệ pass AOI
- Giám sát kho vận theo dõi phân bổ nhiệm vụ AGV

SOP này **không bao gồm**:
- Cài đặt phần mềm hoặc thiết lập môi trường (xem INSTALL.md)
- Cấu hình server backend
- Chỉnh sửa mã nguồn hoặc file cấu hình

---

## 3. Phân công trách nhiệm

| Vai trò | Trách nhiệm |
|---|---|
| **Vận hành viên ca** | Nạp dữ liệu đầu ca; theo dõi KPI; báo cáo bất thường |
| **Kỹ sư sản xuất** | Xác minh độ chính xác dữ liệu OEE; xem biểu đồ theo tầng; lọc theo ngày |
| **Kỹ sư chất lượng** | Xem tỷ lệ pass AOI; điều tra ảnh FAIL nếu tỷ lệ < 90% |
| **Giám sát kho vận** | Theo dõi số lượng nhiệm vụ AGV; xác định trạm bận nhất |
| **IT / Quản trị hệ thống** | Duy trì môi trường Python; xử lý lỗi phần mềm; cập nhật cấu hình |

---

## 4. Yêu cầu hệ thống

### 4.1 Cấu hình phần cứng tối thiểu

| Thành phần | Yêu cầu tối thiểu |
|---|---|
| CPU | Intel Core i5 (thế hệ 8) hoặc tương đương |
| RAM | 8 GB |
| Lưu trữ | 50 GB dung lượng trống |
| Màn hình | Độ phân giải 1366 × 768 (khuyến nghị 1920×1080) |
| Mạng | Kết nối mạng nội bộ nhà máy (IP: 10.177.117.1) |

### 4.2 Yêu cầu phần mềm

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Windows | 10 / 11 (64-bit) | Bắt buộc |
| Python | 3.10 trở lên | Phải có trong PATH hệ thống |
| PyQt5 | 5.15+ | Framework giao diện |
| pandas | 1.5+ | Xử lý dữ liệu |
| matplotlib | 3.6+ | Vẽ biểu đồ |
| xlrd | 2.0+ | Đọc file `.xls` |
| openpyxl | 3.0+ | Đọc file `.xlsx` |

### 4.3 Vị trí file dữ liệu cần thiết

Vận hành viên phải biết vị trí các file dữ liệu trước khi bắt đầu:

| Loại dữ liệu | Vị trí dự kiến | Định dạng file |
|---|---|---|
| Báo cáo OEE | Ổ mạng chia sẻ hoặc USB | `.xls`, `.xlsx`, `.csv` |
| Nhật ký AGV | Thư mục xuất từ server AGV | `.txt` hoặc `.log` (tên: `LogYYYYMMDDHH.txt`) |
| Hình ảnh AOI | Thư mục đầu ra của máy AOI | Thư mục chứa ảnh `.jpg` / `.bmp` / `.png` |

---

## 5. Quy trình khởi động hàng ngày

> ⚠️ **QUAN TRỌNG**: Thực hiện các bước theo đúng thứ tự. Không được bỏ qua bất kỳ bước nào.

### Bước 1 — Mở Terminal (Command Prompt)

1. Nhấn `Win + R`, gõ `cmd`, nhấn **Enter**
2. Điều hướng đến thư mục dashboard:
   ```
   cd D:\factory_dashboard
   ```

### Bước 2 — Khởi động Dashboard

Chạy lệnh sau:
```bash
python main.py
```

**Output terminal dự kiến khi khởi động:**
```
(Không có lỗi nào hiển thị — cửa sổ GUI tự động mở)
```

Nếu GUI **không** mở trong vòng 10 giây, tham khảo [Mục 13 — Khắc phục sự cố](#13-lỗi-thường-gặp-và-khắc-phục).

### Bước 3 — Phóng to cửa sổ

Chương trình sẽ tự động khởi động ở chế độ toàn màn hình.  
Nếu không, nhấn `Win + ↑` hoặc kéo cửa sổ để toàn màn hình.

### Bước 4 — Xác nhận bố cục giao diện

Kiểm tra các panel sau đều hiển thị đầy đủ:

| Panel | Vị trí | Mô tả |
|---|---|---|
| ⚙️ Data Control | Góc trên trái | Nút nạp từng loại dữ liệu |
| 🔄 Total AGV Tasks | Trên giữa | KPI card: Tổng nhiệm vụ AGV |
| 🖼️ AOI Pass Rate | Trên phải | KPI card: Tỷ lệ pass AOI (%) |
| Top Active Stations | Giữa trái | Biểu đồ cột — hoạt động trạm AGV |
| Action Ratio | Giữa | Biểu đồ tròn — tỷ lệ UP/DOWN |
| Hourly Traffic Flow | Giữa phải | Biểu đồ đường — nhiệm vụ AGV theo giờ |
| OEE F4 | Dưới trái | Biểu đồ cột — OEE tầng 4 theo chuyền |
| OEE F5 | Dưới giữa | Biểu đồ cột — OEE tầng 5 theo chuyền |
| AOI Quality Details | Dưới phải | Biểu đồ tròn — PASS vs FAIL |

---

## 6. Nạp dữ liệu OEE

> Dữ liệu OEE hiển thị năng suất (%) của mỗi chuyền sản xuất trên từng tầng.

### Bước 1 — Nhấn "📊 Load OEE File"

Nằm trong panel **⚙️ Data Control** (góc trên trái).

### Bước 2 — Chọn file

Hộp thoại chọn file sẽ mở ra.

- Điều hướng đến thư mục báo cáo OEE
- Chọn một hoặc nhiều file (giữ `Ctrl` để chọn nhiều)
- Định dạng được hỗ trợ: `.xls`, `.xlsx`, `.csv`
- Nhấn **Mở**

> ⚠️ Nếu không chọn file và nhấn Hủy, không có gì xảy ra. Không hiện thông báo lỗi.

### Bước 3 — Chờ xử lý hoàn tất

Theo dõi **cửa sổ terminal** để xem tiến trình:

```
[HH:MM:SS] [INFO] [OEE] Bắt đầu xử lý OEE – đã chọn N file
[HH:MM:SS] [INFO] [OEE] Đang đọc file: filename.xls  (định dạng: .xls)
[HH:MM:SS] [OK  ] [OEE] XLS nạp thành công qua xlrd – 527 dòng
[HH:MM:SS] [INFO] [OEE] Đang gộp 1 dataframe...
[HH:MM:SS] [OK  ] [OEE] Chuyển đổi OEE số hoàn tất – 527/527 dòng hợp lệ
[HH:MM:SS] [OK  ] [OEE] Xử lý hoàn tất sau 0.07s – đang đẩy dữ liệu lên UI
```

Xử lý hoàn tất khi terminal hiển thị **"Xử lý hoàn tất"**.

### Bước 4 — Xác nhận biểu đồ đã cập nhật

Sau khi nạp:
- Biểu đồ **OEE F4** (dưới trái) hiển thị các cột cho từng chuyền tầng 4 (4A, 4B, 4C...)
- Biểu đồ **OEE F5** (dưới giữa) hiển thị các cột cho từng chuyền tầng 5 (5G, 5H...)
- Dropdown **📅 Date Filter** được điền các ngày có sẵn

### Bước 5 — Kiểm tra WARN hoặc ERROR trong terminal

| Thông báo terminal | Hành động cần thực hiện |
|---|---|
| `[WARN] xlrd failed… trying HTML fallback` | Bình thường — file `.xls` được xuất dạng HTML, đã tự động xử lý |
| `[WARN] Column 'OEE' not found` | Thiếu cột OEE — xác minh bạn đã chọn đúng file |
| `[ERROR] Cannot read 'filename.xls'` | File bị hỏng — lấy bản mới từ hệ thống nguồn |
| `[ERROR] No valid data could be read` | Tất cả file đã chọn đều thất bại — liên hệ IT |

---

## 7. Nạp dữ liệu nhật ký AGV

> Dữ liệu nhật ký AGV hiển thị số lượng nhiệm vụ mỗi trạm nhận được và thời điểm xảy ra.

### Bước 1 — Nhấn "📜 Load AGV Logs"

Nằm trong panel **⚙️ Data Control**.

### Bước 2 — Chọn file nhật ký

- Điều hướng đến thư mục xuất nhật ký AGV
- File nhật ký thường có tên: `Log2026040108.txt` (định dạng: `LogYYYYMMDDHH.txt`)
- Chọn tất cả file trong khoảng thời gian cần (giữ `Ctrl` để chọn nhiều)
- Nhấn **Mở**

> 💡 **Mẹo**: Để phân tích cả ngày, chọn tất cả 24 file nhật ký theo giờ của ngày đó (00 đến 23).

### Bước 3 — Theo dõi output terminal

```
[HH:MM:SS] [INFO] [AGV] Bắt đầu xử lý nhật ký AGV – đã chọn 17 file
[HH:MM:SS] [INFO] [AGV] Đang quét: Log2026040108.txt
[HH:MM:SS] [OK  ] [AGV]   → Log2026040108.txt: tìm thấy 24 bản ghi nhiệm vụ
...
[HH:MM:SS] [OK  ] [AGV] Tổng nhiệm vụ: 248  |  Thời gian: 0.21s
[HH:MM:SS] [INFO] [AGV] Trạm bận nhất: [('4C', 80), ('4D-Revlon1-3', 60), ('R650', 40)]
[HH:MM:SS] [INFO] [AGV] Chi tiết hành động: {'DOWN': 124, 'UP': 124}
[HH:MM:SS] [INFO] [AGV] Số khung giờ: 17 giờ – đang đẩy dữ liệu lên UI
```

### Bước 4 — Xác nhận KPI card đã cập nhật

Card **🔄 Total AGV Tasks** phải hiển thị:
- **Số lớn**: Tổng số nhiệm vụ
- **Phụ đề**: Tên trạm bận nhất và thời gian xử lý

### Bước 5 — Xác nhận biểu đồ đã cập nhật

| Biểu đồ | Nội dung mong đợi |
|---|---|
| Top Active Stations | Tối đa 10 cột, sắp xếp giảm dần theo số nhiệm vụ |
| Action Ratio | Biểu đồ tròn với tỷ lệ UP/DOWN |
| Hourly Traffic Flow | Biểu đồ đường, mỗi giờ một điểm dữ liệu |

### Bước 6 — Xử lý số liệu bất thường

| Tình huống | Ý nghĩa | Hành động |
|---|---|---|
| Tổng nhiệm vụ = 0 | Không có dòng nhật ký hợp lệ nào được phân tích | Kiểm tra file có từ đúng thư mục không |
| Chỉ hiện trạm "Unknown(XXXX)" | ID điểm không có trong cấu hình | Báo IT — cần cập nhật POINT_MAP |
| Tỷ lệ Action chỉ có "DOWN" | AGV chỉ ghi nhận lệnh lấy hàng | Kiểm tra tính toàn vẹn của file nhật ký |

---

## 8. Nạp dữ liệu hình ảnh AOI

> Dữ liệu AOI hiển thị kết quả kiểm tra chất lượng sản phẩm — bao nhiêu bo mạch đạt (PASS) hoặc lỗi (FAIL).

### Bước 1 — Nhấn "🖼️ Select AOI Folder"

Nằm trong panel **⚙️ Data Control**.

### Bước 2 — Chọn thư mục AOI

Hộp thoại chọn thư mục sẽ mở ra.

- Điều hướng đến thư mục đầu ra hình ảnh của máy AOI
- Chọn **thư mục gốc** chứa các thư mục con theo ngày/lô
- Nhấn **Chọn Thư Mục**

> ⚠️ Hệ thống sẽ quét đệ quy tất cả thư mục con, tối đa **5 cấp độ sâu**.  
> File không phải ảnh (`.jpg`, `.bmp`, `.png`, `.tif`) sẽ tự động bị bỏ qua.

### Bước 3 — Theo dõi output terminal

```
[HH:MM:SS] [INFO] [AOI] Bắt đầu quét thư mục AOI – đã chọn 1 thư mục
[HH:MM:SS] [INFO] [AOI] Đang duyệt thư mục: D:\AOI\2026-04-02
[HH:MM:SS] [INFO] [AOI]   .: 17 ảnh, bỏ qua 3 file không phải ảnh
[HH:MM:SS] [OK  ] [AOI] Tóm tắt thư mục → Pass: 7 | Fail: 10 | Tỷ lệ pass: 41.2% | Chưa phân loại: 0
[HH:MM:SS] [OK  ] [AOI] Tổng cộng → Pass: 7 | Fail: 10 | Tỷ lệ pass: 41.2%
[HH:MM:SS] [INFO] [AOI] Quét hoàn tất sau 0.01s – đang đẩy dữ liệu lên UI
```

### Bước 4 — Xác nhận KPI card đã cập nhật

Card **🖼️ AOI Pass Rate** sẽ hiển thị:
- **Phần trăm**: Tỷ lệ pass hiện tại
  - 🟢 Xanh lá = ≥ 90% (chấp nhận được)
  - 🔴 Đỏ = < 90% (cần điều tra ngay)
- **Phụ đề**: `Pass: N | Fail: N`

### Bước 5 — Hành động khi tỷ lệ pass thấp

Nếu tỷ lệ pass < 90%:

1. Ghi lại số lượng Pass và Fail từ dashboard
2. Mở thư mục ảnh AOI và sắp xếp theo tên file
3. File có `"all pass"` trong tên = kết quả PASS
4. File có `"fail"` trong tên = kết quả FAIL
5. Báo cáo ngay cho Kỹ sư chất lượng
6. Ghi nhận sự kiện vào báo cáo chất lượng hàng ngày

---

## 9. Đọc và diễn giải Dashboard

### 9.1 KPI Cards

| Card | Ngưỡng bình thường | Hành động khi bất thường |
|---|---|---|
| Total AGV Tasks | Ổn định so với ngày trước | Điều tra nếu giảm > 30% so với ngày trước |
| AOI Pass Rate | ≥ 90% | Báo cáo ngay nếu < 90% |

### 9.2 Biểu đồ OEE (Tầng F4 / F5)

- **Trục Y**: OEE phần trăm (0–100%)
- **Trục X**: Tên chuyền sản xuất (4A, 4B, 4C...)
- **OEE bình thường**: ≥ 85% là mức đẳng cấp thế giới
- **OEE cảnh báo**: < 70% cần điều tra
- **Di chuột lên cột** để xem giá trị OEE chính xác

### 9.3 Biểu đồ cột trạm AGV

- Hiển thị các trạm bận nhất (top 10, không tính PATH)
- Trạm có số nhiệm vụ cao = phục vụ thường xuyên → xác minh lịch AGV phù hợp nhu cầu sản xuất

### 9.4 Biểu đồ tròn tỷ lệ hành động

- **DOWN** = AGV lấy vật liệu (cấp liệu cho máy)
- **UP** = AGV trả về (thu hồi từ máy)
- Tỷ lệ nên xấp xỉ 50/50; mất cân bằng lớn có thể cho thấy nhiệm vụ bị kẹt

### 9.5 Biểu đồ đường lưu lượng theo giờ

- Hiển thị tổng nhiệm vụ AGV mỗi giờ
- Đỉnh nên trùng với thời điểm giao ca
- Khoảng phẳng có thể cho thấy AGV dừng hoặc sản xuất tạm ngừng

---

## 10. Sử dụng bộ lọc ngày

Sau khi nạp dữ liệu OEE, dropdown **📅 Date Filter** được điền các ngày có sẵn.

**Để lọc theo ngày cụ thể:**
1. Nhấn vào dropdown
2. Chọn ngày (định dạng: `YYYY/MM/DD`)
3. Tất cả biểu đồ OEE tự động làm mới cho ngày đó

**Để về lại chế độ xem tất cả ngày:**
1. Chọn `📅 Date Filter (All)` ở đầu danh sách

> ⚠️ Nếu dropdown chỉ hiển thị `"📅 Date Filter (All)"`, hoặc file OEE chưa được nạp, hoặc file không chứa cột ngày (`日`).

---

## 11. Sử dụng chức năng tooltip khi di chuột

Tất cả biểu đồ đều hỗ trợ tooltip hiển thị giá trị chính xác.

**Cách sử dụng:**
1. Di chuột qua bất kỳ cột, múi tròn, hoặc điểm trên đường
2. Một ô tooltip sẽ hiện lên với:
   - **Biểu đồ cột**: Nhãn và giá trị chính xác
   - **Biểu đồ tròn**: Nhãn, số lượng và phần trăm
   - **Biểu đồ đường**: Giờ và số nhiệm vụ

> 💡 Tooltip đặc biệt hữu ích khi các chuyền OEE có giá trị gần nhau, khó phân biệt bằng mắt.

---

## 12. Theo dõi log terminal

Cửa sổ terminal phải **luôn mở** trong quá trình vận hành. Nó phản ánh trạng thái xử lý thời gian thực.

### 12.1 Bảng màu cấp độ log

| Màu sắc | Cấp độ | Ý nghĩa |
|---|---|---|
| 🔵 Xanh ngọc | `INFO` | Bước bình thường đang thực hiện |
| 🟢 Xanh lá | `OK` | Bước hoàn thành thành công |
| 🟡 Vàng | `WARN` | Vấn đề không nghiêm trọng; đã tự động dùng phương án dự phòng |
| 🔴 Đỏ | `ERROR` | Bước thất bại — cần hành động |

### 12.2 Khi nào cần báo cáo lên cấp trên

Báo cáo cho IT hoặc giám sát nếu gặp bất kỳ điều nào sau:

- Thông báo `[ERROR]` làm dừng quá trình xử lý
- Biểu đồ không cập nhật dù terminal hiển thị `[OK] … đang đẩy dữ liệu lên UI`
- Ứng dụng đột ngột đóng
- Terminal hiển thị `Traceback` (Python bị crash)

---

## 13. Lỗi thường gặp và khắc phục

| Lỗi / Triệu chứng | Nguyên nhân có thể | Giải pháp |
|---|---|---|
| GUI không mở | Python chưa cài hoặc môi trường sai | Chạy `python --version` trong CMD; liên hệ IT nếu thiếu |
| `ModuleNotFoundError: PyQt5` | Chưa cài dependencies | Chạy `pip install PyQt5 pandas matplotlib xlrd openpyxl` |
| Biểu đồ trắng sau khi nạp | Sai định dạng file hoặc thiếu cột | Kiểm tra thông báo `[WARN]` / `[ERROR]` trong terminal |
| OEE chỉ có cột F4 (không có F5) | File không có dữ liệu F5 | Xác minh file OEE có dòng với 樓層 = 'F5' |
| Popup "Đang có tác vụ nạp dữ liệu" | Nhấn nút quá nhanh | Chờ tác vụ hiện tại hoàn thành |
| AOI Pass Rate = 0% với Pass/Fail đều = 0 | Chọn sai thư mục (không có ảnh phù hợp) | Xác nhận thư mục chứa ảnh tên có "all pass" hoặc "fail" |
| xls hiển thị `[WARN] xlrd failed` rồi tiếp tục | File `.xls` được lưu dạng HTML | Bình thường — dự phòng tự động; dữ liệu vẫn nạp được |
| `[ERROR] No valid data` cho OEE | Tất cả file đều phân tích thất bại | Lấy bản xuất mới từ hệ thống nguồn |
| Ứng dụng crash (Traceback trong terminal) | Lỗi runtime không mong đợi | Chụp màn hình terminal; khởi động lại; báo IT |

---

## 14. Quy trình kết thúc ngày

### Bước 1 — Chụp ảnh màn hình Dashboard

Trước khi đóng, nhấn `PrtSc` hoặc dùng Snipping Tool (`Win + Shift + S`) để chụp toàn bộ dashboard cho báo cáo ngày.

### Bước 2 — Ghi lại các chỉ số quan trọng

Ghi vào nhật ký / báo cáo hàng ngày:

| Chỉ số | Giá trị hôm nay |
|---|---|
| Tổng nhiệm vụ AGV | ___ |
| Trạm bận nhất | ___ |
| Tỷ lệ pass AOI | __% |
| OEE trung bình F4 | __% |
| OEE trung bình F5 | __% |
| Có bất thường không | Có / Không — mô tả |

### Bước 3 — Đóng ứng dụng

Nhấn `Alt + F4` hoặc nhấn nút X của cửa sổ.  
Sau đó đóng cửa sổ terminal.

### Bước 4 — Lưu trữ file dữ liệu

Chuyển file dữ liệu đã xử lý vào thư mục lưu trữ theo chính sách lưu trữ dữ liệu của cơ sở.

---

## 15. Quy tắc quản lý file dữ liệu

### File OEE
- Quy ước đặt tên: `OEE_Report_YYYYMMDD.xls` (hoặc `.xlsx`)
- Lưu tại: `\\server\shared\OEE\YYYY\MM\`
- Thời gian lưu giữ: tối thiểu 12 tháng

### File nhật ký AGV
- Quy ước đặt tên: `LogYYYYMMDDHH.txt` (do server AGV tự tạo)
- Lưu tại: `\\server\shared\AGV_Logs\YYYY\MM\DD\`
- Thời gian lưu giữ: tối thiểu 6 tháng

### File hình ảnh AOI
- Quy ước đặt tên thư mục: `YYYYMMDD_BatchID\`
- Lưu tại: `\\server\shared\AOI\YYYY\MM\`
- Thời gian lưu giữ: tối thiểu 3 tháng (hoặc theo yêu cầu kiểm toán chất lượng)

> ⚠️ **Không được xóa file nhật ký hoặc hình ảnh gốc** nếu chưa có chữ ký phê duyệt của Quản lý chất lượng.

---

*Kết thúc tài liệu — SOP-SFD-001-VI v1.0*
