# @Context context
# @ImageJ ij
# @Dataset dataset
# @DatasetService datasetService
# @LogService log

import os

from java.io import File

from ij import ImagePlus
from ij import IJ
from ij.plugin.frame import RoiManager


def log_info(message):
	log.info(message)
	print(message)

kymo_extension = ".tif"

parent_folder = File(dataset.getSource()).getParent()

rm = RoiManager(True)

for dataset in datasetService.getDatasets():
	if dataset.getName().startswith("Kymograph_"):

		_, roi_id, roi_name = dataset.getName().split("_")
		roi_name = roi_name.split(".")[0]
	
		#IJ.selectWindow(dataset.getName().split(".")[0])
		IJ.selectWindow(dataset.getName())
		imp = IJ.getImage()
		roi = imp.getRoi()

		if roi is None:
			log_info("No ROI for %s" % dataset.getName())
			
			continue

		rm.reset()
		rm.addRoi(roi)
		roi_path = os.path.join(parent_folder, dataset.getName().replace(kymo_extension, ".zip"))
		rm.runCommand("Save", roi_path)

		log_info("ROI saved at %s" % roi_path)

rm.reset()

		