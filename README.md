# 👟 BSTN Store Scraper

![Python](https://img.shields.io/badge/python-3.13.5-blue.svg) ![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)

Hey! This is a custom-built asynchronous scraper for the BSTN store. I wrote this to easily pull product data (sneakers, streetwear, etc.) without getting blocked by bot protection. It grabs everything from prices and sizes to high-res images and organizes it all neatly into a local SQLite database.

![BSTN-Scraping (1)](https://github.com/user-attachments/assets/0d4e8451-4ca7-4359-87ea-3a16870d6c9d)

## 🔥 What it actually does

* **Sneaks past Cloudflare:** Uses `cloudscraper` so the script looks and acts like a real browser.
* **Smart Sorting:** Automatically figures out if a product is Men's, Women's, or Kids', and categorizes it (Sneakers, Hoodies, Accessories, etc.) based on keywords and specs.
* **Multilingual CLI:** The terminal interface speaks English, Russian, and German. You choose on startup.
* **Media Downloader:** It doesn't just scrape text. It downloads all product images and drops them into unique folders so your local drive stays clean.
* **Test Mode:** Has a quick 1-item test run so you don't have to scrape the entire site just to see if it works.

## 🛠 Tech Stack

* **Core:** Python 3.13.5
* **Bypass & Network:** `cloudscraper` (v1.2.71)
* **Parsing:** `beautifulsoup4` (v4.14.3), `lxml` (v6.0.2)
* **Storage:** `sqlite3`, native `json` & `os` modules

---

## ⚡ Quick Start (No Python needed)

Don't want to install Python or mess with the terminal? You can just download the compiled program.

1. Go to the **[Releases](https://github.com/bereslavsky1/BSTN-Scraping/releases)** tab on the right side of this page.
2. Download the latest `BSTN-Scraper-v1.0.exe` file.
3. Just double-click and run it! *(The database and images will automatically be created in the same folder where the .exe is located).*

<img width="367" height="116" alt="Screenshot_43" src="https://github.com/user-attachments/assets/5d8b0628-270c-42ce-beed-68d436b12888" />


---

## 🚀 How to run it (From source)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/bereslavsky1/BSTN-Scraping.git
   cd BSTN-Scraping
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the engine:**
   ```bash
   python main.py
   ```

## 📊 Data Preview

### Database Structure
<img width="1911" height="602" alt="Screenshot_37" src="https://github.com/user-attachments/assets/9e19052a-2334-4a3d-955f-0bd423b05dc8" />

### Media Downloading
<img width="2023" height="1935" alt="Media Downloading" src="https://github.com/user-attachments/assets/a6ecf085-f47f-4ec8-9714-3dccbd8d431b" />

## 📂 What's inside?

* `main.py` — The core logic and parser.
* `requirements.txt` — Dependencies you need to install.
* `bstn_products.db` — *(Generated on run)* Where all the scraped data lives.
* `product_images/` — *(Generated on run)* Where the high-res pics are saved.

## ✌️ Hit me up

Created by **[bereslavsky1](https://github.com/bereslavsky1)**.  
If you have questions, found a bug, or just want to talk code, drop me an email: daniilbereslavsky@gmail.com

---
*Disclaimer: This tool was built for educational purposes. Please don't spam the servers.*
