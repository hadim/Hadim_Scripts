# @Float(label="dt (sec)", required=true, value=3, stepSize=0.1) dt
# @Float(label="Pixel Size (um)", required=true, value=0.089, stepSize=0.01) pixel_size
# @Float(label="PREPROCESSING | DOG Sigma 1 (um)", required=false, value=0.400, stepSize=0.01) sigma1_um
# @Float(label="PREPROCESSING | DOG Sigma 2 (um)", required=true, value=0.120, stepSize=0.01) sigma2_um
# @Float(label="KYMOGRAPH | Circle Diameter (um)", required=true, value=4.5, stepSize=0.1) diameter_kymograph_um
# @Float(label="DETECTION | Spot Diameter", required=true, value=0.400, stepSize=0.01) diameter_spot_detection_um
# @Float(label="DETECTION | Threshold", required=true, value=25, stepSize=1) threshold_detection
# @String(label="Show images ?", style="radioButtonHorizontal", choices={ "All","Only Kymographs", "None" }, value="None") show_images
# @Boolean(label="Save intermediates images ?", value=True) save_images
# @Boolean(label="Show Results Tables ?", value=True) show_results

# @ImageJ ij
# @Dataset data
# @ImagePlus imp
# @StatusService status
# @LogService logger
# @OpService ops
# @DatasetIOService io
# @LocationService loc

# Step 1 : Convert parameters to pixel
# Step 2 : Create Analysis directory
# Step 3 : Get user selected centrosomes and convert them to cell : each cell can have one or two centrosomes.
# Step 4 : Image preprocessing :
#	1. Do Z Projection if more than one stack on the Z axis
#	2. Aplly DOG filtering (band pass filter on the object of interest
#   3. For each frame : subtract frame t+1 to frame t
# Step 5 : For each cell, do :
#	1. Calculate the circle points around a unique centrosome or the glasses shape points when two centrosomes.
#	2. Save the ROI around the centrosomes as a zip file.
#	3. Compute kymograph and save it.
#	4. Subtract background on the kymograph.
#	5. Detecte spots (nucleation event) on the kymograph.
#	6. Filter spots using Otsu threshold method.
#	7. Add detected spots to ROI Manager and save as a zip file.
#	8. Compute results (nucleation rate, duration, etc)
# Step 6 : Write results to a ResultsTable and save as .csv on disk.
# Step 7 : Write parameters used to a ResultsTable and save as .csv on disk.

import sys; sys.modules.clear()

import os
import math
import shutil
import csv

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.img.display.imagej import ImageJFunctions
from net.imglib2.view import Views
from net.imglib2.img import ImgView

import fiji.plugin.kymographbuilder.KymographFactory as KFactory

from ij.gui import Roi
from ij.gui import PolygonRoi
from ij.gui import OvalRoi
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij import IJ

from java.awt import Polygon

from ij2_tools import do_projection
from ij2_tools import apply_dog_filter
from ij2_tools.subtract import subtract_consecutive_frames
from ij2_tools.geometry import get_circle_points
from ij2_tools.geometry import get_two_circles_points
from ij2_tools.utils import combinations
from ij2_tools.ij1 import get_roi_manager
from ij2_tools.spot_detector import dog_detector
from ij2_tools import print_info


## Fixed parameters

n_points_circle = 30
line_width = 4


## Functions

def log(message):
	print(message)
	status.showStatus(message)
	logger.info(message)

def get_cells(centrosomes, cen_threshold_distance):
	# Check centrosomes close together and add them as a 'cell' dict
	cells = []
	used_centrosomes = []
	for cen1, cen2 in combinations(centrosomes, 2):
		d = math.sqrt((cen1[0] - cen2[0])**2 + (cen1[1] - cen2[1])**2)

		if d < cen_threshold_distance:
			cell = {}
			cell['double'] = True
			cell['cen1'] = cen1
			cell['cen2'] = cen2
			cell['distance'] = d
			cells.append(cell)
			used_centrosomes += [cen1, cen2]

	# Add others "alone" centrosomes as a 'cell' dict
	for cen in centrosomes:
		if cen not in used_centrosomes:
			cell = {}
			cell['double'] = False
			cell['cen1'] = cen
			cell['cen2'] = None
			cell['distance'] = 0
			cells.append(cell)
	return cells

