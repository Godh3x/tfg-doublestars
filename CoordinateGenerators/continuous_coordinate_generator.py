'''
Creates a set of equatorial coordinates in a given range.
'''

import math as mth

file = 'coord'

ramin = 0.00
ramax = 1.00

decmin = 20.00
decmax = 22.00

rashift = 0.02
decshift = 0.01

def run():
  dec = decmin
  while dec <= decmax:
    ra = ramin
    rashift_adj = rashift * abs(mth.cos(dec))
    while ra <= ramax:
      with open('{0}.txt'.format(file), 'a') as out:
        out.write('{0} {1}\n'.format(round(ra,2), "%+2.2f" % dec))
      ra += rashift_adj
    dec += decshift

if __name__ == '__main__':
  run()