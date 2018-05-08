
# coding: utf-8

# In[1]:


import numpy as np
import cv2
import math


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


def detectStationary(img, c):
    conflicto = False
    i=0
    color = [255, 255, 255]
    while(conflicto == False and i < len(c)):
        conflicto, newColor = whiteSurroundings(img, c[i][0])
        if(not(np.array_equal(newColor, color)) and not(np.array_equal(newColor,[255, 255, 255])) and not(np.array_equal(newColor,[0, 0, 0]))):
            if(np.array_equal(color,[255, 255, 255])):
                color = newColor
            else:
                conflicto = True
        i=i+1
    return not conflicto


# In[4]:


def whiteSurroundings(img, pto):
    conflict = False
    color = [255, 255, 255]
    rows, cols,_ = image.shape
    i = -1
    while(i<2 and conflict == False):
        j=-1
        while(j<2 and conflict == False):
            if(pto[1]+ i >=1 and pto[1] +i < rows and pto[0]+ j >=1 and pto[0]+j < cols):
                if (not((img[pto[1]+i][pto[0]+j] ==[255, 255, 255]).all() or (img[pto[1]+i][pto[0]+j] ==[0, 0, 0]).all())):
                    if(np.array_equal(color,[255, 255, 255])):
                        color =img[pto[1]+i][pto[0]+j]
                    elif(not(np.array_equal(color,img[pto[1]+i][pto[0]+j]))):
                        conflict=True
            j=j+1
        i=i+1
    return conflict, color


# In[5]:


def getUseless(image, white):
    cntsWhite= cv2.findContours(white, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]
    listUseless=[]
    for c in cntsWhite:
        if (cv2.contourArea(c)>0):
            if(detectStationary(image, c)):
                listUseless.append(c)
    return listUseless


# In[6]:


def inContourUseless(c, listCont):
    for i in listCont:
        for pto in i:
            if(cv2.pointPolygonTest(c, (pto[0][0],pto[0][1]), False)!=-1):
                return True
    return False


# In[7]:


def matrixCenter(centerFirst, centerLast):
    matrix = [[(0,0) for x in range(len(centerLast))] for y in range(len(centerFirst))]
    for i in range(len(centerFirst)):
        for j in range(len(centerLast)):
            dist=math.sqrt((centerFirst[i][0]-centerLast[j][0])**2+(centerFirst[i][1]-centerLast[j][1])**2)
            ang=math.atan2(centerFirst[i][0]-centerLast[j][0], centerFirst[i][1]-centerLast[j][1]) * (180.0 / math.pi)
            matrix[i][j] =(dist,ang)
    return matrix


# In[8]:


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


# In[9]:


path = 'E:/rafa/docencia/1718/tfg/astro/recolor_no/'
image = cv2.imread(path+'92.11 +62.06.png', 1)
white, first, last = separateColors(image)

cntsFirst= cv2.findContours(first, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]
cntsLast= cv2.findContours(last, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]

listUseless = [] # getUseless(image, white)
centerLast = getCenters(cntsLast, listUseless)
centerFirst = getCenters(cntsFirst, listUseless)


# In[10]:


matriz = matrixCenter(centerFirst,centerLast)
print(matriz)


# In[ ]:



    


# In[11]:


