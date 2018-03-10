import os
import logging
from PIL import Image

# get the logger for the current module
logger = logging.getLogger('workflow.pixel_counter')

# history file to prevent duplicates
histfile = 'pixel_counter_history.log'
hist = logging.getLogger('pixel_counter_history')

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

def colorgroup(pixel):
  '''Assign the given pixel to one of the known color groups(red, green, blue, bkack or white)'''
  # list of known colors and their R G B values
  groups = {  'red' : (255,   0,   0),
            'green' : (  0, 255,   0),
             'blue' : (  0,   0, 255),
            'black' : (  0,   0,   0),
            'white' : (255, 255, 255)}
  # distance between every color group and the pixel
  dist = lambda p1,p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])
  # store the distance results in a dictorionary, key is the color group name and value is the distance
  res = {}
  for c,v in groups.items():
    res[c] = dist(pixel,v)
  # select the color whose distance is the minimum
  color = min(res, key = res.get)
  # if the color selected is black check if the distance to blue or red is 150 or less, if it is
  # the assigned color will be blue or red. This is done to prevent ignoring dark red and blue pixels
  if color == 'black' and res['red'] != res['blue']:
    minc = 'red' if res['red'] < res['blue'] else 'blue'
    if res[minc] - res['black'] <= 150:
      return minc
  return color

def formatter(dict, pixels, out):
  '''Given a dictionary of colors and the total of pixels write in out the desired normalized output'''
  out.write('%red,%blue,%white,prop_blue_red,prop_white_red\n') # header
  # get the normalized values and proportions
  red = dict['red']/pixels
  blue = dict['blue']/pixels
  white = dict['white']/pixels
  prop_b_r = blue/red
  prop_w_r = white/red
  #store them in the file
  out.write('{0},{1},{2},{3},{4}\n'.format(red, blue, white, prop_b_r, prop_w_r))

def process(file, din, dout, dbin):
  '''Count the number of red, green, blue, black and white pixels in a given file'''
  # dictionary to store the pixel count for every recognised color
  count = {  'red' : 0,
           'green' : 0,
            'blue' : 0,
           'black' : 0,
           'white' : 0}
  # open the jpg file
  im = Image.open('{0}/{1}'.format(din,file)).convert('RGB')
  # get the width and height of the opened image
  width,height = im.size
  # total number of pixels, will be used to normalize the count
  pixels = width*height
  # loop through every pixel counting them
  for w in range(width):
    for h in range(height):
      color = colorgroup(im.getpixel((w,h)))
      count[color] += 1
  # remove the file if there's more white than black or there isn't any red or blue
  if count['white'] > count['black'] or (count['red'] == 0 and count['blue'] == 0):
    logger.debug("Moved {0} to {1} because there was more white than black or there wasn't any red or blue".format(file, dbin))
    os.rename('{0}/{1}'.format(din,file), '{0}/{1}'.format(dbin,file))
    return

  # create the associated csv in dout and write the results
  with open('{0}/{1}.csv'.format(dout, file[:-4]), 'w') as out:
    logger.debug('{0} pixel count stored in {0}/{1}.csv'.format(file, dout, file[:-4]))
    formatter(count, pixels, out)
  # register file in history log to prevent future processing
  hist.info('{0}'.format(file))

def run(din, dout, dbin):
  '''Counts the number of pixels for every jpg file inside din, for each file creates a csv in dout.
  If any file is to be deleted it is moved to dbin.'''
  logger.info('Running pixel counter')
  # setup history logging
  logging_setup()

  # input directory check
  if not os.path.isdir(din):
    logger.critical('Input directory, {0}, not found.'.format(din))
    return -99;

  # output directory check
  if not os.path.isdir(dout):
    logger.warning('Output directory, {0}, not found. Creating...'.format(dout))
    os.makedirs(dout)

  # bin directory check
  if not os.path.isdir(dbin):
    logger.warning('Bin directory, {0}, not found. Creating...'.format(dbin))
    os.makedirs(dbin)

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
      logger.debug('Skipped {0} because it has been processed before'.format(fname))
      continue
    # move to bin the jpg file if the size is 0
    if os.stat('{0}/{1}'.format(din,fname)).st_size == 0:
      logger.debug('Moved {0} to bin because file size is 0'.format(fname))
      os.rename('{0}/{1}'.format(din,fname), '{0}/{1}'.format(dbin,fname))
      continue
    # count the pixels in the file
    process(fname, din, dout, dbin)