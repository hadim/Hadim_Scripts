# @ImageJ ij
# @Dataset data

from net.imagej.axis import Axes

from net.imglib2.algorithm.labeling.ConnectedComponents import StructuringElement
from net.imglib2.roi.labeling import LabelRegions

from ij.gui import PointRoi
from ij.plugin.frame import RoiManager

def get_roi_manager(new=False):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm

img = data.getImgPlus()

labeled_img = ij.op().run("cca", img, StructuringElement.EIGHT_CONNECTED)

regions = LabelRegions(labeled_img)
region_labels = list(regions.getExistingLabels())

print("%i regions/particles detected" % len(region_labels))

# Now use IJ1 RoiManager to display the detected regions

rm = get_roi_manager(new=True)
for label in region_labels:

	region = regions.getLabelRegion(label)

	center = region.getCenterOfMass()
	x = center.getDoublePosition(0)
	y = center.getDoublePosition(1)

	roi = PointRoi(x, y)
	if center.numDimensions() >= 3:
		z = center.getDoublePosition(2)
		roi.setPosition(int(z))
	
	rm.addRoi(roi)