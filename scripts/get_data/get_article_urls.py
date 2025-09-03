from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = Options()
options.add_argument('--headless')

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
    

    # July 14th and June 18th has a weird pre score that isn't a missing article
    # Something is wrong with June 16th, 13th, and 10th
    # no article link after April 28th but there should be an article on April 25th
    # March 12th got duplicated for some reason - hopefully fixed in future versions
    # some urls need to be hard coded because they're unlisted from the landing page
    missing_urls =['https://washingtoncitypaper.com/article/768807/needle-doge-21-billion-ice-student-loan-nps-confederate-general-statue/' # August 5th
                   ,'https://washingtoncitypaper.com/article/768741/needle-smithsonian-impeachment-trump/' # August 4th
                   ,'https://washingtoncitypaper.com/article/768637/needle-bove-torture-deportation-impeachment-smithsonian/' # August 1st
                   ,'https://washingtoncitypaper.com/article/768494/needle-pirro-status-check-bove-epa-climate-change/' # July 30th
                   ,'https://washingtoncitypaper.com/article/768423/the-needle-ices-masks-draw-imposters-another-whistleblower-accuses-bove-and-republicans-want-to-rename-the-kennedy-center/' # July 29th
                   ,'https://washingtoncitypaper.com/article/767617/trump-doj-whistleblower/' # July 11th
                   ,'https://washingtoncitypaper.com/article/767471/the-needle-trump-d-c-takeover/' # July 9th
                   ,'https://washingtoncitypaper.com/article/767415/needle-trump-rfk-stadium-bove/' # July 8th
                   ,'https://washingtoncitypaper.com/article/767207/needle-kilmar-ice-immigration/' # July 3rd
                   ,'https://washingtoncitypaper.com/article/762281/needle-ed-martin-russia-kilmar/' # April 16th
                   ,'https://washingtoncitypaper.com/article/762141/needle-immigration-abrego-garcia/' # April 14th
                   ,'https://washingtoncitypaper.com/article/762050/needle-grenell-kennedy-center/' # April 10th 
                   ,'https://washingtoncitypaper.com/article/761857/needle-tariff-deportation-budget-rand-paul/' # April 7th              
                   ]
    urls = urls + missing_urls
    return urls