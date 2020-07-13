import pandas as pd
import numpy as np
import os
import requests
import ast
from bs4 import BeautifulSoup
import subprocess
from scipy.sparse import lil_matrix, csr_matrix
import pickle
from sklearn.decomposition import NMF
from sklearn.decomposition import TruncatedSVD

def get_swap_dict(d):
    return {v: k for k, v in d.items()}

def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)

#使用するユーザと本の抽出
userlist=[]
bookdict={}
with open("booklist_20200706_092102.csv") as f:
    for s_line in f:
        user,userbooklist=s_line.split(":",1)
        if len(ast.literal_eval(userbooklist.split("\n")[0]))<10: #読んだ本が10冊以下の人は含めない
            continue
        userlist.append(user)
        for book in ast.literal_eval(userbooklist.split("\n")[0]):
            if book not in bookdict:
                bookdict[book]=1
            else:
                bookdict[book]+=1

#10冊以上読まれている本だけを残す
bookdict_valid={}
num=0
for key,value in bookdict.items():
    if value>=10:
        bookdict_valid[key]=num
        num+=1

#疎行列の作成
bookset=set([book for book in bookdict_valid.keys()])
mat=lil_matrix((len(userlist),len(bookdict_valid)))
usernum=0
with open("booklist_20200706_092102.csv") as f:
    for s_line in f:
        user,userbooklist=s_line.split(":",1)
        if len(ast.literal_eval(userbooklist.split("\n")[0]))<10: #読んだ本が10冊以下の人は含めない
            continue
        for book in ast.literal_eval(userbooklist.split("\n")[0]):
            if book in bookset:
                mat[usernum,bookdict_valid[book]]=1
        usernum+=1

#辞書のkey-value反転
bookdict_swap = get_swap_dict(bookdict_valid)

#書籍と番号の対応表を保存
pickle_dump(bookdict_swap, 'bookdict.pickle')

#NMFによる次元削減
nmf = NMF(n_components=100, init='random', random_state=42)
book100f_nmf = nmf.fit_transform(mat.T)
pd.DataFrame(book100f_nmf).to_pickle('book100f.nmf.pkl')

#SVDによる次元削減
svd = TruncatedSVD(n_components=100, n_iter=5, random_state=42)
book100f_svd=svd.fit_transform(mat.T)
pd.DataFrame(book100f_svd).to_pickle('book100f_svd.pkl')