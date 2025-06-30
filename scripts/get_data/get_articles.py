import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless')

def get_articles():
    urls = []
    page_number = 1
    driver = webdriver.Chrome(options=options)

    while True:
        url = f'https://washingtoncitypaper.com/article/tag/the-needle/page/{page_number}/'
        driver.get(url)
        print(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="primary"]/header/span/h1/span[2]'))
            )
        except:
            break

        response = driver.page_source

        soup = BeautifulSoup(response, 'html.parser')

        print(f"Page {page_number} processed successfully.")
        articles = soup.find_all('article')
        for idx, article in enumerate(articles, 1):
            figure = article.find('figure')

            if figure:
                anchor = figure.find('a', href=True)

                if anchor:
                    href = anchor['href']
                    urls = urls + [href]
                    # print(f"Article {idx} - Figure link: {href}")

        page_number += 1
    return urls


# Load website 

# Get all article objects

# Get all hrefs

# Get pagination

# Look through pages (maybe try/except?)
#https://washingtoncitypaper.com/article/tag/the-needle/page/[]/