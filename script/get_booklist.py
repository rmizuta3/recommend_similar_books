import requests
from bs4 import BeautifulSoup
import time
import datetime
import logging
import pandas as pd

dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(filename=f'{dt_now}_get_booklist.log', level=logging.INFO)

userlist = pd.read_csv("userlist_20200705_232251.csv", header=None)
url_path = "https://booklog.jp/users/"

# 書籍の取得
for user in userlist[0].values:
    s = requests.Session()
    r = s.get(f"{url_path}{user}")
    soup = BeautifulSoup(r.text)
    time.sleep(1)

    booklist = []
    for div in soup.find_all("div", class_="item-area-img tooltip"):
        booklist.append(div.get('title'))

    with open(f"booklist_{dt_now}.csv", mode='a') as f:
        f.write(f"{user}:{booklist}")
        f.write("\n")

    logging.info(f"{user} done")
