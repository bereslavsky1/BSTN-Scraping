import cloudscraper
from bs4 import BeautifulSoup
import json
import sqlite3
import time
import os
import re
import random

# Settings
DB_NAME = "bstn_products.db"
BASE_IMG_FOLDER = "product_images"

# Headers for browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Translate words
TRANSLATIONS = {
    'en': {
        'Men': 'Men', 'Women': 'Women', 'Unisex': 'Unisex', 'Kids': 'Kids',
        'Shoe Care': 'Shoe Care', 'Socks': 'Socks', 'Headwear': 'Headwear',
        'Bags / Backpacks': 'Bags / Backpacks', 'Accessories (Other)': 'Accessories (Other)',
        'Sneakers': 'Sneakers', 'Boots': 'Boots', 'Slides / Sandals': 'Slides / Sandals',
        'Footwear (Other)': 'Footwear (Other)', 'T-Shirts': 'T-Shirts', 'Hoodies': 'Hoodies',
        'Sweaters / Sweatshirts': 'Sweaters / Sweatshirts', 'Jackets': 'Jackets',
        'Jeans': 'Jeans', 'Pants': 'Pants', 'Shorts': 'Shorts', 'Other': 'Other',
        'lbl_type': 'Type', 'lbl_gender': 'Gender', 'lbl_link': 'Link'
    },
    'ru': {
        'Men': 'Мужское', 'Women': 'Женское', 'Unisex': 'Унисекс', 'Kids': 'Детское',
        'Shoe Care': 'Уход за обувью', 'Socks': 'Носки', 'Headwear': 'Головные уборы',
        'Bags / Backpacks': 'Сумки / Рюкзаки', 'Accessories (Other)': 'Аксессуары (Другое)',
        'Sneakers': 'Кроссовки', 'Boots': 'Ботинки', 'Slides / Sandals': 'Сланцы / Сандалии',
        'Footwear (Other)': 'Обувь (Другое)', 'T-Shirts': 'Футболки', 'Hoodies': 'Худи',
        'Sweaters / Sweatshirts': 'Свитера / Свитшоты', 'Jackets': 'Куртки',
        'Jeans': 'Джинсы', 'Pants': 'Штаны', 'Shorts': 'Шорты', 'Other': 'Другое',
        'lbl_type': 'Тип', 'lbl_gender': 'Пол', 'lbl_link': 'Ссылка'
    },
    'de': {
        'Men': 'Herren', 'Women': 'Damen', 'Unisex': 'Unisex', 'Kids': 'Kinder',
        'Shoe Care': 'Schuhpflege', 'Socks': 'Socken', 'Headwear': 'Kopfbedeckung',
        'Bags / Backpacks': 'Taschen / Rucksäcke', 'Accessories (Other)': 'Accessoires (Sonstige)',
        'Sneakers': 'Sneaker', 'Boots': 'Stiefel', 'Slides / Sandals': 'Sandalen / Badeschuhe',
        'Footwear (Other)': 'Schuhe (Sonstige)', 'T-Shirts': 'T-Shirts', 'Hoodies': 'Hoodies',
        'Sweaters / Sweatshirts': 'Pullover / Sweatshirts', 'Jackets': 'Jacken',
        'Jeans': 'Jeans', 'Pants': 'Hosen', 'Shorts': 'Shorts', 'Other': 'Sonstiges',
        'lbl_type': 'Typ', 'lbl_gender': 'Geschlecht', 'lbl_link': 'Link'
    }
}

