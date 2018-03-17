import os
import shutil
import settings

def main():
  settings.init(False)

  shutil.rmtree(settings.dpics, True)
  shutil.copytree('images_backup', settings.dpics)
  shutil.rmtree(settings.dcsv, True)
  shutil.rmtree(settings.drecolor, True)
  shutil.rmtree(settings.dprecolor, True)
  if os.path.isfile(settings.accepted):
    os.remove(settings.accepted)

  for file in os.listdir(b'./'):
    fname = os.fsdecode(file)
    if fname[-4:] == '.log':
      os.remove(fname)


if __name__ == '__main__':
  main()