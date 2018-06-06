
# coding: utf-8

# In[1]:


import os
import json
import pandas as pd
import numpy as np
import math
import csv
import settings
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
import graphviz
from sklearn import model_selection
from sklearn import metrics
from sklearn.externals import joblib
import cv2


# In[2]:


def separateColors(image):
    height, width, _ = image.shape
    blanco = np.zeros((height,width,1), np.uint8)
    first = np.zeros((height,width,1), np.uint8)
    last = np.zeros((height,width,1), np.uint8)
    for x in range(height):
        for y in range(width):
            if(image[x][y][0] == 255 and image[x][y][1]== 255 and image[x][y][2]== 255):
                blanco[x][y][0] = 255
                first[x][y][0] = 255
                last[x][y][0] = 255
            if(image[x][y][0] == 255):
                last[x][y][0] = 255
            if(image[x][y][2]== 255):
                first[x][y][0] = 255
    return (blanco, first, last)


# In[3]:


def inContourUseless(c, listCont):
    for i in listCont:
        for pto in i:
            if(cv2.pointPolygonTest(c, (pto[0][0],pto[0][1]), False)!=-1):
                return True
    return False


# In[4]:


def getCenters(cnts, listUseless):
    listCenter =[]
    area_limit = 15
    for c in cnts:
        if(cv2.contourArea(c)>area_limit and not(inContourUseless(c, listUseless))):
            M = cv2.moments(c)
            cntX = int(M["m10"] / M["m00"])
            cntY = int(M["m01"] / M["m00"])
            listCenter.append((cntX,cntY,cv2.contourArea(c)))
    return listCenter


# In[5]:


def matrixCenter(centerFirst, centerLast):
    matrix = [[(0,0) for x in range(len(centerLast))] for y in range(len(centerFirst))]
    for i in range(len(centerFirst)):
        for j in range(len(centerLast)):
            dist=math.sqrt((centerFirst[i][0]-centerLast[j][0])**2+(centerFirst[i][1]-centerLast[j][1])**2)
            ang=math.atan2(centerFirst[i][0]-centerLast[j][0], centerFirst[i][1]-centerLast[j][1]) * (180.0 / math.pi)
            matrix[i][j] =(dist,ang)
    return matrix


# In[27]:


