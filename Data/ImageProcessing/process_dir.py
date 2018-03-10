from PIL import Image, ImageDraw
import os

directory = 'trainYes'
fout = 'statsYes'

batch = 1000

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
    color = min(res, key = res.get)
    if color == 'black' and res['red'] != res['blue']:
        minc = 'red' if res['red'] < res['blue'] else 'blue'
        if res[minc] - res['black'] <= 150:
            return minc
    return color


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
    # 1 if you are processing YES examples or 0 if NO
    out.write('"{0}",{1},{2},{3},{4},{5},{6}\n'.format(file,count['red'],count['green'],count['blue'],count['black'],count['white'],1))
    imtrans.save('{0}/Done/{1}.png'.format(directory,file[:-4]), "PNG")
    os.rename(src = '{0}/{1}'.format(directory,file), dst = '{0}/Done/{1}'.format(directory,file))

encdir = os.fsencode(directory)
header = not os.path.isfile('{0}.csv'.format(fout))
with open('{0}.csv'.format(fout), 'a') as out:
    if header:
        out.write('id,red,green,blue,black,white,double\n')
    b = 0
    for file in os.listdir(encdir):
        if b == batch:
            break;

        fname = os.fsdecode(file)
        if not fname.endswith(".jpg"):
            continue

        if os.stat('{0}/{1}'.format(directory,fname)).st_size == 0:
            os.remove('{0}/{1}'.format(directory,fname))
            continue

        process(fname, out)
        b+=1