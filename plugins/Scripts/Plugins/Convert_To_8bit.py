# @DatasetIOService ds
# @ConvertService convert
# @UIService ui

import os
from ij import IJ
from ij import ImagePlus

d = "/home/hadim/Insync/Data/Microscopy/PSF/2016.04.12.T1/raw"
files = os.listdir(d)

for fname in files:
    fpath = os.path.join(d, fname)
    print(fpath)

print(fpath)
dataset = ds.open(fpath)
ui.show(dataset)

imp = convert.convert(dataset, ImagePlus)
IJ.run("8-bit")

ds.save(dataset, fpath) # DOES NOT WORK
