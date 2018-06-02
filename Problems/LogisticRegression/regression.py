
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn import model_selection
from sklearn import metrics
#from sklearn.metrics import classification_report
#from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import seaborn as sb
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


df = pd.read_csv(r"Training\train.csv")
df_val = pd.read_csv(r"Testing\test.csv")
df.describe()


# In[3]:


f = lambda x: x *100
df['%red'] = f(df['%red'])
df['%green'] = f(df['%green'])
df['%blue'] = f(df['%blue'])
df['%black'] = f(df['%black'])
df['%white'] = f(df['%white'])

df_val['%red'] = f(df_val['%red'])
df_val['%green'] = f(df_val['%green'])
df_val['%blue'] = f(df_val['%blue'])
df_val['%black'] = f(df_val['%black'])
df_val['%white'] = f(df_val['%white'])


f = lambda x,y: (x * 100)/(100-y)
df['%red'] = f(df['%red'],df['%black'])
df['%green'] = f(df['%green'],df['%black'])
df['%blue'] = f(df['%blue'],df['%black'])
df['%white'] = f(df['%white'],df['%black'])

df['%red'] = f(df['%red'],df['%green'])
df['%blue'] = f(df['%blue'],df['%green'])
df['%white'] = f(df['%white'],df['%green'])

df_val['%red'] = f(df_val['%red'],df_val['%black'])
df_val['%green'] = f(df_val['%green'],df_val['%black'])
df_val['%blue'] = f(df_val['%blue'],df_val['%black'])
df_val['%white'] = f(df_val['%white'],df_val['%black'])

df_val['%red'] = f(df_val['%red'],df_val['%green'])
df_val['%blue'] = f(df_val['%blue'],df_val['%green'])
df_val['%white'] = f(df_val['%white'],df_val['%green'])


#New features
f = lambda x, y: x/y
df['prop_blue_red'] = f(df['%blue'], df['%red'])
df['prop_white_red'] = f(df['%white'], df['%red'])

f = lambda x, y: x/y
df_val['prop_blue_red'] = f(df_val['%blue'], df_val['%red'])
df_val['prop_white_red'] = f(df_val['%white'], df_val['%red'])

df.pop('id')
df.pop('%black')
df.pop('%green')
df_val.pop('id')
df_val.pop('%black')
df_val.pop('%green')

df.describe()


# In[4]:


#Show the distribution of each feature
df.drop(['double'],1).hist()
plt.show()


# In[5]:


#Show the correlation of every pair of features
df[df.apply(lambda x: np.abs(x - x.mean()) / x.std() < 3)]
print(sb.pairplot(df.dropna(), hue='double',size=5,vars=["%red","%blue","%white","prop_blue_red","prop_white_red"],kind='reg'))


# In[6]:


#df[df.apply(lambda x: np.abs(x - x.mean()) / x.std() < 3).all(axis=1)]
#df.describe()


# In[345]:


#Creation of the model
X = np.array(df.drop(['double'],1))
y = np.array(df['double'])

X_val = np.array(df_val.drop(['double'],1))
y_val = np.array(df_val['double'])
model = linear_model.LogisticRegressionCV(Cs=100, class_weight={0:2.3, 1:3.7}, cv=10, random_state=7)
model.fit(X,y)


# In[346]:


#Store the model and print the confusion matrix
joblib.dump(model, 'model.pkl')
y_pred = model.predict(X_val)
cm = metrics.confusion_matrix(y_val, y_pred)
print(cm)


# In[347]:


#Show accuracy
print(metrics.accuracy_score(y_val, y_pred))


# In[348]:


#Show all the measures
print(metrics.classification_report(y_val, y_pred))

