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

    missing_urls = [
    'https://washingtoncitypaper.com/article/777566/the-needle-fbi-raids-post-reporters-home-ice-data-leaked-and-trump-gives-the-finger-to-a-ford-worker/' # 1/15/2026
    , 'https://washingtoncitypaper.com/article/776937/needle-maduro-demolish-st-elizabeths-kennedy-center-cancelations/' # 1/5/2026
    , 'https://washingtoncitypaper.com/article/776050/the-needle-national-guard-can-stay-in-d-c-for-now-trump-nominates-homophobic-former-pastor-to-federal-bench-and-police-targeted-one-southeast-neighborhood-in-particular/?utm_medium=email&utm_campaign=Newspack%20Newsletter%20%28776108%29&utm_source=612a4959fd&utm_source=Editorial+and+Events&utm_campaign=ab2573ff6e-EMAIL_CAMPAIGN_2025_12_19_04_55&utm_medium=email&utm_term=0_-ab2573ff6e-403149584' # 12/18/2025
    , 'https://washingtoncitypaper.com/article/775840/needle-trump-attacks-slain-director-patel-bungle-another-boat-strike/' # 12/16/2025    
    , 'https://washingtoncitypaper.com/article/775685/the-needle-noem-squirms-indiana-gop-stands-strong-and-trump-fails-again-to-indict-new-yorks-ag/' #12/12/2025
    , 'https://washingtoncitypaper.com/article/775653/needle-rename-blm-plaza-charlie-kirk-release-kilmar-abrego-garcia/' #12/11/2025
    , 'https://washingtoncitypaper.com/article/775556/needle-trumps-mortgages-fraud/' #12/10/2025
    , 'https://washingtoncitypaper.com/article/774779/needle-judge-dismiss-james-comey-letitia-james-doj-whistleblower-family-separations/' #11/5/2025
    , 'https://washingtoncitypaper.com/article/773931/needle-sandwich-guy-acquitted-bowser-doj-investigation-snap/' #11/7/2025
    , 'https://washingtoncitypaper.com/article/773863/needle-flights-reduced-shutdown-sandwitch-hero-awaits-jury-verdict/' #11/6/2025
    , 'https://washingtoncitypaper.com/article/773743/the-needle-trump-orders-more-extrajudicial-killings-dems-win-first-big-post-trump-election-and-masked-ice-impersonators-are-a-problem/' #11/5/2025
    , 'https://washingtoncitypaper.com/article/773428/needle-prosecutors-suspended-jan-6-riot-national-guard-quick-reaction-forces/' #10/30/2025
    , 'https://washingtoncitypaper.com/article/773367/needle-snap-lawsuit-military-kills-14-more-usaid-worker-dog-sketches/' #10/29/2025
    , 'https://washingtoncitypaper.com/article/773308/needle-mpd-hides-shooting-oag-national-guard/' #10/28/2025
    , 'https://washingtoncitypaper.com/article/773120/the-needle-virginia-couple-tried-to-stop-east-wing-demo-pregant-women-are-miscarrying-in-ice-detention-and-dhs-posts-video-with-nazi-favored-song/' #10/24/2025
    , 'https://washingtoncitypaper.com/article/772112/needle-dcps-international-teachers-mpd-immigration-trump-epstein-statue/' #10/3/2025
    , 'https://washingtoncitypaper.com/article/771763/needle-cardinal-immigration-marjorie-taylor-greene-white-house-portland/' #9/29/2025
    , 'https://washingtoncitypaper.com/article/771663/needle-comey-indictment-hegseth-wounded-knee/' #9/26/2025
    , 'https://washingtoncitypaper.com/article/771584/needle-park-police-pursuits-crashes-tylenol-researcher-unreliable-mass-firings-government-shutdown/' #9/25/2025
    , 'https://washingtoncitypaper.com/article/771415/needle-kimmel-trump-epstein-bff-statue-removed/' #9/24/2025
    , 'https://washingtoncitypaper.com/article/771356/needle-jimmy-kimmel-wjla-trump-tylenol-autism/' #9/23/2025
    , 'https://washingtoncitypaper.com/article/771110/needle-kimmel-late-night-show-kirk/' #9/18/2025
    , 'https://washingtoncitypaper.com/article/770990/needle-juvenile-justice-white-supremacist-right-wing-violence-pregnant-isolation/' #9/17/2025
    , 'https://washingtoncitypaper.com/article/770882/the-needle-trump-continues-to-blame-the-left-ignores-own-violent-rhetoric-nps-to-remove-mentions-of-slavery-britain-tv-will-troll-trump-during-uk-visit/' #9/16/2025
    , 'https://washingtoncitypaper.com/article/770637/needle-kirk-trump-pledges-retaliation-birth-control-destroyed/' #9/12/2025
    , 'https://washingtoncitypaper.com/article/770110/the-needle-bowers-orders-indefinite-local-coordination-with-federal-law-enforcement-house-gop-would-eliminate-hiv-funding/'  #9/3/2025 < THIS IS WEIRD
    , 'https://washingtoncitypaper.com/article/770019/the-needle-trump-revokes-harris-secret-service-and-the-stanford-daily-sues-for-free-speech/' #8/29/2025
    , 'https://washingtoncitypaper.com/article/769939/the-needle-mount-pleasant-neighbors-push-back-fda-limits-covid-vaccines-and-the-new-cdc-director-refuses-to-step-down/' #8/28/2025
    , 'https://washingtoncitypaper.com/article/769764/needle-trump-jeanine-pirro/' #8/26/2025
    , 'https://washingtoncitypaper.com/article/769709/needle-trump-cashless-bail-kilmar-detained/' #8/25/2025
    , 'https://washingtoncitypaper.com/article/769455/the-needle-three-more-states-to-send-national-guards-to-d-c-and-five-virginia-school-districts-refuse-to-rescind-trans-affirming-policies/' #8/19/2025
    , 'https://washingtoncitypaper.com/article/769057/needle-truth-social-ai-fema-cuts-smithsonian-trump-impeachment/' #8/11/2025
    , 'https://washingtoncitypaper.com/article/768807/needle-doge-21-billion-ice-student-loan-nps-confederate-general-statue/' #8/5/2025
    , 'https://washingtoncitypaper.com/article/768741/needle-smithsonian-impeachment-trump/' #8/4/2025
    , 'https://washingtoncitypaper.com/article/768637/needle-bove-torture-deportation-impeachment-smithsonian/' #8/1/2025
    , 'https://washingtoncitypaper.com/article/768062/the-needle-trump-says-rename-the-commanders-or-else-and-the-presidents-history-of-doodling/' #7/21/2025
    , 'https://washingtoncitypaper.com/article/767617/trump-doj-whistleblower/' #7/11/2025
    , 'https://washingtoncitypaper.com/article/767471/the-needle-trump-d-c-takeover/' #7/9/2025
    , 'https://washingtoncitypaper.com/article/767415/needle-trump-rfk-stadium-bove/' #7/8/2025
    , 'https://washingtoncitypaper.com/article/767207/needle-kilmar-ice-immigration/' #7/3/2025
    , 'https://washingtoncitypaper.com/article/767013/needle-noem-dark-money-trump-musk/' #7/1/2025
    , 'https://washingtoncitypaper.com/article/766285/needle-truck-tank-pedestrian-trans-medical-care/' #6/18/2025
    , 'https://washingtoncitypaper.com/article/765558/the-needle-travel-ban-2-0-and-illegal-deportations/?utm_medium=email&utm_campaign=17f9568952-EMAIL_CAMPAIGN_2025_06_06_04_17&utm_source=Editorial+and+Events&utm_term=0_-17f9568952-403662922' #6/6/2025 THERE ARE TWO OF THESE. SHOULD BE 6/5/2025?
    #, # MISSING APRIL 25s
    , 'https://washingtoncitypaper.com/article/762281/needle-ed-martin-russia-kilmar/' #4/16/2025
    , 'https://washingtoncitypaper.com/article/762141/needle-immigration-abrego-garcia/' #4/14/2025
    , 'https://washingtoncitypaper.com/article/762050/needle-grenell-kennedy-center/' #4/10/2025
    , 'https://washingtoncitypaper.com/article/761857/needle-tariff-deportation-budget-rand-paul/' #4/7/2025
    ]
    all_urls = list(dict.fromkeys(urls + missing_urls))

    return all_urls

