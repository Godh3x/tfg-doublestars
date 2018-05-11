import logging
import os

# Logs directory
d_log = 'log'


# logger name used by all the app steps
global logger_name
logger_name = 'workflow'

def logpath(file):
    '''
    Given a log file returns the file path
    '''
    return '{0}/{1}'.format(d_log, file)


def create_logger():
    '''
    Creates the logger
    '''
    # create the base logger
    logger = logging.getLogger(logger_name)
    logfile = 'doublestars.log'
    logging_setup(logger, logfile)


def logging_setup(logger, logfile, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    '''
    Sets up a logger for the given parameters
    '''
    # if logs file doesn't exists -> create
    if not os.path.isdir(d_log):
        os.makedirs(d_log)
    # default log level, used in case a message is unespecified.
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('{0}/{1}'.format(d_log, logfile))
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(format)
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)

def init(crlogger=True):
    '''
    Set the global variables and create the app logger
    '''
    # original pictures directory
    global d_pics
    d_pics = 'images'
    # csv storage
    global d_csv
    d_csv = 'csv'
    # images recolors
    global d_recolor
    d_recolor = 'recolor'
    # recolorer list file
    global f_to_recolor
    f_to_recolor = 'recolor.list'
    # zoomed images storage directory
    global d_crop
    d_crop = 'cropped'
    # float value that defines the zooming factor
    global ntiles
    ntiles = 9
    # logistic regression model file
    global f_model
    f_model = 'model.pkl'
    # output directory for stars detected as doubles
    global d_accepted
    d_accepted = 'detected_doubles'

    #### Recolor options
    # maximum distance to pick a red or blue over black
    global recolor_threshold
    recolor_threshold = 150

    #### Parser options
    # maximum error in the angle between two different stars
    global angdiff
    angdiff =  5
    # maximum angle difference between two stars, red and blue, to be considered the same one
    global vangdiff
    vangdiff =  15
    # maximum separation % to be considered a double star
    global sepdiff
    sepdiff = 7 # %
    # maximum area difference to be considered a double star
    global arearatio
    arearatio =  2
    # maximum velocity difference to be considered a double star
    global velocityratio
    velocityratio = 1.3
    # maximum velocity
    global maxv
    maxv=80
    # maximum separation
    global maxsep
    maxsep = 200
    # proper motion conversion factor
    global pmfactor
    pmfactor = 6.8;
    # separation conversion factor
    global sepfactor
    sepfactor  = 1 / 3.95
    # if the number of doubles detected in a picture exceeds this number, the picture is rejected
    global maxdoubles
    maxdoubles = 1
    # if the number of stars detected in a picture exceeds this number, the picture is rejected
    global maxstars
    maxstars = 60
    # proper motion threshold
    global pmthreshold
    pmthreshold = 2500

    if crlogger:
        create_logger()