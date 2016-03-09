# @Float(label="Time Interval (s)", value=1) dt
# @Float(label="Pixel Length (um)", value=1) pixel_length
# @Boolean(label="Do you want to save results files ?", required=False) save_results
# @Boolean(label="Do you want to save ROI files ?", required=False) save_roi
# @ImageJ ij
# @ImagePlus img
# @Dataset data
# @StatusService status

import os
import math

from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable

def main():
	# Get image processor and imgplus
	imp = img.getProcessor()
	imgp = data.getImgPlus()
	fname = data.getSource()
	name  = os.path.basename(fname)
	
	# Get ROIManager
	rm = RoiManager.getInstance()
	if not rm:
		status.warn("Use ROI Manager tool (Analyze>Tools>ROI Manager...).")
		return False

	if len(rm.getRoisAsArray()) == 0:
		status.warn("ROI Manager does not have any ROI.")
		return False
		
	if save_roi:
		roi_path = os.path.splitext(fname)[0] + ".ROI.zip"
		rm.runCommand("Save", roi_path);

	rt = ResultsTable()

	for i, roi in enumerate(rm.getRoisAsArray()):
		x1 = roi.x1
		y1 = roi.y1
		x2 = roi.x2
		y2 = roi.y2

		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1

		run_length = roi.y1 - roi.y2
		run_duration = roi.x2 - roi.x1
		run_speed = run_length / run_duration

		rt.incrementCounter()
		rt.addValue("Track ID", i+1)
		rt.addValue("Track Length (um)", run_length)
		rt.addValue("Track duration (s)", run_duration)
		rt.addValue("Track speed (um/s)", run_speed)
	
	results_path = roi_path = os.path.splitext(fname)[0] + ".Results.csv"
	rt.save(results_path)
	rt.show('Comet Analysis Results for "%s"' % name)

main()