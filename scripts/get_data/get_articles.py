import re
import pandas as pd
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

def get_articles(urls):
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(180)  
    driver.implicitly_wait(10)
    df_events = pd.DataFrame()
    df_scores = pd.DataFrame()
    for id, url in enumerate(urls,1):
        # Extract list of items
        print(url)
        driver.get(url)
        
        # Check to make sure website is accessible otherwise move to next url
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]'))
            )
        
        except:
            pass

        response = driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        date_tag = soup.find('time', class_='entry-date published')
        
        if date_tag:
            date = date_tag['datetime']        
        
        # Articles are inconsistently formatted. Sometimes it's a bullet list, sometimes it's just paragraphs
        ## Bullet list extraction
        list_object = soup.find('ul', class_='wp-block-list')
        entry_div = soup.find('div', class_='entry-content')

        
        if list_object:
            # entry_div = None
            list_items = list_object.find_all('li')
            idx = 1
            
            for  li in list_items:
                text = li.get_text(strip=False)
                event_match = re.match(r'^(.*?)(?:[:?])\s*(.*?)([-+]\d+)\s*\[', text) # regex to capture parts of event_text
                score_match = re.search(r"Today’s score:\s*([+-]?\d+)", text) # regex to get net score for article
                needle_match = re.search(r"Today’s Needle rating:\s*(-?\d+)", text) # regex to get needle score for today

                if event_match:
                    title = event_match.group(1).strip()
                    description = event_match.group(2).strip()
                    score = int(event_match.group(3))
                    df_events_temp = pd.DataFrame({'article_id':[id]
                                            ,'date': [date]
                                            ,'event_id':[idx]
                                            ,'title': [title]
                                            ,'description':[description]
                                            ,'score':[score]
                                            ,'url':[url]
                                            })
                    df_events = pd.concat([df_events,df_events_temp],axis=0)
                    idx += 1

                elif score_match and needle_match:
                    net_score = int(score_match.group(1))
                    needle_rating = int(needle_match.group(1))
                    df_scores_temp = pd.DataFrame({'article_id':[id]
                                                  ,'date':[date]
                                                  ,'net_score':[net_score]
                                                  ,'needle_rating':[needle_rating]
                                                  ,'url':[url]
                                                  })
                    df_scores = pd.concat([df_scores,df_scores_temp],axis=0)

            
                else:
                    pass
                    # print(f"Item {idx} didn’t match expected formats in list")
            
            else:
                pass
                # print("No list content found.")

                
        ## Paragraph extraction
        ### Can use the same extraction methods but need to access the content slightly different
        
        if entry_div:
            paragraphs = entry_div.find_all('p')
            idx = 1
            
            for p in paragraphs:
                text = p.get_text(strip=False)
                event_match = re.match(r'^(.*?)(?:[:?])\s*(.*?)([-+]\d+)\s*\[', text) # regex to capture parts of event_text
                score_match = re.search(r"Today’s score:\s*([+-]?\d+)", text) # regex to get net score for article
                needle_match = re.search(r"Today’s Needle rating:\s*(-?\d+)", text) # regex to get needle score for today
                # print(f"Paragraph {idx}: {p.get_text(strip=False)}")

                if event_match:
                    title = event_match.group(1).strip()
                    description = event_match.group(2).strip()
                    score = int(event_match.group(3))
                    df_events_temp = pd.DataFrame({'article_id':[id]
                                            ,'date': [date]
                                            ,'event_id':[idx]
                                            ,'title': [title]
                                            ,'description':[description]
                                            ,'score':[score]
                                            ,'url':[url]
                                            })
                    df_events = pd.concat([df_events,df_events_temp],axis=0)
                    idx += 1

                elif score_match and needle_match:
                    net_score = int(score_match.group(1))
                    needle_rating = int(needle_match.group(1))
                    df_scores_temp = pd.DataFrame({'article_id':[id]
                                                  ,'date':[date]
                                                  ,'net_score':[net_score]
                                                  ,'needle_rating':[needle_rating]
                                                  ,'url':[url]
                                                  })
                    df_scores = pd.concat([df_scores,df_scores_temp],axis=0)

                else:
                    pass
                    # print(f"Item {idx} didn’t match expected formats in paragraph.")
        
        else:
            pass
            # print("No <div class='entry-content'> found.")
    driver.quit()
    return df_events, df_scores

