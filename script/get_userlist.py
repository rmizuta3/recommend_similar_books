import requests
from bs4 import BeautifulSoup
import time
import datetime
import logging

dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(filename=f'{dt_now}_get_userlist.log', level=logging.INFO)

s = requests.Session()
r = s.get("https://booklog.jp/profiletags")  # プロフィールタグページ
soup = BeautifulSoup(r.text)
time.sleep(1)

# タグリストの抽出（ページ１のみ）
taglist = []
for ul in soup.find_all("ul", class_="tagList"):
    for li in ul.find_all('li'):
        taglist.append(li.find("a").get('href'))

# ユーザリストの取得
userlist = set()
url_path = "https://booklog.jp"
for tag in taglist:
    for page in range(0, 1000):  # 最大1000ページ
        try:
            r = s.get(f"{url_path}{tag}?page={page}")
            soup = BeautifulSoup(r.text)
            time.sleep(1)

            if soup.find_all("div", class_="b15M") == []:  # 空ページまで到達した場合
                break

            for div in soup.find_all("div", class_="b15M"):
                username = div.find("a").get('href').split("/users/")[-1]

                # ファイル書き込み
                if username not in userlist:
                    with open(f"userlist_{dt_now}.csv", mode='a') as f:
                        f.write(username)
                        f.write("\n")

                userlist.add(username)

            logging.info(f"{tag}:{page}")

        except:
            break
