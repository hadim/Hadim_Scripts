# @Boolean(label="Reset ROI Manager") reset_roi
# @File(label="Select a directory", style="directory") parent_dir
# @Dataset dataset
# @DatasetIOService io

import os
from ij.plugin.frame import RoiManager

rm = RoiManager.getInstance()
filename = dataset.getName()

roi_path = os.path.join(parent_dir.toString(), os.path.splitext(filename)[0] + ".zip")
image_path = os.path.join(parent_dir.toString(), os.path.splitext(filename)[0] + ".tif")

rm.runCommand("Deselect")
rm.runCommand("Save", roi_path)
print("ROIs saved at {}".format(roi_path))

io.save(dataset, image_path)
print("Image saved at {}".format(image_path))