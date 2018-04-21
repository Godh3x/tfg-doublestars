import os
import sys
import logging
# Own imports
import settings
import pixel_counter
import recolorer
import logistic_regression
import crop
from threading import Thread, Event
from time import sleep

# create logger with 'workflow'
logger = logging.getLogger('workflow')

# workflow intput-output dictionary
flow = {}

# threads and stop handlers
threads = []
stop_events = []


def define_flow():
    '''Defines the input, output and run method for every step in the workflow.
    The arguments for the callback function will be the result of concatenating
    the every input and output in the given order and a threading event.'''
    flow['dummy'] = {
        'input': [
            None
        ],
        'output': [
            settings.dpics
        ],
        'callback': lambda: None,
    }
    '''
    flow['crop'] = {
        'input': [
            flow['dummy']['output'][0],
        ],
        'output': [
            settings.dcrop
        ],
        'callback': crop.run,
    }
    '''
    flow['pixel_counter'] = {
        'input': [
            flow['dummy']['output'][0]
        ],
        'output': [
            settings.dcsv
        ],
        'callback': pixel_counter.run,
    }

    flow['logistic_regression'] = {
        'input': [
            flow['pixel_counter']['output'][0]
        ],
        'output': [
            settings.accepted
        ],
        'callback': logistic_regression.run,
    }

    flow['recolorer'] = {
        'input': [
            flow['dummy']['output'][0],
            flow['logistic_regression']['output'][0]
        ],
        'output': [
            settings.drecolor,
            settings.dprecolor
        ],
        'callback': recolorer.run,
    }


def prepare_threads():
    '''Use define_flow function and loops through the resulting dictionary to
    creating a thread for each step, once done threads will contain the list of
    threads to launch and stop_events the list of events to raise in order to
    stop each thread.'''
    define_flow()
    for item in flow:
        if item == 'dummy':
            continue
        # new event to stop the thread
        stop_events.append(Event())

        # create the argument list for the run method
        args = ()
        for i in flow[item]['input']:
            args += (i,)
        for i in flow[item]['output']:
            args += (i,)
        args += (stop_events[-1],)

        # define the thread and add it to the list
        threads.append(Thread(
            target=flow[item]['callback'],
            args=args
        ))


def steps():
    '''Executes every step in the workflow.'''
    # prepare the thread for every step
    prepare_threads()
    # launch them
    for t in threads:
        t.start()


def main():
    try:
        settings.init()
        steps()

        while True:
            sleep(1)
    except KeyboardInterrupt:  # preven Ctrl+C exceptions
        print('Interruption detected, stopping threads and closing...')
        # stop threads
        for e in stop_events:
            e.set()
        # wait for threads to stop
        for t in threads:
            t.join()
        # exit
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    main()
