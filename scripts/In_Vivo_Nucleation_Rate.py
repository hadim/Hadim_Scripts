# @Float(label="dt (sec)", required=true, value=3) dt
# @Integer(label="Number of points for Kymo Line", required=true, value=30) n_points_circle
# @Integer(label="Line Width for Kymo Line (pixel)", required=true, value=4) line_width
# @Integer(label="Radius of the line to make the kymograph (pixel)", required=true, value=25) radius
# @Float(label="Radius (for comet detection on kymograph) (pixel)", required=true, value=5) radius_detection
# @Boolean(label="Close all opened window after processing ?", value=False) close_windows
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

from ij.plugin.frame import RoiManager
from ij.gui import Roi
from ij.gui import PolygonRoi
from ij.gui import OvalRoi
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij import IJ
from ij.plugin.filter import DifferenceOfGaussians

from java.awt import Polygon

## Functions

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

def z_project(data):
	z_dim = data.dimensionIndex(Axes.Z)
	if data.dimension(z_dim) == 1:
		return data
	projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != z_dim]
	axis = [data.axis(d) for d in range(0, data.numDimensions()) if d != z_dim]
	z_projected = ops.create().img(projected_dimensions)
	max_op = ops.op(Ops.Stats.Max, data)
	ops.transform().project(z_projected, data, max_op, z_dim)
	z_projected = ij.dataset().create(z_projected)
	z_projected.setAxes(axis)
	return z_projected


def in_circle(point, center, radius):
	return ((point[0] - center[0])**2 + (point[1] - center[1])**2) < radius**2
	

def get_circle_points(x_center, y_center, radius, n=20):
		points = []
		for i in range(0, n+1):
			x = math.cos(2*math.pi/n*i) * radius + x_center
			y =  math.sin(2*math.pi/n*i) * radius + y_center
			points.append([x, y])
		return points
	
	
def get_two_circles_points(x1, y1, x2, y2, radius, n=20):
	xcen, ycen = (x1 + x2) / 2, (y1 + y2) / 2
	
	points1 = get_circle_points(x1, y1, radius, n=n)
	points2 = get_circle_points(x2, y2, radius, n=n)
	
	points1_in_circle_index = [i for i, point in enumerate(points1) if in_circle(point, [x2, y2], radius)]
	points2_in_circle_index = [i for i, point in enumerate(points2) if in_circle(point, [x1, y1], radius)]
	
	points1 = points1[points1_in_circle_index[-1] + 1:] + points1[:points1_in_circle_index[0]]
	points2 = points2[points2_in_circle_index[-1] + 1:] + points2[:points2_in_circle_index[0]]

	return points1 + points2


def get_roi_manager(new=False):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm

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
	else:
		try:
			for root, dirs, files in os.walk(analysis_dir):
			    for f in files:
			        os.remove(os.path.join(root, f))
			    for d in dirs:
			        shutil.rmtree(os.path.join(root, d))
		except OSError:
			pass
	
	# Do Z Projection
	z_projected = z_project(data)
	ij.ui().show("Z_Projection.tif", z_projected)
	z_fname = os.path.join(analysis_dir, "Z_Projection.tif")
	io.save(z_projected, z_fname)
	log.info("Saving Z Projection to %s" % (z_fname))

	# Apply DOG Filtering
	sigma1 = 4.2
	sigma2 = 1.25
	# TODO

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

		if close_windows:
			kymograph_imp.close()

	if close_windows:
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
