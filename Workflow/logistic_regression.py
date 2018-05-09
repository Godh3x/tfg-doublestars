import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.externals import joblib
import os
import sys
import logging
import settings
from threading import Event

# get the logger for the current module
logger = logging.getLogger('{0}.logistic_regression'.format(settings.logger_name))

# history file to prevent duplicates
histfile = 'logistic_regression_history.log'
hist = logging.getLogger('logistic_regression_history')


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


def load(file):
    '''
    Load the data of a given csv file
    '''
    df = pd.read_csv(file)
    return np.array(df)


def predict(model, file):
    '''
    Given a logistic regression model and a file makes a prediction.
    If prediction is 1 means its double, if it's 0 means it isn't.
    '''
    # read the data
    X = load(file)
    # return the prediction
    return model.predict(X)


def loop_step(input, input2, output, stop_event):
    '''
    For every csv file in input make a prediction, if predicted as posible
    double the name is stored in output file.
    '''
    # directory/file check
    if not os.path.isdir(input):
        return 0

    if not os.path.isfile(input2):
        if show:
            logger.critical('Model, {0}, not found.'.format(input2))
        return 0

    # load the logistic regression model
    model = joblib.load(input2)
    # encrypt input directory file
    encinput = os.fsencode(input)
    # loop through every element in input directory
    for file in os.listdir(encinput):
        # decrypt file name
        fname = os.fsdecode(file)
        # ignore file if it isn't a csv
        if not fname.endswith(".csv"):
            continue
        # ignore file if it has been processed before
        if fname in open(settings.logpath(histfile)).read():
            continue
        # make a prediction
        p = predict(model, '{0}/{1}'.format(input, fname))
        os.remove('{0}/{1}'.format(input, fname))
        # if prediction is 1 store it as accepted
        if p[0] == 1:
            with open(output, 'a') as out:
                out.write('{0}.jpg\n'.format(fname[:-4]))
            logger.info('Star {0} predicted as: may be double, added to {1}'.format(fname[:-4],
                                                                                    output))
        else:
            logger.info('Star {0} predicted as: not double')
        hist.info(fname)
        # this check will allow stop events to break the execution sooner
        if stop_event.is_set():
            return 0


def run(input, input2, output, stop_event):
    '''
    Executes loop_step() until thread is stopped.
    '''
    logger.info('Running logistic regression')
    # setup history logging
    logging_setup()

    while not stop_event.is_set():
        loop_step(input, input2, output, stop_event)
        show = False


if __name__ == '__main__':
    try:
        settings.init()
        run(settings.d_csv, settings.f_model, settings.d_to_recolor, Event())
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, closing...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
