# @Float(label="dt (sec)", required=true, value=3) dt
# @Integer(label="Number of points for Kymo Line", required=true, value=30) n_points_circle
# @Integer(label="Line Width for Kymo Line (pixel)", required=true, value=4) line_width
# @Integer(label="Radius of the line to make the kymograph (pixel)", required=true, value=25) radius
# @Float(label="Radius (for comet detection on kymograph) (pixel)", required=true, value=5) radius_detection
# @Float(label="Threshold adjuster", required=true, value=1.0) ktresh
# @Boolean(label="Show images ?", value=False) show_images
# @Boolean(label="Save intermediates images ?", value=True) save_images
# @Boolean(label="Show Results Tables ?", value=True) show_results

# @ImageJ ij
# @ImagePlus imp
# @Dataset data
# @StatusService status
# @LogService log
# @OpService ops
# @DatasetIOService io
# @LocationService loc

# Step 1 : Set image scale to 1
# Step 2 : Create Analysis directory
# Step 3 : Get user selected centrosomes and convert them to cell : each cell can have one or two centrosomes.
# Step 4 : Do Z Projection if more than one stack on the Z axis
# Step 5 : For each cell, do :
#	1. Calculate the circle points around a unique centrosome or the glasses shape points when two centrosomes.
#	2. Save the points are a ROI zip file.
#	3. Compute kymograph and save it on disk.
#	4. Subtract background on the kymograph.
#	5. Detecte spots (nucleation event) on the kymograph.
#	6. Filter spots using Otsu threshold method.
#	7. Add detected spots to ROI Manager and save as a zip file.
#	8. Compute results (nucleation rate, duration, etc)
# Step 6 : Write results to a ResultsTable and save as .csv on disk.
# Step 7 : Write parameters used to a ResultsTable and save as .csv on disk.


import os
import math
import shutil

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.img.display.imagej import ImageJFunctions

import fiji.plugin.kymographbuilder.KymographFactory as KFactory

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Spot
from fiji.plugin.trackmate.detection import DogDetectorFactory
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.util import TMUtils
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

from ij.gui import Roi
from ij.gui import PolygonRoi
from ij.gui import OvalRoi
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij import IJ

from java.awt import Polygon

from ij2_tools import do_z_projection
from ij2_tools import apply_dog_filter
from ij2_tools.geometry import get_circle_points
from ij2_tools.geometry import get_two_circles_points
from ij2_tools.utils import combinations
from ij2_tools.ij1 import get_roi_manager


## Functions

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
		

## Main Code

