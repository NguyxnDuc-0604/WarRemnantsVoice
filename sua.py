import sqlite3

# Kết nối đến file database của dự án
conn = sqlite3.connect("war_remnants_museum.db")
cursor = conn.cursor()

# Thực thi câu lệnh update
cursor.execute(
    """
    UPDATE exhibit
    SET thumbnail_url = 'https://infonet.vietnamnet.vn/can-canh-truc-thang-huyen-thoai-uh-1-cua-my-tai-viet-nam-221151.html'
    WHERE id = 'b0000000-0000-0000-0000-000000000001';
"""
)

# Lưu thay đổi vào file db
conn.commit()
conn.close()

print("Đã cập nhật link ảnh thành công!")