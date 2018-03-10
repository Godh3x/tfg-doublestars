import os
import logging
from PIL import Image, ImageDraw

# get the logger for the current module
logger = logging.getLogger('workflow.recolorer')

# history file to prevent duplicates
histfile = 'recolorer_history.log'
hist = logging.getLogger('recolorer_history')

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

def process(file, din, dout, dout2):
  '''Recolor a given jpg file to it's pure colors'''
  # open the jpg file
  im = Image.open('{0}/{1}'.format(din,file)).convert('RGB')
  # create the recolored canvas for the three images
  imtrans = Image.new('RGB',im.size)
  imtransf = Image.new('RGB',im.size)
  imtransl = Image.new('RGB',im.size)
  # get their drawing context
  d = ImageDraw.Draw(imtrans)
  df = ImageDraw.Draw(imtransf)
  dl = ImageDraw.Draw(imtransl)
  # loop through every pixel recoloring
  width,height = im.size
  for w in range(width):
    for h in range(height):
      color = colorgroup(im.getpixel((w,h)))
      # set color to the normal recolored image
      d.point((w,h), color)
      # color to f image only with red, white or black
      if color in ['red', 'white']:
        df.point((w,h), color)
      else:
        df.point((w,h), 'black')
      # set color to l image only with blue, white or black
      if color in ['blue', 'white']:
        dl.point((w,h), color)
      else:
        dl.point((w,h), 'black')
  # store the normal result in dout directory
  logger.debug('{0} full recolor stored in {1}/{2}.png'.format(file, dout, file[:-4]))
  imtrans.save('{0}/{1}.png'.format(dout,file[:-4]), "PNG")
  # store the partial recolor results in dout2 directory
  logger.debug('{0} red and blue recolors stored in {1}/{2}_f.png and {1}/{2}_l.png'.format(file, dout2, file[:-4]))
  imtransf.save('{0}/{1}_f.png'.format(dout2,file[:-4]), "PNG")
  imtransl.save('{0}/{1}_l.png'.format(dout2,file[:-4]), "PNG")

  # register file in history log to prevent future processing
  hist.info('{0}'.format(file))

def run(listfile, din, dout, dout2):
  '''Recolors every jpg file listed in listfile taking the associated image from din, for each file creates a png file in dout.
  Also creates two pngs *_f, containing only red, white and black pixels, and *_l,containing only blue, white and black pixels'''
  logger.info('Running recolorer')
  # setup history logging
  logging_setup()

  # input list file check
  if not os.path.isfile(listfile):
    logger.warning('Input list file, {0}, not found.'.format(din))
    return 0;

  # input directory check
  if not os.path.isdir(din):
    logger.critical('Image input directory, {0}, not found.'.format(din))
    return -99;

  # output directory check
  if not os.path.isdir(dout):
    logger.warning('Output directory, {0}, not found. Creating...'.format(dout))
    os.makedirs(dout)

  # output directory2 check
  if not os.path.isdir(dout2):
    logger.warning('Output directory, {0}, not found. Creating...'.format(dout2))
    os.makedirs(dout2)

  # loop through every element in input list
  with open(listfile, 'r') as input:
    # recolor every jpg file listed
    for file in input:
      # take only the name without the '\n
      fname = file[:-1]
      # ignore file if it has been processed before
      if fname in open(histfile).read():
        logger.debug('Skipped {0} because it has been processed before'.format(fname))
        continue
      # recolor the picture
      process(fname, din, dout, dout2)