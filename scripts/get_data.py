import pandas as pd
import requests
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

os.makedirs('../input/', exist_ok=True)
os.makedirs('../output/', exist_ok=True)

# Load website 

# Get all article objects

# Get all hrefs

# Get pagination

# Look through pages (maybe try/except?)
#https://washingtoncitypaper.com/article/tag/the-needle/page/[]/