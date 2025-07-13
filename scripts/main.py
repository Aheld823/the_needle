import pandas as pd
import requests
import os
import get_data.get_article_urls as get_article_urls
import get_data.get_articles as get_articles


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

os.makedirs('../input/', exist_ok=True)
os.makedirs('../output/', exist_ok=True)

urls = get_article_urls.get_article_urls()
urls = urls[:6] # temp override to get one page of results at a time

df_events, df_scores = get_articles.get_articles(urls)
print(df_events)
print(df_scores)

df_events.to_csv('../output/events.csv')
df_scores.to_csv('../output/scores.csv')

