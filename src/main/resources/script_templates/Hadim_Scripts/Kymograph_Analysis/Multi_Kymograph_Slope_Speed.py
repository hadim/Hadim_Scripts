# @Float(label="Zoom to apply to kymograph", value=400, required=false) x_axis_calibration
# @Dataset dataset
# @ImageJ ij
# @Dataset dataset
# @DatasetService datasetService
# @LogService log

import os

from java.io import File

from ij import ImagePlus
from ij import IJ
from ij.measure import Measurements
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager

table = ResultsTable()

x_axis_calibration = 0.160 # um
y_axis_calibration = 5 # sec
save_roi = True
kymo_extension = ".tif"

parent_folder = File(dataset.getSource()).getParent()
kymo_folder = os.path.join(parent_folder, "Kymographs-" + os.path.splitext(dataset.getName())[0])

rm = RoiManager(True)

for dataset in datasetService.getDatasets():
	if dataset.getName().startswith("Kymograph_"):

		print(dataset.getName())

		_, roi_id, roi_name = dataset.getName().split("_")
		roi_name = roi_name.split(".")[0]
	
		#IJ.selectWindow(dataset.getName().split(".")[0])
		IJ.selectWindow(dataset.getName())
		imp = IJ.getImage()
		roi = imp.getRoi()

		if roi is None:
			continue

		width = roi.getBounds().width
		height = roi.getBounds().height
		slope = 1.0 * width / height

		width_cal = width * x_axis_calibration
		height_cal = height * y_axis_calibration
		slope_cal = 1.0 * width_cal / height_cal

		table.incrementCounter()
		table.addValue("Kymograph Name", dataset.getName())

		table.addValue("Speeds (um/min)", slope_cal * 60)
		
		table.addValue("Width", width)
		table.addValue("Height", height)
		table.addValue("Slope", slope)

		table.addValue("Width Calibrated (um)", width_cal)
		table.addValue("Height Calibrated (sec)", height_cal)
		table.addValue("Slope Calibrated (um/sec)", slope_cal)

		if save_roi:
			rm.reset()
			rm.addRoi(roi)
			roi_path = os.path.join(parent_folder, dataset.getName().replace(kymo_extension, ".zip"))
			rm.runCommand("Save", roi_path)

rm.reset()
table.show("Kymographs Statistics")
table.save(os.path.join(parent_folder, "Statistics.csv"))

		