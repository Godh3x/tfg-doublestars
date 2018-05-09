import os
import sys
import shutil
import numpy as np
import cv2
import math
import logging
import settings
from threading import Event
import json

# get the logger for the current module
logger = logging.getLogger('{0}.detector'.format(settings.logger_name))

# history file to prevent duplicates
histfile = 'detector_history.log'
hist = logging.getLogger('detector_history')


show = True


def logging_setup():
    '''
    Sets up the logger
    '''
    # format used by the logger
    histformat = '%(message)s'
    # create the logger
    settings.logging_setup(hist, histfile, histformat)
    # ensure this function is only used once
    logging_setup.__code__ = (lambda: None).__code__


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


def getUseless(image, white):
    cntsWhite= cv2.findContours(white, cv2.RETR_LIST ,cv2.CHAIN_APPROX_NONE )[1]
    listUseless=[]
    for c in cntsWhite:
        if (cv2.contourArea(c)>0):
            if(detectStationary(image, c)):
                listUseless.append(c)
    return listUseless


def inContourUseless(c, listCont):
    for i in listCont:
        for pto in i:
            if(cv2.pointPolygonTest(c, (pto[0][0],pto[0][1]), False)!=-1):
                return True
    return False


def matrixCenter(centerFirst, centerLast):
    matrix = [[(0,0) for x in range(len(centerLast))] for y in range(len(centerFirst))]
    for i in range(len(centerFirst)):
        for j in range(len(centerLast)):
            dist=math.sqrt((centerFirst[i][0]-centerLast[j][0])**2+(centerFirst[i][1]-centerLast[j][1])**2)
            ang=math.atan2(centerFirst[i][0]-centerLast[j][0], centerFirst[i][1]-centerLast[j][1]) * (180.0 / math.pi)
            matrix[i][j] =(dist,ang)
    return matrix


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


