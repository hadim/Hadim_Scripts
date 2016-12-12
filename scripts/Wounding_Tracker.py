# @Dataset data
# @ImageJ ij
# @StatusService status

from ij.plugin.frame import RoiManager
from ij.gui import Roi
from ij.gui import PolygonRoi

from net.imagej.axis import Axes

import os


dir_path = os.path.dirname(data.getSource())
roi_path = os.path.join(dir_path, "RoiSet.zip")
all_roi_path = os.path.join(dir_path, "AllRoiSet.zip")
inverted_path = os.path.join(dir_path, data.getName().replace(".tif", "_Inverted.tif"))
masked_path = os.path.join(dir_path, data.getName().replace(".tif", "_Inverted_Masked.tif"))

third_axis = Axes.TIME if data.dimension(Axes.TIME) > 1 else Axes.Z
# Get the number of frames (TIME axis)
nFrames = data.dimension(third_axis)
	
### ROIs Generation

rm = RoiManager.getInstance()
if not rm:
	rm = RoiManager()
rm.runCommand("Deselect")

if not os.path.isfile(all_roi_path):
	
	# Save ROIs
	rm.runCommand("Save", roi_path)
	
	roi_start = rm.getRoisAsArray()[0]
	roi_start.setPosition(1)
	roi_end = rm.getRoisAsArray()[1]
	roi_end.setPosition(nFrames)
	
	x_start = roi_start.getFloatPolygon().xpoints
	y_start = roi_start.getFloatPolygon().ypoints
	x_end = roi_end.getFloatPolygon().xpoints
	y_end = roi_end.getFloatPolygon().ypoints
	
	rois = []
	rois.append(roi_start)
	
	for frame in range(1, nFrames - 1):
		
		x_step = [(xx_end - xx_start) / (nFrames - 1) for xx_start, xx_end, in zip(x_start, x_end)]
		y_step = [(yy_end - yy_start) / (nFrames - 1) for yy_start, yy_end, in zip(y_start, y_end)]
		
		xx = []
		yy = []
		
		for i, (xx_start, xx_step, yy_start, yy_step) in enumerate(zip(x_start, x_step, y_start, y_step)):
			x = xx_start + frame * xx_step
			y = yy_start + frame * yy_step
			xx.append(x)
			yy.append(y)
		
		roi = PolygonRoi(xx, yy, Roi.POLYGON)
		roi.setPosition(frame + 1)
		rois.append(roi)
	
	rois.append(roi_end)
	
	# Add new polygons as ROIs in RoiManager
	rm.runCommand("Reset")
	[rm.addRoi(roi) for roi in rois]
	
	rm.runCommand("Save", all_roi_path)
else:
	rm.runCommand("Deselect")
	rm.runCommand("Reset")
	rm.runCommand("Open", all_roi_path)
	rois = rm.getRoisAsArray()

### Image Filtering

# Filter btw 10 and 40 pixels

### Invert Image for detection

if not os.path.isfile(inverted_path):
	inverted = ij.dataset().create(data)
	inverted = ij.op().run("image.invert", data, inverted)
	ij.dataset().save(inverted, inverted_path)
else:
	inverted = ij.dataset().open(inverted_path)
ij.ui().show(inverted)

### Apply mask
### For each frame apply a mask according to the ROIs

if not os.path.isfile(masked_path):
	x_index = inverted.dimensionIndex(Axes.X)
	y_index = inverted.dimensionIndex(Axes.Y)
	
	masked = ij.op().create().img(inverted)
	
	targetRA = masked.randomAccess()
	dataRA = inverted.randomAccess()
	
	for t in range(0, nFrames):
	
		roi = rois[t]
		x1 = roi.getBoundingRect().x
		y1 = roi.getBoundingRect().y
		x2 = x1 + roi.getBoundingRect().width
		y2 = y1 + roi.getBoundingRect().height
	
		for x in range(x1, x2):
			for y in range(y1, y2):
				dataRA.setPosition([x, y, t])
				targetRA.setPosition([x, y, t])
	
				if roi.contains(x, y):
					targetRA.get().set(dataRA.get())
	
		status.showStatus(t+1, nFrames, "Applying mask to image %i/%i" % (t, nFrames))
		
	ij.dataset().save(masked, masked_path)
else:
	masked = ij.dataset().open(masked_path)

ij.ui().show(masked)