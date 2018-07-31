# @Boolean(label="Reset ROI Manager") reset_roi
# @Dataset dataset

# Save all ROIs in the Roi Manager in a zip file
# within the same folder of the image with a zip extension.

import os
from ij.plugin.frame import RoiManager

rm = RoiManager.getInstance()

filename = dataset.getName()

# getSource() returns a weird path. I need to use replace().
parent_folder = dataset.getSource().replace(filename, "")
roi_path = os.path.join(parent_folder, os.path.splitext(filename)[0] + ".zip")

rm.runCommand("Deselect")
rm.runCommand("Save", roi_path)
print("ROIs saved at {}".format(roi_path))
