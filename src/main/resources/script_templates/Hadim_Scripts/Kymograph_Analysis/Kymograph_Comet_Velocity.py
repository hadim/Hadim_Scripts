# @Float(label="Time Interval (s)", value=1) dt
# @Float(label="Pixel Length (um)", value=1) pixel_length
# @Float(label="Minimal duration of a run (s)", value=0) minimal_duration
# @Float(label="Minimal length of a run (um)", value=0) minimal_length
# @Boolean(label="Do you want to save result file ?", required=False, value=False) save_results
# @Boolean(label="Do you want to save ROI file ?", required=False, value=False) save_roi
# @Boolean(label="Assume x is length and y is time ?", value=True) is_x_length
# @ImageJ ij
# @ImagePlus img
# @Dataset data
# @StatusService status

import os
import math

from ij.plugin.frame import RoiManager
from ij.measure import ResultsTable
from ij.gui import Roi

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

	rt = ResultsTable()

	for i, roi in enumerate(rm.getRoisAsArray()):

		if roi.getType() == Roi.LINE:
			x1 = roi.x1
			y1 = roi.y1
			x2 = roi.x2
			y2 = roi.y2

		elif roi.getType() == Roi.FREELINE or roi.getType() == Roi.POLYLINE:
			xpoints = roi.getInterpolatedPolygon(1, True).xpoints
			ypoints = roi.getInterpolatedPolygon(1, True).ypoints

			# Don't use this ROI if it has only one point
			if len(xpoints) < 2 or len(xpoints) < 2:
				continue
			
			x1 = xpoints[0]
			y1 = ypoints[0]
			x2 = xpoints[-1]
			y2 = ypoints[-1]

		else:
			continue

		if is_x_length:
			x1, y1 = y1, x1
			x2, y2 = y2, x2

		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1

		# Compute line features
		run_length = (y1 - y2) * pixel_length
		run_duration = (x2 - x1) * dt
		run_speed = run_length / run_duration

		# Filter line/track according to length and duration
		if abs(run_duration) < minimal_duration:
			continue
		if abs(run_length) < minimal_length:
			continue

		# Save it to an IJ ResultsTable
		rt.incrementCounter()
		rt.addValue("Track ID", i+1)
		rt.addValue("ROI ID", roi.name)
		rt.addValue("Track  (um)", abs(run_length))
		rt.addValue("Track duration (s)", abs(run_duration))
		rt.addValue("Track speed (um/s)", run_speed)
		rt.addValue("x1", x1)
		rt.addValue("y1", y1)
		rt.addValue("x2", x2)
		rt.addValue("y2", y2)	
	
	rt.show('Comet Analysis Results for "%s"' % name)

	if save_results:
		results_path = roi_path = os.path.splitext(fname)[0] + ".Results.csv"
		rt.save(results_path)

	if save_roi:
		roi_path = os.path.splitext(fname)[0] + ".ROI.zip"
		rm.runCommand("Save", roi_path);

main()