import cloudscraper
from bs4 import BeautifulSoup
import json
import sqlite3
import time
import os
import re
import random

# --- SETTINGS ---
# My database and image folder names
DB_NAME = "bstn_products.db"
BASE_IMG_FOLDER = "product_images"

# Headers to look like a real browser, not a bot
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# --- TRANSLATOR ---
# Words for our database and console
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

# Texts for the console menu
UI = {
    'en': {
        'init': '🚀 System initialization...',
        'db_ready': '🗄 Database ready.',
        'map_main': '🗺️ Opening main sitemap: ',
        'map_list': '📑 Reading product list: ',
        'found_maps': '✅ Found {} product lists. Mode: {}. Press Ctrl+C to stop',
        'open_list': '\n📂 Opening product list [{}/{}]: {}',
        'skip': '⏩ Skip: "{}"',
        'test_done': '\n🛑 TEST MODE: Work completed.',
        'pause_5': '\n♻️ Processed 5 new items. Remaining in THIS list: {}.',
        'pause_list': '\n🏁 List [{}/{}] completely processed!',
        'action_prompt': 'Choose an action:\n  1 - Continue parsing only THIS list\n  2 - Parse the ENTIRE site to the end (non-stop)\n  3 - Exit',
        'choice': 'Your choice (1/2/3): ',
        'cont_list': '▶️ Continuing current list...\n',
        'cont_all': '▶️ Non-stop mode activated. Parsing everything!\n',
        'stop_user': '🛑 Parsing stopped by user.',
        'stop_ctrlc': '\n🛑 Program forcefully stopped by user (Ctrl+C)!',
        'close_db': '🗄 Database connection safely closed.',
        'select_mode': 'Select Mode:',
        'mode_1': '1 - TEST MODE (1 Item)',
        'mode_2': '2 - FULL PARSE',
        'mode_prompt': 'Mode (1 or 2): ',
        'mode_error': '❌ Error: Enter 1 or 2.'
    },
    'ru': {
        'init': '🚀 Инициализация системы...',
        'db_ready': '🗄 База данных готова.',
        'map_main': '🗺️ Открываю главную карту сайта: ',
        'map_list': '📑 Читаю список товаров: ',
        'found_maps': '✅ Найдено {} списков с товарами. Режим: {}. Для остановки нажми Ctrl+C',
        'open_list': '\n📂 Открываю список товаров [{}/{}]: {}',
        'skip': '⏩ Пропуск: "{}"',
        'test_done': '\n🛑 ТЕСТОВЫЙ РЕЖИМ: Работа завершена.',
        'pause_5': '\n♻️ Обработано 5 новых товаров. Осталось в ЭТОМ списке: {}.',
        'pause_list': '\n🏁 Список [{}/{}] полностью обработан!',
        'action_prompt': 'Выберите действие:\n  1 - Продолжить парсинг только ЭТОГО списка\n  2 - Парсить ВЕСЬ сайт до самого конца (без остановок)\n  3 - Завершить работу',
        'choice': 'Ваш выбор (1/2/3): ',
        'cont_list': '▶️ Продолжаем парсинг текущего списка...\n',
        'cont_all': '▶️ Активирован режим нон-стоп. Парсим всё!\n',
        'stop_user': '🛑 Парсинг остановлен пользователем.',
        'stop_ctrlc': '\n🛑 Программа экстренно остановлена пользователем (Ctrl+C)!',
        'close_db': '🗄 Соединение с базе данных безопасно закрыто.',
        'select_mode': 'Выберите режим:',
        'mode_1': '1 - ТЕСТОВЫЙ РЕЖИМ (1 товар)',
        'mode_2': '2 - ПОЛНЫЙ ПОЛЕТ (Парсинг всего сайта)',
        'mode_prompt': 'Режим (1 или 2): ',
        'mode_error': '❌ Ошибка: Введите 1 или 2.'
    },
    'de': {
        'init': '🚀 Systeminitialisierung...',
        'db_ready': '🗄 Datenbank bereit.',
        'map_main': '🗺️ Öffne Haupt-Sitemap: ',
        'map_list': '📑 Lese Produktliste: ',
        'found_maps': '✅ {} Produktlisten gefunden. Modus: {}. Zum Stoppen Strg+C drücken',
        'open_list': '\n📂 Öffne Produktliste [{}/{}]: {}',
        'skip': '⏩ Überspringen: "{}"',
        'test_done': '\n🛑 TESTMODUS: Arbeit abgeschlossen.',
        'pause_5': '\n♻️ 5 neue Artikel verarbeitet. Verbleibend in DIESER Liste: {}.',
        'pause_list': '\n🏁 Liste [{}/{}] vollständig verarbeitet!',
        'action_prompt': 'Aktion wählen:\n  1 - Nur DIESE Liste weiter parsen\n  2 - Die GESAMTE Seite bis zum Ende parsen (Non-Stop)\n  3 - Beenden',
        'choice': 'Deine Wahl (1/2/3): ',
        'cont_list': '▶️ Setze aktuelle Liste fort...\n',
        'cont_all': '▶️ Non-Stop-Modus aktiviert. Parse alles!\n',
        'stop_user': '🛑 Parsen vom Benutzer gestoppt.',
        'stop_ctrlc': '\n🛑 Programm vom Benutzer erzwungen gestoppt (Strg+C)!',
        'close_db': '🗄 Datenbankverbindung sicher geschlossen.',
        'select_mode': 'Modus wählen:',
        'mode_1': '1 - TESTMODUS (1 Artikel)',
        'mode_2': '2 - VOLLSTÄNDIGER PARSE (Gesamte Seite)',
        'mode_prompt': 'Modus (1 oder 2): ',
        'mode_error': '❌ Fehler: Bitte 1 oder 2 eingeben.'
    }
}


