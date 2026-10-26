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
    print("[LỖI] Không tìm thấy file cơ sở dữ liệu war_remnants_museum.db!")
    input("Bấm Enter để thoát...")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("  🎖️ TRÌNH THỰC THI TRUY VẤN SQL BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH")
print(f"  Kết nối Database: {os.path.abspath(db_path)}")
print("=" * 80)
print("💡 GỢI Ý MỘT SỐ CÂU LỆNH MẪU:")
print(" 1. Xem 15 ngôn ngữ:")
print("    SELECT code, name_vi, native_name, flag_icon, voice_code FROM supported_language;")
print(" 2. Xem các ngôn ngữ đã được dịch trong DB:")
print("    SELECT language_code, COUNT(*) AS so_bai FROM localization GROUP BY language_code;")
print(" 3. Xem danh sách hiện vật:")
print("    SELECT code, title, room_id, content_version FROM exhibit;")
print(" 4. Xem từ điển lịch sử:")
print("    SELECT term_vi, term_en, context_note FROM glossary;")
print(" 5. Gõ 'tables' để xem danh sách tất cả các bảng.")
print(" 6. Gõ 'exit' hoặc 'quit' để thoát.")
print("=" * 80)

while True:
    try:
        query = input("\nSQL> ").strip()
        if not query:
            continue
        
        if query.lower() in ["exit", "quit", "q"]:
            print("Tạm biệt!")
            break

        if query.lower() == "tables":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cursor.fetchall()]
            print("Các bảng hiện có trong Database:", ", ".join(tables))
            continue

        cursor.execute(query)
        
        # Nếu là câu lệnh SELECT hoặc trả về dữ liệu
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            if not rows:
                print("-> Kết quả: 0 dòng (Bảng trống hoặc không khớp điều kiện).")
            else:
                # Tính độ rộng cột để in đẹp
                col_widths = [len(c) for c in columns]
                str_rows = []
                for row in rows:
                    str_row = []
                    for idx, val in enumerate(row):
                        s_val = str(val) if val is not None else "NULL"
                        if len(s_val) > 40:
                            s_val = s_val[:37] + "..."
                        str_row.append(s_val)
                        col_widths[idx] = max(col_widths[idx], len(s_val))
                    str_rows.append(str_row)
                
                # In header
                header_line = " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(columns))
                sep_line = "-+-".join("-" * col_widths[i] for i in range(len(columns)))
                print("\n" + header_line)
                print(sep_line)
                
                for r in str_rows:
                    print(" | ".join(r[i].ljust(col_widths[i]) for i in range(len(r))))
                print(f"\n-> Tổng cộng: {len(rows)} bản ghi.")
        else:
            conn.commit()
            print(f"-> Thực thi thành công! (Số dòng bị ảnh hưởng: {cursor.rowcount})")

    except KeyboardInterrupt:
        print("\nĐã thoát.")
        break
    except Exception as e:
        print(f"❌ LỖI SQL: {e}")

conn.close()