def main():
	# Check for points ROI on the image
	roi = imp.getRoi()
	if not roi or not roi.getType() == Roi.POINT:
		status.warn("Please selection one or more points with the multi points tools.")
		return 
	
	points = roi.getContainedPoints()
	centrosomes = [[p.x, p.y] for p in points]
	log.info("%i centrosomes detected" % len(points))

	cells = get_cells(centrosomes, radius*2)
	log.info("%i cells detected" % len(cells))
	
	# Set X and Y scale to 1
	imp.getCalibration().pixelWidth = 1
	imp.getCalibration().pixelHeight = 1
	
	# Init path and create the Analysis folder
	fname = data.getSource()
	dir_path = os.path.dirname(fname)
	
	analysis_dir = os.path.join(dir_path, "Analysis_Nucleation")
	if not os.path.exists(analysis_dir):
		os.makedirs(analysis_dir)
	
	# Do Z Projection
	z_projected = do_z_projection(ij, data, save=save_images, output_dir=analysis_dir)
	if show_images:
		ij.ui().show("z_projected", z_projected)

	# Apply DOG Filtering
	#sigma1 = 4.2
	#sigma2 = 1.25
	#dog = apply_dog_filter(ij, z_projected, sigma1, sigma2, save=save_images, output_dir=analysis_dir)
	#if show_images:
	#	ij.ui().show("dog", dog)

	preprocessed_dataset = z_projected

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
			points = get_two_circles_points(cen1_x, cen1_y, cen2_x, cen2_y, radius, n=n_points_circle)
		else:
			# Draw line around the unique centrosome
			points = get_circle_points(cen1_x, cen1_y, radius=radius, n=n_points_circle)
			
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
	
		kymo_fname = os.path.join(analysis_dir, name + ".tif")
		kymograph_imp = ImageJFunctions.wrap(kymograph, name + ".tif")
		ij.ui().show(name + ".tif", kymograph_imp)
	
		# Do background substraction
		IJ.run(kymograph_imp, "Subtract Background...", "rolling=" + str(50))
			
		# Save the kymo
		IJ.save(kymograph_imp, kymo_fname) 
		log.info("Saving Kymograph for Centrosome #%i to %s" % (i+1, kymo_fname))
	
		# Track spots
		kymograph_imp.getCalibration().pixelWidth = 1
		kymograph_imp.getCalibration().pixelHeight = 1
		
		model = Model()
		model.setLogger(Logger.IJ_LOGGER)
		
		settings = Settings()
		settings.setFrom(kymograph_imp)
		
		settings.detectorFactory = DogDetectorFactory()
		settings.detectorSettings = {
			'DO_SUBPIXEL_LOCALIZATION' : True,
			'RADIUS' : radius_detection / 2.0,
			'TARGET_CHANNEL' : 1,
			'THRESHOLD' : 0.,
			'DO_MEDIAN_FILTERING' : True,
		}
		
		trackmate = TrackMate(model, settings)
		trackmate.checkInput()
		trackmate.execDetection()
		trackmate.execInitialSpotFiltering()
		trackmate.computeSpotFeatures(True)
		trackmate.execSpotFiltering(True)
		
		# Otsu filtering by quality features
		quality = [spot.getFeatures()['QUALITY'] for spot in model.getSpots().iterator(True)]
		threshold = TMUtils.otsuThreshold(quality)
		threshold *= ktresh
		featureFilter = FeatureFilter(Spot.QUALITY, threshold, True)
		spots = model.getSpots()
		spots.filter(featureFilter)
		spots = spots.crop()
		model.setSpots(spots, True)

		# Create, display and save ROIs
		if model.getSpots().getNSpots(False) > 0:
			rm = get_roi_manager(new=True)
			spots = []
			for spot in model.getSpots().iterator(False):
				spots.append(spot)
			
				x = spot.getFeatures()['POSITION_X']
				y = spot.getFeatures()['POSITION_Y']
				spot_radius = spot.getFeatures()['RADIUS']
			
				spot_roi = OvalRoi(x - spot_radius/2, y - spot_radius/2, spot_radius * 2, spot_radius * 2)
				rm.addRoi(spot_roi)
		
			spots_fname = os.path.join(analysis_dir, name + "_Comets_ROI.zip")
			rm.runCommand("Save", spots_fname)
			log.info("Saving detected spots to %s" % (spots_fname))
		else:
			spots = []

		# Calculate the results
		timepoints = data.dimension(data.dimensionIndex(Axes.TIME))
		duration = timepoints * dt
		nucleation_number = len(spots)
		nucleation_rate = (nucleation_number / duration) * 60

		result = {}
		result['fname'] = os.path.basename(dir_path)
		result['cell_id'] = i + 1
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

		if not show_images:
			kymograph_imp.close()

	if not show_images:
		IJ.selectWindow("Z_Projection.tif")
		IJ.getImage().close()
	rm = get_roi_manager(new=True)
	rm.runCommand("Reset")
	
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
	log.info("Saving final results to %s" % (result_fname))

	# Write parameters in csv
	table = ResultsTable() 
	table.incrementCounter()
	table.addValue('Value', "dt")
	table.addValue('Key', dt)
	table.incrementCounter()
	table.addValue('Value', "n_points_circle")
	table.addValue('Key', n_points_circle)
	table.incrementCounter()
	table.addValue('Value', "line_width")
	table.addValue('Key', line_width)
	table.incrementCounter()
	table.addValue('Value', "radius")
	table.addValue('Key', radius)
	table.incrementCounter()
	table.addValue('Value', "radius_detection")
	table.addValue('Key', radius_detection)
	para_fname = os.path.join(analysis_dir, "Parameters.csv")
	table.save(para_fname)
	log.info("Saving parameters to %s" % (para_fname))
	
main()
