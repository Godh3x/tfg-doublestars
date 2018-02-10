from PIL import Image, ImageDraw
import os

directory = 'test'
fout = 'stats'


def colorgroup(pixel):
    groups = {  'red' : (255,   0,   0),
              'green' : (  0, 255,   0),
               'blue' : (  0,   0, 255),
              'black' : (  0,   0,   0),
              'white' : (255, 255, 255)}

    dist = lambda p1,p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])

    res = {}
    for c,v in groups.items():
        res[c] = dist(pixel,v)
    return min(res, key = res.get)


def process(file, out):
    count = {  'red' : 0,
             'green' : 0,
              'blue' : 0,
             'black' : 0,
             'white' : 0}

    im = Image.open('{0}/{1}'.format(directory,file)).convert('RGB')
    imtrans = Image.new('RGB',im.size)

    d = ImageDraw.Draw(imtrans) #Drawing context

    width,height = im.size
    for w in range(width):
        for h in range(height):
            color = colorgroup(im.getpixel((w,h)))
            count[color] += 1
            d.point((w,h), color)

    if count['white'] > count['black'] or (count['red'] == 0 and count['blue'] == 0):
        os.remove('{0}/{1}'.format(directory,fname))
        return

    out.write('{0} {1}\n'.format(file, count))
    imtrans.save('{0}/{1}_T.png'.format(directory,file[:-4]), "PNG")


encdir = os.fsencode(directory)
out = open('{0}.txt'.format(fout), 'w')
for file in os.listdir(encdir):
    fname = os.fsdecode(file)
    if not fname.endswith(".jpg"):
        continue

    if os.stat('{0}/{1}'.format(directory,fname)).st_size == 0:
        os.remove('{0}/{1}'.format(directory,fname))
        continue

    process(fname, out)
out.close()