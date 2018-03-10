import os
import sys
import logging
# Own imports
import pixel_counter
import recolorer
import logistic_regression

# create logger with 'workflow'
logger = logging.getLogger('workflow')

# DIRECTORIES
dpics = 'images' # original pictures directory
dbin = 'bin' # bin directory to store things instead of delete
dcsv = 'csv' # csv storage
drecolor = 'recolor' # images recolors
dprecolor = 'p_recolor' # partial images recolors

def logging_setup(logfile):
  '''Sets up the logger values for every step in the workflow'''
  # default log level, used in case a message is unespecified.
  logger.setLevel(logging.DEBUG)
  # create file handler which logs even debug messages
  fh = logging.FileHandler(logfile)
  fh.setLevel(logging.DEBUG)
  # create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  # add the handlers to the logger
  logger.addHandler(fh)

def abort(step, result):
  '''Method used by the different steps of the workflow to abort due to a critical error,
  denoted by returning code -99'''
  if result != -99:
    return
  logger.error('Execution aborted due to a critical error by {0}'.format(step))
  sys.exit(1)

def steps():
  '''Executes every step in the workflow and manages the possible problems'''
  logger.info('Running workflow steps')

  result = []

  result.append(pixel_counter.run(dpics, dcsv, dbin))
  abort('pixel counter', result[-1])

  result.append(logistic_regression.run(dcsv))
  abort('logistic regression', result[-1])

  # the list file is result[-1] becaues logistic regression run method returns the file storing the accepted list
  result.append(recolorer.run(result[-1], dpics, drecolor, dprecolor))
  abort('recolorer', result[-1])

def main():
  logfile = 'doublestars.log'
  logging_setup(logfile)
  steps()

if __name__ == '__main__':
  main()