import pandas as pd
import requests
import os
import get_data.get_articles as get_articles



abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

os.makedirs('../input/', exist_ok=True)
os.makedirs('../output/', exist_ok=True)

urls = get_articles.get_articles()
print(urls)
