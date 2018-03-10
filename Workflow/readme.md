# Workflow
The idea is to facilitate the use by creating a program that manages the workflow,
so it can be easily modified and run.

The program will follow a list of given steps, but first it is necesarry to met some
prerequisites.

## Prerequisites
First thing is to use the coordinate generators to get a set to process.
Once you have the file use Aladin with the given scripts to get the set of images to
process.

## Steps
 1. _Pixel counter_: create a csv for every picture
 2. _Logistic regression_: discard pictures based on csv data
 3. _Recolorer_: create png's recoloring the pictures approved by the logistic regression