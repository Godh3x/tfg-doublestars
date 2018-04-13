import logging


def init(crlogger=True):
    '''Sets the global variables and initializes them, also create the app logger'''
    # original pictures directory
    global dpics
    dpics = 'images'

    # csv storage
    global dcsv
    dcsv = 'csv'

    # images recolors
    global drecolor
    drecolor = 'recolor'

    # partial images recolors
    global dprecolor
    dprecolor = 'p_recolor'

    # logistic regression model file
    global model
    model = 'model.pkl'

    # logistic regression acceptance list file
    global accepted
    accepted = 'list.accepted'

    # float value that defines the zooming factor
    global ntiles
    ntiles = 9

    # zoomed images storage directory
    global dcrop
    dcrop = 'cropped'

    if crlogger:
        create_logger()


def create_logger():
    '''Ensures the logger is created only once'''
    logger = logging.getLogger('workflow')
    logfile = 'doublestars.log'
    logging_setup(logfile, logger)


def logging_setup(logfile, logger):
    '''Sets up the logger values for every step in the workflow'''
    # default log level, used in case a message is unespecified.
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