def process(originals, file, input, output):
    '''
    Reads the image from input/file, then saves the result of parsing in
    output/file/.
    '''
    # to stop processing files after a certain number of double stars is detected
    doublecount = 0
    # read the image
    image = cv2.imread('{0}/{1}'.format(input, file))
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
    # dictionary to store the results in
    results = {}
    # Parser
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
                    # calculate the angle taken the brightest as reference
                    if (areaA0>areaA1):
                        ang0=math.atan2(centerFirst[x0][0]-centerFirst[x1][0],centerFirst[x0][1]-centerFirst[x1][1]) * (180.0 / math.pi)
                        ang1=math.atan2(centerLast[y0][0]-centerLast[y1][0], centerLast[y0][1]-centerLast[y1][1]) * (180.0 / math.pi)
                    else:
                        ang0=math.atan2(centerFirst[x1][0]-centerFirst[x0][0], centerFirst[x1][1]-centerFirst[x0][1]) * (180.0 / math.pi)
                        ang1=math.atan2(centerLast[y1][0]-centerLast[y0][0], centerLast[y1][1]-centerLast[y0][1]) * (180.0 / math.pi)
                    # proper motion
                    pmAx = centerFirst[x0][0]-centerLast[y0][0]
                    pmAy = centerFirst[x0][1]-centerLast[y0][1]
                    pmBx = centerFirst[x1][0]-centerLast[y1][0]
                    pmBy = centerFirst[x1][1]-centerLast[y1][1]
                    # separation between both star pairs
                    sep0 =math.sqrt((centerFirst[x0][0]-centerFirst[x1][0])**2+(centerFirst[x0][1]-centerFirst[x1][1])**2)
                    sep1 =math.sqrt((centerLast[y0][0]-centerLast[y1][0])**2+(centerLast[y0][1]-centerLast[y1][1])**2)
                    # separation difference in the system
                    dsep = abs(sep0-sep1)
                    # maximum separation in the system
                    sepmax = max(sep0,sep1)
                    # angle diference in the system
                    dang = abs(ang1-ang0)
                    # velocity angle difference
                    dvang = abs(vang1-vang0)
                    '''
                    print(" dang: ",dang," dsep: ",dsep," sepmap: ",sepmax, "%: ",((dsep*100)/sepmax)," es menor:", (((dsep*100)/sepmax) <= settings.sepdiff))
                    print("dist0: ",dist0," ang0: ",ang0," dist1: ",dist1, "ang1: ",ang1, "areaA0: ",centerFirst[x0][2],
                        "areaA1",centerFirst[x1][2], " areaB0: ",centerLast[y0][2], " areaB1: ",centerLast[y1][2])
                    '''
                    ### check criteria
                    # is the maximum separation below threshold?
                    if sepmax <= settings.maxsep:
                        # is the maximum velocity below threshold?
                        # and the minimum is above 0?
                        # is the system ratio below the maximum allowed value?
                        if max(v0,v1) <= settings.maxv and min(v0,v1) > 0 and max(v0,v1)/min(v0,v1) <= settings.velocityratio:
                            # are all areas over 0?
                            # are both system pairs below the maximum allowed value?
                            if min(areaA0,areaA1,areaB0,areaB1) > 0 and max(areaA0,areaB0)/min(areaA0,areaB0) <= settings.arearatio and max(areaA1,areaB1)/min(areaA1,areaB1) <= settings.arearatio:
                                # is system angle difference allowed?
                                if dang <= settings.angdiff:
                                    # is velocity angle difference allowed?
                                    if dvang <= settings.vangdiff:
                                        # does the system separation differ at maximum in the allowed %?
                                        if ((dsep*100)/sepmax) <= settings.sepdiff:
                                            # STAR SYSTEM DETECTED AS DOUBLE
                                            doublecount += 1
                                            if doublecount > settings.maxdoubles:
                                                break
                                            results[doublecount] = {
                                                'Angle difference': dang,
                                                'Separation difference': dsep,
                                                'Maximum separation': sepmax,
                                                'Separation %': ((dsep*100)/sepmax),
                                                'PA': (ang0+ang1)/2,
                                                'Separation': (sep1+sep0)/2*settings.sepfactor,
                                                'Proper Motion A (brightest)': (pmAx*settings.pmfactor,pmAy*settings.pmfactor),
                                                'Proper Motion B': (pmBx*settings.pmfactor,pmBy*settings.pmfactor)
                                            }
                                            # mark the star pairs in the image
                                            cv2.circle(image, (centerFirst[x0][0],centerFirst[x0][1]), 4, (255, 175, 0), -1)
                                            cv2.circle(image, (centerLast[y0][0],centerLast[y0][1]), 4, (255, 150,0 ), -1)
                                            cv2.circle(image, (centerFirst[x1][0],centerFirst[x1][1]), 4, (0, 175, 255), -1)
                                            cv2.circle(image, (centerLast[y1][0],centerLast[y1][1]), 4, (0, 150, 255), -1)
                                            #cv2.imshow("imagen", image)
                                            #cv2.waitKey(0)
                                            #cv2.destroyAllWindows()
                # the following breaks prevent the loops from iterating if the execution was aborted by the inner loop
                if doublecount > settings.maxdoubles:
                    break
            if doublecount > settings.maxdoubles:
                    break
        if doublecount > settings.maxdoubles:
                    break
    ###
    # store the results
    if doublecount > 0 and doublecount <= settings.maxdoubles:
        # Picture has a double star!
        logger.info('Double star system dectected in {0}!'.format(file[:-4]))
        if os.path.isdir('{0}/{1}'.format(output,file[:-4])):
            shutil.rmtree('{0}/{1}'.format(output,file[:-4]))
        os.makedirs('{0}/{1}'.format(output,file[:-4]))
        # move the original and recolored pictures
        os.rename('{0}/{1}.jpg'.format(originals,file[:-4]), '{0}/{1}/original.jpg'.format(output,file[:-4]))
        os.rename('{0}/{1}'.format(input,file), '{0}/{1}/recolor.png'.format(output,file[:-4]))
        # store the colored picture
        cv2.imwrite('{0}/{1}/centers.png'.format(output,file[:-4]),image)
        # store result data in json file
        with open('{0}/{1}/data.json'.format(output,file[:-4]), 'w') as out:
            json.dump(results, out, indent=2)
        #print(results)
    # if the picture was rejected remove associated files
    else:
        logger.info('Rejected {0}: too many double stars'.format(file[:-4]))
        os.remove('{0}/{1}.jpg'.format(originals,file[:-4]))
        os.remove('{0}/{1}'.format(input,file))
    # register file in history log to prevent future processing
    hist.info(file)


def loop_step(originals, input, output, stop_event):
    '''
    Parses every png file inside input, for each file accepted creates a folder
    insite output with the associated data.
    '''
    # input directory check
    if not os.path.isdir(input):
        if show:
            logger.critical('input directory, {0}, not found.'.format(input))
        return 0
    # output directory check
    if not os.path.isdir(output):
        logger.warning('Output directory, {0}, not found. Creating...'.format(output))
        os.makedirs(output)
    # encrypt input directory
    encinput = os.fsencode(input)
    # loop through every element in input directory
    for file in os.listdir(encinput):
        # decrypt file name
        fname = os.fsdecode(file)
        # ignore file if it doesn't end in png
        if not fname.endswith(".png"):
            continue
        # ignore file if it has been processed before
        if fname in open(settings.logpath(histfile)).read():
            logger.info('{0} found in step history file, file removed...'.format(fname))
            os.remove('{0}/{1}'.format(input,fname))
            continue
        # parse the picture
        process(originals, fname, input, output)
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


def run(originals, input, output, stop_event):
    '''
    Executes loop_step() until thread is stopped.
    '''
    logger.info('Running detector')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(originals, input, output, stop_event)
        show = False


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.d_recolor, settings.d_accepted, Event())
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)