#create csv and headers
with open('stars.csv', 'w') as csvfile:
    fields = ['sepmax','max_v','max_v/min_v','max_ra0/min_ra0','max_ra1/min_ra1','dang','dvang','separation','label']
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    
    for dirs in os.walk("detected_doubles"):
        #print(dirs)
        for name in dirs[1]:
            if ("[]" not in name and 'all' not in name and 'detected_doubles' not in name):
                #open data.json and read
                cont = 0
                #THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
                #my_file = os.path.join(THIS_FOLDER, 'myfile.txt')
                file ="C:/Users/Javier CG/Desktop/SVM/detected_doubles/{0}/data.json".format(name)
                with open(file) as jsonfile:
                    data = json.load(jsonfile)
                #extract wds.PA value and wds.Separation value if the 'wds' section exists
                try:
                    wds_PA = data['wds']['PA']
                    wds_Sep = data['wds']['Separation']
                    print(wds_PA)
                    # read the image
                    file ="C:/Users/Javier CG/Desktop/SVM/detected_doubles/{0}/recolor.png".format(name)
                    image = cv2.imread(file)
                    # split images into only-white, only-red(first) and only-blue(last)
                    white, first, last = separateColors(image)
                    # use cv2 to get every contour in the red and blue images
                    cntsFirst= cv2.findContours(first, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]
                    cntsLast= cv2.findContours(last, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]
                    # filter useless images from the picture, NOT-WORKING, to ease the process
                    listUseless = [] # getUseless(image, white)
                    # use the contours to find out the centers of the stars
                    centerLast = getCenters(cntsLast, listUseless)
                    centerFirst = getCenters(cntsFirst, listUseless)
                    # use both center lists to create a matrix containing the traveled distance and the angle variation
                    matrix = matrixCenter(centerFirst,centerLast)

                    for x0 in range(len(centerFirst)):
                        for y0 in range(len(centerLast)):
                            # velocity and velocity angle for the first star pair
                            v0,vang0 = matrix[x0][y0]
                            for x1 in range(x0+1,len(centerFirst)):
                                for y1 in range(y0+1,len(centerLast)):
                                    # velocity and velocity angle for the second star pair
                                    v1,vang1 = matrix[x1][y1]
                                    # areas
                                    areaA0 = centerFirst[x0][2]
                                    areaA1 = centerFirst[x1][2]
                                    areaB0 = centerLast[y0][2]
                                    areaB1 = centerLast[y1][2]
                                    if(min(areaA0,areaA1,areaB0,areaB1,v0,v1) == 0):
                                        continue
                                    # calculate the angle taken the brightest as reference
                                    if (areaA0>areaA1):
                                        ang0=math.atan2(centerFirst[x0][0]-centerFirst[x1][0],centerFirst[x0][1]-centerFirst[x1][1]) * (180.0 / math.pi)
                                        ang1=math.atan2(centerLast[y0][0]-centerLast[y1][0], centerLast[y0][1]-centerLast[y1][1]) * (180.0 / math.pi)
                                    else:
                                        ang0=math.atan2(centerFirst[x1][0]-centerFirst[x0][0], centerFirst[x1][1]-centerFirst[x0][1]) * (180.0 / math.pi)
                                        ang1=math.atan2(centerLast[y1][0]-centerLast[y0][0], centerLast[y1][1]-centerLast[y0][1]) * (180.0 / math.pi)
                                    # separation between both star pairs
                                    sep0 =math.sqrt((centerFirst[x0][0]-centerFirst[x1][0])**2+(centerFirst[x0][1]-centerFirst[x1][1])**2)
                                    sep1 =math.sqrt((centerLast[y0][0]-centerLast[y1][0])**2+(centerLast[y0][1]-centerLast[y1][1])**2)
                                    # separation difference in the system
                                    dsep = abs(sep0-sep1)

                                    # maximum separation in the system
                                    sepmax = max(sep0,sep1)
                                    #maximum velocity in the system
                                    max_v = max(v0,v1)
                                    #maximum velocity in the system divided by the minimum velocity in the system
                                    max_v_min_v = max(v0,v1)/min(v0,v1)
                                    #maximum 
                                    max_ra0_min_ra0 = max(areaA0,areaB0)/min(areaA0,areaB0)

                                    max_ra1_min_ra1 = max(areaA1,areaB1)/min(areaA1,areaB1)
                                    # angle diference in the system
                                    dang = abs(ang1-ang0)
                                    # velocity angle difference
                                    dvang = abs(vang1-vang0)

                                    separation = (dsep*100)/sepmax

                                    #if (abs(((ang0+ang1)/2) - wds_PA) <= data['error']['PA'] and 
                                    #    abs(((sep1+sep0)/2) - wds_Sep) <= data['error']['Separation']):
                                    if (data['1']['Angle difference'] == dang and
                                        data['1']['Separation difference'] == dsep and
                                        data['1']['Maximum separation'] == sepmax and
                                        data['1']['Separation %'] == separation and
                                        data['1']['PA'] == (ang0+ang1)/2):
                                        
                                        label = 1
                                        cont += 1
                                        print(cont)
                                    else:
                                        label = 0
                                    #insert all values in
                                    writer.writerow({'sepmax':sepmax, 'max_v':max_v, 'max_v/min_v':max_v_min_v,
                                                     'max_ra0/min_ra0':max_ra0_min_ra0, 'max_ra1/min_ra1':max_ra1_min_ra1,
                                                     'dang':dang, 'dvang':dvang, 'separation':separation, 'label':label})
                except:
                    continue


# In[28]:


df = pd.read_csv('stars.csv')
df.describe()


# In[29]:


X = np.array(df.drop(['label'],1))
y = np.array(df['label'])
#clf = DecisionTreeClassifier(class_weight={0:2.3, 1:3.7},random_state=7)
#clf.fit(X, y)
clf = joblib.load('model.pkl')
#joblib.dump(clf, 'model.pkl')


# In[30]:


y_pred = clf.predict(X)

print(metrics.confusion_matrix(y, y_pred))
print(metrics.accuracy_score(y, y_pred))
print(metrics.classification_report(y, y_pred))


# In[31]:


dot_data = export_graphviz(clf, out_file="tree.dot",
                feature_names=['sepmax','max_v','max_v/min_v','max_ra0/min_ra0','max_ra1/min_ra1','dang','dvang','separation'],
                class_names=True,
                filled=True, rounded=True,
                special_characters=True)

