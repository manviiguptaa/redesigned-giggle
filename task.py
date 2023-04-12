import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3

def scrape_verge_articles(url):
    driver = webdriver.Chrome() 
    driver.get(url)
    link1 = driver.find_elements(By.CSS_SELECTOR, 'a.hover\\:shadow-underline-inherit.after\\:absolute.after\\:inset-0')
    link2 = driver.find_elements(By.CSS_SELECTOR, 'a.after\\:absolute.after\\:inset-0.group-hover\\:shadow-underline-blurple.dark\\:group-hover\\:shadow-underline-franklin')
    links = link2 + link1
    data = []
    id = 0
    for link in links:
        url = link.get_attribute('href')
        if url.startswith('https://www.theverge.com/2023'):
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            title = soup.find('meta', property='og:title')['content']
            author = soup.find('meta', {'name': 'parsely-author'})['content']
            date = soup.find('meta', {'name': 'parsely-pub-date'})['content']
            date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            data.append([id, url, title, author, formatted_date])
            id+=1
    driver.quit()
    return data

def save_data_to_csv(data):
    filename = datetime.now().strftime("%d%m%Y") + '_verge.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'URL', 'Title', 'Author', 'Date'])
        writer.writerows(data)
    print(f"Data has been saved to {filename}")

def save_data_to_db(data):
    conn = sqlite3.connect('verge_articles.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY, url TEXT, title TEXT, author TEXT, date TEXT)')

    for article in data:
        id, url, title, author, date = article
        c.execute('INSERT OR REPLACE INTO articles (id, url, title, author, date) VALUES (?, ?, ?, ?, ?)', (id, url, title, author, date))

    conn.commit()
    conn.close()
    print("Data has been saved to the database.")


if __name__ == '__main__':
    url = "https://www.theverge.com/"
    data = scrape_verge_articles(url)
    save_data_to_csv(data)
    save_data_to_db(data)
