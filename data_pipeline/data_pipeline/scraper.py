import os
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://books.toscrape.com/"
CATEGORIES = [
    "catalogue/category/books/travel_2/index.html",
    "catalogue/category/books/mystery_3/index.html",
    "catalogue/category/books/historical-fiction_4/index.html"
]

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
GBP_TO_INR = 105.50

def scrape_books():
    books = []
    for cat_url in CATEGORIES:
        url = BASE_URL + cat_url
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        category_name = soup.find("h1").text
        
        articles = soup.find_all("article", class_="product_pod")
        for art in articles:
            title = art.h3.a["title"]
            price_text = art.find("p", class_="price_color").text
            rating_text = art.find("p", class_="star-rating")["class"][1]
            avail_text = art.find("p", class_="instock availability").text.strip()
            
            books.append({
                "title": title,
                "price_raw": price_text,
                "rating_text": rating_text,
                "availability_text": avail_text,
                "category": category_name
            })
    return pd.DataFrame(books)

def clean_data(df):
    df["price_gbp"] = df["price_raw"].str.replace("£", "").astype(float)
    df["rating"] = df["rating_text"].map(RATING_MAP).fillna(0).astype(int)
    df["in_stock"] = df["availability_text"].str.contains("In stock", case=False).astype(int)
    df["price_inr"] = df["price_gbp"] * GBP_TO_INR
    return df

def setup_and_load_db(df, db_path="zepto_catalog.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (category_id)
        );
    """)
    
    categories = df["category"].unique()
    for cat in categories:
        cursor.execute("INSERT OR IGNORE INTO categories (category_name) VALUES (?)", (cat,))
    conn.commit()
    
    cat_df = pd.read_sql("SELECT * FROM categories", conn)
    df = df.merge(cat_df, left_on="category", right_on="category_name")
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (row["title"], row["price_gbp"], row["price_inr"], row["rating"], row["in_stock"], row["category_id"]))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    df_raw = scrape_books()
    df_clean = clean_data(df_raw)
    setup_and_load_db(df_clean)
    print("Data Pipeline Execution Completed Successfully.")