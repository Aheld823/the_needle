from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os 

options = Options()
options.add_argument("--headless=new") 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
                     
chrome_bin = os.getenv('CHROME_BIN')
if chrome_bin:
    options.binary_location = chrome_bin

def get_article_urls(limit):
    urls = []
    page_number = 1 # temp override
    driver = webdriver.Chrome(options=options)

    while True:
        url = f'https://washingtoncitypaper.com/article/tag/the-needle/page/{page_number}/'
        driver.get(url)
        print(url)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="primary"]/header/span/h1/span[2]'))
            )
        except:
            print(f'No more after {page_number}')
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
        if limit == page_number:
            False
            break
        else:
            page_number += 1

    driver.quit()

    missing_urls = ['https://washingtoncitypaper.com/article/766285/needle-truck-tank-pedestrian-trans-medical-care/'

    ]
    all_urls = list(dict.fromkeys(urls + missing_urls))

    return all_urls

