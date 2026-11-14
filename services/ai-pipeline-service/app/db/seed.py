import uuid
from sqlalchemy.orm import Session
from app.db.models import (
    Exhibit,
    ContentSource,
    TourRoute,
    Glossary,
    SupportedLanguage,
    Localization,
    AudioMedia
)

def seed_database(db: Session):
    """
    Tự động khởi tạo dữ liệu mẫu chuẩn theo PRD (Bảo tàng Chứng tích Chiến tranh)
    nếu cơ sở dữ liệu chưa có dữ liệu.
    """
    # 1. Khởi tạo 15 Ngôn ngữ khả dụng (Supported Languages)
    if db.query(SupportedLanguage).count() == 0:
        print("[DB] Dang khoi tao danh muc 15 ngon ngu kha dung (Supported Languages)...")
        languages_data = [
            {"code": "vi", "name_vi": "Tiếng Việt", "native_name": "Tiếng Việt", "flag_icon": "🇻🇳", "voice_code": "vi-VN-HoaiMyNeural", "is_default": True, "sort_order": 1},
            {"code": "en", "name_vi": "Tiếng Anh", "native_name": "English", "flag_icon": "🇬🇧", "voice_code": "en-US-JennyNeural", "is_default": True, "sort_order": 2},
            {"code": "fr", "name_vi": "Tiếng Pháp", "native_name": "Français", "flag_icon": "🇫🇷", "voice_code": "fr-FR-DeniseNeural", "is_default": False, "sort_order": 3},
            {"code": "zh", "name_vi": "Tiếng Trung", "native_name": "中文", "flag_icon": "🇨🇳", "voice_code": "zh-CN-XiaoxiaoNeural", "is_default": False, "sort_order": 4},
            {"code": "ja", "name_vi": "Tiếng Nhật", "native_name": "日本語", "flag_icon": "🇯🇵", "voice_code": "ja-JP-NanamiNeural", "is_default": False, "sort_order": 5},
            {"code": "ko", "name_vi": "Tiếng Hàn", "native_name": "한국어", "flag_icon": "🇰🇷", "voice_code": "ko-KR-SunHiNeural", "is_default": False, "sort_order": 6},
            {"code": "es", "name_vi": "Tiếng Tây Ban Nha", "native_name": "Español", "flag_icon": "🇪🇸", "voice_code": "es-ES-ElviraNeural", "is_default": False, "sort_order": 7},
            {"code": "de", "name_vi": "Tiếng Đức", "native_name": "Deutsch", "flag_icon": "🇩🇪", "voice_code": "de-DE-KatjaNeural", "is_default": False, "sort_order": 8},
            {"code": "ru", "name_vi": "Tiếng Nga", "native_name": "Русский", "flag_icon": "🇷🇺", "voice_code": "ru-RU-SvetlanaNeural", "is_default": False, "sort_order": 9},
            {"code": "it", "name_vi": "Tiếng Ý", "native_name": "Italiano", "flag_icon": "🇮🇹", "voice_code": "it-IT-ElsaNeural", "is_default": False, "sort_order": 10},
            {"code": "th", "name_vi": "Tiếng Thái", "native_name": "ภาษาไทย", "flag_icon": "🇹🇭", "voice_code": "th-TH-PremwadeeNeural", "is_default": False, "sort_order": 11},
            {"code": "id", "name_vi": "Tiếng Indonesia", "native_name": "Bahasa Indonesia", "flag_icon": "🇮🇩", "voice_code": "id-ID-GadisNeural", "is_default": False, "sort_order": 12},
            {"code": "km", "name_vi": "Tiếng Khmer", "native_name": "ភាសាខ្មែរ", "flag_icon": "🇰🇭", "voice_code": "km-KH-PisethNeural", "is_default": False, "sort_order": 13},
            {"code": "lo", "name_vi": "Tiếng Lào", "native_name": "ພາສາລາວ", "flag_icon": "🇱🇦", "voice_code": "lo-LA-KeomanyNeural", "is_default": False, "sort_order": 14},
            {"code": "ar", "name_vi": "Tiếng Ả Rập", "native_name": "العربية", "flag_icon": "🇸🇦", "voice_code": "ar-SA-ZariyahNeural", "is_default": False, "sort_order": 15},
        ]
        for l in languages_data:
            db.add(SupportedLanguage(**l))
        db.commit()

    # 2. Khởi tạo Glossary nếu chưa có
    if db.query(Glossary).count() == 0:
        glossary_items = [
            Glossary(term_vi="Ấp Bắc", term_en="Ap Bac", context_note="Địa danh chiến dịch năm 1963"),
            Glossary(term_vi="Chiến dịch Hồ Chí Minh", term_en="Ho Chi Minh Campaign", context_note="Chiến dịch mùa Xuân 1975 giải phóng miền Nam"),
            Glossary(term_vi="Chứng tích chiến tranh", term_en="War Remnants", context_note="Tên chính thức của bảo tàng"),
            Glossary(term_vi="Mậu Thân 1968", term_en="Tet Offensive 1968", context_note="Cuộc Tổng tiến công và nổi dậy Xuân Mậu Thân"),
            Glossary(term_vi="Bảo tàng Chứng tích Chiến tranh", term_en="War Remnants Museum", context_note="Tên tổ chức"),
            Glossary(term_vi="Chuồng cọp", term_en="Tiger Cages", context_note="Hệ thống giam giữ đặc biệt tại nhà tù Côn Đảo"),
            Glossary(term_vi="Vua chiến trường", term_en="King of Battlefield", context_note="Biệt danh pháo tự hành M107 175mm"),
        ]
        db.add_all(glossary_items)
        db.commit()

    # 3. Khởi tạo Tuyến tham quan TourRoute nếu chưa có
    if db.query(TourRoute).count() == 0:
        tour_routes = [
            TourRoute(
                id="a0000000-0000-0000-0000-000000000001",
                title="Tuyến 1: Hiện vật ngoài trời & Phương tiện chiến tranh",
                description="Khám phá các loại máy bay, trực thăng và xe tăng chủ lực trong Chiến tranh Việt Nam được trưng bày tại sân ngoài trời.",
                ordered_exhibits_json=["UH1-BELL", "T54-390", "M107-175"],
                estimated_time=30,
                is_active=True
            ),
            TourRoute(
                id="a0000000-0000-0000-0000-000000000002",
                title="Tuyến 2: Chứng tích tội ác & Ký ức lịch sử",
                description="Tìm hiểu các chứng tích nhà tù, hậu quả chiến tranh và thắng lợi của Chiến dịch Hồ Chí Minh lịch sử.",
                ordered_exhibits_json=["CONDAO-CAGE", "HOCHIMINH-CAMPAIGN"],
                estimated_time=45,
                is_active=True
            )
        ]
        db.add_all(tour_routes)
        db.commit()

    # 4. Khởi tạo 5 hiện vật tiêu biểu
    if db.query(Exhibit).count() == 0:
        initial_exhibits = [
            {
                "id": "b0000000-0000-0000-0000-000000000001",
                "code": "UH1-BELL",
                "title": "Máy bay trực thăng UH-1 Iroquois 'Huey'",
                "title_en": "UH-1 Iroquois 'Huey' Helicopter",
                "room_id": "OUTDOOR",
                "zone": "Khu trưng bày ngoài trời",
                "period": "1962 - 1975",
                "latitude": 10.7794,
                "longitude": 106.6922,
                "radius": 15,
                "thumbnail_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80",
                "original_text": "Trực thăng UH-1 Iroquois, thường được gọi là 'Huey', là biểu tượng không quân của quân đội Mỹ trong Chiến tranh Việt Nam. Được sử dụng từ năm 1962 đến 1975 với các nhiệm vụ đổ quân chiến thuật, cứu thương và yểm trợ hoả lực. Chiếc máy bay trưng bày tại đây là một trong những chứng tích ghi lại các cuộc càn quét khốc liệt trên chiến trường miền Nam."
            },
            {
                "id": "b0000000-0000-0000-0000-000000000002",
                "code": "T54-390",
                "title": "Xe tăng T-54B số hiệu 390",
                "title_en": "T-54B Tank No. 390",
                "room_id": "OUTDOOR",
                "zone": "Sân trưng bày cơ giới ngoài trời",
                "period": "1975",
                "latitude": 10.7796,
                "longitude": 106.6925,
                "radius": 15,
                "thumbnail_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",
                "original_text": "Xe tăng T-54B số hiệu 390 thuộc Đại đội 4, Tiểu đoàn 1, Lữ đoàn Tăng - Thiết giáp 203. Vào lúc 10 giờ 45 phút ngày 30 tháng 4 năm 1975, chiếc xe tăng này đã húc đổ cổng chính Dinh Độc Lập, đánh dấu thời khắc giải phóng hoàn toàn miền Nam, thống nhất non sông."
            },
            {
                "id": "b0000000-0000-0000-0000-000000000003",
                "code": "M107-175",
                "title": "Pháo tự hành M107 175mm 'Vua chiến trường'",
                "title_en": "M107 175mm Self-Propelled Gun",
                "room_id": "OUTDOOR",
                "zone": "Khu trưng bày pháo binh ngoài trời",
                "period": "1968 - 1975",
                "latitude": 10.7792,
                "longitude": 106.6928,
                "radius": 15,
                "thumbnail_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
                "original_text": "Pháo tự hành hạng nặng M107 cỡ nòng 175mm từng được mệnh danh là 'Vua chiến trường' của quân đội Mỹ với tầm bắn tối đa lên tới hơn 32 km. Khẩu pháo này từng tham gia nhiều chiến dịch ác liệt tại Quảng Trị, Đường 9 Nam Lào và Đông Nam Bộ."
            },
            {
                "id": "b0000000-0000-0000-0000-000000000004",
                "code": "CONDAO-CAGE",
                "title": "Mô hình phục dựng Chuồng cọp Côn Đảo",
                "title_en": "Con Dao Tiger Cages Replica",
                "room_id": "ROOM-02",
                "zone": "Khu chứng tích tội ác chiến tranh",
                "period": "1940 - 1975",
                "latitude": None,
                "longitude": None,
                "radius": 10,
                "thumbnail_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=800&q=80",
                "original_text": "Chuồng cọp Côn Đảo là hệ thống giam giữ bí mật đặc biệt khắc nghiệt do chính quyền thực dân và tay sai xây dựng nhằm đày ải, tra tấn tinh thần và thể xác các chiến sĩ yêu nước. Không gian ngột ngạt, xiềng xích và vôi bột rải từ trên cao thể hiện tội ác tột cùng nhưng cũng là biểu tượng sáng ngời của ý chí bất khuất."
            },
            {
                "id": "b0000000-0000-0000-0000-000000000005",
                "code": "HOCHIMINH-CAMPAIGN",
                "title": "Sa bàn Chiến dịch Hồ Chí Minh lịch sử",
                "title_en": "Historical Ho Chi Minh Campaign Diorama",
                "room_id": "ROOM-03",
                "zone": "Phòng trưng bày lịch sử tổng hợp",
                "period": "Tháng 4/1975",
                "latitude": None,
                "longitude": None,
                "radius": 10,
                "thumbnail_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
                "original_text": "Chiến dịch Hồ Chí Minh diễn ra từ ngày 26 đến 30 tháng 4 năm 1975 là chiến dịch quyết chiến chiến lược lớn nhất trong lịch sử dân tộc. Bằng 5 cánh quân tiến công thần tốc, quân và dân ta đã đập tan bộ máy chiến tranh đầu não, giải phóng Sài Gòn và non sông thu về một mối."
            }
        ]

        for item in initial_exhibits:
            ex = Exhibit(
                id=item["id"],
                code=item["code"],
                title=item["title"],
                title_en=item["title_en"],
                room_id=item["room_id"],
                zone=item["zone"],
                period=item["period"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                radius=item["radius"],
                thumbnail_url=item["thumbnail_url"],
                content_version=1,
                is_published=True,
                is_active=True
            )
            cs = ContentSource(
                exhibit_id=item["id"],
                original_text=item["original_text"],
                content_version=1
            )
            db.add(ex)
            db.add(cs)
        db.commit()

    # 5. Khởi tạo Bản dịch Đa ngôn ngữ (Localization) và Tệp âm thanh (AudioMedia)
    if db.query(Localization).count() == 0:
        print("[DB] Dang khoi tao cac ban dich da ngon ngu (Localization) va AudioMedia...")
        
        # Danh mục bản dịch chuẩn bị sẵn cho các hiện vật tiêu biểu
        multilingual_seeds = [
            # UH-1 Iroquois
            {
                "exhibit_id": "b0000000-0000-0000-0000-000000000001",
                "exhibit_code": "UH1-BELL",
                "translations": [
                    {
                        "lang": "en",
                        "title": "UH-1 Iroquois 'Huey' Helicopter",
                        "text": "The UH-1 Iroquois helicopter, commonly known as the 'Huey', is an aviation icon of the U.S. military during the Vietnam War. Used from 1962 to 1975 for tactical troop transport, medical evacuation, and close air support. The aircraft displayed here is one of the historic remnants documenting fierce sweeps across the southern battlefields.",
                        "duration": 22.5
                    },
                    {
                        "lang": "fr",
                        "title": "Hélicoptère UH-1 Iroquois 'Huey'",
                        "text": "L'hélicoptère UH-1 Iroquois, communément appelé 'Huey', est une icône de l'aviation militaire américaine pendant la guerre du Vietnam. Utilisé de 1962 à 1975 pour le transport tactique de troupes, les évacuations sanitaires et l'appui aérien. L'appareil exposé ici témoigne des violentes opérations militaires menées dans le Sud.",
                        "duration": 24.0
                    },
                    {
                        "lang": "zh",
                        "title": "UH-1“易洛魁”休伊直升机",
                        "text": "UH-1“易洛魁”直升机，通常被称为“休伊”（Huey），是越南战争期间美军空中力量的标志。它在1962年至1975年间服役，主要执行战术运兵、战场医疗救援和空中火力支援任务。此处展出的这架直升机是记录南部战场激烈扫荡的历史见证。",
                        "duration": 20.0
                    },
                    {
                        "lang": "ja",
                        "title": "UH-1 イロコイ 'ヒューイ' ヘリコプター",
                        "text": "UH-1イロコイヘリコプター（通称「ヒューイ」）は、ベトナム戦争における米軍航空戦力の象徴です。1962年から1975年まで戦術的な兵員輸送、救護、火力支援に投入されました。ここに展示されている機体は、南部戦線における激戦の歴史を物語る貴重な証拠です。",
                        "duration": 21.0
                    },
                    {
                        "lang": "ko",
                        "title": "UH-1 이로쿼이 '휴이' 헬리콥터",
                        "text": "UH-1 이로쿼이(Iroquois) 헬리콥터는 일명 '휴이(Huey)'로 널리 알려진 베트남 전쟁 당시 미군의 상징적인 항공기입니다. 1962년부터 1975년까지 전술 병력 수송, 의무 후송, 화력 지원 임무에 투입되었습니다. 이곳에 전시된 기체는 치열했던 남부 전장의 역사를 증언하는 중요한 유물입니다.",
                        "duration": 23.0
                    },
                    {
                        "lang": "es",
                        "title": "Helicóptero UH-1 Iroquois 'Huey'",
                        "text": "El helicóptero UH-1 Iroquois, comúnmente apodado 'Huey', es un emblema de la aviación del ejército estadounidense durante la Guerra de Vietnam. Utilizado entre 1962 y 1975 para el transporte táctico de tropas, evacuación médica y apoyo aéreo. El ejemplar exhibido es testimonio de los duros combates en el sur.",
                        "duration": 22.0
                    },
                    {
                        "lang": "de",
                        "title": "UH-1 Iroquois 'Huey' Hubschrauber",
                        "text": "Der Hubschrauber UH-1 Iroquois, allgemein als 'Huey' bekannt, ist das bekannteste Luftfahrzeugsymbol der US-Streitkräfte im Vietnamkrieg. Eingesetzt von 1962 bis 1975 für taktische Truppentransporte, Verwundetentransporte und Luftnahunterstützung. Die hier ausgestellte Maschine ist ein historisches Zeugnis jener Kämpfe.",
                        "duration": 23.5
                    },
                    {
                        "lang": "ru",
                        "title": "Вертолёт UH-1 Iroquois 'Хьюи'",
                        "text": "Вертолёт UH-1 Iroquois, широко известный как 'Хьюи' (Huey), стал символом военной авиации США во время войны во Вьетнаме. Использовался с 1962 по 1975 год для тактической переброски десанта, медицинской эвакуации и огневой поддержки. Представленный здесь борт — одно из свидетельств ожесточённых боёв на юге страны.",
                        "duration": 24.5
                    }
                ]
            },
            # T-54B Tank 390
            {
                "exhibit_id": "b0000000-0000-0000-0000-000000000002",
                "exhibit_code": "T54-390",
                "translations": [
                    {
                        "lang": "en",
                        "title": "T-54B Tank No. 390",
                        "text": "T-54B Tank No. 390 belonged to Company 4, Battalion 1, Armored Brigade 203. At 10:45 AM on April 30, 1975, this tank crashed through the main gates of the Independence Palace, marking the historic moment of the complete liberation of South Vietnam and national reunification.",
                        "duration": 18.0
                    },
                    {
                        "lang": "fr",
                        "title": "Char T-54B numéro 390",
                        "text": "Le char T-54B numéro 390 appartenait à la 4e compagnie, 1er bataillon, 203e brigade blindée. À 10h45 le 30 avril 1975, ce char a enfoncé les grilles principales du Palais de l'Indépendance, marquant la libération totale du Sud et la réunification nationale.",
                        "duration": 19.5
                    },
                    {
                        "lang": "zh",
                        "title": "390号T-54B坦克",
                        "text": "390号T-54B坦克隶属于第203装甲旅第1营第4连。1975年4月30日上午10点45分，正是这辆坦克撞开了独立宫正门，标志着越南南方彻底解放、国家实现完全统一的历史性时刻。",
                        "duration": 17.0
                    },
                    {
                        "lang": "ja",
                        "title": "390号車 T-54B戦車",
                        "text": "390号車T-54B戦車は、第203機甲旅団第1大隊第4中隊に所属していました。1975年4月30日午前10時45分、この戦車は独立宮殿の正門を突破し、南部完全解放と祖国統一の歴史的瞬間を刻みました。",
                        "duration": 18.5
                    },
                    {
                        "lang": "ko",
                        "title": "390호 T-54B 전차",
                        "text": "390호 T-54B 전차는 제203기갑여단 제1대대 제4중대 소속이었습니다. 1975년 4월 30일 오전 10시 45분, 이 전차가 독립궁 정문을 들이받고 진입함으로써 베트남 남부의 완전한 해방과 조국 통일의 역사적 순간을 알렸습니다.",
                        "duration": 19.0
                    },
                    {
                        "lang": "es",
                        "title": "Tanque T-54B número 390",
                        "text": "El tanque T-54B número 390 perteneció a la 4ª Compañía, 1er Batallón, 203ª Brigada Blindada. A las 10:45 horas del 30 de abril de 1975, este tanque derribó la puerta principal del Palacio de la Independencia, marcando el momento histórico de la reunificación de Vietnam.",
                        "duration": 18.5
                    }
                ]
            },
            # M107 175mm
            {
                "exhibit_id": "b0000000-0000-0000-0000-000000000003",
                "exhibit_code": "M107-175",
                "translations": [
                    {
                        "lang": "en",
                        "title": "M107 175mm Self-Propelled Gun",
                        "text": "The M107 175mm heavy self-propelled gun was once dubbed the 'King of the Battlefield' by the U.S. military with a maximum firing range of over 32 km. This artillery piece participated in many fierce campaigns in Quang Tri, Route 9 Southern Laos, and the Southeast region.",
                        "duration": 19.0
                    },
                    {
                        "lang": "fr",
                        "title": "Canon automoteur M107 175mm",
                        "text": "Le canon automoteur lourd M107 de 175 mm était surnommé le 'Roi du champ de bataille' par l'armée américaine, avec une portée maximale de plus de 32 km. Cette pièce d'artillerie a participé à de nombreuses batailles intenses à Quang Tri et sur la Route 9.",
                        "duration": 20.0
                    },
                    {
                        "lang": "zh",
                        "title": "M107 175毫米自行火炮“战场之王”",
                        "text": "M107型175毫米重型自行火炮曾被美军誉为“战场之王”，其最大射程超过32公里。该门火炮曾参与广治省、9号公路及东南部地区的多次激烈战役。",
                        "duration": 18.0
                    },
                    {
                        "lang": "ja",
                        "title": "M107 175mm 自走カノン砲 '戦場の王'",
                        "text": "175mm重自走砲M107は、最大射程32km以上を誇り、かつて米軍から「戦場の王」と称されました。この砲はクアンチやラオス南部9号線での激戦に投入されました。",
                        "duration": 19.0
                    }
                ]
            },
            # Con Dao Tiger Cages
            {
                "exhibit_id": "b0000000-0000-0000-0000-000000000004",
                "exhibit_code": "CONDAO-CAGE",
                "translations": [
                    {
                        "lang": "en",
                        "title": "Con Dao Tiger Cages Replica",
                        "text": "The Con Dao Tiger Cages were a secret, exceptionally harsh detention system built by colonial and puppet regimes to torture patriotic revolutionary fighters. The cramped cells, chains, and lime powder thrown from above reflect wartime cruelty and the indomitable spirit of prisoners.",
                        "duration": 21.0
                    },
                    {
                        "lang": "fr",
                        "title": "Reconstitution des cages de tigre de Con Dao",
                        "text": "Les cages de tigre de Con Dao constituaient un système de détention secret et impitoyable conçu pour briser les patriotes révolutionnaires vietnamiens. L'espace confiné et la chaux vive jetée du haut des grilles témoignent de la cruauté carcérale et du courage des détenus.",
                        "duration": 22.0
                    },
                    {
                        "lang": "zh",
                        "title": "昆仑岛虎笼复原模型",
                        "text": "昆仑岛“虎笼”是殖民当局设立的极其残酷的秘密监禁系统，用于折磨爱国志士。狭窄的空间、铁链以及从上方倾倒的生石灰，展现了战争罪行以及被捕革命战士不屈不挠的意志。",
                        "duration": 19.0
                    },
                    {
                        "lang": "ja",
                        "title": "コンダオ島「虎の檻」再現模型",
                        "text": "コンダオ刑務所の「虎の檻」は、愛国的な革命戦士を収容・拷問するために作られた極めて過酷な秘密牢獄です。狭小な独房や上から浴びせられた生石灰は、当時の残虐性と不屈の精神を今に伝えています。",
                        "duration": 20.0
                    }
                ]
            },
            # Ho Chi Minh Campaign Diorama
            {
                "exhibit_id": "b0000000-0000-0000-0000-000000000005",
                "exhibit_code": "HOCHIMINH-CAMPAIGN",
                "translations": [
                    {
                        "lang": "en",
                        "title": "Historical Ho Chi Minh Campaign Diorama",
                        "text": "The Ho Chi Minh Campaign from April 26 to April 30, 1975, was the largest strategic battle in Vietnamese modern history. Advancing along five rapid spearheads, our armed forces shattered the puppet government's apparatus, liberating Saigon and reunifying the fatherland.",
                        "duration": 20.0
                    },
                    {
                        "lang": "fr",
                        "title": "Diorama de la Campagne Ho Chi Minh",
                        "text": "La campagne Ho Chi Minh, menée du 26 au 30 avril 1975, fut la plus grande bataille stratégique de l'histoire moderne du pays. Grâce à cinq colonnes d'assaut foudroyantes, Saigon fut libérée, marquant la réunification complète du Vietnam.",
                        "duration": 21.0
                    },
                    {
                        "lang": "zh",
                        "title": "历史性胡志明战役沙盘",
                        "text": "1975年4月26日至30日展开的胡志明战役是越南民族历史上规模最大的战略决战。凭借五路大军神速挺进，彻底粉碎了敌军核心指挥机构，解放西贡，实现祖国统一。",
                        "duration": 18.0
                    },
                    {
                        "lang": "ja",
                        "title": "歴史的ホーチミン作戦ジオラマ",
                        "text": "1975年4月26日から30日にかけて展開されたホーチミン作戦は、民族史上最大の戦略的決戦でした。5つの進撃部隊が電撃的に進撃し、サイゴンを完全解放して祖国統一を達成しました。",
                        "duration": 19.0
                    }
                ]
            }
        ]

        for item in multilingual_seeds:
            for trans in item["translations"]:
                loc_id = str(uuid.uuid4())
                
                # Tạo timestamps giả lập đồng bộ
                words = trans["text"].split(". ")
                timestamps = []
                cur_t = 0.0
                step = round(trans["duration"] / max(len(words), 1), 2)
                for w_idx, w in enumerate(words):
                    end_t = round(cur_t + step, 2)
                    timestamps.append({
                        "id": w_idx,
                        "start": cur_t,
                        "end": end_t,
                        "text": w.strip() + ("." if not w.endswith(".") else "")
                    })
                    cur_t = end_t

                loc = Localization(
                    id=loc_id,
                    exhibit_id=item["exhibit_id"],
                    language_code=trans["lang"],
                    translated_title=trans["title"],
                    translated_text=trans["text"],
                    timestamps_json=timestamps,
                    content_version=1,
                    is_reviewed=True
                )
                db.add(loc)

                audio = AudioMedia(
                    id=str(uuid.uuid4()),
                    localization_id=loc_id,
                    file_url=f"/output/{item['exhibit_code']}/{item['exhibit_code']}_{trans['lang']}.mp3",
                    storage_path=f"./output/{item['exhibit_code']}/{item['exhibit_code']}_{trans['lang']}.mp3",
                    duration_seconds=trans["duration"],
                    bitrate_kbps=128,
                    voice_code=f"{trans['lang']}-Neural",
                    status="ready"
                )
                db.add(audio)

        db.commit()

    print("[DB] Khoi tao co so du lieu hoan tat day du 7 bang va 15 ngon ngu!")
