import pandas as pd
import os

def gap_check(df_scores):
    os.chdir(os.path.dirname(__file__))
    df_scores['previous_test'] = df_scores['needle_rating'] - df_scores['net_score']
    score_gaps = df_scores[df_scores['previous_test'] != df_scores['needle_rating_previous']]

    return (score_gaps)


# df_events = pd.read_excel('../input/events.xlsx')
# df_scores = pd.read_excel('../input/scores.xlsx')
# df_scores['previous_test'] = df_scores['needle_rating'] - df_scores['net_score']
# score_gaps = df_scores[df_scores['previous_test'] != df_scores['needle_rating_previous']]
