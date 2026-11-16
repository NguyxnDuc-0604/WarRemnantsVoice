import sys
import os
import sqlite3

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Tìm file db
db_paths = [
    os.path.join(os.path.dirname(__file__), "war_remnants_museum.db"),
    os.path.join(os.path.dirname(__file__), "services", "ai-pipeline-service", "war_remnants_museum.db")
]

db_path = None
for p in db_paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("[ERROR] Khong tim thay file co so du lieu war_remnants_museum.db!")
    sys.exit(1)

print("=" * 85)
print(f"  HE THONG CO SO DU LIEU BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH (PRD V1.0)")
print(f"  Duong dan Database: {db_path}")
print("=" * 85)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Lấy danh sách bảng
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cursor.fetchall()]

# Định nghĩa các bảng theo PRD
all_tables = [
    "supported_language",
    "exhibit",
    "content_source",
    "localization",
    "audio_media",
    "tour_route",
    "glossary",
    "listening_metric"
]

# 1. Hiển thị phần Ngôn ngữ khả dụng trước tiên (Đáp ứng yêu cầu của thầy)
if "supported_language" in tables:
    cursor.execute("SELECT code, name_vi, native_name, flag_icon, voice_code, is_active FROM supported_language ORDER BY sort_order ASC")
    langs = cursor.fetchall()
    print(f"\n🌐 DANH MỤC 15 NGÔN NGỮ KHẢ DỤNG TRONG DATABASE (BẢNG: supported_language):")
    print("-" * 85)
    print(f"  {'STT':<4} {'Mã':<6} {'Tên Tiếng Việt':<20} {'Tên Bản Địa':<20} {'Cờ':<5} {'Model Giọng Đọc (TTS)'}")
    print("-" * 85)
    for idx, (code, n_vi, n_nat, flag, voice, active) in enumerate(langs, 1):
        flag_str = flag if flag else ""
        print(f"  {idx:<4} {code:<6} {n_vi:<20} {n_nat:<20} {flag_str:<5} {voice}")
    print("-" * 85)

# 2. Thống kê số lượng bản dịch trong bảng localization
if "localization" in tables:
    cursor.execute("SELECT language_code, COUNT(*) FROM localization GROUP BY language_code ORDER BY COUNT(*) DESC")
    loc_stats = cursor.fetchall()
    cursor.execute("SELECT COUNT(DISTINCT exhibit_id) FROM localization")
    ex_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM localization")
    total_loc = cursor.fetchone()[0]
    print(f"\n📚 THỐNG KÊ BẢN DỊCH ĐÃ SỐ HÓA TRONG DATABASE (BẢNG: localization):")
    print(f"  - Tổng số bản dịch: {total_loc} bản ghi")
    print(f"  - Số hiện vật đã dịch: {ex_count} hiện vật")
    print(f"  - Các ngôn ngữ đã có dữ liệu bản dịch & phụ đề:")
    loc_details = [f"{code.upper()} ({cnt} bài)" for code, cnt in loc_stats]
    print(f"    {' | '.join(loc_details)}")

print(f"\n[+] TỔNG SỐ BẢNG HIỆN CÓ: {len(tables)} bảng")
print("=" * 85)

for tbl in all_tables:
    if tbl in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"PRAGMA table_info({tbl})")
        columns = cursor.fetchall()
        col_names = [f"{col[1]} ({col[2]})" for col in columns]
        
        print(f"\n* BẢNG: [{tbl.upper()}]  --  Số lượng bản ghi: {count}")
        print(f"  Các cột: {', '.join(col_names)}")
        
        # In mẫu vài dòng
        cursor.execute(f"SELECT * FROM {tbl} LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            print("  Dữ liệu mẫu (Top 3 bản ghi):")
            for idx, r in enumerate(rows, 1):
                short_r = [str(val)[:45] + "..." if isinstance(val, str) and len(str(val)) > 45 else str(val) for val in r]
                print(f"    [{idx}] {short_r}")
        else:
            print("    (Chưa có bản ghi - sẽ phát sinh khi khách nghe/dịch)")
    else:
        print(f"\n[!] BẢNG: [{tbl.upper()}] chưa được tạo trong SQLite!")

conn.close()
print("\n" + "=" * 85)
print("  HOÀN TẤT KIỂM TRA CƠ SỞ DỮ LIỆU!")
print("=" * 85)
