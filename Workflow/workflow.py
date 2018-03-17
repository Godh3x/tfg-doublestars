import os
import sys
import logging
# Own imports
import settings
import pixel_counter
import recolorer
import logistic_regression
from threading import Thread

# create logger with 'workflow'
logger = logging.getLogger('workflow')
threads = []

def prepare_threads():
  '''Prepares a thread for evert step and insert it in threads in order'''
  threads.append(Thread(target = pixel_counter.run, args = (settings.dpics, settings.dcsv)))
  threads.append(Thread(target = logistic_regression.run, args = (settings.dcsv, )))
  threads.append(Thread(target = recolorer.run,\
    args = (settings.accepted, settings.dpics, settings.drecolor, settings.dprecolor)))

def steps():
  '''Executes every step in the workflow and manages the possible problems'''
  # prepare the thread for every step
  prepare_threads()
  # launch them
  for t in threads:
    t.start()

def main():
  settings.init()
  steps()

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt: # preven Ctrl+C exceptions
    print('Interruption detected, closing...')
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)