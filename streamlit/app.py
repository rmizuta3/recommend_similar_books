import pandas as pd
import streamlit as st
import pickle
import numpy as np
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from sudachipy import tokenizer
from sudachipy import dictionary


def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data


@st.cache(allow_output_mutation=True)  # オプションつけないとかなり遅い
def read_file():
    mat_svd = np.array(pd.read_pickle('book100f_svd_limit.pkl'))
    mat_nmf = np.array(pd.read_pickle('book100f_NMF_limit.pkl'))
    bookdict = pickle_load('bookdict_limit.pickle')
    return mat_svd, mat_nmf, bookdict


def calc_cos_matrix(mat, indexnum):
    """
    参考：https://stackoverflow.com/questions/41905029/create-cosine-similarity-matrix-numpy
    """
    mat_batch = mat[np.newaxis, indexnum]
    d = mat_batch @ mat.T
    norm1 = (mat_batch**2).sum(axis=1, keepdims=True) ** .5
    norm2 = (mat**2).sum(axis=1, keepdims=True) ** .5
    return d/norm1/norm2.T


def get_swap_dict(d):
    return {v: k for k, v in d.items()}


# sudachiの設定
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

st.write("このサイトについて：https://rmizutaa.hatenablog.com/entry/2020/07/14/214609")
st.title("類似本レコメンド(仮)")

mat_svd, mat_nmf, bookdict = read_file()
bookarr = [book for book in bookdict.values()]
bookdict_swap = get_swap_dict(bookdict)
searchword = st.text_input("タイトル又は著者名で検索").split()
# st.write(searchword)
searchword_parsed = ""
for word in searchword:
    if word in ["AND", "OR", "NOT"]:
        searchword_parsed += " ".join([m.surface()
                                       for m in tokenizer_obj.tokenize(word, mode)])
    else:
        searchword_parsed += " ("
        searchword_parsed += " ".join([m.surface()
                                       for m in tokenizer_obj.tokenize(word, mode)])
        searchword_parsed += ") "
# st.write(searchword_parsed)
ix = open_dir("index")
qp = QueryParser("content", schema=ix.schema)

outarr = []
if len(searchword_parsed) != 0:
    # for item in bookarr:
    #    if searchword in item:
    #        outarr.append(item)
    q = qp.parse(searchword_parsed)
    with ix.searcher() as s:  # with内で処理する必要あり
        results = s.search(q, limit=999, sortedby="count",
                           reverse=True)  # 本の登場数でソート
        for i in results:
            outarr.append(i.values()[2])

    st.write(f"候補数：{len(outarr)}件")
    if len(outarr) != 0:
        target_title = st.selectbox('検索したい本を選択してください', outarr)

        drmethod = st.selectbox('次元削減手法を選択してください', ('SVD', 'NMF'))
        if drmethod == "NMF":
            cos_matrix = calc_cos_matrix(mat_nmf, bookdict_swap[target_title])
        elif drmethod == "SVD":
            cos_matrix = calc_cos_matrix(mat_svd, bookdict_swap[target_title])

        books = pd.Series(cos_matrix[0]).replace(
            np.inf, np.nan).fillna(0).argsort()[::-1][:31].map(bookdict)
        cos_sim = np.sort(pd.Series(cos_matrix[0]).replace(
            np.inf, np.nan).fillna(0))[::-1][:31]

        result = pd.DataFrame()
        result["著書名"] = books.values[1:]
        result["類似度"] = cos_sim[1:]

        st.markdown("### 類似度上位30件")
        st.table(result)
