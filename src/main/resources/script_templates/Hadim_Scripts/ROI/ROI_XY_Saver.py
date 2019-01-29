# @Dataset dataset
# This script has been originally created by Malina Iwanski.

import os
import csv

from ij.plugin.frame import RoiManager

rm = RoiManager.getInstance()
numrois = rm.getCount()

filename = dataset.getName()
parent_folder = dataset.getSource().replace(filename, "")
coords_path = os.path.join(parent_folder, os.path.splitext(filename)[0] + ".csv")

headers = ['id', 'roi_name', 'x', 'y']
csvfile = open(coords_path, 'w')
csvwriter = csv.DictWriter(csvfile, delimiter=',', quotechar='"', fieldnames=headers)
csvwriter.writeheader()

for i, roi in enumerate(rm.getRoisAsArray()):
	xx = roi.getFloatPolygon().xpoints
	yy = roi.getFloatPolygon().ypoints

	for x, y in zip(xx, yy):
		data = {}
		data['id'] = i
		data['roi_name'] = roi.getName()
		data['x'] = x
		data['y'] = y
		csvwriter.writerow(data)

csvfile.close()
rm.runCommand("Deselect")

print("ROI coordinates saved at %s" % coords_path)
