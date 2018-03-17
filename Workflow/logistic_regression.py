import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.externals import joblib
import os
import sys
import logging
import settings

# get the logger for the current module
logger = logging.getLogger('workflow.logistic_regression')

# history file to prevent duplicates
histfile = 'logistic_regression_history.log'
hist = logging.getLogger('logistic_regression_history')

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
  logging_setup.__code__ = (lambda:None).__code__

def load(file):
  '''Load the data of a given csv file'''
  df = pd.read_csv(file)
  return np.array(df)

def predict(model, file):
  '''Given a logistic regression model and a file makes a prediction.
  If prediction is 1 means its double, if it's 0 means it isn't.'''
  # read the data
  X = load(file)
  # return the prediction
  return model.predict(X)

def run(din):
  '''Infinite loop executing loop_step()'''
  logger.info('Running logistic regression')
  # setup history logging
  logging_setup()

  while True:
    loop_step(din)
    show = False

def loop_step(din):
  '''For every csv file in din make a prediction, if predicted as posible double
  the name is stored in accepted file.'''
  # input directory check
  if not os.path.isdir(din):
    return 0

  if not os.path.isfile(settings.model):
    if show:
      logger.critical('Model, {0}, not found.'.format(settings.model))
    return 0

  # load the logistic regression model
  model = joblib.load(settings.model)
  # encrypt input directory file
  encdin = os.fsencode(din)
  # loop through every element in input directory
  for file in os.listdir(encdin):
    # decrypt file name
    fname = os.fsdecode(file)
    # ignore file if it isn't a csv
    if not fname.endswith(".csv"):
      continue
    # ignore file if it has been processed before
    if fname in open(histfile).read():
      continue
    # make a prediction
    p = predict(model, '{0}/{1}'.format(din, fname))
    os.remove('{0}/{1}'.format(din, fname))
    # if prediction is 1 store it as accepted
    if p == 1:
      with open(settings.accepted, 'a') as out:
        out.write('{0}.jpg\n'.format(fname[:-4]))
      logger.info('Star {0} predicted as: may be double, added to {1}'.format(fname[:-4],\
        settings.accepted))
    else:
      logger.info('Star {0} predicted as: not double')
    hist.info(fname)

if __name__ == '__main__':
  try:
    settings.init()
    run(settings.dcsv)
  except KeyboardInterrupt: # preven Ctrl+C exceptions
    print('Interruption detected, closing...')
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)