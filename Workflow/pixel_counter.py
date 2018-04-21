import os
import sys
import logging
from PIL import Image
import settings
from threading import Event

# get the logger for the current module
logger = logging.getLogger('workflow.pixel_counter')

# history file to prevent duplicates
histfile = 'pixel_counter_history.log'
hist = logging.getLogger('pixel_counter_history')

show = True


def logging_setup():
    '''Sets up the logger values for every step in the workflow'''
    # default log level, used in case a message is unespecified.
    hist.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(histfile)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    hist.addHandler(fh)
    # ensure this function is only used once
    logging_setup.__code__ = (lambda: None).__code__


def colorgroup(pixel):
    '''Assign the given pixel to one of the known color groups(red, green, blue, bkack or white)'''
    # list of known colors and their R G B values
    groups = {'red': (255,   0,   0),
              'green': (0, 255,   0),
              'blue': (0,   0, 255),
              'black': (0,   0,   0),
              'white': (255, 255, 255)}
    # distance between every color group and the pixel

    def dist(p1, p2): return abs(p1[0] - p2[0]) + \
        abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])
    # store the distance results in a dictorionary, key is the color group name and value is the distance
    res = {}
    for c, v in groups.items():
        res[c] = dist(pixel, v)
    # select the color whose distance is the minimum
    color = min(res, key=res.get)
    # if the color selected is black check if the distance to blue or red is 150 or less, if it is
    # the assigned color will be blue or red. This is done to prevent ignoring dark red and blue pixels
    if color == 'black' and res['red'] != res['blue']:
        minc = 'red' if res['red'] < res['blue'] else 'blue'
        if res[minc] - res['black'] <= 150:
            return minc
    return color


def formatter(dict, pixels, out):
    '''Given a dictionary of colors and the total of pixels write in out the desired normalized output'''
    out.write('%red,%blue,%white,prop_blue_red,prop_white_red\n')  # header
    # get the normalized values and proportions
    red = (dict['red']/pixels)*100
    blue = (dict['blue']/pixels)*100
    white = (dict['white']/pixels)*100
    prop_b_r = blue/red
    prop_w_r = white/red
    # store them in the file
    out.write('{0},{1},{2},{3},{4}\n'.format(
        red, blue, white, prop_b_r, prop_w_r))


def process(file, input, output):
    '''Count the number of red, green, blue, black and white pixels in a given file'''
    # dictionary to store the pixel count for every recognised color
    count = {'red': 0,
             'green': 0,
             'blue': 0,
             'black': 0,
             'white': 0}
    # open the jpg file
    im = Image.open('{0}/{1}'.format(input, file)).convert('RGB')
    # get the width and height of the opened image
    width, height = im.size
    # total number of pixels, will be used to normalize the count
    pixels = width*height
    # loop through every pixel counting them
    for w in range(width):
        for h in range(height):
            color = colorgroup(im.getpixel((w, h)))
            count[color] += 1
    # remove the file if there's more white than black or there isn't any red or blue
    if count['white'] > count['black'] or (count['red'] == 0 and count['blue'] == 0):
        logger.debug("Deleted {0} because there was more white than black or there wasn't any \
      red or blue".format(file, dbin))
        os.remove('{0}/{1}'.format(input, file))
        return

    # create the associated csv in output and write the results
    with open('{0}/{1}.csv'.format(output, file[:-4]), 'w') as out:
        logger.debug(
            '{0} pixel count stored in {0}/{1}.csv'.format(file, output, file[:-4]))
        formatter(count, pixels, out)
    # register file in history log to prevent future processing
    hist.info('{0}'.format(file))


def run(input, output, stop_event):
    '''Infinite loop executing loop_step()'''
    logger.info('Running pixel counter')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(input, output, stop_event)
        show = False


def loop_step(input, output, stop_event):
    '''Counts the number of pixels for every jpg file inside input, for each file creates a csv in output.'''

    # input directory check
    if not os.path.isdir(input):
        if show:
            logger.critical('Input directory, {0}, not found.'.format(input))
        return 0

    # output directory check
    if not os.path.isdir(output):
        logger.warning(
            'Output directory, {0}, not found. Creating...'.format(output))
        os.makedirs(output)

    # encrypt input directory file
    encinput = os.fsencode(input)
    # loop through every element in input directory
    for file in os.listdir(encinput):
        # decrypt file name
        fname = os.fsdecode(file)
        # ignore file if it doesn't end in jpg
        if not fname.endswith(".jpg"):
            continue
        # ignore file if it has been processed before
        if fname in open(histfile).read():
            continue
        # delete the jpg file if the size is 0
        if os.stat('{0}/{1}'.format(input, fname)).st_size == 0:
            logger.debug('Deleted {0} because file size is 0'.format(fname))
            os.remove('{0}/{1}'.format(input, fname))
            continue
        # count the pixels in the file
        process(fname, input, output)
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.dpics, settings.dcsv, Event())
    except Keyboarinputterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
