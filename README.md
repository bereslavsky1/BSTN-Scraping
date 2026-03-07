# 👟 BSTN Store Scraper

![Python](https://img.shields.io/badge/python-3.13.5-blue.svg) ![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)

Hey! This is a custom-built asynchronous scraper for the BSTN store. I wrote this to easily pull product data (sneakers, streetwear, etc.) without getting blocked by bot protection. It grabs everything from prices and sizes to high-res images and organizes it all neatly into a local SQLite database.

**[PLACE_HOLDER_FOR_GIF_TERMINAL]**

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

## 🚀 How to run it

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
**[PLACE_HOLDER_FOR_IMG_DB]**

### Media Downloading
**[PLACE_HOLDER_FOR_IMG_FOLDERS]**

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