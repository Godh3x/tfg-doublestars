import os
import sys
import logging
import image_slicer as imgsl
import settings
from threading import Event

# get the logger for the current module
logger = logging.getLogger('{0}.crop'.format(settings.logger_name))

# history file to prevent duplicates
histfile = 'crop_history.log'
hist = logging.getLogger('crop_history')


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


def process(file, input, output, only_center):
    '''
    Reads the image from input/file, then saves the result of cropping in
    output/file. The number of tiles is defined by the ntiles variable in settings.
    '''
    tiles = imgsl.slice('{0}/{1}'.format(input, file),
                        settings.ntiles, save=False)
    if only_center:
        imgsl.save_tiles((tiles[4],), directory='{0}_tmp'.format(output), prefix=file[:-4], format='jpg')
        os.rename('{0}_tmp/{1}_02_02.jpg'.format(output, file[:-4]), '{0}/{1}'.format(output, file))
    else:
        imgsl.save_tiles(tiles, directory=output, prefix=file, format='jpg')
    # register file in history log to prevent future processing
    hist.info(file)


def loop_step(input, output, stop_event, only_center):
    '''
    Crops every jpg file inside input, for each file creates a jpg file in output.
    '''
    # input directory check
    if not os.path.isdir(input):
        if show:
            logger.critical('input directory, {0}, not found.'.format(input))
        return 0
    # output directory check
    if not os.path.isdir(output):
        logger.warning(
            'Output directory, {0}, not found. Creating...'.format(output))
        os.makedirs(output)
    # temporal output directory check
    if not os.path.isdir('{0}_tmp'.format(output)):
        os.makedirs('{0}_tmp'.format(output))
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
        if fname in open(settings.logpath(histfile)).read():
            continue
        # delete the jpg file if the size is 0
        if os.stat('{0}/{1}'.format(input, fname)).st_size == 0:
            logger.debug('Deleted {0} because file size is 0'.format(fname))
            os.remove('{0}/{1}'.format(input, fname))
            continue
        # count the pixels in the file
        process(fname, input, output, only_center)
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


def run(input, output, stop_event, only_center=True):
    '''
    Executes loop_step() until thread is stopped.
    '''
    logger.info('Running crop')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(input, output, stop_event, only_center)
        show = False


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.d_pics, settings.d_crop, Event())
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
