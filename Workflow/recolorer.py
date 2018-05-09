import os
import sys
import shutil
import logging
from PIL import Image, ImageDraw
import settings
from threading import Event

# get the logger for the current module
logger = logging.getLogger('{0}.recolorer'.format(settings.logger_name))

# history file to prevent duplicates
histfile = 'recolorer_history.log'
hist = logging.getLogger('recolorer_history')


show = True


def logging_setup():
    '''
    Sets up the logger format
    '''
    # define history file
    histformat = '%(message)s'
    # format history file
    settings.logging_setup(hist, histfile, histformat)
    # ensure this function is only used once
    logging_setup.__code__ = (lambda: None).__code__


def colorgroup(pixel):
    '''
    Assign the given pixel to one of the known color groups
    (red, green, blue, bkack or white)
    '''
    # list of known colors and their R G B values
    groups = {
        'red': (255,   0,   0),
        'green': (0, 255,   0),
        'blue': (0,   0, 255),
        'black': (0,   0,   0),
        'white': (255, 255, 255)
        }
    # distance between every color group and the pixel
    dist = lambda p1, p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])
    # store the distance results in a dictorionary, key is the color group name and value is the distance
    res = {}
    for c, v in groups.items():
        res[c] = dist(pixel, v)
    # select the color whose distance is the minimum
    color = min(res, key=res.get)
    # if the color selected is black check if the distance to blue or red is recolor_threshold or less, if it is
    # the assigned color will be blue or red. This is done to prevent ignoring dark red and blue pixels
    if color == 'black' and res['red'] != res['blue']:
        minc = 'red' if res['red'] < res['blue'] else 'blue'
        if res[minc] - res['black'] <= settings.recolor_threshold:
            return minc
    return color


def process(file, dimages, dout):
    '''
    Recolor a given jpg file to pure colors
    '''
    # open the jpg file
    im = Image.open('{0}/{1}'.format(dimages, file)).convert('RGB')
    # create the recolored canvas for the image
    imtrans = Image.new('RGB', im.size)
    # get the drawing context
    d = ImageDraw.Draw(imtrans)
    # loop through every pixel recoloring
    width, height = im.size
    for w in range(width):
        for h in range(height):
            color = colorgroup(im.getpixel((w, h)))
            # set color to the normal recolored image
            d.point((w, h), color)
    # store the result in dout directory
    logger.debug('{0} full recolor stored in {1}/{2}.png'.format(file, dout, file[:-4]))
    imtrans.save('{0}_temp/{1}.png'.format(dout, file[:-4]), "PNG")
    os.rename('{0}_temp/{1}.png'.format(dout, file[:-4]), '{0}/{1}.png'.format(dout, file[:-4]))
    # register file in history log to prevent future processing
    hist.info('{0}'.format(file))


def loop_list(input, dimages, dout, stop_event):
    '''
    Loop through every element in input list
    '''
    with open(input, 'r') as input:
        # recolor every jpg file listed
        for file in input:
            # take only the name without the '\n
            fname = file[:-1]
            # ignore file if it has been processed before
            if fname in open(settings.logpath(histfile)).read():
                continue
            # recolor the picture
            process(fname, dimages, dout)
            # remove the original picture
            #os.remove('{0}/{1}'.format(dimages, fname))
            # this check will allow stop events to break the execution sooner
            if stop_event.is_set():
                return 0

def loop_all(dimages, dout, stop_event):
    '''
    Loop through every element in dimages
    '''
    # encrypt input directory file
    encinput = os.fsencode(dimages)
    # loop through every element in input directory
    for file in os.listdir(encinput):
        # decrypt file name
        fname = os.fsdecode(file)
        # ignore file if it isnt a picture
        if not fname.endswith('.jpg'):
            continue
        # ignore file if it has been processed before
        if fname in open(settings.logpath(histfile)).read():
            continue
        # recolor the picture
        process(fname, dimages, dout)
        # remove the original picture
        #os.remove('{0}/{1}'.format(dimages, fname))
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


def loop_step(input, dimages, dout, stop_event):
    '''
    Recolors every jpg file listed in input file or all, if stated by setting
    input to 'all',taking the images from  dimages, for each file creates a png
    file in dout.
    Also creates two pngs *_f, containing only red, white and black pixels, and
    *_l,containing only blue, white and black pixels.
    '''
    # input directory check
    if not os.path.isdir(dimages):
        if show:
            logger.critical('Image input directory, {0}, not found.'.format(dimages))
        return 0
    # output directory check
    if not os.path.isdir(dout):
        logger.warning('Output directory, {0}, not found. Creating...'.format(dout))
        os.makedirs(dout)
    # temporal output directory check
    if not os.path.isdir('{0}_temp'.format(dout)):
        logger.warning('Temporal output directory, {0}_temp, not found. Creating...'.format(dout))
        os.makedirs('{0}_temp'.format(dout))
    # input check
    if input == 'all':
        loop_all(dimages, dout, stop_event)
    elif not os.path.isfile(input):
        return 0
    else:
        loop_list(input, dimages, dout, stop_event)


def run(input, dimages, dout, stop_event):
    '''
    Executes loop_step() until thread is stopped.
    '''
    logger.info('Running recolorer')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(input, dimages, dout, stop_event)
        show = False
    # remove temporal directory
    if os.path.isdir('{0}_temp'.format(dout)):
        shutil.rmtree('{0}_temp'.format(dout))


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.f_to_recolor, settings.d_pics, settings.d_recolor, Event())
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
