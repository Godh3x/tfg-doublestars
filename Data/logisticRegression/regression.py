
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sb
get_ipython().magic('matplotlib inline')


# In[3]:


df = pd.read_csv(r"TrainingSet\statsTrainingSet.csv")
df.head()


# In[71]:


df = df.dropna(1)
red = df['red']
green = df['green']
blue = df['blue']
black = df['black']
white = df['white']

f = lambda x, y: x+y
red = f(red, green)
red = f(red, blue)
red = f(red, black)
red = f(red, white)

f = lambda x, y: (x/y)*100
df['%red'] = f(df['red'],red)
df['%green'] = f(df['green'],red)
df['%blue'] = f(df['blue'],red)
df['%black'] = f(df['black'],red)
df['%white'] = f(df['white'],red)
df.head()


# In[72]:


df.pop('id')
df.pop('red')
df.pop('green')
df.pop('blue')
df.pop('black')
df.pop('white')


# In[73]:


df.drop(['doble(1:yes 0:no)'],1).hist()
plt.show()


# In[74]:


sb.pairplot(df.dropna(), hue='doble(1:yes 0:no)',size=5,vars=["%red","%green","%blue","%black","%white"],kind='reg')


# In[76]:


X = np.array(df.drop(['doble(1:yes 0:no)'],1))
y = np.array(df['doble(1:yes 0:no)'])
model = linear_model.LogisticRegression()
model.fit(X,y)
model.score(X,y)

