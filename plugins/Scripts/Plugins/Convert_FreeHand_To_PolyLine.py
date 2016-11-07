# @Integer(label="Points Density", value=10) points_density
# @StatusService status

from ij.plugin.frame import RoiManager
from ij.gui import Roi
from ij.gui import PolygonRoi


def main():
	
	rm = RoiManager.getInstance()
	rm.runCommand("Deselect")
	if not rm:
		status.warn("Use ROI Manager tool (Analyze>Tools>ROI Manager...).")
		return False
	
	if len(rm.getRoisAsArray()) == 0:
		status.warn("ROI Manager does not have any ROI.")
		return False

	newRois = []
	for i, roi in enumerate(rm.getRoisAsArray()):
		
		# Select only FreeLine/FreeHand ROIs
		if roi.type == Roi.FREELINE:
		
			x = []
			y = []
			xRoi = roi.getPolygon().xpoints
			yRoi = roi.getPolygon().ypoints
			
			for j in range(0, roi.getNCoordinates(), points_density):
				x.append(xRoi[j])
				y.append(yRoi[j])
	
			# Delete old ROI
			rm.select(i)
			rm.runCommand("Delete")

			newRoi = PolygonRoi(x, y, Roi.POLYLINE)
			newRois.append(newRoi)

	for roi in newRois:
		# Add new ROI
		rm.addRoi(roi)
	
	rm.runCommand("Deselect")

main()
			