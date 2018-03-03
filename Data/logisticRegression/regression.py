
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
get_ipython().magic('matplotlib inline')


# In[2]:


df = pd.read_csv(r"TrainingSet\statsTrainingSet.csv")
df_val = pd.read_csv(r"ValidationSet\statsValidationSet.csv")
df.describe()


# In[4]:


#Normalization of the parameters
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

#New features
f = lambda x, y: x/y
df['prop_blue_red'] = f(df['%blue'], df['%red'])
df['prop_white_red'] = f(df['%white'], df['%red'])

#Same process with the validation set
df_val = df_val.dropna(1)
red = df_val['red']
green = df_val['green']
blue = df_val['blue']
black = df_val['black']
white = df_val['white']

f = lambda x, y: x+y
red = f(red, green)
red = f(red, blue)
red = f(red, black)
red = f(red, white)

f = lambda x, y: (x/y)*100
df_val['%red'] = f(df_val['red'],red)
df_val['%green'] = f(df_val['green'],red)
df_val['%blue'] = f(df_val['blue'],red)
df_val['%black'] = f(df_val['black'],red)
df_val['%white'] = f(df_val['white'],red)
f = lambda x, y: x/y
df_val['prop_blue_red'] = f(df_val['%blue'], df_val['%red'])
df_val['prop_white_red'] = f(df_val['%white'], df_val['%red'])
df_val.describe()


# In[5]:


#Elimination of useles features
df.pop('id')
df.pop('red')
df.pop('green')
df.pop('blue')
df.pop('black')
df.pop('white')
df.pop('%black')
df.pop('%green')

df_val.pop('id')
df_val.pop('red')
df_val.pop('green')
df_val.pop('blue')
df_val.pop('black')
df_val.pop('white')
df_val.pop('%black')
df_val.pop('%green')


# In[6]:


df.describe()


# In[7]:


#Show the distribution of each feature
df.drop(['doble'],1).hist()
plt.show()


# In[8]:


#Show the correlation of every pair of features
sb.pairplot(df.dropna(), hue='doble',size=5,vars=["%red","%blue","%white","prop_blue_red","prop_white_red"],kind='reg')


# In[9]:


#df[df.apply(lambda x: np.abs(x - x.mean()) / x.std() < 3).all(axis=1)]
#df.describe()


# In[10]:


#Creation of the model
X = np.array(df.drop(['doble'],1))
y = np.array(df['doble'])

X_val = np.array(df_val.drop(['doble'],1))
y_val = np.array(df_val['doble'])
model = linear_model.LogisticRegression(C=0.01)
model.fit(X,y)


# In[11]:


#Store the model and print the confusion matrix
joblib.dump(model, 'model.pkl')
y_pred = model.predict(X_val)
cm = metrics.confusion_matrix(y_val, y_pred)
print(cm)


# In[12]:


#Show accuracy
print(metrics.accuracy_score(y_val, y_pred))


# In[13]:


#Show all the measures
print(metrics.classification_report(y_val, y_pred))

