import os
import sys
import logging
import image_slicer as imgsl
import settings
from threading import Event

# get the logger for the current module
logger = logging.getLogger('workflow.crop')

# history file to prevent duplicates
histfile = 'crop_history.log'
hist = logging.getLogger('crop_history')

show = True


def logging_setup():
    '''Sets up the logger'''
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


def process(file, din, dout, only_center):
    '''Reads the image from din/file, then saves the result of cropping in
    dout/file. The number of tiles is defined by the ntiles variable in settings.'''
    tiles = imgsl.slice('{0}/{1}'.format(din, file),
                        settings.ntiles, save=False)
    if only_center:
        imgsl.save_tiles((tiles[4],), directory=dout,
                         prefix=file[:-4], format='jpg')
        os.rename('{0}/{1}_02_02.jpg'.format(dout,
                                             file[:-4]), '{0}/{1}'.format(dout, file))
    else:
        imgsl.save_tiles(tiles, directory=dout, prefix=file, format='jpg')

    # register file in history log to prevent future processing
    hist.info('{0}'.format(file))


def run(din, dout, stop_event, only_center=True):
    '''Infinite loop executing loop_step()'''
    logger.info('Running crop')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(din, dout, stop_event, only_center)
        show = False


def loop_step(din, dout, stop_event, only_center):
    '''Crops every jpg file inside din, for each file creates a jpg file in dout.'''

    # input directory check
    if not os.path.isdir(din):
        if show:
            logger.critical('Input directory, {0}, not found.'.format(din))
        return 0

    # output directory check
    if not os.path.isdir(dout):
        logger.warning(
            'Output directory, {0}, not found. Creating...'.format(dout))
        os.makedirs(dout)

    # encrypt input directory file
    encdin = os.fsencode(din)
    # loop through every element in input directory
    for file in os.listdir(encdin):
        # decrypt file name
        fname = os.fsdecode(file)
        # ignore file if it doesn't end in jpg
        if not fname.endswith(".jpg"):
            continue
        # ignore file if it has been processed before
        if fname in open(histfile).read():
            continue
        # delete the jpg file if the size is 0
        if os.stat('{0}/{1}'.format(din, fname)).st_size == 0:
            logger.debug('Deleted {0} because file size is 0'.format(fname))
            os.remove('{0}/{1}'.format(din, fname))
            continue
        # count the pixels in the file
        process(fname, din, dout, only_center)
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.dpics, settings.dcrop, Event())
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
