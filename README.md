# Project Connect Four

Project Connect Four được xây dựng bằng **Python** và **Pygame CE**, mô phỏng trò chơi thả cờ quen thuộc với giao diện trực quan, dễ sử dụng và có tích hợp AI ở nhiều mức độ.

## Giới thiệu

**Connect Four** là trò chơi chiến thuật dành cho 2 người chơi.  
Mục tiêu là tạo được **4 quân cờ liên tiếp** theo một trong các hướng sau:

- Ngang
- Dọc
- Chéo chính
- Chéo phụ

Trong project này, người chơi có thể tương tác thông qua giao diện đồ họa, lựa chọn mức độ khó và thi đấu với AI được xây dựng trong chương trình.

## Chức năng chính

- Giao diện trang chủ trực quan
- Chọn mức độ chơi với AI
- Chơi game Connect Four trên giao diện đồ họa
- Xử lý thao tác thả quân theo từng cột
- Kiểm tra điều kiện thắng / hòa
- AI tự động tính toán nước đi
- Chuyển đổi giữa các màn hình trong game
- Hỗ trợ âm thanh trong quá trình chơi

## Các mức độ chơi

Project hiện hỗ trợ các mức độ chơi với AI như:

- **Easy**
- **Medium**
- **Hard**

Tùy theo cấu hình trong chương trình, AI sẽ có chiến lược và thời gian phản hồi khác nhau ở từng mức độ.

## Cấu trúc thư mục

```text
BTL_Connect4/
│
├── .venv/                    # Môi trường ảo Python
├── components/               # Các thành phần giao diện
│   ├── board_view.py
│   ├── button.py
│   └── setting_icon.py
│
├── core/                     # Xử lý logic chính của game
│   ├── AI.py
│   ├── board.py
│   └── rule_checker.py
│
├── screens/                  # Các màn hình giao diện
│   ├── game_page.py
│   ├── home_page.py
│   └── mode_select_page.py
│
├── config.py                 # Cấu hình chung
├── fragments.mp3             # File âm thanh
├── main.py                   # File chạy chính
├── requirements.txt          # Danh sách thư viện cần cài
├── settings.json             # File cấu hình game
└── test.py                   # File test
```
## Hướng dẫn cài đặt và chạy Project
1. Clone project từ GitHub
git clone https://github.com/DieuLinh245/Project_ConnectFour.git
2. Di chuyển vào thư mục project
cd Project_ConnectFour
3. Tạo môi trường ảo
python -m venv .venv
4. Kích hoạt môi trường ảo
Trên Windows: .venv\Scripts\activate
Trên macOS / Linux: source .venv/bin/activate
5. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
6. Chạy chương trình
python main.py

## Cách sử dụng
1. Mở chương trình
2. Tại giao diện trang chủ, chọn bắt đầu chơi
3. Chọn mức độ chơi mong muốn
4. Thả quân vào cột muốn đánh
5. Tiếp tục chơi cho đến khi có kết quả thắng, thua hoặc hòa

## Mô tả các file chính
main.py
Là file khởi chạy chính của chương trình, dùng để tạo cửa sổ game và điều hướng giữa các màn hình.
core/AI.py
Xử lý logic AI, lựa chọn nước đi cho máy theo từng mức độ khó.
core/board.py
Quản lý dữ liệu bàn cờ và trạng thái các ô.
core/rule_checker.py
Kiểm tra điều kiện thắng, hòa và các luật của trò chơi.
screens/home_page.py
Xây dựng giao diện trang chủ.
screens/mode_select_page.py
Xây dựng giao diện chọn mức độ chơi.
screens/game_page.py
Hiển thị giao diện bàn cờ và xử lý tương tác chính trong game.

## Yêu cầu hệ thống
Python 3.12 trở lên
pip
Hệ điều hành Windows / macOS / Linux

## Thành viên thực hiện
1. Tạ Bách Đạt
2. Nguyễn Diệu Linh
3. Lê Nhật Long
