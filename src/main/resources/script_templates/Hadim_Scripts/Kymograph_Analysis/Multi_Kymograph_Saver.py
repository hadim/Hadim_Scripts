# @Context context
# @ImageJ ij
# @Dataset dataset
# @DatasetService datasetService
# @LogService log

import os

from ij import ImagePlus
from ij import IJ
from ij.plugin.frame import RoiManager
from ij import WindowManager

def log_info(message):
	log.info(message)
	print(message)

kymo_extension = ".tif"

parent_folder = os.path.dirname(dataset.getSource())
kymo_folder = os.path.join(parent_folder, "Kymographs-" + os.path.splitext(dataset.getName())[0])

rm = RoiManager(True)
rm.runCommand("Reset")

# Ugly IJ1 hack but no choice for now...
for dataset_name in WindowManager.getImageTitles():

	if dataset_name.startswith("Kymograph_"):

		_, roi_id, roi_name = dataset_name.split("_")
		roi_name = roi_name.split(".")[0]
		
		if dataset_name.endswith(kymo_extension):
			roi_path = os.path.join(parent_folder, kymo_folder, dataset_name.replace(kymo_extension, ".zip"))
		else:
			roi_path = os.path.join(parent_folder, kymo_folder, dataset_name + ".zip")

		IJ.selectWindow(dataset_name)
		imp = IJ.getImage()
		roi = imp.getRoi()

		if roi is None:
			log_info("No ROI for %s" % dataset_name)
			continue

		rm.runCommand("Reset")
		rm.addRoi(roi)
		rm.runCommand("Save", roi_path)

		log_info("ROI saved at %s" % roi_path)

rm.runCommand("Reset")

		