import pandas as pd
import os
from urllib.request import urlretrieve
import jieba.analyse
from jieba.analyse import extract_tags
import numpy as np



if not os.path.exists ("dict.txt.big"):
  url = "https://github.com/fxsjy/jieba/raw/master/extra_dict/dict.txt.big"
  urlretrieve(url, "dict.txt.big")
jieba.set_dictionary ('dict.txt.big')

# 跟分類一樣先使用爬蟲等功能製作一個含文章內容的 DataFrame 存成 train.csv 準備。
df = pd.read_csv ('train.csv')


# 載入和訓練 word2vec，要準備另外一個 txt 將製作一個含文章內容，但用 Jieba 分詞且移除所有的標點符號的文件。參考 Content_NoS.py。
from gensim.models import word2vec
sentences = word2vec.LineSentence('train_NoS.txt')
model = word2vec.Word2Vec(sentences)


# 將字轉成向量
def docvec(article):

    tags = extract_tags(article, None, withWeight=True)
    total = np.zeros((100, ))
    norm = 0.
    for t, w in tags:
        if t in model.wv:
            total = total + w * model.wv[t]
            norm = norm + w
    return total / norm

dv = df["Content"].apply(docvec)


#存向量表
f = open('article.txt' ,'w')
f.write('{} {}\n'.format(len(dv), 100))
for i, v in enumerate(dv):
    s = ' '.join(map(str, list(v)))
    f.write('{} {}\n'.format(i, s))
f.close()
print (f"{ssss}")
# load 向量表
import gensim
d2v = gensim.models.KeyedVectors.load_word2vec_format('./article.txt', binary=False)

i = input("選擇一篇文章:")
print("原文標題:", df.iloc[int(i)]["Title"])
print("原文內容:", df.iloc[int(i)]["Content"])

for si, sv in d2v.most_similar(i, topn=2):
    print("*" * 50)
    print("相似度:", sv)
    print("推薦標題:", df.iloc[int(si)]["Title"])
    print("推薦內容:", df.iloc[int(si)]["Content"])