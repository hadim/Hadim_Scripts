# @Dataset data
# @ImageJ ij

from ij import IJ
from net.imglib2.img.display.imagej import ImageJFunctions

imp = ImageJFunctions.wrap(data, data.getName())

filtered_imp = imp.clone()
imp = IJ.run(filtered_imp, "Bandpass Filter...", "filter_large=40 filter_small=10 suppress=None tolerance=5 autoscale saturate processStack=true")
filtered_imp.show()

#IJ.save(filtered_imp, "/home/hadim/filtered.tif")
#data_filtered = ij.dataset().open("/home/hadim/filtered.tif")
#ij.ui().show(data_filtered)

