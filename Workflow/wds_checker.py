import os
import logging
import settings
import json
from threading import Event
import urllib.request as req


# wds url to download the data
url = 'http://ad.usno.navy.mil/wds/Webtextfiles/wdsweb_summ.txt'


# get the logger for the current module
logger = logging.getLogger('{0}.wds_checker'.format(settings.logger_name))

# history file to prevent duplicates
histfile = 'wds_checker_history.log'
hist = logging.getLogger('wds_checker_history')


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


def process(e, input, data):
    '''
    Reads the data from input/e/data.json, then stores the desired data, also
    compares both.
    '''
    with open('{0}/{1}/data.json'.format(input,e), 'r') as inp:
        datajson = json.load(inp)
    datajson['wds'] = {
      'PA': (int(data[38:41])+int(data[42:45]))/2,
      'Separation': (float(data[46:51]) + float(data[52:57]))/2,
      'Proper Motion A (brightest)': (int(data[80:84]), int(data[84:88])),
      'Proper Motion B': (int(data[89:93]), int(data[93:97]))
    }
    datajson['error'] = {
      'PA': datajson['wds']['PA']-datajson['1']['PA'],
      'Separation': datajson['wds']['Separation']-datajson['1']['Separation'],
      'Proper Motion A (brightest)': (datajson['wds']['Proper Motion A (brightest)'][0]-datajson['1']['Proper Motion A (brightest)'][0],
        datajson['wds']['Proper Motion A (brightest)'][1]-datajson['1']['Proper Motion A (brightest)'][1]),
      'Proper Motion B': (datajson['wds']['Proper Motion B'][0]-datajson['1']['Proper Motion B'][0],
        datajson['wds']['Proper Motion B'][1]-datajson['1']['Proper Motion B'][1])
    }
    # store result data in json file
    with open('{0}/{1}/data.json'.format(input,e), 'w') as out:
        json.dump(datajson, out, indent=2)


def loop_step(input, stop_event):
  '''
  Crops every jpg file inside input, for each file creates a jpg file in output.
  '''
  # input directory check
  if not os.path.isdir(input):
      logger.critical('input directory, {0}, not found.'.format(input))
      return 0
  # found
  # Try to get the data from the url
  try:
    data = req.urlopen(url).readlines()
    # encrypt input directory file
    encinput = os.fsencode(input)
    # loop through every element in input directory
    for e in os.listdir(encinput):
      # decrypt element name
      ename = os.fsdecode(e)
      # remove whitespaces to match wds
      ejoin = ''.join(ename.split())
      # ignore file if it has been processed before
      if ename in open(settings.logpath(histfile)).read():
          continue
      # process the element if theres any data about it
      for line in data:
        dline = os.fsdecode(line)
        if ejoin in dline:
          process(ename, input, dline)
          break
      # register file in history log to prevent future processing
      hist.info(e)
      # this check will allow stop events to break the execution sooner
      if stop_event.is_set():
          return 0
  except req.HTTPError:
      logger.warning('URL not found: {0}'.format(url))

def run(input, stop_event):
  '''
  Executes loop_step() until thread is stopped.
  '''
  logger.info('Running wds checker')
  # setup history logging
  logging_setup()

  while not stop_event.is_set():
      loop_step(input, stop_event)


if __name__ == '__main__':
  try:
      settings.init()
      run(settings.d_accepted, Event())
  except KeyboardInterrupt:  # preven Ctrl+C exceptions
      print('Interruption detected, closing...')
      try:
          sys.exit(0)
      except SystemExit:
          os._exit(0)