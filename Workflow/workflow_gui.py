import os
import sys
import logging
from threading import Thread, Event
import tkinter as tk
import importlib
# Own imports
import settings
import pixel_counter
import recolorer
import logistic_regression

# create logger with 'workflow'
logger = logging.getLogger('workflow')

# threads and stop handlers
thread_dict = {}
stop_events = []

# main window
window = tk.Tk()


def config_thread(id, callback, args):
  '''Configs id thread, the thread will be called using the given callback and args'''
  e = Event()
  t = Thread(target = callback, args = args + (e,))
  f = tk.Frame(window)
  l = tk.Label(f, text = id)
  l.pack(side = tk.LEFT)
  s = tk.Label(f, text = 'Running', fg = 'green')
  s.pack(side = tk.LEFT)
  b = tk.Button(f, text = 'Stop', command = lambda: stop_thread(id))
  b.pack(side = tk.LEFT)
  f.pack()
  thread_dict[id] = {
    'stop_event': e,
    'thread': t,
    'label': l,
    'status': s,
    'button': b,
    'frame': f,
    'callback': callback,
    'args': args + (e,)
    }

def prepare_threads():
  '''Prepares every thread using config_thread()'''
  config_thread(id = 'pixel_counter', callback = pixel_counter.run,\
    args = (settings.dpics, settings.dcsv))

  config_thread(id = 'logistic_regression', callback = logistic_regression.run,\
    args = (settings.dcsv,))

  config_thread(id = 'recolorer', callback = recolorer.run,\
    args = (settings.accepted, settings.dpics, settings.drecolor, settings.dprecolor))

def steps():
  '''Executes every step in the workflow and manages the possible problems'''
  # prepare the thread for every step
  prepare_threads()
  # launch them
  for v in thread_dict.values():
    v['thread'].start()

def on_close():
  '''Define window actions on close'''
  # stop threads
  for v in thread_dict.values():
    v['button'].config(text = '', command = lambda: None)
    v['status'].config(text = 'Stopping', fg = 'yellow')
    v['stop_event'].set()

  # wait for threads
  for v in thread_dict.values():
    v['thread'].join()
    v['status'].config(text = 'Stopped', fg = 'red')
  # exit
  window.destroy()

def stop_thread(index):
  '''Function used by buttons to stop a running thread'''
  v = thread_dict[index]
  # tell the thread to stop
  v['stop_event'].set()
  v['status'].config(text = 'Stopping', fg = 'yellow')
  window.update()
  # wait for the thread to stop
  v['thread'].join()
  v['status'].config(text = 'Stopped', fg = 'red')
  # change thread button
  v['button'].config(text = 'Start', command = lambda: run_thread(index))
  window.update()

def run_thread(index):
  '''Function used by buttons to start a stopped thread'''
  v = thread_dict[index]
  # tell the thread to stop
  v['stop_event'].clear()
  v['status'].config(text = 'Running', fg = 'green')
  # reload the module to restart
  importlib.reload(sys.modules[index])
  # create the thread again and run it
  v['thread'] = Thread(target = v['callback'], args = v['args'])
  v['thread'].start()
  # change thread button
  v['button'].config(text = 'Stop', command = lambda: stop_thread(index))
  window.update()

def run():
  settings.init()
  steps()

def main():
  run()
  # set on_close() as the handler for window
  window.protocol('WM_DELETE_WINDOW', on_close)
  # run
  window.mainloop()

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt: # preven Ctrl+C exceptions
    print('Interruption detected, closing...')
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)