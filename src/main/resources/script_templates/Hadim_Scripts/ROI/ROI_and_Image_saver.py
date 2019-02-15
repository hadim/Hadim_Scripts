# @File(label="Select a directory", style="directory") parent_dir
# @Dataset dataset
# @DatasetIOService io
# @OpService ops
# @DatasetService ds

import os
from ij.plugin.frame import RoiManager

def get_axis(axis_type):
	from net.imagej.axis import Axes
	return {'X': Axes.X, 'Y': Axes.Y, 'Z': Axes.Z, 'TIME': Axes.TIME,
		     'CHANNEL': Axes.CHANNEL}.get(axis_type, Axes.Z)
 
def crop(ops, data, intervals):
	from net.imglib2.util import Intervals
	
	intervals_start = [data.min(d) for d in range(0, data.numDimensions())]
	intervals_end = [data.max(d) for d in range(0, data.numDimensions())]
 
	for axis_type, interval in intervals.items():
		index = data.dimensionIndex(get_axis(axis_type))
		intervals_start[index] = interval[0]
		intervals_end[index] = interval[1]
 
	intervals = Intervals.createMinMax(*intervals_start + intervals_end)
	output = ops.run("transform.crop", data, intervals, True)
	return output

rm = RoiManager.getInstance()
filename = dataset.getName()

roi_path = os.path.join(parent_dir.toString(), os.path.splitext(filename)[0] + ".zip")
image_path = os.path.join(parent_dir.toString(), os.path.splitext(filename)[0] + ".tif")

rm.runCommand("Deselect")
rm.runCommand("Save", roi_path)
print("ROIs saved at {}".format(roi_path))

# Crop the image
z_position = rm.getRoi(0).getZPosition()
intervals = {'Z': [z_position, z_position]}
output = crop(ops, dataset, intervals)
output = ops.run("transform.dropSingletonDimensionsView", output)
output = ds.create(output)

io.save(output, image_path)
print("Image saved at {}".format(image_path))