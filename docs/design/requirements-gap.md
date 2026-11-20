# Phân tích khoảng trống — Requirements v2.0

Phạm vi đối chiếu: nội dung yêu cầu đã trích xuất từ PDF/DOCX với `docs/PRD.md`, `docs/SCREENS.md` và `docs/design/specs/*`. Nhãn **đủ** nghĩa là tài liệu dự án đã nêu rõ ở mức phù hợp; **một phần** nghĩa là có ý hoặc thành phần liên quan nhưng thiếu chi tiết/nhãn/chức năng; **thiếu** nghĩa là chưa thấy trong các tài liệu đối chiếu.

| Lĩnh vực | Tài liệu yêu cầu nói gì | PRD/SCREENS/specs | Ghi chú |
|---|---|---|---|
| Navigation và module | Sáu module: `Market Overview`, `Market Data`, `Market News & Intelligence`, `Market Forecast`, `Market Analysis & Recommendations`, `AI Assistant & Reporting`; quản trị bố trí riêng theo quyền. | một phần | Có các route tương ứng, nhưng nhãn prototype rút gọn thành `Market News`, `Forecast`, `Analysis`, `AI Assistant`, `Reports`; cần thống nhất navigation sáu module và admin riêng theo quyền. |
| Market Overview | Snapshot các giá trị, đơn vị, thay đổi, market/ingestion timestamp, source, data status, quality; highlights, drivers và briefing có nguồn. | đủ | PRD/SCREENS/specs đã bao phủ metric cards, tape, freshness, provenance, highlights, drivers và briefing. |
| Market Data và chart modes | Chuỗi thời gian, so sánh, khoảng thời gian và chế độ `intraday`, `daily`, `weekly`, `monthly` nếu nguồn hỗ trợ. | một phần | Có time series, comparison và range tabs; chưa nêu đủ bốn chart modes theo đúng yêu cầu. |
| Crack spread | Công thức cấu hình, Formula ID, input, quy đổi đơn vị, thời điểm và version; không trộn futures/physical nếu chưa cấu hình. | đủ | Đã có trong PRD, screen map và business module ở mức chức năng chính. |
| News input | Nhập nội dung, URL nếu được phép, báo cáo nghiên cứu; upload PDF, Word, Excel và định dạng được hỗ trợ. | một phần | PRD có text + PDF/text upload; URL input và Word/Excel upload chưa được nêu đầy đủ. |
| News pipeline | 11 bước từ tiếp nhận, kiểm tra, trích xuất, chuẩn hóa, deduplication, phân loại, entity/event, tóm tắt, liên kết thị trường, lưu/index đến feed/workflow; mỗi bước có trạng thái, lỗi, retry hoặc kiểm tra thủ công. | một phần | Có processing states và pipeline khái quát; thiếu mô tả 11 bước cùng trạng thái/lỗi/retry từng bước. |
| News topics | 12 nhóm: `Crude Supply`, `Crude Demand`, `Refining Operations`, `Refined Products`, `OPEC+`, `Geopolitics`, `Shipping & Freight`, `Inventory`, `Macroeconomics`, `FX`, `Energy Policy`, `Other`. | một phần | Có topic filtering và một số nhóm trong prototype flow; chưa ghi đủ danh mục 12 chủ đề. |
| News deduplication | Phân biệt 4 quan hệ: trùng lặp gần như hoàn toàn; phiên bản cập nhật cùng sự kiện; bài độc lập cùng sự kiện; thông tin mới có giá trị bổ sung; không xóa nguồn. | một phần | Có duplicate candidate, linked articles và không xóa nguồn; chưa đặc tả đủ bốn loại quan hệ. |
| Continuous monitoring | Theo dõi nguồn cấu hình, tự động nhận nội dung mới, phát hiện sự kiện, cập nhật topic và cảnh báo theo điều kiện; phụ thuộc license/khả năng nguồn. | thiếu | Chưa thấy trong PRD/SCREENS/specs. |
| Source manager | Quản lý 8 trường: Source ID/tên, loại nguồn, loại dữ liệu, tần suất cập nhật, trạng thái kết nối, quy tắc kiểm tra, quyền sử dụng/phân loại, lỗi ingestion. | thiếu | Có source/provenance và admin data sources ở mức màn hình, nhưng chưa nêu đủ source manager và 8 trường. |
| Forecast | Nhập dự báo, version bất biến, source/horizon/methodology, so sánh actual và Absolute Error, Percentage Error, MAE, MAPE, Bias theo nguồn/instrument/horizon. | đủ | PRD/SCREENS/specs bao phủ forecast register, version history và evaluation; một số trường chi tiết cần đối chiếu khi triển khai. |
| Analysis | Trend, financial time series, cross-market; phân biệt dữ liệu quan sát, tương quan, giả thuyết, kết luận có bằng chứng. | một phần | Có Analysis, deterministic analytics, evidence ledger và correlation; các chủ đề/phân biệt đầy đủ của PDF chưa được nêu hết. |
| Market Impact Analysis | Bảy câu hỏi: sự kiện là gì; thị trường/chỉ số liên quan; cơ chế tác động; dữ liệu hỗ trợ; yếu tố thay đổi kết quả; chỉ số cần theo dõi; mức độ không chắc chắn. | thiếu | Chưa có đặc tả bảy câu hỏi trong screen map/specs. |
| Geopolitical Intelligence | Theo dõi xung đột/bất ổn, gián đoạn nguồn cung, chính sách năng lượng, trừng phạt, tuyến vận tải và rủi ro logistics; liên kết với thị trường/nguồn cung/vận tải. | một phần | Có Geopolitics trong news và key drivers; chưa có phạm vi phân tích Geopolitical Intelligence đầy đủ. |
| Recommendation | Mỗi khuyến nghị có 7 trường: bối cảnh; dữ liệu/nguồn tham chiếu; lập luận; giả định; không chắc chắn; độ tin cậy/giới hạn; thời điểm tạo/phiên bản. | một phần | Có Recommendation, confidence, uncertainty và evidence trong glossary/business module; chưa nêu đầy đủ bảy trường như một hợp đồng UI. |
| AI Assistant | Chat theo quyền, nguồn tham chiếu, phân biệt dữ kiện/tính toán/nhận định, đính kèm tài liệu, yêu cầu báo cáo; hiển thị bảng và biểu đồ khi phù hợp. | một phần | Chat, citations, tool trace và attach đã có; yêu cầu hiển thị bảng/biểu đồ chưa được nêu rõ trong PRD/SCREENS/specs. |
| Reporting | 7 loại: `Morning Briefing`, `End-of-day Report`, `Daily Market Report`, `Weekly Market Report`, `Monthly Market Report`, `On-demand Market Analysis`, `Event-driven Market Report`; version, cutoff, nguồn và PDF theo quyền. | một phần | Có report builder, preview, version và export; chưa liệt kê đủ bảy loại báo cáo. |
| Quyền truy cập | RBAC kết hợp Department, Data Classification, document-level permissions và individual permissions; quyền xem và xuất/chia sẻ độc lập. | một phần | Có ba role, classification và backend enforcement; Department-level và document-level permission chưa được đặc tả đầy đủ trong UI/docs. |
| Thời gian và lineage | Sáu loại mốc: `Event Time`, `Publication Time`, `Market Time`, `Ingestion Time`, `Processing Time`, `Creation Time`; kết quả phải truy ngược input, nguồn, thời điểm, formula/method, version và AI liên quan. | một phần | Có market/ingestion/publication timestamps, provenance và source ledger; thiếu bộ sáu mốc và data lineage đầy đủ. |
| AI Evaluation | Rubric 10 nhóm: `Factual Accuracy`, `Source Grounding`, `Extraction Accuracy`, `Summarization Quality`, `Financial Reasoning`, `Tool Selection`, `Task Completion`, `Permission Compliance`, `Latency`, `Cost`. | thiếu | Có audit/execution metadata và validation, nhưng chưa có AI Evaluation rubric 10 nhóm. |
| Theme | PDF/DOCX không có câu nào yêu cầu dark theme hoặc light theme. | — | Đây là kết luận về tài liệu yêu cầu; người dùng tự yêu cầu ghi rõ điểm này. Hướng hiện tại trong design specs là warm paper/light surface (`--paper`, `--surface`, sidebar petrol), không phải yêu cầu từ PDF/DOCX. |