# --- MAKE SYSTEM READY ---
def init_system(lang):
    # Make folder if we don't have it
    if not os.path.exists(BASE_IMG_FOLDER):
        os.makedirs(BASE_IMG_FOLDER)

    # Open database and create table for our items
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       unique_id
                       TEXT
                       UNIQUE,
                       gender
                       TEXT,
                       item_type
                       TEXT,
                       category
                       TEXT,
                       brand
                       TEXT,
                       name
                       TEXT,
                       color
                       TEXT,
                       price
                       TEXT,
                       description
                       TEXT,
                       sizes
                       TEXT,
                       is_available
                       INTEGER,
                       url
                       TEXT
                       UNIQUE,
                       folder_path
                       TEXT,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    conn.commit()
    conn.close()
    print(UI[lang]['db_ready'])


# --- FIND TYPE AND GENDER ---
def analyze_item_type(category, name, table_gender=None):
    # Make text lowercase to search easier
    cat_lower = category.lower()
    name_lower = name.lower()

    # Look for men, women or kids words in the text
    has_men = re.search(r'\b(men|mens|herren)\b', name_lower) or re.search(r'\b(men|mens|herren)\b', cat_lower)
    has_women = re.search(r'\b(wmns|women|womens|damen)\b', name_lower) or re.search(r'\b(women|damen)\b', cat_lower)
    has_unisex = re.search(r'\bunisex\b', name_lower) or re.search(r'\bunisex\b', cat_lower)
    has_kids = re.search(r'\b(kids|kinder|gs|ps|td|infant|toddler)\b', name_lower) or re.search(r'\b(kids|kinder)\b',
                                                                                                cat_lower)

    # Decide gender
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

    item_type = "Other"

    # Decide what clothes it is (sneakers, hoodie, pants...)
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


# --- GET XML LINKS ---
def get_sub_sitemaps(scraper, main_url, lang):
    print(UI[lang]['map_main'] + main_url)
    res = scraper.get(main_url, headers=HEADERS)
    if res.status_code != 200: return []
    soup = BeautifulSoup(res.text, "xml")
    return [loc.text.strip() for loc in soup.find_all("loc") if "/sitemap/eu_de/sitemap-" in loc.text]


def get_product_urls(scraper, sitemap_url, lang):
    print(UI[lang]['map_list'] + sitemap_url)
    res = scraper.get(sitemap_url, headers=HEADERS)
    if res.status_code != 200: return []
    soup = BeautifulSoup(res.text, "xml")
    return [l.text for l in soup.find_all("loc") if "/p/" in l.text]


