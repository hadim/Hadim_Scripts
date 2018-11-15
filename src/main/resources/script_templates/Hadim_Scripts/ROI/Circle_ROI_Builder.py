# @Float(label="Diameter of the circle ROI (pixel)", value=7) circle_diam

from ij.plugin.frame import RoiManager
from ij.gui import OvalRoi

rm = RoiManager.getInstance()

new_rois = []
for roi in rm.getRoisAsArray():
	assert roi.getTypeAsString() == 'Point', "ROI needs to be a point"
	x_center = roi.getContainedPoints()[0].x - (circle_diam / 2) + 0.5
	y_center = roi.getContainedPoints()[0].y - (circle_diam / 2) + 0.5
	new_roi = OvalRoi(x_center, y_center, circle_diam, circle_diam)
	new_rois.append(new_roi)

rm.reset()

for new_roi in new_rois:
	rm.addRoi(new_roi)

print("Done")
