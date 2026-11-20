/* Bilingual copy layer for the BSR Market Intelligence design prototype.
 *
 * English source strings are the translation keys. Vietnamese is the default
 * language. Two application points share one catalog:
 *   - applyI18n(root) translates rendered markup (text nodes and a small set of
 *     attributes) after each render, so templates stay readable in English.
 *   - t(key, vars) translates strings that are built in JavaScript with
 *     interpolation (toasts, validation messages, aria labels, titles).
 * The production build should replace this layer with a real i18n library and
 * reuse this catalog as its message file. See docs/design/specs/i18n.md.
 */
(function () {
  'use strict';

  const STORAGE_KEY = 'bsr.lang';
  const DEFAULT_LANG = 'vi';
  const LANGS = [
    { code: 'vi', label: 'Tiếng Việt', short: 'VI' },
    { code: 'en', label: 'English', short: 'EN' }
  ];

  /* ---------- Vietnamese catalog: exact rendered text ---------- */
  const VI = {
    /* Shell and navigation */
    'Skip to main content': 'Bỏ qua đến nội dung chính',
    'Main navigation': 'Điều hướng chính',
    'Collapse sidebar': 'Thu gọn thanh bên',
    'Expand sidebar': 'Mở rộng thanh bên',
    'Workspace': 'Không gian làm việc',
    'Market Overview': 'Tổng quan thị trường',
    'Overview': 'Tổng quan',
    'Market Data': 'Dữ liệu thị trường',
    'Market News & Intelligence': 'Tin tức & tình báo thị trường',
    'Market News': 'Tin thị trường',
    'Market Forecast': 'Dự báo thị trường',
    'Forecast': 'Dự báo',
    'Market Analysis & Recommendations': 'Phân tích & khuyến nghị thị trường',
    'Analysis': 'Phân tích',
    'Intelligence': 'Trợ lý & báo cáo',
    'AI Assistant & Reporting': 'Trợ lý AI & báo cáo',
    'AI Assistant': 'Trợ lý AI',
    'Reports': 'Báo cáo',
    'Governance': 'Quản trị',
    'Administration': 'Quản trị hệ thống',
    'Restricted data is filtered at the backend, including AI retrieval.':
      'Dữ liệu hạn chế bị chặn ngay từ máy chủ, kể cả khi AI đi tìm.',
    'Demo role': 'Vai trò demo',
    'Search workspace': 'Tìm kiếm không gian làm việc',
    'Notifications': 'Thông báo',
    'Account menu': 'Menu tài khoản',
    'Open navigation': 'Mở điều hướng',
    'Latest ingestion across permitted sources': 'Lần nạp mới nhất trên các nguồn được phép',
    'Mixed freshness': 'Độ mới hỗn hợp',
    'Market tape': 'Bảng giá thị trường',
    'Restricted prices hidden': 'Giá hạn chế bị ẩn',
    'Close panel': 'Đóng bảng',
    'Close dialog': 'Đóng hộp thoại',
    'Dismiss notification': 'Bỏ qua thông báo',
    'Language': 'Ngôn ngữ',
    'Switch language': 'Chuyển ngôn ngữ',

    /* Roles and departments */
    'Leadership': 'Ban lãnh đạo',
    'Internal user': 'Người dùng nội bộ',
    'Internal': 'Nội bộ',
    'Executive Office': 'Văn phòng điều hành',
    'Commercial': 'Kinh doanh',
    'Market Intelligence': 'Phân tích thị trường',

    /* Login */
    'Reasonary AI · Auker intelligence layer': 'Reasonary AI · Lớp trí tuệ Auker',
    'Crude · Products · Cross-market context': 'Dầu thô · Sản phẩm · Phân tích liên thị trường',
    'One desk for the market': 'Toàn cảnh thị trường dầu khí',
    'and its evidence.': 'Diễn biến và tác động.',
    'Track markets, connect data, verify forecasts, and ask within your access rights.':
      'Theo sát thị trường, kết nối dữ liệu, kiểm chứng dự báo và hỏi đáp theo quyền truy cập.',
    'Permission-aware by design': 'Thiết kế theo quyền truy cập',
    'Source-grounded AI': 'AI dựa trên nguồn',
    'Deterministic analytics': 'Phân tích tất định',
    'Enter the workspace': 'Vào không gian làm việc',
    'Choose a demo role. Permissions and visible data change immediately.':
      'Chọn vai trò để xem. Quyền và dữ liệu hiển thị đổi ngay theo vai trò đó.',
    'Executive Office · market view, reports, restricted view':
      'Văn phòng điều hành · xem thị trường, báo cáo, dữ liệu hạn chế',
    'Market Intelligence · data operations, news, forecasts, audit':
      'Phân tích thị trường · nhập liệu, tin tức, dự báo, kiểm toán',
    'Commercial · approved market information only':
      'Kinh doanh · chỉ xem thông tin thị trường đã duyệt',
    'Demo environment.': 'Môi trường demo.',
    'All prices, news, forecasts and reports are synthetic and labelled. No live licensed feeds are connected. Restricted data is hidden for the Internal user role at the API boundary in the implemented application.':
      'Toàn bộ giá, tin tức, dự báo và báo cáo ở đây đều là số liệu mô phỏng, đã ghi rõ nhãn. Chưa kết nối nguồn dữ liệu có bản quyền nào. Khi triển khai thật, người dùng nội bộ sẽ không nhận được dữ liệu hạn chế ngay từ lớp API.',
    'Preparing your workspace…': 'Đang chuẩn bị không gian làm việc…',
    'Demo identity verified': 'Đã xác thực danh tính demo',
    'Loading permitted scope': 'Đang tải phạm vi được phép',
    'Opening overview': 'Đang mở tổng quan',
    'If the scope cannot be resolved, the workspace denies the route instead of showing unfiltered data.':
      'Nếu không xác định được phạm vi quyền, hệ thống đóng luôn màn hình đó chứ không hiển thị dữ liệu chưa lọc.',

    /* Shared labels */
    'Source': 'Nguồn',
    'Quality': 'Chất lượng',
    'Classification': 'Phân loại',
    'Data status': 'Trạng thái dữ liệu',
    'Market time': 'Thời điểm thị trường',
    'Market timestamp': 'Thời điểm thị trường',
    'Ingestion timestamp': 'Thời điểm nạp',
    'Ingested': 'Đã nạp',
    'Published': 'Đã phát hành',
    'Value': 'Giá trị',
    'Date': 'Ngày',
    'Version': 'Phiên bản',
    'Status': 'Trạng thái',
    'Result': 'Kết quả',
    'Action': 'Hành động',
    'Actor': 'Người thực hiện',
    'Object': 'Đối tượng',
    'Time': 'Thời gian',
    'Type': 'Loại',
    'Model': 'Mô hình',
    'Tools': 'Công cụ',
    'Latency': 'Độ trễ',
    'Cost': 'Chi phí',
    'Validation': 'Kiểm chứng',
    'Task': 'Tác vụ',
    'Role': 'Vai trò',
    'Scope': 'Phạm vi',
    'Range': 'Khoảng thời gian',
    'Instrument': 'Công cụ',
    'Close': 'Đóng',
    'Cancel': 'Hủy',
    'Preview': 'Xem trước',
    'Export': 'Xuất',
    'Search': 'Tìm kiếm',
    'Allowed': 'Được phép',
    'Denied': 'Bị từ chối',
    'Included': 'Đã bao gồm',
    'Excluded before AI': 'Loại trừ trước khi tới AI',
    'Connected': 'Đã kết nối',
    'Manual': 'Thủ công',
    'Pending': 'Chờ duyệt',
    'Valid': 'Hợp lệ',
    'Succeeded': 'Thành công',
    'Fallback': 'Dự phòng',
    'Passed': 'Đạt',
    'Refused': 'Từ chối',
    'Public': 'Công khai',
    'Confidential': 'Bảo mật',
    'Restricted': 'Hạn chế',
    'Real-time': 'Thời gian thực',
    'Delayed': 'Trễ',
    'End-of-day': 'Cuối ngày',
    'Futures': 'Hợp đồng tương lai',
    'Physical': 'Vật chất',
    'Calculated': 'Tính toán',
    'Index': 'Chỉ số',
    'Exchange rate': 'Tỷ giá',
    'index': 'chỉ số',
    'Processed': 'Đã xử lý',
    'Processing': 'Đang xử lý',
    'Failed': 'Thất bại',
    'Duplicate candidate': 'Nghi trùng lặp',
    'Duplicate candidates': 'Nghi trùng lặp',
    'Other': 'Khác',
    'missing': 'thiếu',
    'None available for your role.': 'Vai trò của bạn không xem được mục này.',
    'Restricted source': 'Nguồn hạn chế',
    'Pending review': 'Chờ duyệt',
    'Selected file': 'Tệp đã chọn',
    'Upload rejected.': 'Tải lên bị từ chối.',
    'Preview · not yet saved': 'Xem trước · chưa lưu',
    'Awaiting processing.': 'Đang chờ xử lý.',

    /* Overview */
    'Market overview': 'Tổng quan thị trường',
    'The market, with its receipts.': 'Thị trường, kèm theo bằng chứng.',
    'A consolidated view of crude, products, cracks and the evidence behind each number. Demo data is synthetic.':
      'Dầu thô, sản phẩm, crack và bằng chứng đứng sau từng con số, gom về một màn hình. Số liệu ở đây là mô phỏng.',
    'Quick input': 'Nhập nhanh',
    'Generate briefing': 'Tạo bản tin',
    'session change': 'vs. phiên trước',
    'Change against the previous session close, not against the prior stored observation':
      'Chênh lệch so với giá đóng cửa phiên trước, không tính theo lần ghi nhận trước đó',
    'Mkt': 'TT',
    'Market pulse': 'Diễn biến chính',
    'Chart range': 'Khoảng biểu đồ',
    'Event markers show linked market events. Select a marker for its source and affected instruments. Chart values are demo observations, not live prices.':
      'Các mốc trên biểu đồ là sự kiện thị trường có liên quan. Bấm vào một mốc để xem nguồn tin và những hàng hoá chịu ảnh hưởng. Số liệu trên biểu đồ là dữ liệu mô phỏng, không phải giá thị trường trực tiếp.',
    'Key market drivers': 'Điều gì đang chi phối thị trường',
    'Qualitative signals with a directional strength score, not a price forecast':
      'Các tín hiệu định tính, có chấm điểm độ mạnh, không phải dự báo giá',
    'What matters now': 'Đáng chú ý hôm nay',
    'Market highlights': 'Tin nổi bật thị trường',
    'Official sources': 'Nguồn chính thức',
    'User items': 'Người dùng',
    'No official-source items yet': 'Chưa có tin từ nguồn chính thức',
    'No user items yet': 'Chưa có tin người dùng',
    'No AI interpretation yet': 'Chưa có luận giải AI',
    'Source facts are separated from AI interpretation': 'Dữ kiện lấy từ nguồn được để riêng, không trộn với phần AI diễn giải',
    'Open news feed →': 'Mở dòng tin →',
    'Supply risk is supporting crude; product cracks are doing the real work.':
      'Rủi ro nguồn cung đang đỡ giá dầu thô, nhưng phần đáng chú ý nhất lại nằm ở crack sản phẩm.',
    'Brent held above $78 while gasoline and diesel cracks firmed. The move is supported by freight disruption and Asian blending demand, not by a broad crude-supply shock.':
      'Brent vẫn trụ trên 78 USD trong khi crack xăng và diesel cùng khởi sắc. Động lực đến từ gián đoạn vận tải và nhu cầu pha trộn ở châu Á, chứ chưa phải từ một cú sốc nguồn cung trên diện rộng.',
    'Brent +2.70% to $78.42; WTI +0.71% to $74.18.':
      'Brent +2,70% lên 78,42 USD; WTI +0,71% lên 74,18 USD.',
    'Gasoline crack +3.67% to $18.35/bbl; diesel crack −1.1%.':
      'Crack xăng +3,67% lên 18,35 USD/thùng; crack dầu diesel −1,1%.',
    'Red Sea freight and OPEC+ commentary remain the key watch items.':
      'Hai điểm cần bám sát: cước vận tải Biển Đỏ và các phát biểu từ OPEC+.',
    'Open briefing →': 'Mở bản tin →',
    'Ask the market desk': 'Hỏi bộ phận phân tích',
    'Answers are scoped to your permissions': 'Câu trả lời giới hạn theo quyền của bạn',
    'Ask a market question': 'Đặt câu hỏi về thị trường',
    'What is driving the recent move in gasoline cracks?':
      'Vì sao crack xăng biến động mạnh dạo gần đây?',
    'Gasoline cracks': 'Crack xăng',
    'Brent vs WTI': 'Brent so với WTI',
    'Supply news': 'Tin nguồn cung',
    'Continue in AI Assistant': 'Tiếp tục trong Trợ lý AI',
    'Data quality': 'Độ tin cậy dữ liệu',
    'Permitted observations only': 'Chỉ số liệu quan sát được phép',
    'Pending quality check': 'Chờ kiểm tra chất lượng',
    'Restricted instruments visible': 'Đang hiển thị cả dữ liệu hạn chế',
    'Restricted instruments hidden': 'Dữ liệu hạn chế đã được ẩn',
    'View audit': 'Xem kiểm toán',
    'Policy': 'Chính sách',
    'Open source context': 'Mở ngữ cảnh nguồn',
    'View data table': 'Xem bảng dữ liệu',
    'Hide data table': 'Ẩn bảng dữ liệu',
    '· indexed to 100': '· chuẩn hóa về 100',

    /* Market data */
    'Market data': 'Dữ liệu thị trường',
    'Every series carries its source.': 'Mỗi chuỗi số liệu đều ghi rõ nguồn.',
    'Explore historical observations, compare instruments and inspect how each crack spread was calculated.':
      'Xem lại dữ liệu theo ngày, so sánh các hàng hoá, và kiểm tra cách từng mức crack được tính ra.',
    'Add observation': 'Thêm quan sát',
    'Export CSV': 'Xuất CSV',
    'Export requires export permission': 'Xuất dữ liệu cần quyền xuất',
    'Instruments': 'Hàng hoá & chỉ số',
    'Crude oil': 'Dầu thô',
    'Refined products': 'Sản phẩm tinh chế',
    'FX & macro': 'Ngoại hối & vĩ mô',
    'Crack spreads': 'Chênh lệch crack',
    'Refinery operations': 'Vận hành nhà máy lọc dầu',
    'Restricted data included': 'Đã bao gồm dữ liệu hạn chế',
    'Restricted data hidden': 'Dữ liệu hạn chế bị ẩn',
    'Compare series': 'So sánh chuỗi',
    'Indexed to 100 to compare different units': 'Quy về 100 để so sánh được các đơn vị khác nhau',
    'event markers included': 'đã bao gồm mốc sự kiện',
    'Calculation provenance': 'Nguồn gốc phép tính',
    'Reproducible from stored inputs and formula version': 'Tính lại được từ dữ liệu gốc đã lưu và phiên bản công thức',
    'versioned formula': 'công thức có phiên bản',
    'No mixed price types': 'Không trộn loại giá',
    'Observations': 'Dữ liệu theo ngày',
    'Latest 12 permitted records · Δ is versus the prior stored observation; the header change is session-over-session · historical data is preserved':
      '12 lần ghi nhận gần nhất mà bạn được xem · Δ là chênh lệch so với lần ghi trước; còn con số ở đầu trang là so với phiên trước · dữ liệu cũ vẫn giữ nguyên',
    'Market date': 'Ngày thị trường',
    'Δ vs prior obs.': 'Δ so với lần trước',
    'Change versus the prior stored observation, not the session change shown above':
      'Chênh lệch so với lần ghi nhận trước, khác với con số theo phiên ở phía trên',
    'Market timestamp and ingestion timestamp are stored separately.':
      'Thời điểm thị trường và thời điểm nạp vào hệ thống được lưu thành hai mốc riêng.',
    'Open provenance →': 'Mở nguồn gốc →',
    'Event-linked series': 'Chuỗi liên kết sự kiện',
    'Events on or near the selected range': 'Sự kiện trong hoặc gần khoảng đã chọn',
    'All news →': 'Tất cả tin →',
    'No linked events': 'Không có sự kiện liên kết',
    'No permitted event in the current demo data is linked to this instrument.':
      'Trong bộ dữ liệu mô phỏng hiện tại, không có sự kiện nào bạn được xem gắn với hàng hoá này.',
    'Inspect event →': 'Xem sự kiện →',
    'over session change': 'so với phiên trước',
    'Market observation': 'Quan sát thị trường',
    'Open in Market Data': 'Mở trong Dữ liệu thị trường',
    'Market time is when the value was recorded; ingestion time is when the platform received it. The dashboard marks delayed and manual data rather than presenting it as real-time.':
      'Thời điểm thị trường là lúc con số được ghi lại; thời điểm nạp là lúc hệ thống nhận được. Dữ liệu trễ hay nhập tay đều được gắn nhãn riêng, không hiển thị như số liệu thời gian thực.',

    /* News */
    'Market news & intelligence': 'Tin tức & phân tích thị trường',
    'Read the source, then the interpretation.': 'Đọc bài gốc trước, rồi mới tin phần diễn giải.',
    'Filter permitted news, inspect provenance and compare what each source adds. AI summaries never replace the original.':
      'Lọc những tin bạn được xem, tra lại nguồn gốc, và so xem mỗi nguồn nói thêm được gì. Phần tóm tắt của AI không bao giờ thay thế bài gốc.',
    'Add news': 'Thêm tin',
    'Mark reviewed': 'Đánh dấu đã xem',
    'Search news': 'Tìm tin',
    'Topic': 'Chủ đề',
    'All topics': 'Tất cả chủ đề',
    'All sources': 'Tất cả nguồn',
    'No matching items': 'Không có mục phù hợp',
    'Try a different topic, source or search term. Restricted items are excluded before filtering.':
      'Thử chủ đề, nguồn hoặc từ khoá khác. Những mục bị hạn chế đã được loại ra từ trước khi lọc.',
    'Restricted sources included for this role.': 'Nguồn hạn chế được bao gồm cho vai trò này.',
    'Restricted sources are absent from this feed and its counts.':
      'Nguồn hạn chế không có trong dòng tin này, và cũng không được tính vào số lượng.',
    'Ask about the news →': 'Hỏi về tin tức →',
    'Coverage comparison': 'So sánh độ phủ',
    'What sources share, and what is additive': 'Điều các nguồn cùng có và điều bổ sung',
    'Shared:': 'Cùng có:',
    'Additive:': 'Bổ sung:',
    'Article count is not a trust score. This view shows coverage and unique detail, not a conclusion that one source is more reliable.':
      'Số bài nhiều không có nghĩa là đáng tin hơn. Mục này chỉ cho thấy độ phủ và những chi tiết riêng của từng nguồn, không kết luận nguồn nào tốt hơn.',
    'Processing queue': 'Hàng đợi xử lý',
    'Pipeline status for permitted items': 'Trạng thái đường ống cho các mục được phép',
    'Mark useful': 'Đánh dấu hữu ích',
    'Mark important': 'Đánh dấu quan trọng',
    'Report duplicate': 'Báo trùng lặp',
    'Open news detail': 'Mở chi tiết tin',
    'News intelligence': 'Phân tích tin tức',
    'Original source content': 'Nội dung gốc từ nguồn',
    'AI summary': 'Tóm tắt AI',
    'AI insight': 'Nhận định AI',
    'Linked instruments': 'Công cụ liên kết',
    'Useful': 'Hữu ích',
    'Important': 'Quan trọng',
    'Open linked data': 'Mở dữ liệu liên kết',

    /* Chart modes (Market Data) */
    'Chart mode': 'Chế độ biểu đồ',
    'Intraday': 'Trong ngày',
    'Daily': 'Theo ngày',
    'Weekly': 'Theo tuần',
    'Monthly': 'Theo tháng',
    'Demo intraday data': 'Dữ liệu trong ngày mô phỏng',
    'Synthetic demo session (30-minute buckets). No licensed intraday feed is connected in this prototype.':
      'Phiên mô phỏng tự tạo (mỗi điểm 30 phút). Bản mẫu này chưa kết nối nguồn dữ liệu trong ngày có bản quyền.',
    'Aggregated from the stored daily series, one point per 7-day bucket (last stored value).':
      'Tổng hợp từ chuỗi ngày đã lưu, mỗi điểm là một khối 7 ngày (lấy giá trị lưu cuối cùng).',
    'Aggregated from the stored daily series, one point per calendar month (last stored value).':
      'Tổng hợp từ chuỗi ngày đã lưu, mỗi điểm là một tháng dương lịch (lấy giá trị lưu cuối cùng).',
    'Stored daily observations as ingested from the source.':
      'Các quan sát ngày đã lưu, đúng như khi nạp từ nguồn.',

    /* News topics (12 groups) */
    'Crude Supply': 'Nguồn cung dầu thô',
    'Crude Demand': 'Nhu cầu dầu thô',
    'Refining Operations': 'Vận hành lọc dầu',
    'Refined Products': 'Sản phẩm tinh chế',
    'Geopolitics': 'Địa chính trị',
    'Shipping & Freight': 'Vận tải & cước biển',
    'Inventory': 'Tồn kho',
    'Macroeconomics': 'Kinh tế vĩ mô',
    'FX': 'Tỷ giá',
    'Energy Policy': 'Chính sách năng lượng',
    'Other': 'Khác',

    /* News pipeline (11 steps) */
    'Processing pipeline': 'Đường ống xử lý',
    'steps': 'bước',
    'Intake': 'Tiếp nhận',
    'Validation': 'Kiểm tra',
    'Extraction': 'Trích xuất',
    'Metadata normalization': 'Chuẩn hoá metadata',
    'Deduplication': 'Loại trùng lặp',
    'Classification': 'Phân loại',
    'Entity & event': 'Thực thể & sự kiện',
    'Summarization': 'Tóm tắt',
    'Market linking': 'Liên kết thị trường',
    'Store & index': 'Lưu & lập chỉ mục',
    'Feed & workflow': 'Dòng tin & quy trình',
    'Done': 'Xong',
    'Failed': 'Lỗi',
    'Review': 'Cần xem lại',
    'In progress': 'Đang chạy',
    'Queued': 'Đang chờ',
    'Retry': 'Chạy lại',
    'Manual check': 'Kiểm tra thủ công',
    'Duplicate candidate — retained and linked, not deleted':
      'Nghi trùng — vẫn giữ và liên kết, không xoá',
    'Extraction failed: unsupported document structure':
      'Trích xuất lỗi: cấu trúc tài liệu không được hỗ trợ',
    'Awaiting manual check': 'Đang chờ kiểm tra thủ công',
    'Each step records its own status. A failed step can be retried; a flagged step needs a manual check before the item reaches the feed.':
      'Mỗi bước ghi trạng thái riêng. Bước lỗi có thể chạy lại; bước bị đánh dấu phải được kiểm tra thủ công trước khi vào dòng tin.',
    'Step {step} queued for retry. Demo state only — no real reprocessing runs in this prototype.':
      'Bước {step} đã xếp hàng chạy lại. Chỉ là trạng thái demo — bản mẫu này không xử lý lại thật.',
    'Step {step} flagged for manual check. A reviewer confirms the result before the item reaches the feed.':
      'Bước {step} đã được đánh dấu để kiểm tra thủ công. Người xem xét xác nhận kết quả trước khi mục đó vào dòng tin.',

    /* News deduplication relations */
    'Deduplication relation': 'Quan hệ trùng lặp',
    'Near-identical duplicate': 'Trùng gần như hoàn toàn',
    'Same facts, same wording. The later item is linked to the original and kept for provenance.':
      'Cùng dữ kiện, cùng cách diễn đạt. Bài đến sau được liên kết với bài gốc và vẫn giữ để truy nguyên.',
    'Updated version of the same event': 'Phiên bản cập nhật của cùng sự kiện',
    'A later report revises or extends the same event. Both versions are retained with their timestamps.':
      'Bài đến sau sửa hoặc mở rộng cùng sự kiện. Cả hai phiên bản đều được giữ kèm mốc thời gian.',
    'Independent article, same event': 'Bài độc lập cùng sự kiện',
    'A separate outlet reports the same event. Retained as an independent source for coverage comparison.':
      'Một cơ quan khác đưa tin cùng sự kiện. Vẫn giữ như nguồn độc lập để so sánh độ phủ.',
    'New information with additive value': 'Thông tin mới có giá trị bổ sung',
    'Adds a detail the original lacks. Retained, linked and marked as additive.':
      'Bổ sung chi tiết mà bài gốc chưa có. Vẫn giữ, liên kết và đánh dấu là phần bổ sung.',
    'Deduplication never deletes a source. Items are linked, labelled and retained.':
      'Loại trùng lặp không bao giờ xoá nguồn. Các mục được liên kết, gắn nhãn và giữ lại.',

    /* Continuous monitoring */
    'Continuous monitoring': 'Theo dõi liên tục',
    'Configured sources and condition-based alerts': 'Nguồn đã cấu hình và cảnh báo theo điều kiện',
    'Demo': 'Demo',
    'Monitored sources': 'Nguồn đang theo dõi',
    'Alert conditions': 'Điều kiện cảnh báo',
    'Polling': 'Đang lấy tin định kỳ',
    'Scheduled': 'Theo lịch',
    'Paused': 'Tạm dừng',
    'Triggered': 'Đã kích hoạt',
    'Watching': 'Đang theo dõi',
    'Licence pending': 'Chờ cấp phép',
    'Every 15 min': 'Mỗi 15 phút',
    'Every 30 min': 'Mỗi 30 phút',
    'Weekly release': 'Phát hành hàng tuần',
    'Monitoring depends on source licensing and technical access. Alerts are conditions on permitted content, not trading signals.':
      'Theo dõi phụ thuộc vào bản quyền nguồn và khả năng truy cập kỹ thuật. Cảnh báo là điều kiện trên nội dung được phép xem, không phải tín hiệu giao dịch.',

    /* News intake (URL + document upload) */
    'Source URL (optional)': 'URL nguồn (không bắt buộc)',
    'URL intake is available because your role may ingest licensed sources. The link is stored as provenance; the publisher article is never republished.':
      'Nhập bằng URL khả dụng vì vai trò của bạn được phép nạp nguồn có bản quyền. Đường dẫn chỉ được lưu để truy nguyên; bài của nhà xuất bản không bao giờ được đăng lại.',
    'URL intake is not available for your role. Paste the source content instead.':
      'Vai trò của bạn không được nhập bằng URL. Hãy dán nội dung nguồn thay thế.',
    'Attach source document (optional)': 'Đính kèm tài liệu nguồn (không bắt buộc)',
    'Supported formats: {formats}, up to {size} MB. PDF, Word (.doc/.docx) and Excel (.xls/.xlsx) are extracted, validated and classified before indexing.':
      'Định dạng hỗ trợ: {formats}, tối đa {size} MB. PDF, Word (.doc/.docx) và Excel (.xls/.xlsx) được trích xuất, kiểm tra và phân loại trước khi lập chỉ mục.',
    'CSV, XLS/XLSX, PDF, DOC/DOCX': 'CSV, XLS/XLSX, PDF, DOC/DOCX',

    /* Source manager (8 fields) */
    'Source manager': 'Quản lý nguồn',
    'Eight configured fields per source · synthetic demo values':
      'Tám trường cấu hình cho mỗi nguồn · giá trị demo mô phỏng',
    'Source ID / name': 'Mã / tên nguồn',
    'Source type': 'Loại nguồn',
    'Data type': 'Loại dữ liệu',
    'Update frequency': 'Tần suất cập nhật',
    'Connection status': 'Trạng thái kết nối',
    'Validation rule': 'Quy tắc kiểm tra',
    'Usage rights / classification': 'Quyền sử dụng / phân loại',
    'Ingestion error': 'Lỗi nạp dữ liệu',
    'None': 'Không có',
    'Exchange feed': 'Nguồn sàn giao dịch',
    'Licensed assessment': 'Đánh giá giá có bản quyền',
    'Central bank reference': 'Tham chiếu ngân hàng trung ương',
    'News wire': 'Hãng tin',
    'Futures': 'Hợp đồng tương lai',
    'Physical assessments': 'Đánh giá giá vật chất',
    'FX reference rate': 'Tỷ giá tham chiếu',
    'News articles': 'Bài tin',
    'Real-time (demo)': 'Trực tiếp (demo)',
    'End-of-day': 'Cuối ngày',
    'Delayed (daily)': 'Chậm (hàng ngày)',
    'Manual / licensed integration pending': 'Thủ công / chờ tích hợp có bản quyền',
    'Connected': 'Đã kết nối',
    'Manual': 'Thủ công',
    'Price > 0, timestamp within 5 min of market time':
      'Giá > 0, mốc thời gian trong vòng 5 phút so với giờ thị trường',
    'Assessment present for every business day; no mixed price types':
      'Có đánh giá cho mọi ngày làm việc; không trộn loại giá',
    'Rate within ±2% of the prior reference': 'Tỷ giá trong khoảng ±2% so với tham chiếu trước',
    'Headline, source and publication time required before indexing':
      'Phải có tiêu đề, nguồn và thời điểm phát hành trước khi lập chỉ mục',
    'Last run 13 Nov 2026 · 2 items rejected: missing publication time':
      'Lần chạy cuối 13/11/2026 · 2 mục bị loại: thiếu thời điểm phát hành',

    /* Forecast */
    'Forecast intelligence': 'Phân tích dự báo',
    'Keep every version. Test it later.': 'Lưu lại từng phiên bản, để sau còn đối chiếu.',
    'Forecasts are stored immutably by source, instrument and horizon. Error metrics are computed deterministically from stored values.':
      'Mỗi dự báo được lưu cố định theo nguồn, hàng hoá và kỳ hạn, không sửa lại được. Chỉ số sai số do hệ thống tính tự động từ dữ liệu đã lưu.',
    'Add forecast': 'Thêm dự báo',
    'All instruments': 'Tất cả công cụ',
    'Period / horizon': 'Kỳ / kỳ hạn',
    'Actual': 'Thực tế',
    'Error': 'Sai số',
    'Versions →': 'Phiên bản →',
    'No forecasts match the selected filters.': 'Không có dự báo nào khớp bộ lọc đã chọn.',
    'Versioned records are never overwritten. Missing actuals are not treated as zero.':
      'Bản đã lưu không bao giờ bị ghi đè. Chỗ thiếu số thực tế thì để trống, không tính là 0.',
    'Forecast vs actual': 'Dự báo so với thực tế',
    'Permitted forecasts with a recorded actual': 'Dự báo được phép có giá trị thực tế đã ghi',
    'No evaluated forecasts in the current selection. Actual values must be recorded before error metrics can be computed.':
      'Trong lựa chọn hiện tại chưa có dự báo nào đủ điều kiện đánh giá. Phải có số thực tế thì mới tính được sai số.',
    'Deterministic accuracy': 'Độ chính xác tất định',
    'MAE': 'MAE',
    'mean absolute error': 'sai số tuyệt đối trung bình',
    'MAPE': 'MAPE',
    'when actual ≠ 0': 'khi thực tế ≠ 0',
    'Bias': 'Độ lệch',
    'forecast − actual': 'dự báo − thực tế',
    'Metrics are calculated by the analytical service from stored forecast versions and actual observations. The LLM does not compute them.':
      'Các chỉ số này do bộ phận phân tích tính từ phiên bản dự báo đã lưu và số liệu thực tế. Mô hình ngôn ngữ không tham gia tính toán.',
    'Latest version activity': 'Hoạt động phiên bản mới nhất',
    'Immutable revisions': 'Bản sửa đổi bất biến',
    'Method notes': 'Ghi chú phương pháp',
    'Store methodology and source document': 'Lưu phương pháp và tài liệu nguồn',
    'Each version retains its methodology, publication date, ingestion date and source document. A revised outlook creates a new version; the prior version remains available for comparison.':
      'Mỗi phiên bản lưu kèm phương pháp, ngày phát hành, ngày nạp và tài liệu gốc. Khi điều chỉnh dự báo, hệ thống tạo phiên bản mới và giữ nguyên bản cũ để đối chiếu.',
    'Forecast versus actual values': 'Giá trị dự báo so với thực tế',
    'Source / instrument': 'Nguồn / công cụ',
    'Forecast version': 'Phiên bản dự báo',
    'Version history': 'Lịch sử phiên bản',
    'Current': 'Hiện tại',
    'Prior version': 'Phiên bản trước',
    'Every update creates a new version. The prior version is never overwritten. Error metrics are deterministic and require a recorded actual.':
      'Cứ cập nhật là sinh ra một phiên bản mới, bản cũ không bị ghi đè. Sai số được tính tự động và chỉ tính khi đã có số thực tế.',
    'methodology:': 'phương pháp:',

    /* Analysis */
    'Market analysis': 'Phân tích thị trường',
    'Facts, calculations, then judgement.': 'Số liệu, phép tính, rồi mới tới nhận định.',
    'A versioned analysis workspace. The recommendation is decision support, not an executed business decision.':
      'Nơi làm phân tích, mỗi bản đều có phiên bản. Phần khuyến nghị chỉ để tham khảo khi ra quyết định, không phải quyết định kinh doanh đã được thực thi.',
    'Create report': 'Tạo báo cáo',
    'Active analysis · v1': 'Phân tích đang hoạt động · v1',
    'Source-grounded': 'Dựa trên nguồn',
    'Observed facts': 'Sự kiện quan sát được',
    'Sources: ICE (demo), CME (demo), Platts (demo), Reuters (demo)':
      'Nguồn: ICE (demo), CME (demo), Platts (demo), Reuters (demo)',
    'Open source ledger →': 'Mở sổ nguồn →',
    'Deterministic calculations': 'Phép tính tất định',
    'Produced by analytical services, reproducible from inputs': 'Do bộ phận phân tích tính ra, có thể tính lại từ dữ liệu gốc',
    'Cross-market correlation': 'Tương quan liên thị trường',
    '20-session rolling correlation matrix · correlation is not causation':
      'Tương quan trượt 20 phiên · có tương quan không có nghĩa là nhân quả',
    'Observed co-movement only. A statistical relationship does not establish that one variable caused the other. Hypotheses must be tested against event and supply evidence.':
      'Đây chỉ là mức độ cùng nhịp quan sát được. Tương quan thống kê không chứng minh được cái này gây ra cái kia; muốn khẳng định phải đối chiếu với dữ kiện sự kiện và nguồn cung.',
    'Assumptions and limitations': 'Giả định và giới hạn',
    'What would change this read': 'Điều gì sẽ thay đổi nhận định này',
    'Recommendation · AI interpretation': 'Khuyến nghị · Diễn giải AI',
    'Decision support': 'Hỗ trợ quyết định',
    'Medium confidence': 'Độ tin cậy trung bình',
    'Watch next': 'Theo dõi tiếp',
    'This is not a trading instruction or an automatic business decision. Authorized humans remain responsible for action.':
      'Đây không phải lệnh giao dịch, cũng không phải quyết định kinh doanh tự động. Người có thẩm quyền vẫn là người chịu trách nhiệm.',
    'Turn into report →': 'Chuyển thành báo cáo →',
    'Evidence ledger': 'Sổ bằng chứng',
    'Inputs behind the analysis': 'Dữ liệu đầu vào phía sau phân tích',
    'Market observations': 'Số liệu quan sát thị trường',
    'News items': 'Mục tin tức',
    'Forecast versions': 'Phiên bản dự báo',
    'Formula versions': 'Phiên bản công thức',
    'AI execution': 'Lần chạy AI',
    'Uncertainty': 'Bất định',
    'What is not established': 'Điều chưa được xác lập',
    'The freight move is confirmed by source reporting, but its duration and crude-supply impact are unknown. Demo data limits quantitative confidence; production analysis must use licensed observations and BSR\'s official formulas.':
      'Nguồn tin xác nhận được việc cước vận tải tăng, nhưng chưa rõ việc này kéo dài bao lâu và ảnh hưởng đến nguồn cung dầu thô ra sao. Dữ liệu mô phỏng không đủ để đưa ra con số chắc chắn; phân tích thật phải dùng số liệu có bản quyền và công thức chính thức của BSR.',

    /* Assistant */
    'AI assistant': 'Trợ lý AI',
    'Ask inside the boundary.': 'Hỏi trong phạm vi bạn được xem.',
    'A permission-scoped research assistant. It retrieves permitted data, uses registered tools and cites what it used.':
      'Trợ lý tra cứu, chỉ làm việc trong phạm vi quyền của bạn. Trợ lý lấy dữ liệu bạn được xem, dùng các công cụ đã đăng ký và trích dẫn nguồn đã dùng.',
    'Attach document': 'Đính kèm tài liệu',
    'Report workspace': 'Không gian báo cáo',
    'Market intelligence assistant': 'Trợ lý phân tích thị trường',
    'Auker orchestration · demo provider adapter': 'Điều phối Auker · bộ nối nhà cung cấp demo',
    'Retrieving permitted data and validating sources…': 'Đang lấy dữ liệu bạn được xem và kiểm lại nguồn…',
    'Ask a question': 'Đặt câu hỏi',
    'Ask about prices, cracks, news, forecasts or a permitted document…':
      'Hỏi về giá, crack, tin tức, dự báo, hoặc một tài liệu bạn được xem…',
    'Remove attachment': 'Bỏ đính kèm',
    'Enter to send · Shift+Enter for a new line · answers cite permitted sources':
      'Enter để gửi · Shift+Enter để xuống dòng · câu trả lời đều kèm trích dẫn nguồn',
    'Attach': 'Đính kèm',
    'Send': 'Gửi',
    'Permission context': 'Ngữ cảnh phân quyền',
    'Applied before retrieval': 'Áp dụng trước khi truy xuất',
    'Max classification': 'Mức phân loại tối đa',
    'Restricted data': 'Dữ liệu hạn chế',
    'Export permission': 'Quyền xuất',
    'Trace ID': 'Mã truy vết',
    'Answer discipline': 'Kỷ luật trả lời',
    'What the assistant must show': 'Những gì trợ lý phải trình bày',
    'Source facts': 'Sự kiện từ nguồn',
    'cited': 'có trích dẫn',
    'Calculations': 'Phép tính',
    'analytical service': 'dịch vụ phân tích',
    'AI interpretation': 'Diễn giải AI',
    'labelled': 'có gắn nhãn',
    'stated': 'được nêu rõ',
    'Output validation': 'Kiểm chứng đầu ra',
    'schema checked': 'đã kiểm tra lược đồ',
    'Recent executions': 'Lần chạy gần đây',
    'Auditable task runs': 'Lượt chạy có thể kiểm toán',
    'What should we investigate?': 'Chúng ta nên tìm hiểu điều gì?',
    'Ask about a price move, a crack spread, a source comparison, forecast accuracy or a permitted news theme. The assistant will show its sources and tool trace.':
      'Thử hỏi về một biến động giá, một mức crack, so sánh giữa các nguồn, độ chính xác của dự báo, hoặc một chủ đề tin bạn được xem. Trợ lý sẽ chỉ rõ nguồn và các bước đã tra.',
    'What is driving gasoline cracks?': 'Điều gì đang chi phối crack xăng?',
    'Compare Brent and WTI over 30 days.': 'So sánh Brent và WTI trong 30 ngày.',
    'Which news could affect crude supply?': 'Tin nào có thể ảnh hưởng nguồn cung dầu thô?',
    'How accurate are Brent forecasts?': 'Dự báo Brent chính xác đến đâu?',
    'What does the physical Brent market show?': 'Brent vật chất đang diễn biến thế nào?',
    'Summarize this morning\'s market briefing.': 'Tóm tắt bản tin thị trường sáng nay.',
    'Auker demo adapter': 'Bộ nối demo Auker',
    'Tool execution · completed': 'Thực thi công cụ · hoàn tất',

    /* Reports */
    'A snapshot that stays put.': 'Bản chụp cố định, không lặng lẽ đổi thay.',
    'Build a report, cite its sources and keep each version. Export is a separate permission from viewing.':
      'Tạo báo cáo, trích dẫn nguồn và giữ từng phiên bản. Xuất là quyền riêng, tách khỏi quyền xem.',
    'New report': 'Báo cáo mới',
    'Report builder': 'Trình tạo báo cáo',
    'On-demand market analysis · permitted data only': 'Phân tích thị trường theo yêu cầu · chỉ dữ liệu được phép',
    'Export allowed': 'Được phép xuất',
    'Export denied for role': 'Vai trò không được xuất',
    'Report type': 'Loại báo cáo',
    'On-demand Market Analysis': 'Phân tích thị trường theo yêu cầu',
    'Morning Briefing': 'Bản tin sáng',
    'End-of-day Report': 'Báo cáo cuối ngày',
    'Daily Market Report': 'Báo cáo thị trường ngày',
    'Weekly Market Report': 'Báo cáo thị trường tuần',
    'Monthly Market Report': 'Báo cáo thị trường tháng',
    'Event-driven Market Report': 'Báo cáo thị trường theo sự kiện',
    'Last 7 days': '7 ngày qua',
    'Last 30 days': '30 ngày qua',
    'Last 90 days': '90 ngày qua',
    'Week to date': 'Từ đầu tuần',
    'Month to date': 'Từ đầu tháng',
    'Market overview, news and analysis': 'Tổng quan thị trường, tin tức và phân tích',
    'Market data and crack spreads': 'Dữ liệu thị trường và chênh lệch crack',
    'News and source coverage': 'Tin tức và độ phủ nguồn',
    'Forecast accuracy': 'Độ chính xác dự báo',
    'Restricted physical and internal margin': 'Giá vật chất hạn chế và biên nội bộ',
    'The report freezes its data cut-off and sources. Later source updates do not silently change the stored version.':
      'Báo cáo cố định mốc cắt dữ liệu và nguồn. Các cập nhật nguồn sau đó không âm thầm thay đổi phiên bản đã lưu.',
    'Generate report': 'Tạo báo cáo',
    'Report register': 'Sổ đăng ký báo cáo',
    'Immutable versions · source references retained': 'Phiên bản bất biến · giữ tham chiếu nguồn',
    'Export permission required': 'Cần quyền xuất',
    'Version rules': 'Quy tắc phiên bản',
    'What is retained': 'Những gì được giữ lại',
    'Report ID, type, requester and creation time.': 'Mã báo cáo, loại, người yêu cầu và thời điểm tạo.',
    'Data cut-off and source references.': 'Mốc cắt dữ liệu và tham chiếu nguồn.',
    'AI model/allocation metadata per retention policy.': 'Siêu dữ liệu mô hình/phân bổ AI theo chính sách lưu trữ.',
    'Full content and immutable version number.': 'Toàn bộ nội dung và số phiên bản bất biến.',
    'Approval status when a workflow is configured.': 'Trạng thái phê duyệt khi có cấu hình quy trình.',
    'Export policy': 'Chính sách xuất',
    'Viewing is not sharing': 'Xem không phải chia sẻ',
    'Your role can export permitted reports. Every export is audited.':
      'Vai trò của bạn được xuất các báo cáo được phép. Mọi lần xuất đều được kiểm toán.',
    'Your role can view reports but cannot export them. The export endpoint would deny the request and record it in the audit log.':
      'Vai trò của bạn được xem báo cáo nhưng không được xuất. Điểm cuối xuất sẽ từ chối yêu cầu và ghi vào nhật ký kiểm toán.',
    'Review permission model': 'Xem lại mô hình phân quyền',
    'Report preview': 'Xem trước báo cáo',
    'Executive read': 'Nhận định điều hành',
    'Observed market facts': 'Sự kiện thị trường quan sát được',
    'What is driving it': 'Điều gì đang chi phối',
    'Sources': 'Nguồn',
    'Generated by BSR Market Intelligence · Synthetic demo content · AI-assisted, human-reviewed before use.':
      'Tạo bởi BSR Market Intelligence · Nội dung demo mô phỏng · Có hỗ trợ AI, được người kiểm duyệt trước khi dùng.',
    'Print / Save PDF': 'In / Lưu PDF',
    'Export denied': 'Xuất bị từ chối',

    /* Admin */
    'Administration is restricted.': 'Quản trị hệ thống bị hạn chế.',
    'Your role does not have access to user, source or audit administration. The navigation entry is hidden and the backend would deny this route. Switch to the Market Intelligence demo role to inspect the governance views.':
      'Vai trò của bạn không có quyền quản trị người dùng, nguồn hay kiểm toán. Mục điều hướng bị ẩn và máy chủ sẽ từ chối tuyến này. Chuyển sang vai trò demo Phân tích thị trường để xem các góc nhìn quản trị.',
    'Return to Overview': 'Quay lại Tổng quan',
    'Administration & governance': 'Quản trị & điều hành',
    'The system of record.': 'Hệ thống lưu trữ chuẩn.',
    'Demo governance view: role matrix, data sources, AI executions and append-only audit evidence.':
      'Góc nhìn quản trị demo: ma trận phân quyền, nguồn dữ liệu, lần chạy AI và bằng chứng kiểm toán chỉ ghi thêm.',
    'Export audit': 'Xuất kiểm toán',
    'Role matrix': 'Ma trận phân quyền',
    'Backend-enforced capabilities': 'Quyền năng do máy chủ thực thi',
    'Capability': 'Quyền năng',
    'View market data': 'Xem dữ liệu thị trường',
    'View Restricted': 'Xem dữ liệu hạn chế',
    'Export reports': 'Xuất báo cáo',
    'Ingest data / news': 'Nạp dữ liệu / tin tức',
    'Manage forecasts': 'Quản lý dự báo',
    'View audit log': 'Xem nhật ký kiểm toán',
    'AI queries': 'Truy vấn AI',
    'Viewing and exporting are separate permissions.': 'Xem và xuất là hai quyền riêng biệt.',
    'Data sources': 'Nguồn dữ liệu',
    'Configured demo connectors': 'Bộ nối demo đã cấu hình',
    'Futures · real-time demo · Internal': 'Hợp đồng tương lai · demo thời gian thực · Nội bộ',
    'Physical assessments · end-of-day · Restricted': 'Đánh giá vật chất · cuối ngày · Hạn chế',
    'FX reference · delayed · Internal': 'Tỷ giá tham chiếu · trễ · Nội bộ',
    'News · manual / licensed integration pending': 'Tin tức · thủ công / chờ tích hợp có bản quyền',
    'Commercial integrations depend on licensing and technical access. No licensed feed is connected in this demo.':
      'Tích hợp thương mại phụ thuộc bản quyền và quyền truy cập kỹ thuật. Không có nguồn có bản quyền nào được kết nối trong bản demo này.',
    'AI executions': 'Lần chạy AI',
    'Task, model, latency, cost, validation': 'Tác vụ, mô hình, độ trễ, chi phí, kiểm chứng',
    'Audit log': 'Nhật ký kiểm toán',
    'Append-only · latest permitted events': 'Chỉ ghi thêm · sự kiện được phép gần nhất',
    'Class.': 'Phân loại',
    'Every sensitive view, upload, export, permission change and AI request is recorded.':
      'Mọi lượt xem nhạy cảm, tải lên, xuất, thay đổi quyền và yêu cầu AI đều được ghi lại.',

    /* Audit actions and results */
    'AI request': 'Yêu cầu AI',
    'Report generated': 'Đã tạo báo cáo',
    'Restricted data viewed': 'Đã xem dữ liệu hạn chế',
    'News uploaded': 'Đã tải tin lên',
    'Restricted data requested': 'Yêu cầu dữ liệu hạn chế',
    'News processed': 'Đã xử lý tin',
    'Document uploaded': 'Đã tải tài liệu lên',
    'Manual observation added': 'Đã thêm quan sát thủ công',
    'Report export denied': 'Từ chối xuất báo cáo',
    'Report exported': 'Đã xuất báo cáo',
    'Market data exported': 'Đã xuất dữ liệu thị trường',
    'News feedback: like': 'Phản hồi tin: hữu ích',
    'News feedback: duplicate': 'Phản hồi tin: trùng lặp',
    'Pipeline': 'Đường ống',
    'system': 'hệ thống',

    /* Modals and drawers */
    'Quick data input': 'Nhập dữ liệu nhanh',
    'Data entry requires Market Intelligence access': 'Nhập dữ liệu cần quyền Phân tích thị trường',
    'Manual input': 'Nhập thủ công',
    'File upload': 'Tải tệp lên',
    'Quality state': 'Trạng thái chất lượng',
    'Note (optional)': 'Ghi chú (tùy chọn)',
    'e.g. 78.64': 'ví dụ 78,64',
    'e.g. BSR Internal': 'ví dụ BSR Internal',
    'Context for the reviewer': 'Ngữ cảnh cho người kiểm duyệt',
    'Manual data is marked as Manual and Pending until reviewed. Market time and ingestion time are stored separately. A duplicate check runs before confirmation.':
      'Dữ liệu thủ công được đánh dấu Thủ công và Chờ duyệt cho đến khi được kiểm duyệt. Thời điểm thị trường và thời điểm nạp được lưu riêng. Kiểm tra trùng lặp chạy trước khi xác nhận.',
    'Data file': 'Tệp dữ liệu',
    'Preview & confirm': 'Xem trước & xác nhận',
    'Add a market observation': 'Thêm quan sát thị trường',
    'Enter a numeric value before previewing. No data has been written.':
      'Nhập giá trị số trước khi xem trước. Chưa có dữ liệu nào được ghi.',
    'Enter a source before previewing. No data has been written.':
      'Nhập nguồn trước khi xem trước. Chưa có dữ liệu nào được ghi.',
    'News intake': 'Tiếp nhận tin',
    'Add a news item': 'Thêm mục tin',
    'Headline': 'Tiêu đề',
    'Headline from the source': 'Tiêu đề từ nguồn',
    'Reuters / Platts / internal': 'Reuters / Platts / nội bộ',
    'Summary or body': 'Tóm tắt hoặc nội dung',
    'Paste the source content or a short summary': 'Dán nội dung nguồn hoặc tóm tắt ngắn',
    'Add to pipeline': 'Đưa vào đường ống',
    'The item enters the processing pipeline: validation, extraction, metadata normalization, deduplication, classification and indexing. Original content is retained.':
      'Mục này đi vào đường ống xử lý: kiểm chứng, trích xuất, chuẩn hóa siêu dữ liệu, loại trùng, phân loại và lập chỉ mục. Nội dung gốc được giữ lại.',
    'Workspace search': 'Tìm kiếm không gian làm việc',
    'Search instruments, news and reports': 'Tìm công cụ, tin tức và báo cáo',
    'Search instruments, news, reports…': 'Tìm công cụ, tin tức, báo cáo…',
    'Search title, summary, entity…': 'Tìm tiêu đề, tóm tắt, thực thể…',
    'No permitted match. Try a different term.': 'Không có kết quả được phép. Thử từ khóa khác.',
    'Data freshness': 'Độ mới dữ liệu',
    '2 delayed feeds · USD/VND and DXY': '2 nguồn trễ · USD/VND và DXY',
    'Forecast activity': 'Hoạt động dự báo',
    'EIA Brent v3 added · 12 Nov 2026': 'Đã thêm EIA Brent v3 · 12/11/2026',
    'Permission check': 'Kiểm tra phân quyền',
    '1 denied Restricted request · audit logged': '1 yêu cầu Hạn chế bị từ chối · đã ghi kiểm toán',
    'Report ready': 'Báo cáo đã sẵn sàng',
    'Morning Briefing R-2026-041 v2': 'Bản tin sáng R-2026-041 v2',
    'Classification ceiling': 'Mức phân loại tối đa',
    'Admin': 'Quản trị',
    'Sign out to role selection': 'Đăng xuất về chọn vai trò',
    'rejected, see the error above': 'bị từ chối, xem lỗi phía trên',
    'queued for validation and extraction on confirm': 'chờ kiểm chứng và trích xuất khi xác nhận',
    'The selected file is kept below so you can retry with a supported file.':
      'Tệp đã chọn được giữ bên dưới để bạn thử lại với định dạng được hỗ trợ.',
    'Document uploaded and queued for processing. Original retained; classification applied.':
      'Tài liệu đã tải lên và chờ xử lý. Bản gốc được giữ; đã áp dụng phân loại.',
    'Uploaded document queued for text extraction, classification and indexing.':
      'Tài liệu đã tải lên đang chờ trích xuất văn bản, phân loại và lập chỉ mục.',
    'AI insight will be generated after extraction and validation.':
      'Nhận định AI sẽ được tạo sau khi trích xuất và kiểm chứng.',
    'Original file retained in object storage (demo simulation).':
      'Tệp gốc được giữ trong kho đối tượng (mô phỏng demo).',
    'Document attached to the AI context. Classification and permission checks will apply.':
      'Tài liệu đã đính kèm vào ngữ cảnh AI. Kiểm tra phân loại và quyền sẽ được áp dụng.',

    /* Toasts */
    'Demo role switched. Visible data and actions update to the new permission scope.':
      'Đã chuyển vai trò demo. Dữ liệu và hành động hiển thị cập nhật theo phạm vi quyền mới.',
    'Marked important for follow-up.': 'Đã đánh dấu quan trọng để theo dõi.',
    'Removed from important items.': 'Đã bỏ khỏi mục quan trọng.',
    'Feedback saved with your name and timestamp.': 'Đã lưu phản hồi kèm tên và thời điểm của bạn.',
    'Duplicate report saved for review. The source remains visible.':
      'Đã lưu báo cáo trùng lặp để xem xét. Nguồn vẫn hiển thị.',
    'That item is not available for your role.': 'Mục đó không khả dụng với vai trò của bạn.',
    'News import requires Market Intelligence access. This action is not available for your role.':
      'Nhập tin cần quyền Phân tích thị trường. Hành động này không khả dụng với vai trò của bạn.',
    'Headline and source are required. Nothing was saved.':
      'Cần có tiêu đề và nguồn. Không có dữ liệu nào được lưu.',
    'News item queued for processing. Original content retained; classification applied.':
      'Mục tin đã vào hàng đợi xử lý. Nội dung gốc được giữ; đã áp dụng phân loại.',
    'Restricted scope is not permitted for your role. No report was generated.':
      'Phạm vi hạn chế không được phép với vai trò của bạn. Không có báo cáo nào được tạo.',
    'Report generated and versioned. Sources and data cut-off frozen.':
      'Đã tạo báo cáo và gán phiên bản. Nguồn và mốc cắt dữ liệu được cố định.',
    'Export denied: your role can view this report but cannot export it. The attempt was recorded in the audit log.':
      'Xuất bị từ chối: vai trò của bạn được xem báo cáo này nhưng không được xuất. Lần thử đã được ghi vào nhật ký kiểm toán.',
    'Analysis versioning is enabled. This demo retains v1 and exposes the evidence ledger.':
      'Đã bật phiên bản phân tích. Bản demo giữ v1 và hiển thị sổ bằng chứng.',
    'Source ledger: ICE, CME, Platts, Reuters, BSR Analytical, formula CS-GAS-2.1.':
      'Sổ nguồn: ICE, CME, Platts, Reuters, BSR Analytical, công thức CS-GAS-2.1.',
    'Export allowed for your role. Downloads and prints are audited.':
      'Vai trò của bạn được phép xuất. Mọi lượt tải và in đều được kiểm toán.',
    'Export denied for your role. Viewing remains available.':
      'Vai trò của bạn không được xuất. Quyền xem vẫn khả dụng.',
    'CSV export simulated. Audit entry recorded.': 'Đã mô phỏng xuất CSV. Đã ghi nhật ký kiểm toán.',
    'Export denied: export permission is separate from view permission.':
      'Xuất bị từ chối: quyền xuất tách riêng khỏi quyền xem.',
    'Forecast export simulated. Audit entry recorded.': 'Đã mô phỏng xuất dự báo. Đã ghi nhật ký kiểm toán.',
    'Audit export simulated. In production this is a restricted, audited export.':
      'Đã mô phỏng xuất kiểm toán. Trong môi trường thực tế đây là bản xuất hạn chế và được kiểm toán.',
    'Administration permission required.': 'Cần quyền quản trị hệ thống.',
    'All permitted visible items marked reviewed for this demo session.':
      'Đã đánh dấu đã xem cho mọi mục được phép hiển thị trong phiên demo này.',

    /* Data content: instruments */
    'Brent Crude Futures': 'Hợp đồng tương lai dầu thô Brent',
    'WTI Crude Futures': 'Hợp đồng tương lai dầu thô WTI',
    'Brent Physical Dated': 'Brent vật chất giao ngay',
    'Gasoline RON95 (FOB Singapore)': 'Xăng RON95 (FOB Singapore)',
    'Diesel 10ppm (FOB Singapore)': 'Dầu diesel 10ppm (FOB Singapore)',
    'Jet Fuel A-1 (FOB Singapore)': 'Nhiên liệu bay A-1 (FOB Singapore)',
    'Fuel Oil 180 CST (FOB Singapore)': 'Dầu FO 180 CST (FOB Singapore)',
    'US Dollar Index': 'Chỉ số đô la Mỹ',
    'Gasoline Crack Spread': 'Chênh lệch crack xăng',
    'Diesel Crack Spread': 'Chênh lệch crack dầu diesel',
    '3-2-1 Composite Crack': 'Crack tổng hợp 3-2-1',
    'BSR Indicative Refining Margin': 'Biên lợi nhuận lọc dầu tham chiếu BSR',
    'Brent': 'Brent',
    'WTI': 'WTI',
    'Brent Dated': 'Brent Dated',
    'RON95': 'RON95',
    'Diesel': 'Dầu diesel',
    'Jet A-1': 'Jet A-1',
    'Fuel oil': 'Dầu FO',
    'DXY': 'DXY',
    'Gasoline crack': 'Crack xăng',
    'Diesel crack': 'Crack dầu diesel',
    '3-2-1 crack': 'Crack 3-2-1',
    'BSR margin': 'Biên BSR',
    'Front-month Brent futures, ICE. Demo series illustrative of market shape.':
      'Hợp đồng tương lai Brent tháng gần nhất, ICE. Chuỗi demo minh họa hình dạng thị trường.',
    'Front-month WTI futures, CME. Demo series illustrative of market shape.':
      'Hợp đồng tương lai WTI tháng gần nhất, CME. Chuỗi demo minh họa hình dạng thị trường.',
    'Dated Brent physical assessment. Restricted commercial data.':
      'Đánh giá Brent vật chất giao ngay. Dữ liệu thương mại hạn chế.',
    'Gasoline RON95 FOB Singapore assessment used for crack reference.':
      'Đánh giá xăng RON95 FOB Singapore dùng làm tham chiếu crack.',
    'Diesel 10ppm FOB Singapore assessment.': 'Đánh giá dầu diesel 10ppm FOB Singapore.',
    'Jet Fuel A-1 FOB Singapore assessment.': 'Đánh giá nhiên liệu bay A-1 FOB Singapore.',
    'Fuel oil 180 CST FOB Singapore. Quality check pending.':
      'Dầu FO 180 CST FOB Singapore. Đang chờ kiểm tra chất lượng.',
    'State Bank of Vietnam reference rate. Delayed demo feed.':
      'Tỷ giá tham chiếu Ngân hàng Nhà nước Việt Nam. Nguồn demo bị trễ.',
    'US Dollar Index, delayed demo feed.': 'Chỉ số đô la Mỹ, nguồn demo bị trễ.',
    'Gasoline crack versus Brent futures. Formula CS-GAS-2.1, no price-type mixing.':
      'Crack xăng so với hợp đồng tương lai Brent. Công thức CS-GAS-2.1, không trộn loại giá.',
    'Diesel crack versus Brent futures. Formula CS-DSL-2.0.':
      'Crack dầu diesel so với hợp đồng tương lai Brent. Công thức CS-DSL-2.0.',
    'Illustrative 3-2-1 composite using two gasoline barrels and one diesel barrel against three crude barrels.':
      'Crack tổng hợp 3-2-1 minh họa, dùng hai thùng xăng và một thùng dầu diesel so với ba thùng dầu thô.',
    'Indicative internal refining margin. Confidential; illustrative only.':
      'Biên lợi nhuận lọc dầu nội bộ tham chiếu. Bảo mật; chỉ mang tính minh họa.',
    'RON95 physical − Brent futures. Converted to USD/bbl.':
      'RON95 vật chất − hợp đồng tương lai Brent. Quy đổi sang USD/thùng.',
    'Diesel physical − Brent futures. Converted to USD/bbl.':
      'Dầu diesel vật chất − hợp đồng tương lai Brent. Quy đổi sang USD/thùng.',
    '(2 × gasoline + 1 × diesel − 3 × Brent) / 3. Demo formula.':
      '(2 × xăng + 1 × dầu diesel − 3 × Brent) / 3. Công thức demo.',
    'RON95 (FOB Singapore)': 'RON95 (FOB Singapore)',
    'Diesel 10ppm (FOB Singapore)': 'Dầu diesel 10ppm (FOB Singapore)',
    'Brent futures': 'Hợp đồng tương lai Brent',

    /* Data content: events, drivers, highlights */
    'OPEC+ agrees November output path': 'OPEC+ thống nhất lộ trình sản lượng tháng 11',
    'Red Sea freight disruption widens': 'Gián đoạn vận tải Biển Đỏ lan rộng',
    'Dung Quat unit maintenance begins': 'Bắt đầu bảo dưỡng phân xưởng Dung Quất',
    'US crude inventories fall more than expected': 'Tồn kho dầu thô Mỹ giảm mạnh hơn dự kiến',
    'Policy': 'Chính sách',
    'Logistics': 'Vận tải',
    'Refining': 'Lọc dầu',
    'Inventory': 'Tồn kho',
    'Supply': 'Nguồn cung',
    'Demand': 'Nhu cầu',
    'Macro': 'Vĩ mô',
    'OPEC+ discipline': 'Kỷ luật OPEC+',
    'Voluntary cuts extended through Q4; compliance signal firming.':
      'Cắt giảm tự nguyện được gia hạn hết quý 4; tín hiệu tuân thủ đang vững lên.',
    'Middle East risk': 'Rủi ro Trung Đông',
    'Shipping insurance costs elevated along the Gulf routes.':
      'Chi phí bảo hiểm vận tải tăng cao trên các tuyến Vịnh.',
    'Asia gasoline demand': 'Nhu cầu xăng châu Á',
    'Regional cracks supported by resilient mobility demand.':
      'Crack khu vực được hỗ trợ bởi nhu cầu đi lại vẫn bền.',
    'Industrial diesel demand': 'Nhu cầu dầu diesel công nghiệp',
    'Soft manufacturing prints cap upside in middle distillates.':
      'Số liệu sản xuất yếu hạn chế đà tăng của sản phẩm trung gian.',
    'Freight & insurance': 'Cước vận tải & bảo hiểm',
    'Red Sea diversions keep product arb windows uneven.':
      'Việc chuyển hướng qua Biển Đỏ khiến cửa sổ chênh lệch giá sản phẩm không đều.',
    'USD / VND': 'USD / VND',
    'Stable reference rate reduces imported-cost volatility.':
      'Tỷ giá tham chiếu ổn định giúp giảm biến động chi phí nhập khẩu.',
    'Brent holds above $78 as supply risk offsets demand caution':
      'Brent giữ trên 78 USD khi rủi ro nguồn cung bù đắp sự thận trọng về nhu cầu',
    'Gasoline crack widens on stronger Asian blending demand':
      'Crack xăng mở rộng nhờ nhu cầu pha trộn châu Á mạnh hơn',
    'AI read: product cracks are doing more work than crude direction':
      'Nhận định AI: crack sản phẩm đang đóng vai trò lớn hơn hướng dầu thô',
    'Source fact': 'Sự kiện từ nguồn',
    'Crude supply': 'Nguồn cung dầu thô',
    'Geopolitics': 'Địa chính trị',
    'Refined products': 'Sản phẩm tinh chế',
    'Asia demand': 'Nhu cầu châu Á',
    'Cross-market': 'Liên thị trường',
    'Deterministic inputs + cited news': 'Dữ liệu đầu vào tất định + tin được trích dẫn',

    /* Data content: news */
    'OPEC+ signals patience on output as Brent tests $78':
      'OPEC+ phát tín hiệu kiên nhẫn về sản lượng khi Brent thử mốc 78 USD',
    'Delegates indicated the group is unlikely to accelerate unwinding voluntary cuts before the next ministerial meeting, keeping near-term supply expectations tight.':
      'Các đại biểu cho biết nhóm khó có thể đẩy nhanh việc dỡ bỏ cắt giảm tự nguyện trước cuộc họp bộ trưởng tiếp theo, giữ kỳ vọng nguồn cung ngắn hạn ở mức thắt chặt.',
    'Sourced reporting placeholder for the prototype. The original article remains accessible from the licensed provider in production.':
      'Nội dung báo chí mô phỏng cho bản nguyên mẫu. Trong môi trường thực tế, bài gốc vẫn truy cập được từ nhà cung cấp có bản quyền.',
    'AI interpretation: the signal supports the front of the Brent curve, but the market reaction is modest because the decision was partly expected.':
      'Diễn giải AI: tín hiệu hỗ trợ phần đầu đường cong Brent, nhưng phản ứng thị trường khiêm tốn vì quyết định đã được dự báo một phần.',
    'Red Sea diversions add a week to Gulf–Asia product voyages':
      'Chuyển hướng Biển Đỏ làm chuyến sản phẩm Gulf–Asia dài thêm một tuần',
    'Freight assessments for Gulf–Asia routes rose again as operators extended diversions, tightening effective product availability in the east.':
      'Đánh giá cước tuyến Gulf–Asia tăng trở lại khi các hãng kéo dài chuyển hướng, làm nguồn cung sản phẩm thực tế ở phía đông thắt chặt hơn.',
    'Sourced reporting placeholder for the prototype.':
      'Nội dung báo chí mô phỏng cho bản nguyên mẫu.',
    'AI interpretation: the freight move is more material for product arb economics than for absolute crude direction.':
      'Diễn giải AI: diễn biến cước vận tải tác động mạnh hơn tới kinh tế chênh lệch giá sản phẩm so với hướng giá dầu thô tuyệt đối.',
    'US crude inventories fall more than expected: EIA':
      'Tồn kho dầu thô Mỹ giảm mạnh hơn dự kiến: EIA',
    'Commercial crude stocks declined while gasoline inventories built modestly, a mixed signal for the crude–product complex.':
      'Tồn kho dầu thô thương mại giảm trong khi tồn kho xăng tăng nhẹ, một tín hiệu trái chiều cho phức hợp dầu thô - sản phẩm.',
    'AI interpretation: crude draws support flat price, but the product build limits the read-through to cracks.':
      'Diễn giải AI: tồn kho dầu thô giảm hỗ trợ giá giao ngay, nhưng tồn kho sản phẩm tăng hạn chế tác động lan sang crack.',
    'Dung Quat begins planned maintenance on CDU':
      'Dung Quất bắt đầu bảo dưỡng theo kế hoạch phân xưởng chưng cất dầu thô',
    'A planned crude distillation unit maintenance window begins, with product output and crude intake adjusted according to the internal plan.':
      'Khung bảo dưỡng phân xưởng chưng cất dầu thô theo kế hoạch bắt đầu, sản lượng sản phẩm và lượng dầu thô đầu vào được điều chỉnh theo kế hoạch nội bộ.',
    'Internal operations note (demo placeholder).': 'Ghi chú vận hành nội bộ (mô phỏng demo).',
    'AI interpretation: the maintenance window is already reflected in the internal plan; monitor product cracks for unintended tightening.':
      'Diễn giải AI: khung bảo dưỡng đã được phản ánh trong kế hoạch nội bộ; theo dõi crack sản phẩm để phát hiện thắt chặt ngoài dự kiến.',
    'OPEC+ keeps output path steady, delegates say':
      'OPEC+ giữ nguyên lộ trình sản lượng, các đại biểu cho biết',
    'A near-identical account of the OPEC+ signal, adding one detail on the next ministerial date.':
      'Bản tin gần như trùng khớp về tín hiệu OPEC+, bổ sung một chi tiết về ngày họp bộ trưởng tiếp theo.',
    'AI interpretation: duplicate candidate linked to N-2411. Adds the ministerial date, so the source is retained and linked, not removed.':
      'Diễn giải AI: nghi trùng lặp liên kết với N-2411. Có bổ sung ngày họp bộ trưởng nên nguồn được giữ và liên kết, không bị xóa.',
    'Asian refiners trim spot crude purchases for December':
      'Các nhà máy lọc dầu châu Á cắt giảm mua dầu thô giao ngay tháng 12',
    'Several regional refiners reduced December spot requirements, pointing to softer near-term crude demand in Asia.':
      'Một số nhà máy lọc dầu trong khu vực giảm nhu cầu giao ngay tháng 12, cho thấy nhu cầu dầu thô ngắn hạn ở châu Á yếu hơn.',
    'AI interpretation: a demand-side offset to the supply narrative; keep it in the watch list rather than the base case.':
      'Diễn giải AI: yếu tố bù trừ phía nhu cầu so với câu chuyện nguồn cung; nên đưa vào danh sách theo dõi thay vì kịch bản cơ sở.',
    'Platts physical Brent assessment: dated cargoes firm':
      'Đánh giá Brent vật chất Platts: hàng giao ngay vững giá',
    'Restricted physical assessment detail. Visible only to roles with Restricted access.':
      'Chi tiết đánh giá vật chất hạn chế. Chỉ hiển thị với vai trò có quyền Hạn chế.',
    'Licensed physical assessment placeholder.': 'Đánh giá vật chất có bản quyền (mô phỏng).',
    'AI interpretation is withheld from unauthorized roles at retrieval time.':
      'Diễn giải AI bị giữ lại với vai trò không có quyền ngay tại thời điểm truy xuất.',
    'OPEC+': 'OPEC+',
    'Shipping & freight': 'Vận tải & cước',
    'Crude demand': 'Nhu cầu dầu thô',
    'Refining operations': 'Vận hành lọc dầu',
    'Red Sea': 'Biển Đỏ',
    'Singapore': 'Singapore',
    'United States': 'Hoa Kỳ',
    'Asia': 'Châu Á',
    'North Sea': 'Biển Bắc',
    'Dung Quat': 'Dung Quất',
    'BSR': 'BSR',

    /* Data content: forecasts, reports, coverage, analysis */
    'Q1 2027': 'Quý 1/2027',
    'Dec 2026': 'Tháng 12/2026',
    '3-month': '3 tháng',
    '1-month': '1 tháng',
    'STEO baseline': 'Cơ sở STEO',
    'Balances + inventory model': 'Cán cân + mô hình tồn kho',
    'Analytics spot outlook': 'Triển vọng giao ngay của bộ phận phân tích',
    'Demo internal scenario': 'Kịch bản nội bộ demo',
    'Morning briefing — supply risk meets product strength':
      'Bản tin sáng — rủi ro nguồn cung gặp sức mạnh sản phẩm',
    'Week 46 — cracks carry the narrative': 'Tuần 46 — crack dẫn dắt câu chuyện',
    'Hormuz disruption — exposure and watch list': 'Gián đoạn Hormuz — mức độ ảnh hưởng và danh sách theo dõi',
    'Event-driven Analysis': 'Phân tích theo sự kiện',
    'Final': 'Hoàn tất',
    'OPEC+ output signal': 'Tín hiệu sản lượng OPEC+',
    'Extension of voluntary cuts; next ministerial date': 'Gia hạn cắt giảm tự nguyện; ngày họp bộ trưởng tiếp theo',
    'Bloomberg adds the ministerial date; Reuters adds delegate count':
      'Bloomberg bổ sung ngày họp bộ trưởng; Reuters bổ sung số lượng đại biểu',
    'Red Sea freight': 'Cước vận tải Biển Đỏ',
    'Diversions and rising insurance costs': 'Chuyển hướng và chi phí bảo hiểm tăng',
    'Platts adds Gulf–Asia freight route assessments': 'Platts bổ sung đánh giá cước tuyến Gulf–Asia',
    'US inventories': 'Tồn kho Mỹ',
    'Crude draw, gasoline build': 'Dầu thô giảm, xăng tăng',
    'Weekly inventory levels and product breakdown': 'Mức tồn kho tuần và phân tích theo sản phẩm',
    'What is driving the recent move in product cracks, and what should BSR watch next?':
      'Điều gì đang chi phối diễn biến gần đây của crack sản phẩm, và BSR nên theo dõi gì tiếp theo?',
    'Gasoline crack (CS-GAS-2.1) is $18.35/bbl, +3.67% from 12 Nov (17.70), the last two stored sessions.':
      'Crack xăng (CS-GAS-2.1) ở 18,35 USD/thùng, +3,67% so với 12/11 (17,70) — hai phiên lưu cuối.',
    'Brent futures are $78.42/bbl, +2.70% from 12 Nov (76.36); WTI is $74.18/bbl, +0.71%.':
      'Brent tương lai ở 78,42 USD/thùng, +2,70% so với 12/11 (76,36); WTI ở 74,18 USD/thùng, +0,71%.',
    'Red Sea freight assessments have risen for a second week.':
      'Đánh giá cước vận tải Biển Đỏ tăng tuần thứ hai liên tiếp.',
    '5-day return, Brent': 'Lợi suất 5 ngày, Brent',
    'close-to-close, 5 sessions': 'đóng cửa đến đóng cửa, 5 phiên',
    '20-day realised volatility, Brent': 'Biến động thực hiện 20 ngày, Brent',
    'annualised stdev of daily log returns': 'độ lệch chuẩn năm hóa của lợi suất logarit ngày',
    'Brent–WTI spread': 'Chênh lệch Brent–WTI',
    'Brent futures − WTI futures': 'Hợp đồng tương lai Brent − hợp đồng tương lai WTI',
    'Gasoline crack change': 'Thay đổi crack xăng',
    'CS-GAS-2.1, session change': 'CS-GAS-2.1, thay đổi phiên',
    'Demo series are illustrative and are not official BSR or Platts assessments.':
      'Chuỗi demo chỉ mang tính minh họa, không phải đánh giá chính thức của BSR hay Platts.',
    'The freight signal is treated as a product-arbitrage input, not proof of crude supply loss.':
      'Tín hiệu cước vận tải được coi là đầu vào cho chênh lệch giá sản phẩm, không phải bằng chứng mất nguồn cung dầu thô.',
    'No restricted physical assessment is included for unauthorized roles.':
      'Không có đánh giá vật chất hạn chế nào được đưa vào cho vai trò không có quyền.',
    'Keep product cracks as the primary watch item; do not extrapolate a crude-supply shock from the freight move alone.':
      'Giữ crack sản phẩm là hạng mục theo dõi chính; không suy ra cú sốc nguồn cung dầu thô chỉ từ diễn biến cước vận tải.',
    'Medium': 'Trung bình',
    'The crack move is supported by product-specific freight and Asian blending demand, while crude flat price remains range-bound. The evidence supports a watch stance, not a trading instruction.':
      'Diễn biến crack được hỗ trợ bởi cước vận tải riêng cho sản phẩm và nhu cầu pha trộn châu Á, trong khi giá dầu thô giao ngay vẫn đi ngang trong biên độ. Bằng chứng ủng hộ thế theo dõi, không phải chỉ dẫn giao dịch.',
    'Gasoline crack vs 20-day average': 'Crack xăng so với trung bình 20 ngày',
    'Red Sea freight assessments': 'Đánh giá cước vận tải Biển Đỏ',
    'OPEC+ ministerial commentary': 'Bình luận của bộ trưởng OPEC+',
    'Dung Quat maintenance progress': 'Tiến độ bảo dưỡng Dung Quất',
    'Synthetic demo data for review. Not live BSR or licensed market data.':
      'Dữ liệu demo mô phỏng để đánh giá. Không phải dữ liệu trực tiếp của BSR hay dữ liệu thị trường có bản quyền.',
    'CSV, XLSX, PDF, DOC/DOCX': 'CSV, XLSX, PDF, DOC/DOCX',
    '1 document · processing': '1 tài liệu · đang xử lý',
    '1 source · processing': '1 nguồn · đang xử lý',
    'Restricted source': 'Nguồn hạn chế',
    'Linked to N-2411': 'Liên kết tới N-2411',
    'Linked to N-2411 · 1 additive detail': 'Liên kết tới N-2411 · 1 chi tiết bổ sung',
    '3 sources · 2 unique details': '3 nguồn · 2 chi tiết riêng',
    '4 sources · 3 unique details': '4 nguồn · 3 chi tiết riêng',
    '2 sources · 1 unique detail': '2 nguồn · 1 chi tiết riêng',
    '1 source · 2 unique details': '1 nguồn · 2 chi tiết riêng',
    '2 sources · 1 unique detail': '2 nguồn · 1 chi tiết riêng',
    '13–14 Nov 2026': '13–14/11/2026',
    '9–15 Nov 2026': '9–15/11/2026',
    '1–12 Nov 2026': '1–12/11/2026',
    '14 Nov 2026 · 09:30 ICT': '14/11/2026 · 09:30 ICT',
    '14 Nov 2026 · 09:42 ICT': '14/11/2026 · 09:42 ICT',
    '14 Nov 2026 · 09:15 ICT': '14/11/2026 · 09:15 ICT',
    '14 Nov 2026 · 09:20 ICT': '14/11/2026 · 09:20 ICT',
    '13 Nov 2026 · 17:40 ICT': '13/11/2026 · 17:40 ICT',
    '12 Nov 2026 · 15:10 ICT': '12/11/2026 · 15:10 ICT',
    '12 Nov 2026': '12/11/2026',
    '10 Nov 2026': '10/11/2026',
    '13 Nov 2026': '13/11/2026',
    '11 Nov 2026': '11/11/2026',
    '14 Nov 2026': '14/11/2026',
    '13 Nov 2026 · 18:30 ICT': '13/11/2026 · 18:30 ICT',
    '14 Nov 2026 · 08:30 ICT': '14/11/2026 · 08:30 ICT',
    '14 Nov 2026 · 08:32 ICT': '14/11/2026 · 08:32 ICT',
    '14 Nov 2026 · 08:28 ICT': '14/11/2026 · 08:28 ICT',
    '14 Nov 2026 · 08:20 ICT': '14/11/2026 · 08:20 ICT',
    '14 Nov 2026 · 08:22 ICT': '14/11/2026 · 08:22 ICT',
    '14 Nov 2026 · 09:00 ICT': '14/11/2026 · 09:00 ICT',
    '14 Nov 2026 · 09:02 ICT': '14/11/2026 · 09:02 ICT',
    '13 Nov 2026 · 17:00 ICT': '13/11/2026 · 17:00 ICT',
    '13 Nov 2026 · 17:04 ICT': '13/11/2026 · 17:04 ICT',
    '14 Nov 2026 · 07:05 ICT': '14/11/2026 · 07:05 ICT',
    '14 Nov 2026 · 07:06 ICT': '14/11/2026 · 07:06 ICT',
    '14 Nov 2026 · 07:50 ICT': '14/11/2026 · 07:50 ICT',
    '14 Nov 2026 · 08:02 ICT': '14/11/2026 · 08:02 ICT',
    '14 Nov 2026 · 06:40 ICT': '14/11/2026 · 06:40 ICT',
    '14 Nov 2026 · 06:58 ICT': '14/11/2026 · 06:58 ICT',
    '13 Nov 2026 · 22:30 ICT': '13/11/2026 · 22:30 ICT',
    '13 Nov 2026 · 22:41 ICT': '13/11/2026 · 22:41 ICT',
    '13 Nov 2026 · 16:20 ICT': '13/11/2026 · 16:20 ICT',
    '13 Nov 2026 · 16:25 ICT': '13/11/2026 · 16:25 ICT',
    '14 Nov 2026 · 07:58 ICT': '14/11/2026 · 07:58 ICT',
    '14 Nov 2026 · 08:06 ICT': '14/11/2026 · 08:06 ICT',
    '13 Nov 2026 · 14:10 ICT': '13/11/2026 · 14:10 ICT',
    '13 Nov 2026 · 14:23 ICT': '13/11/2026 · 14:23 ICT',
    '14 Nov 2026 · 09:05 ICT': '14/11/2026 · 09:05 ICT',
    '14 Nov 2026 · 08:58 ICT': '14/11/2026 · 08:58 ICT',
    '14 Nov 2026 · 08:31 ICT': '14/11/2026 · 08:31 ICT',
    '14 Nov 2026, 08:10 ICT': '14/11/2026, 08:10 ICT',
    '13 Nov 2026, 19:05 ICT': '13/11/2026, 19:05 ICT',
    '14 Nov 2026, 09:15 ICT': '14/11/2026, 09:15 ICT',
    'Reuters · 14 Nov 2026, 08:10 ICT': 'Reuters · 14/11/2026, 08:10 ICT',
    'Platts · 13 Nov 2026, 19:05 ICT': 'Platts · 13/11/2026, 19:05 ICT',
    'AI interpretation · 14 Nov 2026, 09:15 ICT': 'Diễn giải AI · 14/11/2026, 09:15 ICT',

    /* ---------- Recommendation record (seven fields) ---------- */
    'Recommendation record · seven fields': 'Bản khuyến nghị · bảy trường',
    'Context': 'Bối cảnh',
    'Data and sources': 'Dữ liệu và nguồn',
    'Reasoning': 'Lập luận',
    'Assumptions': 'Giả định',
    'Uncertainties': 'Không chắc chắn',
    'Confidence and limits': 'Độ tin cậy và giới hạn',
    'Timing and version': 'Thời điểm và phiên bản',
    'Gasoline crack CS-GAS-2.1 has firmed for two sessions while Brent stays range-bound between $77 and $79; the question is whether the product move is a durable signal or a freight-driven spike.':
      'Crack xăng CS-GAS-2.1 đã tăng hai phiên trong khi Brent đi ngang trong dải 77–79 USD; câu hỏi là liệu đà tăng của sản phẩm có bền hay chỉ là cú nhảy do cước vận tải.',
    'ICE Brent futures (demo), CME WTI futures (demo), Platts RON95 and diesel assessments (demo), Reuters OPEC+ reporting (demo), Platts Red Sea freight assessments (demo), formula CS-GAS-2.1.':
      'Hợp đồng tương lai Brent trên ICE (demo), WTI trên CME (demo), đánh giá RON95 và dầu diesel của Platts (demo), tin OPEC+ của Reuters (demo), đánh giá cước Biển Đỏ của Platts (demo), công thức CS-GAS-2.1.',
    'Product cracks rose while crude flat price held. Freight assessments for Gulf–Asia routes rose for a second week and Asian blending demand is described as resilient, so the product-specific evidence carries the signal rather than a crude-supply thesis.':
      'Crack sản phẩm tăng trong khi giá dầu thô đi ngang. Đánh giá cước tuyến Vùng Vịnh – châu Á tăng tuần thứ hai và nhu cầu pha trộn châu Á được mô tả là vẫn vững, nên bằng chứng riêng cho sản phẩm mang tín hiệu chính chứ không phải luận điểm nguồn cung dầu thô.',
    'Freight disruption persists through the next assessment window.': 'Gián đoạn cước vận tải kéo dài qua kỳ đánh giá tiếp theo.',
    'No unplanned crude supply loss is assumed.': 'Không giả định có tổn thất nguồn cung dầu thô ngoài kế hoạch.',
    'Demo series are illustrative and not official BSR or Platts assessments.': 'Chuỗi demo chỉ mang tính minh hoạ, không phải đánh giá chính thức của BSR hay Platts.',
    'The duration of the freight disruption and its read-through to crude supply are not established. A single two-session move is a thin sample for a trend claim.':
      'Thời gian kéo dài của gián đoạn cước vận tải và mức lan toả sang nguồn cung dầu thô chưa được xác lập. Một đợt tăng hai phiên là mẫu quá mỏng để khẳng định xu hướng.',
    'Medium confidence: source-confirmed freight and crack observations, but a short sample and no independent confirmation of duration.':
      'Độ tin cậy trung bình: cước vận tải và crack đã được nguồn xác nhận, nhưng mẫu ngắn và chưa có xác nhận độc lập về thời gian kéo dài.',
    'Created 14 Nov 2026 · 09:30 ICT · data cut-off 14 Nov 2026 · 09:15 ICT': 'Tạo 14/11/2026 · 09:30 ICT · cắt dữ liệu 14/11/2026 · 09:15 ICT',
    'Analysis v1 · formula CS-GAS-2.1 · AI execution AI-8F2A': 'Phân tích v1 · công thức CS-GAS-2.1 · lượt chạy AI AI-8F2A',

    /* ---------- Market Impact Analysis (seven questions) ---------- */
    'Market Impact Analysis': 'Phân tích tác động thị trường',
    'Seven standard questions, one demo answer each': 'Bảy câu hỏi chuẩn, mỗi câu một dòng trả lời demo',
    'Which products or valuations are affected?': 'Sản phẩm hoặc định giá nào bị ảnh hưởng?',
    'Gasoline crack (CS-GAS-2.1) and diesel crack first; Brent and WTI flat price only indirectly.':
      'Crack xăng (CS-GAS-2.1) và crack dầu diesel trước tiên; giá dầu thô Brent và WTI chỉ bị ảnh hưởng gián tiếp.',
    'How large is the impact, quantified?': 'Tác động lớn đến mức nào, định lượng ra sao?',
    'Gasoline crack +3.67% and Brent +2.70% between the last two stored sessions (12 Nov → 14 Nov); Brent–WTI spread $4.24/bbl.':
      'Crack xăng +3,67% và Brent +2,70% giữa hai phiên lưu cuối (12/11 → 14/11); chênh lệch Brent–WTI 4,24 USD/thùng.',
    'What price zone or range applies?': 'Vùng giá hoặc dải giá nào áp dụng?',
    'Brent $77–$79 range; gasoline crack watch band $17.20–$18.60/bbl around the 20-day average.':
      'Brent trong dải 77–79 USD; dải theo dõi crack xăng 17,20–18,60 USD/thùng quanh trung bình 20 ngày.',
    'Is this an event or a fundamental parameter?': 'Đây là sự kiện hay thông số cơ bản?',
    'A freight event layered on a product-fundamental trend; the crude fundamental balance is unchanged in this demo.':
      'Một sự kiện cước vận tải nằm trên xu hướng cơ bản của sản phẩm; cán cân cơ bản của dầu thô không đổi trong bản demo này.',
    'Which data release dates must be watched?': 'Những ngày phát hành dữ liệu nào cần theo dõi?',
    'EIA weekly inventories (next release 19 Nov 2026), next OPEC+ ministerial date, weekly Platts freight assessments.':
      'Tồn kho hàng tuần của EIA (phát hành kế tiếp 19/11/2026), ngày họp bộ trưởng OPEC+ tiếp theo, đánh giá cước hàng tuần của Platts.',
    'What are the limits of this conclusion?': 'Giới hạn của kết luận này là gì?',
    'Two-session sample, synthetic data, no licensed physical assessment for unauthorized roles, correlation is not causation.':
      'Mẫu hai phiên, dữ liệu tổng hợp, không có đánh giá vật chất có bản quyền cho vai trò không được phép, tương quan không phải quan hệ nhân quả.',
    'What would be needed to validate it?': 'Cần gì để hợp lệ hoá kết luận?',
    'A third week of freight assessments, an independent source on route duration, and a recorded actual to score the forecast version.':
      'Tuần thứ ba của đánh giá cước, một nguồn độc lập về thời gian tuyến vận tải, và một giá trị thực tế được ghi để chấm điểm phiên bản dự báo.',

    /* ---------- Geopolitical Intelligence ---------- */
    'Geopolitical Intelligence': 'Tình báo địa chính trị',
    'Conflict, supply disruption, energy policy, sanctions and shipping routes': 'Xung đột, gián đoạn nguồn cung, chính sách năng lượng, trừng phạt và tuyến vận tải',
    'OPEC+ decisions': 'Quyết định của OPEC+',
    'Delegates signal patience on unwinding voluntary cuts; next ministerial date is the trigger to watch.':
      'Các đại diện cho thấy sự kiên nhẫn trong việc dỡ bỏ cắt giảm tự nguyện; ngày họp bộ trưởng tiếp theo là mốc cần theo dõi.',
    'Sanction risk': 'Rủi ro trừng phạt',
    'Demo scenario: tighter secondary-sanction scrutiny on a crude exporter would raise freight and insurance costs.':
      'Kịch bản demo: việc siết chặt trừng phạt thứ cấp với một nước xuất khẩu dầu thô sẽ đẩy chi phí vận tải và bảo hiểm lên cao.',
    'Chokepoint and shipping': 'Điểm nghẽn và vận tải',
    'Red Sea diversions add about a week to Gulf–Asia product voyages; Hormuz remains open in this demo.':
      'Việc chuyển hướng qua Biển Đỏ làm tuyến sản phẩm Vùng Vịnh – châu Á dài thêm khoảng một tuần; Hormuz vẫn thông trong bản demo này.',
    'Energy policy shift': 'Thay đổi chính sách năng lượng',
    'Demo scenario: a refining-capacity policy change in Asia would shift product arb economics rather than crude direction.':
      'Kịch bản demo: thay đổi chính sách công suất lọc dầu ở châu Á sẽ dịch chuyển kinh tế chênh lệch giá sản phẩm hơn là hướng giá dầu thô.',
    'Brent, WTI': 'Brent, WTI',
    'Brent Dated, freight': 'Brent Dated, cước vận tải',
    'Diesel, jet': 'Dầu diesel, nhiên liệu bay',
    'RON95, fuel oil': 'RON95, dầu nhiên liệu',
    'risk': 'rủi ro',
    'High': 'Cao',
    'Low': 'Thấp',
    'Medium': 'Trung bình',
    'Linked to': 'Liên kết tới',
    'Geopolitical items are synthetic demo scenarios. They link an event to market, supply and freight exposure; they are not a forecast.':
      'Các mục địa chính trị là kịch bản demo tổng hợp. Chúng liên kết một sự kiện với mức phơi nhiễm thị trường, nguồn cung và cước vận tải; đây không phải dự báo.',

    /* ---------- Assistant answer figure ---------- */
    'Data behind this answer': 'Dữ liệu đứng sau câu trả lời',

    /* ---------- Timeline and data lineage ---------- */
    'Timeline · six timestamp types': 'Dòng thời gian · sáu loại mốc thời gian',
    'Data lineage': 'Truy xuất nguồn gốc dữ liệu',
    'Market time': 'Thời điểm thị trường',
    'Event time': 'Thời điểm sự kiện',
    'Publication time': 'Thời điểm công bố',
    'Ingestion time': 'Thời điểm nạp dữ liệu',
    'Processing time': 'Thời điểm xử lý',
    'Creation time': 'Thời điểm tạo',
    'Every result can be traced back to its input, source, timestamp, formula or method and version. The six timestamps are kept separately because they answer different questions.':
      'Mọi kết quả đều truy ngược được về đầu vào, nguồn, thời điểm, công thức hoặc phương pháp và phiên bản. Sáu mốc thời gian được giữ riêng vì chúng trả lời những câu hỏi khác nhau.',
    'Source': 'Nguồn',
    'Processing path': 'Đường dẫn xử lý',
    'Inputs used': 'Đầu vào đã dùng',
    'Formula / method': 'Công thức / phương pháp',
    'AI execution': 'Lượt chạy AI',
    'Reuters (demo) · wire article': 'Reuters (demo) · bài hãng tin',
    'Platts (demo) · freight assessment note': 'Platts (demo) · ghi chú đánh giá cước',
    'Intake → validation → extraction → normalisation → deduplication → classification → entity/event → summary → market link → store/index':
      'Tiếp nhận → kiểm tra → trích xuất → chuẩn hoá → loại trùng → phân loại → thực thể/sự kiện → tóm tắt → liên kết thị trường → lưu/chỉ mục',
    'Article text, publication time, entity list (OPEC+, Brent), linked series brent_futures and wti_futures':
      'Nội dung bài, thời điểm công bố, danh sách thực thể (OPEC+, Brent), chuỗi liên kết brent_futures và wti_futures',
    'Assessment text, route list (Gulf–Asia), linked series diesel and jet':
      'Nội dung đánh giá, danh sách tuyến (Vùng Vịnh – châu Á), chuỗi liên kết diesel và jet',
    'Relevance scoring v1.2 (demo) · no market calculation applied': 'Chấm điểm liên quan v1.2 (demo) · không áp dụng phép tính thị trường',
    'AI-8F19 · news_summarization · demo-orchestrator/small': 'AI-8F19 · news_summarization · demo-orchestrator/small',
    'News item v1 · not revised': 'Mục tin v1 · chưa sửa đổi',

    /* ---------- Admin: users, permissions, AI evaluation ---------- */
    'Users and permission scope': 'Người dùng và phạm vi quyền',
    'Department-level and document-level permissions are separate from the role': 'Quyền theo phòng ban và quyền theo tài liệu tách biệt với vai trò',
    'User': 'Người dùng',
    'Department-level permission': 'Quyền theo phòng ban',
    'Document-level permission': 'Quyền theo tài liệu',
    'Department': 'Phòng ban',
    'Max classification': 'Phân loại tối đa',
    'Restricted documents: allowed': 'Tài liệu hạn chế: được phép',
    'Restricted documents: denied': 'Tài liệu hạn chế: bị từ chối',
    'Export: allowed': 'Xuất: được phép',
    'Export: denied': 'Xuất: bị từ chối',
    'Department scope, classification ceiling and document-level view/export rights are enforced server-side before serialization. Hiding a control is not the enforcement.':
      'Phạm vi phòng ban, mức phân loại tối đa và quyền xem/xuất theo tài liệu được máy chủ thực thi trước khi tuần tự hoá. Ẩn một nút trên giao diện không phải là biện pháp thực thi.',
    'AI Evaluation rubric': 'Bộ tiêu chí đánh giá AI',
    'Ten evaluation groups · synthetic demo scores': 'Mười nhóm tiêu chí · điểm demo tổng hợp',
    'Criterion': 'Tiêu chí',
    'Score': 'Điểm',
    'Note': 'Ghi chú',
    'Scores are synthetic demo values for layout review, not measured production quality.':
      'Điểm là giá trị demo tổng hợp để duyệt bố cục, không phải chất lượng đo được trong môi trường thật.',
    'Factual Accuracy': 'Độ chính xác dữ kiện',
    'Source Grounding': 'Neo nguồn',
    'Extraction Accuracy': 'Độ chính xác trích xuất',
    'Summarization Quality': 'Chất lượng tóm tắt',
    'Financial Reasoning': 'Lập luận tài chính',
    'Tool Selection': 'Chọn công cụ',
    'Task Completion': 'Hoàn thành tác vụ',
    'Permission Compliance': 'Tuân thủ phân quyền',
    'Latency': 'Độ trễ',
    'Cost': 'Chi phí',
    'Stated observations match the stored series; no invented prices.': 'Số liệu quan sát khớp với chuỗi đã lưu; không có giá bịa ra.',
    'Every factual claim carries a permitted source reference.': 'Mọi khẳng định dữ kiện đều có tham chiếu nguồn được phép.',
    'Entity and topic extraction checked against a demo sample of news items.': 'Trích xuất thực thể và chủ đề được đối chiếu với một mẫu tin demo.',
    'Summaries keep the source attribution and do not present generated text as the article.': 'Bản tóm tắt giữ ghi công nguồn và không trình bày văn bản do máy tạo như bài gốc.',
    'Interpretation is separated from deterministic calculation; weaker on multi-step inference.': 'Diễn giải được tách khỏi phép tính tất định; yếu hơn ở suy luận nhiều bước.',
    'Registered tools chosen for the task; one fallback run recorded.': 'Công cụ đã đăng ký được chọn cho tác vụ; có một lượt chạy dự phòng được ghi lại.',
    'Answer delivered with sources and tool trace in the demo executions.': 'Câu trả lời được đưa ra kèm nguồn và vết công cụ trong các lượt chạy demo.',
    'Restricted data excluded before the task; refusal path verified for the Internal role.': 'Dữ liệu hạn chế bị loại trước tác vụ; đường từ chối đã được kiểm với vai trò Nội bộ.',
    'Demo executions ranged 0.9s–2.8s; no production benchmark.': 'Các lượt chạy demo trong khoảng 0,9s–2,8s; chưa có chuẩn đối sánh môi trường thật.',
    'Demo cost per execution $0.004–$0.041; not a production allocation.': 'Chi phí demo mỗi lượt chạy 0,004–0,041 USD; không phải phân bổ chi phí thật.'
  };

  /* ---------- Whole-string patterns for interpolated text ---------- */
  const VI_PATTERNS = [
    [/^(\d+) visible$/, '$1 hiển thị'],
    [/^(\d+) items?$/, '$1 mục'],
    [/^(\d+) drivers$/, '$1 yếu tố'],
    [/^(\d+) runs$/, '$1 lượt chạy'],
    [/^(\d+) events$/, '$1 sự kiện'],
    [/^(\d+) reports$/, '$1 báo cáo'],
    [/^(\d+) versions$/, '$1 phiên bản'],
    [/^(\d+) evaluated$/, '$1 đã đánh giá'],
    [/^(\d+) connected$/, '$1 đã kết nối'],
    [/^(\d+) roles$/, '$1 vai trò'],
    [/^(\d+) calculations$/, '$1 phép tính'],
    [/^(\d+) series$/, '$1 chuỗi'],
    [/^(\d+) cited$/, '$1 được trích dẫn'],
    [/^(\d+) articles?$/, '$1 bài'],
    [/^(\d+) sources? · (\d+) unique details?$/, '$1 nguồn · $2 chi tiết riêng'],
    [/^Linked to (N-\d+) · (\d+) additive details?$/, 'Liên kết tới $1 · $2 chi tiết bổ sung'],
    [/^(\d+) documents? · processing$/, '$1 tài liệu · đang xử lý'],
    [/^(\d+) sources? · processing$/, '$1 nguồn · đang xử lý'],
    [/^Brent and WTI futures · (\d+) sessions · unit USD\/bbl$/, 'Hợp đồng tương lai Brent và WTI · $1 phiên · đơn vị USD/thùng'],
    [/^(.+) · (\d+)-session view$/, '$1 · khung $2 phiên'],
    [/^Data cut-off 09:15 ICT · (\d+) versions kept$/, 'Cắt dữ liệu 09:15 ICT · giữ $1 phiên bản'],
    [/^Across (\d+) evaluated versions$/, 'Trên $1 phiên bản đã đánh giá'],
    [/^Version (\d+) · Data cut-off (.+)$/, 'Phiên bản $1 · Cắt dữ liệu $2'],
    [/^Version (\d+) · (.+)$/, 'Phiên bản $1 · $2'],
    [/^AI market briefing · v(\d+)$/, 'Bản tin thị trường AI · v$1'],
    [/^AI interpretation · (.+)$/, 'Diễn giải AI · $1'],
    [/^Tool execution · (.+)$/, 'Thực thi công cụ · $1'],
    [/^Validation: (.+) · (.+)$/, 'Kiểm chứng: $1 · $2'],
    [/^(.+) scope$/, 'Phạm vi $1'],
    [/^Open details for (.+)$/, 'Mở chi tiết cho $1'],
    [/^(.+) with (\d+) event markers?$/, '$1 với $2 mốc sự kiện'],
    [/^(.+) time series$/, 'Chuỗi thời gian $1'],
    [/^(.+) chart$/, 'Biểu đồ $1'],
    [/^Market data · (.+)$/, 'Dữ liệu thị trường · $1'],
    [/^News · (.+)$/, 'Tin tức · $1'],
    [/^Report · v(\d+)$/, 'Báo cáo · v$1'],
    [/^Applying the (.+) permission scope\. Restricted data and actions are resolved before the workspace renders\.$/,
      'Đang áp dụng phạm vi quyền $1. Dữ liệu và hành động hạn chế được xác định trước khi không gian làm việc hiển thị.'],
    [/^Your demo role is (.+)\. Switch to $/, 'Vai trò demo của bạn là $1. Chuyển sang '],
    [/^in the top bar to enter an observation\. The input control is shown for discoverability, but the backend would reject the write\.$/,
      'trên thanh trên cùng để nhập một quan sát. Ô nhập vẫn hiển thị để dễ khám phá, nhưng máy chủ sẽ từ chối thao tác ghi.'],
    [/^May contain (.+)\.$/, 'Có thể chứa $1.'],
    [/^Restricted data if explicitly selected$/, 'dữ liệu hạn chế nếu được chọn rõ ràng'],
    [/^Internal data only$/, 'chỉ dữ liệu nội bộ'],
    [/^Supported demo formats: (.+), up to (\d+) MB\. The upload is validated, stored, classified and queued for extraction\. It is not applied directly to market observations until reviewed\.$/,
      'Định dạng demo được hỗ trợ: $1, tối đa $2 MB. Tệp tải lên được kiểm chứng, lưu trữ, phân loại và đưa vào hàng đợi trích xuất. Tệp không được áp dụng trực tiếp vào số liệu quan sát thị trường cho đến khi được kiểm duyệt.'],
    [/^File is ([\d.]+) MB, above the (\d+) MB limit\. Nothing was stored\.$/,
      'Tệp có dung lượng $1 MB, vượt giới hạn $2 MB. Không có dữ liệu nào được lưu.'],
    [/^Unsupported format \((.+)\)\. Allowed: (.+)\. Nothing was stored\.$/,
      'Định dạng không được hỗ trợ ($1). Cho phép: $2. Không có dữ liệu nào được lưu.'],
    [/^Choose a file before confirming\. Nothing was uploaded\.$/,
      'Chọn một tệp trước khi xác nhận. Không có tệp nào được tải lên.'],
    [/^Upload rejected\. (.+)$/, 'Tải lên bị từ chối. $1'],
    [/^(.+) updated to (.+)\. Audit entry recorded\.$/, 'Đã cập nhật $1 thành $2. Đã ghi nhật ký kiểm toán.'],
    [/^(.+) · (\d+) KB · rejected, see the error above\.$/, '$1 · $2 KB · bị từ chối, xem lỗi phía trên.'],
    [/^(.+) · (\d+) KB · queued for validation and extraction on confirm\.$/,
      '$1 · $2 KB · chờ kiểm chứng và trích xuất khi xác nhận.'],
    [/^(.+) · (\d+) KB$/, '$1 · $2 KB'],
    [/^(.+) · (\d+) (?:sources?|nguồn)$/, '$1 · $2 nguồn']
  ];

  /* ---------- Long-form assistant answers ---------- */
  const AI = {
    refusal: {
      en: '<p class="refusal">Restricted data is not available to your role.</p><p>I can discuss permitted futures, product assessments and public news. I cannot retrieve restricted physical prices or internal margins, and I will not infer them from other data.</p><p class="small muted">The backend excluded Restricted records before the AI task was created. This is an authorization boundary, not a prompt instruction.</p>',
      vi: '<p class="refusal">Dữ liệu hạn chế không khả dụng với vai trò của bạn.</p><p>Tôi có thể trao đổi về hợp đồng tương lai, đánh giá sản phẩm và tin tức công khai trong phạm vi được phép. Tôi không thể truy xuất giá vật chất hạn chế hoặc biên lợi nhuận nội bộ, và sẽ không suy diễn chúng từ dữ liệu khác.</p><p class="small muted">Máy chủ đã loại bỏ các bản ghi Hạn chế trước khi tác vụ AI được tạo. Đây là ranh giới phân quyền, không phải chỉ dẫn trong prompt.</p>'
    },
    physical: {
      en: '<p>Permitted restricted assessment: <strong>Brent Dated at {value} {unit}</strong>, {pct} over the session, from {source}. Market time {marketTime}; ingested {ingestionTime}.</p><p>This is a source observation, not a forecast. It is visible because your role carries Restricted access. Viewing it does not grant permission to export or share it.</p>',
      vi: '<p>Đánh giá hạn chế được phép: <strong>Brent Dated ở {value} {unit}</strong>, {pct} trong phiên, từ {source}. Thời điểm thị trường {marketTime}; đã nạp {ingestionTime}.</p><p>Đây là số liệu quan sát từ nguồn, không phải dự báo. Nó hiển thị vì vai trò của bạn có quyền Hạn chế. Việc xem không cấp quyền xuất hoặc chia sẻ dữ liệu này.</p>'
    },
    crack: {
      en: '<p><strong>Observed:</strong> the gasoline crack (formula {crackId}) is <span class="calc">{crackVal} USD/bbl</span>, {crackPct} over the session. Brent futures are {brentVal} USD/bbl, {brentPct}.</p><p><strong>Evidence:</strong> product-specific freight assessments rose for a second week, and Asian blending demand is described as resilient in the cited source reporting. Diesel crack is {dieselPct}, so this is not a uniform product-strength move.</p><p><strong>AI interpretation:</strong> the balance of evidence supports a product-crack watch stance rather than a crude-supply shock thesis. The freight signal is real in the source data, but its duration and crude-supply impact are not established.</p><p><strong>What to watch:</strong> gasoline crack versus its 20-day average, Red Sea freight, and the next OPEC+ ministerial commentary.</p>',
      vi: '<p><strong>Ghi nhận:</strong> crack xăng (công thức {crackId}) ở <span class="calc">{crackVal} USD/bbl</span>, {crackPct} trong phiên. Hợp đồng tương lai Brent ở {brentVal} USD/bbl, {brentPct}.</p><p><strong>Bằng chứng:</strong> đánh giá cước vận tải riêng cho sản phẩm tăng tuần thứ hai, và nhu cầu pha trộn châu Á được mô tả là vẫn vững trong các nguồn được trích dẫn. Crack dầu diesel là {dieselPct}, nên đây không phải một đợt tăng đồng đều của toàn bộ sản phẩm.</p><p><strong>Diễn giải AI:</strong> cán cân bằng chứng nghiêng về thế theo dõi crack sản phẩm hơn là luận điểm sốc nguồn cung dầu thô. Tín hiệu cước vận tải là thật trong dữ liệu nguồn, nhưng thời gian kéo dài và tác động lên nguồn cung dầu thô chưa được xác lập.</p><p><strong>Cần theo dõi:</strong> crack xăng so với trung bình 20 ngày, cước vận tải Biển Đỏ, và bình luận tiếp theo của OPEC+.</p>'
    },
    forecast: {
      en: '<p><strong>Deterministic result:</strong> across {n} permitted forecast versions with a recorded actual, MAE is <span class="calc">{mae}</span>. The error calculation is performed by the analytical service from stored forecast versions and actual observations.</p><p><strong>Source comparison:</strong> EIA\'s Brent v3 is $79.50 against a recorded actual of $77.35 (+$2.15); IEA\'s WTI v2 is $72.60 against $73.66 (−$1.06). Missing actuals are not treated as zero, so the comparison is limited to evaluated versions.</p><p><strong>Interpretation:</strong> a single error pair is not enough to rank sources. Compare by instrument, horizon and sample size before drawing a conclusion.</p>',
      vi: '<p><strong>Kết quả tất định:</strong> trên {n} phiên bản dự báo được phép có giá trị thực tế, MAE là <span class="calc">{mae}</span>. Phép tính sai số do dịch vụ phân tích thực hiện từ các phiên bản dự báo đã lưu và số liệu quan sát thực tế.</p><p><strong>So sánh nguồn:</strong> Brent v3 của EIA là 79,50 USD so với thực tế 77,35 (+2,15); WTI v2 của IEA là 72,60 so với 73,66 (−1,06). Giá trị thực tế thiếu không được coi là 0, nên so sánh chỉ giới hạn ở các phiên bản đã đánh giá.</p><p><strong>Diễn giải:</strong> một cặp sai số không đủ để xếp hạng nguồn. Cần so sánh theo công cụ, kỳ hạn và cỡ mẫu trước khi kết luận.</p>'
    },
    news: {
      en: '<p><strong>Source facts:</strong> delegates signalled patience on unwinding OPEC+ voluntary cuts; Red Sea diversions added roughly a week to Gulf–Asia product voyages; several Asian refiners trimmed December spot crude requirements.</p><p><strong>Why it matters:</strong> the first two items support crude and product tightness, while the third is a demand-side offset. The news set does not support a single-direction conclusion.</p><p><strong>AI interpretation:</strong> keep the product-freight channel as the higher-conviction read and treat the crude-supply story as a scenario risk. This is not a trading recommendation.</p>',
      vi: '<p><strong>Sự kiện từ nguồn:</strong> các đại biểu phát tín hiệu kiên nhẫn trong việc dỡ bỏ cắt giảm tự nguyện của OPEC+; việc chuyển hướng qua Biển Đỏ làm các chuyến sản phẩm Gulf–Asia dài thêm khoảng một tuần; một số nhà máy lọc dầu châu Á cắt giảm nhu cầu dầu thô giao ngay tháng 12.</p><p><strong>Vì sao quan trọng:</strong> hai thông tin đầu hỗ trợ thế thắt chặt dầu thô và sản phẩm, trong khi thông tin thứ ba là yếu tố bù trừ phía nhu cầu. Tập tin tức không đủ để kết luận một chiều.</p><p><strong>Diễn giải AI:</strong> giữ kênh cước vận tải sản phẩm là nhận định có độ tin cậy cao hơn và coi câu chuyện nguồn cung dầu thô là rủi ro kịch bản. Đây không phải khuyến nghị giao dịch.</p>'
    },
    prices: {
      en: '<p><strong>Observed:</strong> Brent is <span class="calc">{brentVal} USD/bbl</span> ({brentPct}), WTI is <span class="calc">{wtiVal} USD/bbl</span> ({wtiPct}). The Brent–WTI spread is <span class="calc">{spread} USD/bbl</span>, computed by the analytical service.</p><p><strong>Context:</strong> the move is modest and broadly shared across the two benchmarks. The cited OPEC+ reporting points to patience on supply, which supports the front of the curve, but the market reaction suggests the signal was partly expected.</p><p><strong>AI interpretation:</strong> the evidence supports a range-within-tightness read, not a breakout call. Watch the dollar, freight and the next inventory print for confirmation.</p>',
      vi: '<p><strong>Ghi nhận:</strong> Brent ở <span class="calc">{brentVal} USD/bbl</span> ({brentPct}), WTI ở <span class="calc">{wtiVal} USD/bbl</span> ({wtiPct}). Chênh lệch Brent–WTI là <span class="calc">{spread} USD/bbl</span>, do dịch vụ phân tích tính toán.</p><p><strong>Bối cảnh:</strong> mức biến động khiêm tốn và lan tỏa trên cả hai chuẩn. Thông tin OPEC+ được trích dẫn cho thấy sự kiên nhẫn về nguồn cung, hỗ trợ phần đầu đường cong, nhưng phản ứng thị trường cho thấy tín hiệu đã được dự báo một phần.</p><p><strong>Diễn giải AI:</strong> bằng chứng nghiêng về nhận định đi ngang trong thế thắt chặt, không phải dự báo bứt phá. Theo dõi đồng USD, cước vận tải và số liệu tồn kho tiếp theo để xác nhận.</p>'
    },
    snapshot: {
      en: '<p><strong>Snapshot:</strong> Brent {brentVal} USD/bbl ({brentPct}), WTI {wtiVal} ({wtiPct}), gasoline crack {crackVal} USD/bbl ({crackPct}).</p><p><strong>What is driving it:</strong> supply patience from OPEC+ and elevated Red Sea freight are the main cited signals. Product cracks carry more of the narrative than crude flat price.</p><p><strong>Interpretation:</strong> the evidence is consistent with a tightening-supply bias, but it does not establish a large supply shock. Keep the watch list narrow and require confirmation from inventory and freight data.</p>',
      vi: '<p><strong>Tóm tắt:</strong> Brent {brentVal} USD/bbl ({brentPct}), WTI {wtiVal} ({wtiPct}), crack xăng {crackVal} USD/bbl ({crackPct}).</p><p><strong>Điều gì đang chi phối:</strong> sự kiên nhẫn nguồn cung từ OPEC+ và cước vận tải Biển Đỏ cao là các tín hiệu chính được trích dẫn. Crack sản phẩm chiếm phần lớn câu chuyện hơn là giá dầu thô.</p><p><strong>Diễn giải:</strong> bằng chứng nhất quán với xu hướng thắt chặt nguồn cung, nhưng chưa xác lập một cú sốc nguồn cung lớn. Giữ danh sách theo dõi hẹp và cần xác nhận từ dữ liệu tồn kho và cước vận tải.</p>'
    }
  };

  const ATTRS = ['title', 'aria-label', 'placeholder', 'alt', 'data-q'];
  const MONTHS = { Jan: '01', Feb: '02', Mar: '03', Apr: '04', May: '05', Jun: '06', Jul: '07', Aug: '08', Sep: '09', Oct: '10', Nov: '11', Dec: '12' };
  const MONTH_RE = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)';

  let lang = readLang();
  const listeners = [];

  function readLang() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === 'vi' || stored === 'en') return stored;
    } catch (e) { /* storage unavailable (file:// or private mode) */ }
    return DEFAULT_LANG;
  }

  function getLang() { return lang; }
  function isVi() { return lang === 'vi'; }

  function setLang(next) {
    if (next !== 'vi' && next !== 'en') return;
    lang = next;
    try { window.localStorage.setItem(STORAGE_KEY, next); } catch (e) { /* ignore */ }
    document.documentElement.lang = next;
    listeners.forEach((fn) => { try { fn(next); } catch (e) { /* keep other listeners alive */ } });
  }

  function onChange(fn) { listeners.push(fn); }

  function interpolate(template, vars) {
    if (!vars) return template;
    return template.replace(/\{(\w+)\}/g, (m, key) => (vars[key] == null ? m : String(vars[key])));
  }

  /* Translate a string built in JavaScript. The key is the English source. */
  function t(key, vars) {
    if (lang !== 'vi') return interpolate(key, vars);
    const template = tIn(key);
    return interpolate(template, vars);
  }

  /* Translate a long-form assistant answer from the AI catalog. */
  function ai(key, vars) {
    const entry = AI[key];
    if (!entry) return '';
    return interpolate(lang === 'vi' ? entry.vi : entry.en, vars);
  }

  function transformDates(text) {
    let out = text;
    out = out.replace(new RegExp('\\b(\\d{1,2})[–-](\\d{1,2}) ' + MONTH_RE + ' (\\d{4})\\b', 'g'),
      (m, a, b, mon, year) => a + '–' + b + '/' + MONTHS[mon] + '/' + year);
    out = out.replace(new RegExp('\\b(\\d{1,2}) ' + MONTH_RE + ' (\\d{4})\\b', 'g'),
      (m, day, mon, year) => day + '/' + MONTHS[mon] + '/' + year);
    out = out.replace(new RegExp('\\b(\\d{1,2}) ' + MONTH_RE + '\\b', 'g'),
      (m, day, mon) => day + '/' + MONTHS[mon]);
    out = out.replace(/\bQ([1-4]) (\d{4})\b/g, (m, q, year) => 'Quý ' + q + '/' + year);
    out = out.replace(new RegExp('\\b' + MONTH_RE + ' (\\d{4})\\b', 'g'),
      (m, mon, year) => MONTHS[mon] + '/' + year);
    return out;
  }

  function translate(text, depth) {
    if (lang !== 'vi' || depth > 3) return text;
    const trimmed = text.trim();
    if (!trimmed) return text;
    let out = VI[trimmed];
    if (out === undefined) {
      for (let i = 0; i < VI_PATTERNS.length; i++) {
        const rule = VI_PATTERNS[i];
        const match = rule[0].exec(trimmed);
        if (match) {
          out = typeof rule[1] === 'function' ? rule[1](match, depth) : trimmed.replace(rule[0], rule[1]);
          break;
        }
      }
    }
    if (out === undefined) out = transformDates(trimmed);
    if (out === trimmed) return text;
    const lead = text.match(/^\s*/)[0];
    const trail = text.match(/\s*$/)[0];
    return lead + out + trail;
  }

  const SKIP_TAGS = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1, SVG: 1, TITLE: 1 };

  /* Marks product chrome that the text pass may translate. User-authored text
     (chat questions, supplied headlines, uploaded file names) is never marked,
     so it is never rewritten. */
  const I18N_ATTR = 'data-i18n';

  function applyI18n(root) {
    if (!root || typeof root !== 'object') return;
    if (lang !== 'vi') return;
    const doc = root.ownerDocument || document;
    const walker = doc.createTreeWalker(root, 4 /* NodeFilter.SHOW_TEXT */, null);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const parent = node.parentNode;
      if (!parent || SKIP_TAGS[parent.nodeName]) return;
      if (parent.closest && parent.closest('[data-i18n-skip]')) return;
      const next = translate(node.nodeValue, 0);
      if (next !== node.nodeValue) node.nodeValue = next;
    });
    const elements = [root];
    if (root.querySelectorAll) Array.prototype.push.apply(elements, Array.from(root.querySelectorAll('*')));
    elements.forEach((el) => {
      if (!el.getAttribute) return;
      ATTRS.forEach((attr) => {
        const value = el.getAttribute(attr);
        if (!value) return;
        const next = translate(value, 0);
        if (next !== value) el.setAttribute(attr, next);
      });
    });
  }
  /* --- Bilingual product copy -------------------------------------------
     Rendered interfaces are translated by matching the English strings the
     templates emit, so a string that is not in VI is shown in English.
     These helpers translate product copy in JavaScript without that gap. */

  const CATALOG = {
    /* Shared metadata labels */
    'Product name': { vi: 'BSR Market Intelligence' },
    'Auker subtitle': { vi: 'Reasonary AI · Lớp trí tuệ Auker' },
    'Reasonary AI · Auker': { vi: 'Reasonary AI · Auker' },
    'Sign in': { vi: 'Đăng nhập' },
    'Status names': {
      vi: { 'Real-time': 'Thời gian thực', 'End-of-day': 'Cuối ngày', 'Delayed': 'Trễ', 'Manual': 'Thủ công', 'Valid': 'Hợp lệ', 'Pending': 'Chờ duyệt', 'Succeeded': 'Thành công', 'Fallback': 'Dự phòng', 'Passed': 'Đạt' }
    },
    'Quality states': { vi: { 'Valid': 'Hợp lệ', 'Pending': 'Chờ duyệt' } },
    'Classification names': { vi: { 'Public': 'Công khai', 'Internal': 'Nội bộ', 'Confidential': 'Bảo mật', 'Restricted': 'Hạn chế' } },
    'Price types': { vi: { 'Futures': 'Hợp đồng tương lai', 'Physical': 'Vật chất', 'Calculated': 'Tính toán', 'Index': 'Chỉ số', 'Exchange rate': 'Tỷ giá' } },
    'Price type': { vi: 'Loại giá' },
    'Market ticker': { vi: 'Mã thị trường' },
    'Not started': { vi: 'Chưa bắt đầu' },
    'No extension': { vi: 'không có phần mở rộng' },
    'No evaluated value': { vi: 'chưa có giá trị đánh giá' },
    'Not available': { vi: 'không có dữ liệu' },
    'Others': { vi: 'Khác' },
    'Session change suffix': { vi: 'so với phiên trước' },
    'Mkt short': { vi: 'TT' },
    'Version word': { vi: 'Phiên bản' },
    'Clear': { vi: 'Xóa' },
    'View': { vi: 'Xem' },
    'View data table': { vi: 'Xem bảng dữ liệu' },
    'Hide data table': { vi: 'Ẩn bảng dữ liệu' },
    'Toggle light/dark theme': { vi: 'Chuyển chế độ tối/sáng' },
    'Switch between light and dark theme': { vi: 'Chuyển giao diện sáng/tối' },
    'Display mode': { vi: 'Chế độ hiển thị' },
    'Light mode': { vi: 'Chế độ sáng' },
    'Dark mode': { vi: 'Chế độ tối' },
    'Open in Market Data': { vi: 'Mở trong Dữ liệu thị trường' },
    'Close chart': { vi: 'Đóng biểu đồ' },
    'Chart: {name}': { vi: 'Biểu đồ: {name}' },
    'Time range': { vi: 'Khoảng thời gian' },
    'Chart uses simulated data. Market time is when the price was recorded; ingestion time is when the platform received it.': { vi: 'Biểu đồ dùng dữ liệu mô phỏng. Thời điểm thị trường là lúc ghi nhận giá; thời điểm nạp là lúc nền tảng nhận dữ liệu.' }
  };

  function tIn(key, vars) {
    if (lang !== 'vi') return interpolate(key, vars);
    if (VI[key] !== undefined) return interpolate(VI[key], vars);
    const entry = CATALOG[key];
    if (entry && typeof entry.vi === 'string') return interpolate(entry.vi, vars);
    const patterned = translate(key, 0);
    if (patterned !== key) return interpolate(patterned, vars);
    return interpolate(key, vars);
  }

  const label = (value) => (lang === 'vi' && VI[value] !== undefined ? VI[value] : value);

  function instrument(i) {
    if (lang !== 'vi' || !i) return i;
    const out = Object.assign({}, i);
    ['name', 'short', 'group', 'priceType', 'dataStatus', 'quality', 'classification', 'description'].forEach((key) => {
      if (out[key] != null) out[key + '_label'] = label(out[key]);
    });
    if (out.formula) out.formula = Object.assign({}, out.formula, { rule_label: label(out.formula.rule) });
    return out;
  }

  function news(n) {
    if (lang !== 'vi' || !n) return n;
    const out = Object.assign({}, n);
    ['title', 'summary', 'original', 'insight', 'status', 'classification', 'source', 'coverage'].forEach((key) => {
      if (out[key] != null) out[key + '_label'] = label(out[key]);
    });
    out.topic_labels = (n.topics || []).map(label);
    out.entity_labels = (n.entities || []).map(label);
    return out;
  }

  function event(ev) {
    if (lang !== 'vi' || !ev) return ev;
    const out = Object.assign({}, ev);
    ['title', 'type', 'source'].forEach((key) => { if (out[key] != null) out[key + '_label'] = label(out[key]); });
    return out;
  }

  function forecast(f) {
    if (lang !== 'vi' || !f) return f;
    const out = Object.assign({}, f);
    ['source', 'instrumentLabel', 'period', 'horizon', 'methodology', 'classification'].forEach((key) => {
      if (out[key] != null) out[key + '_label'] = label(out[key]);
    });
    return out;
  }

  function report(r) {
    if (lang !== 'vi' || !r) return r;
    const out = Object.assign({}, r);
    ['type', 'title', 'range', 'status', 'classification'].forEach((key) => {
      if (out[key] != null) out[key + '_label'] = label(out[key]);
    });
    return out;
  }

  /* Display helper: `lb(obj, 'classification')` returns the translated label
     when present, otherwise the original value. */
  function lb(obj, key) {
    if (!obj) return '';
    const translated = obj[key + '_label'];
    return translated != null ? translated : obj[key];
  }

    /* Role labels: "Market Intelligence" is also the product name, so the role
     keeps its English `label` as the logic key and exposes `label_label` for
     display. */
  function localizeRole(role) {
    if (!role) return role;
    const out = Object.assign({}, role, { label_label: role.label, department_label: role.department });
    if (lang === 'vi') {
      out.label_label = role.label_vi || role.label;
      out.department_label = role.department_vi || role.department;
    }
    return out;
  }

  window.I18N = {
    LANGS: LANGS,
    DEFAULT_LANG: DEFAULT_LANG,
    getLang: getLang,
    setLang: setLang,
    onChange: onChange,
    isVi: isVi,
    t: t,
    ai: ai,
    translate: translate,
    applyI18n: applyI18n,
    localizeRole: localizeRole,
    lb: lb,
    instrument: instrument,
    news: news,
    event: event,
    forecast: forecast,
    report: report
  };
})();