# --- PARSE ONE PRODUCT ---
def parse_and_download_item(item_url, scraper):
    try:
        # Go to product page
        res = scraper.get(item_url, timeout=15)
        if res.status_code != 200: return None

        soup = BeautifulSoup(res.text, "html.parser")

        category = "Unknown"
        color = "Unknown"

        # Look for hidden JSON data on the page
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

        # Also check ld+json for brand and description
        script_tag = soup.find("script", type="application/ld+json")
        if not script_tag: return None
        data = json.loads(script_tag.string)

        brand = data.get("brand", {}).get("name", "Unknown").replace(" ", "_")
        name = data.get("name", "Unknown")
        sku = data.get("sku", "no-sku")

        # Fix description (change HTML <br> to normal lines)
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

        # Get price and check if product is in stock
        offers = data.get("offers", [])
        price = f"{offers[0].get('price')} {offers[0].get('priceCurrency')}" if offers else "0"
        is_available = 1 if "InStock" in (offers[0].get("availability", "")) else 0
        sizes = list(set(re.findall(r'"size":"(.*?)"', res.text)))

        table_gender = None
        # Look at the specs table to be 100% sure about gender
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

        # Call our function to get final type and gender
        gender, item_type = analyze_item_type(category, name, table_gender)

        # Find all images for this product
        image_urls = []
        gallery_containers = soup.find_all("div", {"data-testid": "zoomable-image-container"})
        for container in gallery_containers:
            img_tag = container.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag.get("src")
                if img_url not in image_urls: image_urls.append(img_url)

        # Fallback if first method did not work
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

        # Generate a random 5 numbers ID to make folder name unique!
        unique_id = str(random.randint(10000, 99999))
        clean_name = re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")
        folder_name = f"{unique_id}_{clean_name}"
        product_folder = os.path.join(BASE_IMG_FOLDER, folder_name)

        if not os.path.exists(product_folder):
            os.makedirs(product_folder)

        # Download pictures and save them to folder
        count = 0
        for i, img_url in enumerate(image_urls, 1):
            file_path = os.path.join(product_folder, f"{i}.jpg")
            if os.path.exists(file_path):
                count += 1
                continue
            try:
                clean_img_url = img_url.replace('&', '&')
                img_data = scraper.get(clean_img_url, timeout=10).content
                with open(file_path, "wb") as f:
                    f.write(img_data)
                count += 1
            except:
                pass

        return (unique_id, gender, item_type, category, brand, name, color, price, desc, ", ".join(sizes), is_available,
                item_url, product_folder)

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# --- MAIN SCRIPT START HERE ---
if __name__ == "__main__":
    print("========================================")
    print("👟 BSTN Scraper Initializing 👟")
    print("========================================")

    # Ask user what language they want
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

    # Ask user for work mode
    print(f"\n[{LANG.upper()}] {UI[LANG]['select_mode']}")
    print(f"  {UI[LANG]['mode_1']}")
    print(f"  {UI[LANG]['mode_2']}")

    while True:
        mode_choice = input(UI[LANG]['mode_prompt']).strip()
        if mode_choice in ['1', '2']:
            break
        print(UI[LANG]['mode_error'])

    # Save mode (True if 1, False if 2)
    is_test_mode = (mode_choice == '1')

    print(f"\n{UI[LANG]['init']}")
    init_system(LANG)
    scraper = cloudscraper.create_scraper()

    main_sitemap = "https://media.bstn.com/sitemap/eu_de/sitemap.xml"
    sub_maps = get_sub_sitemaps(scraper, main_sitemap, LANG)

    if sub_maps:
        # Open database with timeout so it doesn't crash if locked
        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()

        mode_text = "TEST" if is_test_mode else "FULL"
        print(UI[LANG]['found_maps'].format(len(sub_maps), mode_text))

        parsed_count = 0
        pause_after_5 = True
        pause_after_map = True
        stop_parsing = False

        try:
            # Loop for every sitemap list
            for map_idx, current_map_url in enumerate(sub_maps, 1):
                if stop_parsing:
                    break

                print(UI[LANG]['open_list'].format(map_idx, len(sub_maps), current_map_url))
                all_products = get_product_urls(scraper, current_map_url, LANG)
                total_products = len(all_products)

                # Loop for every product link
                for url in all_products:
                    if stop_parsing:
                        break

                    # Check if we already have this product in DB
                    cursor.execute("SELECT name FROM products WHERE url = ?", (url,))
                    existing_product = cursor.fetchone()

                    if existing_product:
                        print(UI[LANG]['skip'].format(existing_product[0]))
                        print(f"   ↳ {TRANSLATIONS[LANG]['lbl_link']}: {url}")
                        continue

                    # Parse product!
                    result = parse_and_download_item(url, scraper)

                    if result:
                        # Save it to our database
                        cursor.execute('''
                                       INSERT INTO products (unique_id, gender, item_type, category, brand, name, color,
                                                             price, description, sizes, is_available, url, folder_path)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                       ''', result)
                        conn.commit()
                        parsed_count += 1

                        # Get correct translation for console print
                        disp_gender = TRANSLATIONS[LANG].get(result[1], result[1])
                        disp_type = TRANSLATIONS[LANG].get(result[2], result[2])

                        lbl_type = TRANSLATIONS[LANG]['lbl_type']
                        lbl_gender = TRANSLATIONS[LANG]['lbl_gender']
                        lbl_link = TRANSLATIONS[LANG]['lbl_link']

                        # Print success message
                        print(f"✅ [{parsed_count}] {result[5]} (ID: {result[0]})")
                        print(f"   ↳ {lbl_type}: {disp_type} | {lbl_gender}: {disp_gender}")
                        print(f"   ↳ {lbl_link}: {result[11]}")

                        # Stop if user chose test mode
                        if is_test_mode and parsed_count >= 1:
                            print(UI[LANG]['test_done'])
                            stop_parsing = True
                            break

                        # Ask user what to do after 5 products
                        if parsed_count == 5 and pause_after_5 and not is_test_mode:
                            print(UI[LANG]['pause_5'].format(total_products - 5))
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

                    # Sleep a little bit so website doesn't block us
                    delay = random.uniform(1.5, 3.5)
                    time.sleep(delay)

                # Ask user what to do when sitemap list is finished
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
            # If user presses Ctrl+C, stop program safely
            print(UI[LANG]['stop_ctrlc'])
        finally:
            # Close database so file is not locked
            conn.close()
            print(UI[LANG]['close_db'])