# UI texts
UI = {
    'en': {
        'init': '🚀 System start...',
        'db_ready': '🗄 DB ready. Path: {}',
        'map_main': '🗺️ Open main map: ',
        'map_list': '📑 Read list: ',
        'found_maps': '✅ Found {} lists. Mode: {}. Press Ctrl+C to stop',
        'open_list': '\n📂 Open list [{}/{}]: {}',
        'skip': '⏩ Skip: "{}"',
        'test_done': '\n🛑 TEST DONE.',
        'pause_5': '\n♻️ 5 items done. Left in list: {}.',
        'pause_list': '\n🏁 List [{}/{}] done!',
        'action_prompt': 'Choose:\n  1 - Continue THIS list\n  2 - Parse ALL (non-stop)\n  3 - Exit',
        'choice': 'Choice (1/2/3): ',
        'cont_list': '▶️ Continue list...\n',
        'cont_all': '▶️ Parse ALL!\n',
        'stop_user': '🛑 Stopped by user.',
        'stop_ctrlc': '\n🛑 Stopped by Ctrl+C!',
        'close_db': '🗄 DB closed safely.',
        'select_mode': 'Select Mode:',
        'mode_1': '1 - TEST (1 Item)',
        'mode_2': '2 - FULL PARSE',
        'mode_prompt': 'Mode (1/2): ',
        'mode_error': '❌ Error: Enter 1 or 2.',
        'exit_prompt': 'Press Enter to exit...',
        'err_server': '⚠️ Server error: {}. Wait 10s...',
        'err_timeout_list': '⏳ Timeout list. Wait 15s...',
        'err_cf_ban': '🛑 Block (Code {})! Sleep {}m {}s... (Attempt {}/3)',
        'err_conn': '⏳ Connect error: {}',
        'err_sleep': '   Sleep {}m {}s... (Attempt {}/3)',
        'err_skip': '❌ Skip item.',
        'err_critical': '\n❌ CRITICAL ERROR: {}',
        'err_folder': '⚠️ Error creating folder: {}. Skipping item.'
    },
    'ru': {
        'init': '🚀 Запуск...',
        'db_ready': '🗄 БД готова: {}',
        'map_main': '🗺️ Открываю карту: ',
        'map_list': '📑 Читаю список: ',
        'found_maps': '✅ Найдено {} списков. Режим: {}. Ctrl+C для стопа',
        'open_list': '\n📂 Открываю список [{}/{}]: {}',
        'skip': '⏩ Пропуск: "{}"',
        'test_done': '\n🛑 ТЕСТ ЗАВЕРШЕН.',
        'pause_5': '\n♻️ 5 товаров готово. Осталось в списке: {}.',
        'pause_list': '\n🏁 Список [{}/{}] готов!',
        'action_prompt': 'Выбор:\n  1 - Только ЭТОТ список\n  2 - ВЕСЬ сайт (нон-стоп)\n  3 - Выход',
        'choice': 'Выбор (1/2/3): ',
        'cont_list': '▶️ Продолжаем список...\n',
        'cont_all': '▶️ Парсим всё!\n',
        'stop_user': '🛑 Остановлено.',
        'stop_ctrlc': '\n🛑 Экстренный стоп (Ctrl+C)!',
        'close_db': '🗄 БД закрыта.',
        'select_mode': 'Выберите режим:',
        'mode_1': '1 - ТЕСТ (1 товар)',
        'mode_2': '2 - ПОЛНЫЙ ПАРСИНГ',
        'mode_prompt': 'Режим (1/2): ',
        'mode_error': '❌ Ошибка: Введите 1 или 2.',
        'exit_prompt': 'Нажми Enter для выхода...',
        'err_server': '⚠️ Ошибка сервера: {}. Ждем 10с...',
        'err_timeout_list': '⏳ Таймаут. Ждем 15с...',
        'err_cf_ban': '🛑 Блок (Код {})! Спим {}м {}с... (Попытка {}/3)',
        'err_conn': '⏳ Ошибка: {}',
        'err_sleep': '   Спим {}м {}с... (Попытка {}/3)',
        'err_skip': '❌ Товар пропущен.',
        'err_critical': '\n❌ КРИТИЧЕСКАЯ ОШИБКА: {}',
        'err_folder': '⚠️ Ошибка создания папки: {}. Пропуск товара.'
    },
    'de': {
        'init': '🚀 Start...',
        'db_ready': '🗄 DB bereit: {}',
        'map_main': '🗺️ Öffne Hauptkarte: ',
        'map_list': '📑 Lese Liste: ',
        'found_maps': '✅ {} Listen gefunden. Modus: {}. Strg+C für Stopp',
        'open_list': '\n📂 Öffne Liste [{}/{}]: {}',
        'skip': '⏩ Überspringe: "{}"',
        'test_done': '\n🛑 TEST FERTIG.',
        'pause_5': '\n♻️ 5 Artikel fertig. Rest in Liste: {}.',
        'pause_list': '\n🏁 Liste [{}/{}] fertig!',
        'action_prompt': 'Wahl:\n  1 - Nur DIESE Liste\n  2 - ALLES parsen (Non-Stop)\n  3 - Ende',
        'choice': 'Wahl (1/2/3): ',
        'cont_list': '▶️ Liste fortsetzen...\n',
        'cont_all': '▶️ Alles parsen!\n',
        'stop_user': '🛑 Gestoppt.',
        'stop_ctrlc': '\n🛑 Strg+C Stopp!',
        'close_db': '🗄 DB geschlossen.',
        'select_mode': 'Modus wählen:',
        'mode_1': '1 - TEST (1 Artikel)',
        'mode_2': '2 - VOLLSTÄNDIG',
        'mode_prompt': 'Modus (1/2): ',
        'mode_error': '❌ Fehler: 1 oder 2 eingeben.',
        'exit_prompt': 'Enter drücken...',
        'err_server': '⚠️ Serverfehler: {}. 10s warten...',
        'err_timeout_list': '⏳ Timeout. 15s warten...',
        'err_cf_ban': '🛑 Blockiert (Code {})! Schlafe {}m {}s... (Versuch {}/3)',
        'err_conn': '⏳ Fehler: {}',
        'err_sleep': '   Schlafe {}m {}s... (Versuch {}/3)',
        'err_skip': '❌ Artikel übersprungen.',
        'err_critical': '\n❌ KRITISCHER FEHLER: {}',
        'err_folder': '⚠️ Fehler beim Erstellen des Ordners: {}. Artikel übersprungen.'
    }
}


