'''
Creates a set of random equatorial coordinates in a given range.
'''
import random as rnd
import os

n = 100000
file = "randomneg"

ramin = 0.00
ramax = 360.00

decmin = -90.00
decmax = -20.00

def run():
  count = n
  while count > 0:
    ra = round(rnd.uniform(ramin, ramax), 2)
    dec = round(rnd.uniform(decmin, decmax), 2)
    c = '{0} {1}\n'.format(ra, "%+2.2f" % dec)
    if c in open('{0}.txt'.format(file), 'r').read():
      continue
    with open('{0}.txt'.format(file), 'a') as out:
      out.write(c)
    count -= 1

if __name__ == '__main__':
  if os.path.isfile('{0}.txt'.format(file)):
    os.remove('{0}.txt'.format(file))
  with open('{0}.txt'.format(file), 'w'): pass
  run()