## Các khoảng trống cần đưa vào UI redesign

- Navigation phải thể hiện đủ sáu module theo tên gốc hoặc có mapping nhãn được phê duyệt; `Administration` phải là khu vực riêng và ẩn/hiện theo quyền.
- AI Assistant cần có vùng hiển thị bảng/biểu đồ khi câu trả lời phù hợp, không chỉ chat text.
- Report builder cần hỗ trợ bảy loại báo cáo: `Morning Briefing`, `End-of-day Report`, `Daily Market Report`, `Weekly Market Report`, `Monthly Market Report`, `On-demand Market Analysis`, `Event-driven Market Report`.
- Market Data cần các chế độ biểu đồ `intraday`, `daily`, `weekly`, `monthly`.
- News intake cần URL input có điều kiện và upload Word/Excel bên cạnh PDF; pipeline cần 11 bước, trạng thái/lỗi/retry hoặc kiểm tra thủ công ở từng bước.
- News cần đủ 12 chủ đề, bốn quan hệ deduplication và continuous monitoring có điều kiện cảnh báo.
- Cần source manager với 8 trường, quyền Department-level/document-level, sáu loại mốc thời gian và data lineage.
- Cần bổ sung AI Evaluation rubric 10 nhóm, Recommendation 7 trường, Geopolitical Intelligence và Market Impact Analysis với 7 câu hỏi.

## Kết luận về theme

**TÀI LIỆU PDF/DOCX KHÔNG yêu cầu dark/light theme — đây là yêu cầu do người dùng tự yêu cầu thêm khi thực hiện gap analysis.** Các design specs hiện có chọn hướng warm paper/light surface; cần xem đây là quyết định thiết kế hiện tại, không gán ngược cho tài liệu yêu cầu nguồn.