def add_row(table, value, key):
		table.incrementCounter()
		table.addValue('Value', value)
		table.addValue('Key', str(key))

def get_points_in_result(result_file):
	points = []
	f = open(result_file, 'rb')
	reader = csv.reader(f)
	for i, row in enumerate(reader):
		if i > 0:
			points.append([float(row[7]), float(row[8])])
			if row[9] != 'None':
				points.append([float(row[9]), float(row[10])])
	f.close()
	return points

## Main Code

def main():

	fname = data.getSource()
	dir_path = os.path.dirname(fname)
	analysis_dir = os.path.join(dir_path, "Analysis_Nucleation")

	## Convert parameters in pixel
	message = "Parameters scaled in pixel : \n"
	sigma1 = sigma1_um / pixel_size
	message += "DOG Sigma 1 : %0.2f\n" % sigma1
	sigma2 = sigma2_um / pixel_size
	message += "DOG Sigma 2 : %0.2f\n" % sigma2
	diameter_kymograph = diameter_kymograph_um / pixel_size
	radius_kymograph = diameter_kymograph / 2
	message += "Circle Diameter : %0.2f\n" % diameter_kymograph
	diameter_spot_detection = diameter_spot_detection_um / pixel_size
	radius_spot_detection = diameter_spot_detection / 2
	message += "Spot Diameter : %0.2f" % diameter_spot_detection
	log(message)

	# Check for points ROI on the image
	roi = imp.getRoi()
	if not roi or not roi.getType() == Roi.POINT:
		centrosomes = get_points_in_result(os.path.join(analysis_dir, "Results.csv"))
	else:
		points = roi.getContainedPoints()
		centrosomes = [[p.x, p.y] for p in points]

	if not centrosomes:
		status.warn("Please selection one or more points with the multi points tools.")
		return

	# Get centrosomes positions
	log("%i centrosomes detected" % len(centrosomes))

	# Get cell objects
	cells = get_cells(centrosomes, diameter_kymograph)
	log("%i cells detected" % len(cells))

	# Init path and create the Analysis folder
	if not os.path.exists(analysis_dir):
		os.makedirs(analysis_dir)

	# Do Z Projection
	z_projected = do_projection(ij, data, axis_type="Z", method="Max", save=save_images, output_dir=analysis_dir)
	if show_images == "All":
		ij.ui().show("z_projected", z_projected)

	# Apply DOG Filtering
	dog = apply_dog_filter(ij, z_projected, sigma1, sigma2, save=save_images, output_dir=analysis_dir)
	if show_images == "All":
		ij.ui().show("dog", dog)

	# Subtract frame t+1 to frame for each frames
	subtracted = subtract_consecutive_frames(ij, dog, save=save_images, output_dir=analysis_dir)
	if show_images == "All":
		ij.ui().show("subtracted", subtracted)

	preprocessed_dataset = subtracted

	# Iterate over all centrosomes
	results = []
	for i, cell in enumerate(cells):

		name = "Cell_%i_Kymograph" % (i+1)

		cen1_x = cell['cen1'][0]
		cen1_y = cell['cen1'][1]
		cen2_x = None
		cen2_y = None

		if cell['double']:
			cen2_x = cell['cen2'][0]
			cen2_y = cell['cen2'][1]
			# Draw line around both centrosomes
			points = get_two_circles_points(cen1_x, cen1_y, cen2_x, cen2_y, radius=radius_kymograph, n=n_points_circle)
		else:
			# Draw line around the unique centrosome
			points = get_circle_points(cen1_x, cen1_y, radius=radius_kymograph, n=n_points_circle)

		xpoints, ypoints = list(zip(*points))
		circle = PolygonRoi(xpoints, ypoints, Roi.POLYLINE)
		circle.setStrokeWidth(line_width)
		rm = get_roi_manager(new=True)
		rm.addRoi(circle)

		# Save the ROI
		rm.runCommand("Save", os.path.join(analysis_dir, name + "_Line_ROI.zip"))
		rm.runCommand("Reset")

		# Create kymograph
		kfactory = KFactory(ij.context(), preprocessed_dataset, circle)
		kfactory.build()
		kymograph = kfactory.getKymograph()

		# Do background substraction
		# TODO

		kymo_fname = os.path.join(analysis_dir, name + ".tif")
		log("Saving Kymograph for Centrosome #%i to %s" % (i+1, kymo_fname))
		kymograph.setSource(kymo_fname)
		ij.io().save(kymograph, kymo_fname)

		if show_images in ["All","Only Kymographs"]:
			ij.ui().show(kymo_fname, kymograph)

		# Remove a possible singleton dimension...
		kymograph_view = ij.op().run("transform.dropSingletonDimensionsView", kymograph)
		kymograph = ImgView.wrap(kymograph_view, ij.op().run("create.imgFactory", kymograph))
		kymograph = ij.dataset().create(kymograph)

		# Track spots
		spots = dog_detector(ij, kymograph, radius=radius_spot_detection, relative_threshold=None,
							 absolute_threshold=threshold_detection, doSubpixel=True, doMedian=False,
							 calibration=[1, 1, 1])

		if len(spots) > 0:
			rm = get_roi_manager(new=True)
			for spot in spots:
				rm.addRoi(spot)

			spots_fname = os.path.join(analysis_dir, name + "_Comets_ROI.zip")
			rm.runCommand("Save", spots_fname)
			log("Saving detected spots to %s" % (spots_fname))

		# Calculate the results
		timepoints = data.dimension(data.dimensionIndex(Axes.TIME))
		duration = timepoints * dt
		nucleation_number = len(spots)
		nucleation_rate = (nucleation_number / duration) * 60

		result = {}
		result['fname'] = os.path.basename(dir_path)
		result['cell_id'] = i + 1
		result['double'] = cell['double']
		result['cen1_x'] = cell['cen1'][0]
		result['cen1_y'] = cell['cen1'][1]
		if cell['double']:
			result['cen2_x'] = cell['cen2'][0]
			result['cen2_y'] = cell['cen2'][1]
		else:
			result['cen2_x'] = None
			result['cen2_y'] = None
		result['nucleation_number'] = nucleation_number
		result['duration'] = duration
		result['nucleation_rate'] = nucleation_rate
		results.append(result)

		log("## Centrosome #%i : %f nucleations/min " % (i+1, result['nucleation_rate']))

	# Clean Roi Manager
	get_roi_manager(new=True)

	# Write results in csv
	table = ResultsTable()
	for result in results:
		table.incrementCounter()
		table.addValue('Filename', result['fname'])
		table.addValue('Cell ID #', str(result['cell_id']))
		table.addValue('Nucleation Rate (min-1)', str(result['nucleation_rate']))
		table.addValue('Time (s)', str(result['duration']))
		table.addValue('Nucleation Events', str(result['nucleation_number']))
		table.addValue('double', str(result['double']))
		table.addValue('cen1_x', str(result['cen1_x']))
		table.addValue('cen1_y', str(result['cen1_y']))
		table.addValue('cen2_x', str(result['cen2_x']))
		table.addValue('cen2_y', str(result['cen2_y']))
	if show_results:
		table.show('Results Nucleation Rate')
	result_fname = os.path.join(analysis_dir, "Results.csv")
	table.save(result_fname)
	log("Saving final results to %s" % (result_fname))

	# Write parameters in csv
	table = ResultsTable()
	add_row(table, "dt", dt)
	add_row(table, "pixel_size", pixel_size)
	add_row(table, "sigma1", sigma1 * pixel_size)
	add_row(table, "sigma2", sigma2 * pixel_size)
	add_row(table, "diameter_kymograph", diameter_kymograph * pixel_size)
	add_row(table, "diameter_spot_detection", diameter_spot_detection * pixel_size)
	add_row(table, "threshold_detection", threshold_detection)
	para_fname = os.path.join(analysis_dir, "Parameters.csv")
	table.save(para_fname)
	log("Saving parameters to %s" % (para_fname))

main()
