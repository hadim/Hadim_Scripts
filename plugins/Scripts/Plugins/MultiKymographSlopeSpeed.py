# @Context context
# @DatasetService datasetService
# @ImageDisplayService imgDisplayService
# @Dataset dataset
# @ImageJ ij
# @LogService log

import os
"""
for dataset in datasetService.getDatasets():
	if dataset.getName().startswith("Kymograph_"):
		print(dataset)"""

print(imgDisplayService.getImageDisplays())
for display in imgDisplayService.getImageDisplays():
	print(display.getActiveView().getData())

print(imgDisplayService.getActiveImageDisplay())