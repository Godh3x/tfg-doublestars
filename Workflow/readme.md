# Workflow
The idea is to facilitate the use by creating a program that manages the workflow,
so it can be easily modified and run.

The program will follow a list of given steps, but first it is necesarry to met some
prerequisites.

## Prerequisites
First thing is to use the coordinate generators to get a set to process.
Once you have the file use Aladin with the given scripts to get the set of images to
process.

## Usage
1. Open [settings.py](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/settings.py) and modify the folders to match the ones the workflow should use.
 Note: The only folder that must exist is the one containing pictures (settings.d_pics)
2. Open [workflow.py](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/workflow.py) and define the steps to use.
 In order to do this you should add/modify the entries if flow defined in _define_flow()_.
 A step definition follows this structure:
 ```py
 flow['step'] = {
        'input': [
            flow['other']['output'][0],
            settings.directory
        ],
        'output': [
            settings.directory
        ],
        'callback': step.run,
}
 ```
 Input list tells the step where to obtain the data, may come from another step or be set manually.
 Output list is where the results will be stored.
 Callback is the function defined inside the step the thread will call.
 
 Note: The callback function must be defined as follows: step.run(input1, input2, ..., output1, output2, ..., stop_event)
 Note2: No further modifications are required, the workflow will create the threads for you.
 
 3. Run workflow.py

## Steps
 1. _Pixel counter_: create a csv for every picture
 2. _Logistic regression_: discard pictures based on csv data
 3. _Recolorer_: create png's recoloring the pictures approved by the logistic regression
