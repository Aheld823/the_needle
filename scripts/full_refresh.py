import pandas as pd
import os
import get_data.get_article_urls as get_article_urls
import get_data.get_articles as get_articles
from gap_check import gap_check

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.makedirs('../input/', exist_ok=True)
os.makedirs('../output/', exist_ok=True)

def main():
    urls = get_article_urls.get_article_urls(limit = None)
    df_events, df_scores = get_articles.get_articles(urls)
    
    df_events['date'] = pd.to_datetime(df_events['date'], utc=True)
    df_events['date'] = df_events['date'].dt.tz_localize(None)
    df_events = df_events.astype({'article_id': 'object'
                                ,'date': 'datetime64[ns]'
                                ,'event_id':'object'
                                ,'title':'object'
                                ,'description': 'object'
                                ,'score':int
                                ,'url':'object'})
    df_events['date'] = df_events['date'].dt.normalize()
    df_events['date_str'] = df_events['date'].dt.strftime('%m/%d/%y')
    # Invert artcile_id scale so that the first article is #1
    df_events['article_id'] = df_events['article_id'].rank(method='first', ascending=False).astype(int)

    
    df_scores['date'] = pd.to_datetime(df_scores['date'], utc=True)
    df_scores['date'] = df_scores['date'].dt.tz_localize(None)
    df_scores = df_scores.astype({'article_id': 'object'
                                ,'date': 'datetime64[ns]'
                                ,'net_score': int
                                ,'needle_rating':int
                                ,'url':'object'})
    df_scores['date'] = df_scores['date'].dt.normalize()
    # Drop duplicates for date
    df_scores = df_scores.drop_duplicates(subset=['date'])
    df_scores['needle_rating_previous'] = df_scores['needle_rating'].shift(-1)
    # Invert artcile_id scale so that the first article is #1
    df_scores['article_id'] = df_scores['article_id'].rank(method='first', ascending=False).astype(int)

    score_gaps = gap_check(df_scores)
    print(f'Score gaps found:\n{len(score_gaps)}')

    df_events.to_excel('../input/events.xlsx')
    df_scores.to_excel('../input/scores.xlsx')
    score_gaps.to_excel('../output/score_gaps.xlsx')
    return

if __name__ == "__main__":
    main()