angdiff =  5
vangdiff =  15
sepdiff = 7 # %
arearatio =  2
velocidadratio = 1.3
maxv=80
maxsep = 200
for x0 in range(len(centerFirst)):
    for y0 in range(len(centerLast)):
        v0,vang0 = matriz[x0][y0]        
        for x1 in range(x0+1,len(centerFirst)):
            for y1 in range(y0+1,len(centerLast)):
                v1,vang1 = matriz[x1][y1]    
                # son pareja?
                
                roja0 = centerFirst[x0][2]
                roja1 = centerFirst[x1][2]
                azul0 = centerLast[y0][2]
                azul1 = centerLast[y1][2]
                
                if (roja0>roja1):                
                    ang0=math.atan2(centerFirst[x0][0]-centerFirst[x1][0],centerFirst[x0][1]-centerFirst[x1][1]) * (180.0 / math.pi)
                    ang1=math.atan2(centerLast[y0][0]-centerLast[y1][0], centerLast[y0][1]-centerLast[y1][1]) * (180.0 / math.pi)
                else:
                    ang0=math.atan2(centerFirst[x1][0]-centerFirst[x0][0], centerFirst[x1][1]-centerFirst[x0][1]) * (180.0 / math.pi)
                    ang1=math.atan2(centerLast[y1][0]-centerLast[y0][0], centerLast[y1][1]-centerLast[y0][1]) * (180.0 / math.pi)
                sep0 =math.sqrt((centerFirst[x0][0]-centerFirst[x1][0])**2+(centerFirst[x0][1]-centerFirst[x1][1])**2)
                sep1 =math.sqrt((centerLast[y0][0]-centerLast[y1][0])**2+(centerLast[y0][1]-centerLast[y1][1])**2)
                dsep = abs(sep0-sep1)
                sepmax = max(sep0,sep1)
                dang = abs(ang1-ang0)
                dvang = abs(vang1-vang0)
                '''
                print(" dang: ",dang," dsep: ",dsep," sepmap: ",sepmax, "%: ",((dsep*100)/sepmax)," es menor:", (((dsep*100)/sepmax) <= sepdiff))
                print("dist0: ",dist0," ang0: ",ang0," dist1: ",dist1, "ang1: ",ang1, "roja0: ",centerFirst[x0][2],
                      "roja1",centerFirst[x1][2], " azul0: ",centerLast[y0][2], " azul1: ",centerLast[y1][2])
                '''
                if max(sep0,sep1)<=maxsep:
                    if max(v0,v1)<=maxv and min(v0,v1)>0 and max(v0,v1)/min(v0,v1)<=velocidadratio:
                        if min(roja0,azul0)>0 and max(roja0,azul0)/min(roja0,azul0) <= arearatio and  max(roja1,azul1)/min(roja1,azul1) <= arearatio:
                            if   dang<=angdiff:
                                if dvang <= vangdiff:
                                    if ((dsep*100)/sepmax)<=sepdiff:                     
                                        print(" dang: ",dang," dsep: ",dsep," sepmap: ",sepmax, "%: ",((dsep*100)/sepmax)," es menor:", (((dsep*100)/sepmax) <= sepdiff))
                                        print("sep0: ",sep0," ang0: ",ang0," sep1: ",sep1, "ang1: ",ang1, "roja0: ",centerFirst[x0][2],
                                              "roja1",centerFirst[x1][2], " azul0: ",centerLast[y0][2], " azul1: ",centerLast[y1][2])
                                        cv2.circle(image, (centerFirst[x0][0],centerFirst[x0][1]), 4, (255, 175, 0), -1)
                                        cv2.circle(image, (centerLast[y0][0],centerLast[y0][1]), 4, (255, 150,0 ), -1)                 
                                        cv2.circle(image, (centerFirst[x1][0],centerFirst[x1][1]), 4, (0, 175, 255), -1)
                                        cv2.circle(image, (centerLast[y1][0],centerLast[y1][1]), 4, (0, 150, 255), -1)                 
                                        cv2.imshow("imagen", image)
                                        cv2.waitKey(0)
                                        cv2.destroyAllWindows()
print("Hecho")


# In[12]:


'''
for pto in centerFirst:
    cv2.circle(image, (pto[0],pto[1]), 4, (255, 175, 0), -1)
    print(pto)
    cv2.imshow("imagen", image)
    cv2.waitKey(0)
    cv2.circle(image, (pto[0],pto[1]), 4, (0, 0, 0), -1)
    cv2.destroyAllWindows()

for pto in centerLast:
    cv2.circle(image, (pto[0],pto[1]), 4, (0, 255, 0), -1)
    print(pto)
    cv2.imshow("imagen", image)
    cv2.waitKey(0)
    cv2.circle(image, (pto[0],pto[1]), 4, (0, 0, 0), -1)
    cv2.destroyAllWindows()

cv2.imshow("imagen", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''

