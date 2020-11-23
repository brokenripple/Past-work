# -*- coding: utf-8 -*-
"""Cluster.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lW0ESKp8qnqrmVpGsXFfsTKDc_CTtK25

Find different cycle
"""

import sklearn
import matplotlib
from sklearn.datasets import load_iris 
import pandas as pd
iris = load_iris ()

# find the key of the dataset and rebuild the dataset as an array
for key, value in iris.items():
  print (key)

df = pd.DataFrame(iris["data"], columns = iris ["feature_names"])
pd.options.display.max_rows = 20
# df.to_csv ("iris.csv", encoding="utf-8", index = False)
# df ["target"] = iris ["target"] (not used in cluster)
df
print (type(df))

from sklearn.cluster import KMeans
clu = KMeans(n_clusters=3)
clu.fit (df)
# k-means++ optimize the initial selection.

"""cluster_centers_ndarray of shape (n_clusters, n_features)
Coordinates of cluster centers. If the algorithm stops before fully converging (see tol and max_iter), these will not be consistent with labels_.

labels_ndarray of shape (n_samples,)
Labels of each point

inertia_float
Sum of squared distances of samples to their closest cluster center.

n_iter_int
Number of iterations run.
"""

df["labeel"] = clu.labels_
df

clu.cluster_centers_

"""class sklearn.tree.DecisionTreeClassifier(*, criterion='gini', splitter='best', max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=None, random_state=None, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, class_weight=None, presort='deprecated', ccp_alpha=0.0)

not the actual values in dataset
within cycle plus and average > a smaller better
outsiide cycle plus and average > b larger better
a*(1/b)
1-(a/b) = biggerthe better, within 1 (same as r^2)
"""

from sklearn.metrics import silhouette_score
# try how many clusters
for cycle_no in range (2,11): 
  test = KMeans (n_clusters=cycle_no)
  test.fit(iris["data"])
  s = silhouette_score (iris["data"], test.labels_)
  print (cycle_no, "cycle_no score is:", s)

"""https://seaborn.pydata.org/generated/seaborn.scatterplot.html#seaborn.scatterplot

eaborn.scatterplot(*, x=None, y=None, hue=None, style=None, size=None, data=None, palette=None, hue_order=None, hue_norm=None, sizes=None, size_order=None, size_norm=None, markers=True, style_order=None, x_bins=None, y_bins=None, units=None, estimator=None, ci=95, n_boot=1000, alpha=None, x_jitter=None, y_jitter=None, legend='auto', ax=None, **kwargs)
"""

import matplotlib.pyplot as plt
import seaborn as sns

sns.scatterplot (df["sepal length (cm)"],
        df["petal length (cm)"],
        hue = iris["target"])

