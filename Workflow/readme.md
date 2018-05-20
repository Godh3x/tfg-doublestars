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
 1. _[Pixel counter](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/pixel_counter.py)_: create a csv for every picture containen the % of pixels of each color.
 2. _[Logistic regression](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/logistic_regression.py)_: discard pictures based on csv data.
 3. _[Recolorer]()_: create png's recoloring the pictures approved by the logistic regression
 4. _[Crop](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/crop.py)_: for each jpg in input create a jpg in output, the output jpg corresponds to the middle sector of the original picture if we divide it in 9.
 5. _[Detector](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/detector.py)_: Given a folder of recolored pictures tries to match certain criteria, the pictures that match it will be stored in output. In addition to the recolored picture this step will store the original one and a json with important data about the double star system detected.
 6. _[wds_detector](https://github.com/Godh3x/tfg-doublestars/blob/master/Workflow/wds_checker.py)_: Takes the json given by the detector and tries to find the system in wds, if found will sotre also the data from wds and calculate the error in the detector data.
