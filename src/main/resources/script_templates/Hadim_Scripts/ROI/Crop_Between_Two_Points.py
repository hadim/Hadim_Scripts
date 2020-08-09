# @Integer(label="Set the box size", value=50) box_size

# @ImageJ ij
# @Dataset ds
# @OpService ops
# @DatasetService datasetService

import math

from net.imglib2.util import Intervals
from net.imagej.axis import Axes

from ij.gui import Line
from ij.plugin.frame import RoiManager

# Initialize some variables
img = ds.getImgPlus()
rois = RoiManager.getInstance().getRoisAsArray()

start = rois[0]
end = rois[1]

z_start = start.getPosition()
z_end = end.getPosition()

x_start = start.getContainedPoints()[0].x
y_start = start.getContainedPoints()[0].y

x_end = end.getContainedPoints()[0].x
y_end = end.getContainedPoints()[0].y

images = []

length = math.sqrt((x_start - x_end) ** 2 + (y_start - y_end) ** 2)
unit_length = length / (z_end - z_start)

# Iterate over each frame in z
for i, z in enumerate(range(z_start, z_end)):

	print("Processing frame %i/%i" % (i + 1, z_end - z_start))

	d = i * unit_length
	x = int(round(x_start + (d * (x_end - x_start) / length), 0))
	y = int(round(y_start + (d * (y_end - y_start) / length), 0))

	# Crop the dataset around the current centered point
	x1 = int(x - box_size / 2)
	y1 = int(y - box_size / 2)
	x2 = int(x + box_size / 2)
	y2 = int(y + box_size / 2)
	intervals = Intervals.createMinMax(x1, y1, z, x2 - 1, y2 - 1, z)
	cropped_img = ops.transform().crop(img, intervals)

	images.append(cropped_img)

cropped_images = ops.run("transform.stackView", [images])
final_dataset = datasetService.create(cropped_images)
ij.ui().show(final_dataset)