def init_system(lang):
    # Make folder
    if not os.path.exists(BASE_IMG_FOLDER):
        os.makedirs(BASE_IMG_FOLDER)

    # Create DB table
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       unique_id TEXT UNIQUE,
                       gender TEXT,
                       item_type TEXT,
                       category TEXT,
                       brand TEXT,
                       name TEXT,
                       color TEXT,
                       price TEXT,
                       description TEXT,
                       sizes TEXT,
                       is_available INTEGER,
                       url TEXT UNIQUE,
                       folder_path TEXT,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )
                   ''')
    conn.commit()
    conn.close()

    db_path = os.path.abspath(DB_NAME)
    print(UI[lang]['db_ready'].format(db_path))


def analyze_item_type(category, name, table_gender=None):
    cat_lower = category.lower()
    name_lower = name.lower()

    # Find gender
    has_men = re.search(r'\b(men|mens|herren)\b', name_lower) or re.search(r'\b(men|mens|herren)\b', cat_lower)
    has_women = re.search(r'\b(wmns|women|womens|damen)\b', name_lower) or re.search(r'\b(women|damen)\b', cat_lower)
    has_unisex = re.search(r'\bunisex\b', name_lower) or re.search(r'\bunisex\b', cat_lower)
    has_kids = re.search(r'\b(kids|kinder|gs|ps|td|infant|toddler)\b', name_lower) or re.search(r'\b(kids|kinder)\b',
                                                                                                cat_lower)

    if table_gender:
        gender = table_gender
    elif has_unisex or (has_men and has_women):
        gender = "Unisex"
    elif has_kids:
        gender = "Kids"
    elif has_women:
        gender = "Women"
    elif has_men:
        gender = "Men"
    else:
        gender = "Unisex"

    # Find type
    item_type = "Other"
    if "care" in cat_lower or "cleaning" in name_lower or "cleaner" in name_lower or "kit" in name_lower:
        item_type = "Shoe Care"
    elif "socks" in cat_lower or "socks" in name_lower:
        item_type = "Socks"
    elif "caps" in cat_lower or "hat" in cat_lower or "beanie" in name_lower:
        item_type = "Headwear"
    elif "bags" in cat_lower or "backpack" in name_lower:
        item_type = "Bags / Backpacks"
    elif "accessories" in cat_lower:
        item_type = "Accessories (Other)"
    elif "sneaker" in cat_lower or "sneaker" in name_lower or "shoe" in name_lower:
        item_type = "Sneakers"
    elif "boots" in cat_lower or "boots" in name_lower:
        item_type = "Boots"
    elif "slides" in cat_lower or "sandals" in cat_lower:
        item_type = "Slides / Sandals"
    elif "footwear" in cat_lower:
        item_type = "Footwear (Other)"
    elif "t-shirt" in cat_lower or "tee" in name_lower:
        item_type = "T-Shirts"
    elif "hoodie" in cat_lower or "hoodie" in name_lower:
        item_type = "Hoodies"
    elif "sweater" in cat_lower or "crewneck" in name_lower:
        item_type = "Sweaters / Sweatshirts"
    elif "jacket" in cat_lower or "coat" in name_lower:
        item_type = "Jackets"
    elif "jeans" in cat_lower or "jeans" in name_lower:
        item_type = "Jeans"
    elif "pants" in cat_lower or "sweatpants" in cat_lower or "trousers" in name_lower:
        item_type = "Pants"
    elif "shorts" in cat_lower or "shorts" in name_lower:
        item_type = "Shorts"

    return gender, item_type


def get_sub_sitemaps(scraper, main_url, lang):
    print(UI[lang]['map_main'] + main_url)
    for attempt in range(1, 4):
        try:
            res = scraper.get(main_url, headers=HEADERS, timeout=20)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "xml")
                return [loc.text.strip() for loc in soup.find_all("loc") if "/sitemap/eu_de/sitemap-" in loc.text]

            # Catch bans
            if res.status_code in [403, 429, 502, 503, 504]:
                ban_time = random.randint(60, 180)
                print(UI[lang]['err_cf_ban'].format(res.status_code, ban_time // 60, ban_time % 60, attempt))
                time.sleep(ban_time)
            else:
                time.sleep(10)
        except Exception:
            time.sleep(15)
    return []


def get_product_urls(scraper, sitemap_url, lang):
    print(UI[lang]['map_list'] + sitemap_url)
    for attempt in range(1, 4):
        try:
            res = scraper.get(sitemap_url, headers=HEADERS, timeout=20)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "xml")
                return [l.text for l in soup.find_all("loc") if "/p/" in l.text]

            # Catch bans
            if res.status_code in [403, 429, 502, 503, 504]:
                ban_time = random.randint(60, 180)
                print(UI[lang]['err_cf_ban'].format(res.status_code, ban_time // 60, ban_time % 60, attempt))
                time.sleep(ban_time)
            else:
                print(UI[lang]['err_server'].format(res.status_code))
                time.sleep(10)
        except Exception:
            print(UI[lang]['err_timeout_list'])
            time.sleep(15)
    return []


def parse_and_download_item(item_url, scraper, lang):
    for attempt in range(1, 4):
        try:
            res = scraper.get(item_url, timeout=15)

            # Check if blocked
            if res.status_code in [403, 429, 502, 503, 504]:
                ban_time = random.randint(60, 300)
                print(UI[lang]['err_cf_ban'].format(res.status_code, ban_time // 60, ban_time % 60, attempt))
                time.sleep(ban_time)
                continue
            elif res.status_code != 200:
                return None

            soup = BeautifulSoup(res.text, "html.parser")

            category = "Unknown"
            color = "Unknown"

            # Parse JSON
            next_data_tag = soup.find("script", id="__NEXT_DATA__")
            if next_data_tag:
                try:
                    next_data = json.loads(next_data_tag.string)
                    prod_details = next_data.get("props", {}).get("pageProps", {}).get("productDetails", {}).get(
                        "productDetails", {})

                    cat1 = prod_details.get("category_level_1", "")
                    cat2 = prod_details.get("category_level_2", "")
                    if cat1 and cat2:
                        category = f"{cat1} / {cat2}"
                    elif cat1:
                        category = cat1

                    color = prod_details.get("color", "Unknown")
                except:
                    pass

            # Parse ld+json
            script_tag = soup.find("script", type="application/ld+json")
            if not script_tag: return None
            data = json.loads(script_tag.string)

            brand = data.get("brand", {}).get("name", "Unknown").replace(" ", "_")
            name = data.get("name", "Unknown")

            # Clean text
            desc = data.get("description", "")
            if desc:
                desc = desc.replace("<br />", "\n").replace("<br>", "\n")
                desc = BeautifulSoup(desc, "html.parser").get_text(separator=" ")
                desc = re.sub(r'\n\s+', '\n', desc).strip()

            if color == "Unknown": color = data.get("color", "Unknown")
            if isinstance(color, list):
                color = ", ".join([str(c) for c in color])
            else:
                color = str(color)

            # Get price and stock
            offers = data.get("offers", [])
            price = f"{offers[0].get('price')} {offers[0].get('priceCurrency')}" if offers else "0"
            is_available = 1 if "InStock" in (offers[0].get("availability", "")) else 0
            sizes = list(set(re.findall(r'"size":"(.*?)"', res.text)))

            table_gender = None

            # Get table data
            specs_table = soup.find("table", id="product-attribute-specs-table")
            if specs_table:
                table_text = specs_table.get_text(separator=" ").lower()
                has_table_men = re.search(r'\b(men|mens|herren)\b', table_text)
                has_table_women = re.search(r'\b(wmns|women|womens|damen)\b', table_text)

                if re.search(r'\bunisex\b', table_text) or (has_table_men and has_table_women):
                    table_gender = "Unisex"
                elif re.search(r'\b(kids|kinder|gs|ps|td)\b', table_text):
                    table_gender = "Kids"
                elif has_table_women:
                    table_gender = "Women"
                elif has_table_men:
                    table_gender = "Men"

            gender, item_type = analyze_item_type(category, name, table_gender)

            # Get images
            image_urls = []
            gallery_containers = soup.find_all("div", {"data-testid": "zoomable-image-container"})
            for container in gallery_containers:
                img_tag = container.find("img")
                if img_tag and img_tag.get("src"):
                    img_url = img_tag.get("src")
                    if img_url not in image_urls: image_urls.append(img_url)

            # Second image check
            if not image_urls:
                all_imgs = soup.find_all("img", src=re.compile(r"img\.bstn\.com"))
                for img in all_imgs:
                    img_url = img.get("src")
                    if img_url and len(img_url) > 50 and img_url not in image_urls: image_urls.append(img_url)

            if not image_urls:
                ld_img = data.get("image", [])
                if isinstance(ld_img, list):
                    image_urls.extend(ld_img)
                elif ld_img:
                    image_urls.append(ld_img)

            # Generate unique ID (10 digits)
            unique_id = str(random.randint(1000000000, 9999999999))

            # Remove bad symbols like \t or \n
            clean_name = re.sub(r'[\\/*?:"<>|\t\n\r]', " ", name)
            # Remove extra spaces and use underscore
            clean_name = re.sub(r'\s+', " ", clean_name).strip().replace(" ", "_")

            folder_name = f"{unique_id}_{clean_name}"
            product_folder = os.path.join(BASE_IMG_FOLDER, folder_name)

            # Try to make folder. Skip if Windows says error
            try:
                if not os.path.exists(product_folder):
                    os.makedirs(product_folder)
            except Exception as e:
                print(UI[lang]['err_folder'].format(folder_name))
                return None

            # Download images
            count = 0
            for i, img_url in enumerate(image_urls, 1):
                file_path = os.path.join(product_folder, f"{i}.jpg")
                if os.path.exists(file_path):
                    count += 1
                    continue
                try:
                    clean_img_url = img_url.replace('&amp;', '&')
                    img_data = scraper.get(clean_img_url, timeout=10).content
                    with open(file_path, "wb") as f:
                        f.write(img_data)
                    count += 1
                except:
                    pass

            return (unique_id, gender, item_type, category, brand, name, color, price, desc, ", ".join(sizes),
                    is_available, item_url, product_folder)

        except Exception as e:
            # Network error
            ban_time = random.randint(60, 300)
            print(UI[lang]['err_conn'].format(e))
            print(UI[lang]['err_sleep'].format(ban_time // 60, ban_time % 60, attempt))
            time.sleep(ban_time)

    print(UI[lang]['err_skip'])
    return None


if __name__ == "__main__":
    print("========================================")
    print("👟 BSTN Scraper Initializing 👟")
    print("========================================")

    # Select language
    print("Select Language / Выберите язык / Sprache wählen:")
    print("  1 - English (Default)")
    print("  2 - Русский")
    print("  3 - Deutsch")

    lang_input = input("Language (1/2/3): ").strip()
    if lang_input == '2':
        LANG = 'ru'
    elif lang_input == '3':
        LANG = 'de'
    else:
        LANG = 'en'

    # Select mode
    print(f"\n[{LANG.upper()}] {UI[LANG]['select_mode']}")
    print(f"  {UI[LANG]['mode_1']}")
    print(f"  {UI[LANG]['mode_2']}")

    while True:
        mode_choice = input(UI[LANG]['mode_prompt']).strip()
        if mode_choice in ['1', '2']:
            break
        print(UI[LANG]['mode_error'])

    is_test_mode = (mode_choice == '1')

    print(f"\n{UI[LANG]['init']}")
    init_system(LANG)
    scraper = cloudscraper.create_scraper()

    main_sitemap = "https://media.bstn.com/sitemap/eu_de/sitemap.xml"
    sub_maps = get_sub_sitemaps(scraper, main_sitemap, LANG)

    if sub_maps:
        # DB connection
        conn = sqlite3.connect(DB_NAME, timeout=30)
        cursor = conn.cursor()

        mode_text = "TEST" if is_test_mode else "FULL"
        print(UI[LANG]['found_maps'].format(len(sub_maps), mode_text))

        parsed_count = 0
        pause_after_5 = True
        pause_after_map = True
        stop_parsing = False

        try:
            # Loop sitemaps
            for map_idx, current_map_url in enumerate(sub_maps, 1):
                if stop_parsing:
                    break

                print(UI[LANG]['open_list'].format(map_idx, len(sub_maps), current_map_url))
                all_products = get_product_urls(scraper, current_map_url, LANG)
                total_products = len(all_products)

                # Loop links
                for url in all_products:
                    if stop_parsing:
                        break

                    # Check DB
                    cursor.execute("SELECT name FROM products WHERE url = ?", (url,))
                    existing_product = cursor.fetchone()

                    if existing_product:
                        print(UI[LANG]['skip'].format(existing_product[0]))
                        print(f"   ↳ {TRANSLATIONS[LANG]['lbl_link']}: {url}")
                        continue

                    # Scrape data
                    result = parse_and_download_item(url, scraper, LANG)

                    if result:
                        # Save to DB
                        cursor.execute('''
                                       INSERT INTO products (unique_id, gender, item_type, category, brand, name, color,
                                                             price, description, sizes, is_available, url, folder_path)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                       ''', result)
                        conn.commit()
                        parsed_count += 1

                        # Print info
                        disp_gender = TRANSLATIONS[LANG].get(result[1], result[1])
                        disp_type = TRANSLATIONS[LANG].get(result[2], result[2])

                        lbl_type = TRANSLATIONS[LANG]['lbl_type']
                        lbl_gender = TRANSLATIONS[LANG]['lbl_gender']
                        lbl_link = TRANSLATIONS[LANG]['lbl_link']

                        print(f"✅ [{parsed_count}] {result[5]} (ID: {result[0]})")
                        print(f"   ↳ {lbl_type}: {disp_type} | {lbl_gender}: {disp_gender}")
                        print(f"   ↳ {lbl_link}: {result[11]}")

                        # Check test mode
                        if is_test_mode and parsed_count >= 1:
                            print(UI[LANG]['test_done'])
                            stop_parsing = True
                            break

                        # Ask after 5
                        if parsed_count == 5 and pause_after_5 and not is_test_mode:
                            print(UI[LANG]['pause_5'].format(total_products - (all_products.index(url) + 1)))
                            print(UI[LANG]['action_prompt'])

                            user_input = input(UI[LANG]['choice']).strip()

                            if user_input == '1':
                                pause_after_5 = False
                                print(UI[LANG]['cont_list'])
                            elif user_input == '2':
                                pause_after_5 = False
                                pause_after_map = False
                                print(UI[LANG]['cont_all'])
                            else:
                                print(UI[LANG]['stop_user'])
                                stop_parsing = True
                                break

                    # Wait against ban
                    delay = random.uniform(3.0, 6.0) if not pause_after_map else random.uniform(1.5, 3.5)
                    time.sleep(delay)

                # Ask end list
                if not stop_parsing and pause_after_map and not is_test_mode and map_idx < len(sub_maps):
                    print(UI[LANG]['pause_list'].format(map_idx, len(sub_maps)))
                    print(UI[LANG]['action_prompt'])

                    user_input = input(UI[LANG]['choice']).strip()

                    if user_input == '1':
                        print(UI[LANG]['cont_list'])
                    elif user_input == '2':
                        pause_after_map = False
                        print(UI[LANG]['cont_all'])
                    else:
                        print(UI[LANG]['stop_user'])
                        stop_parsing = True
                        break

        except KeyboardInterrupt:
            print(UI[LANG]['stop_ctrlc'])
        except Exception as e:
            # Catch critical crash
            print(UI[LANG]['err_critical'].format(e))
        finally:
            conn.close()
            print(UI[LANG]['close_db'])

            print("\n========================================")
            input(UI[LANG]['exit_prompt'])