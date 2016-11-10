# @Float(label="dt (sec)", required=true, value=3) dt
# @Integer(label="Number of points for Kymo Line", required=true, value=20) n_points_circle
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

import os
import math

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.img.display.imagej import ImageJFunctions

import fiji.plugin.kymographbuilder.KymographFactory as KFactory

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import DogDetectorFactory

import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

from ij.plugin.frame import RoiManager
from ij.gui import Roi
from ij.gui import PolygonRoi
from ij.gui import OvalRoi
from ij.measure import Calibration
from ij.measure import ResultsTable
from ij import IJ

from java.awt import Polygon

## Functions

def z_project(data):
	z_dim = data.dimensionIndex(Axes.Z)
	projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != z_dim]
	axis = [data.axis(d) for d in range(0, data.numDimensions()) if d != z_dim]
	z_projected = ops.create().img(projected_dimensions)
	max_op = ops.op(Ops.Stats.Max, data)
	ops.transform().project(z_projected, data, max_op, z_dim)
	z_projected = ij.dataset().create(z_projected)
	z_projected.setAxes(axis)
	return z_projected


def get_circle_points(x_center, y_center, radius, n=20):
	xpoints = []
	ypoints = []
	for i in range(0, n+1):
		x = math.cos(2*math.pi/n*i) * radius + x_center
		y =  math.sin(2*math.pi/n*i) * radius + y_center
		xpoints.append(int(x))
		ypoints.append(int(y))
	return xpoints[:-1], ypoints[:-1]


def get_roi_manager(new=False):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm
		
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
	
	# Set X and Y scale to 1
	imp.getCalibration().pixelWidth = 1
	imp.getCalibration().pixelHeight = 1
	
	# Init path and create the Analysis folder
	fname = data.getSource()
	dir_path = os.path.dirname(fname)
	
	analysis_dir = os.path.join(dir_path, "Analysis")
	if not os.path.exists(analysis_dir):
		os.makedirs(analysis_dir)
	
	# Do Z Projection
	z_projected = z_project(data)
	ij.ui().show("Z_Projection.tif", z_projected)
	z_fname = os.path.join(analysis_dir, "Z_Projection.tif")
	io.save(z_projected, z_fname)
	log.info("Saving Z Projection to %s" % (z_fname))

	# Iterate over all centrosomes
	results = []
	for i, (cen_x, cen_y) in enumerate(centrosomes[:]):
	
		name = "Cen%i_Kymograph" % (i+1)
	
		# Draw line around the centrosomes
		xpoints, ypoints = get_circle_points(cen_x, cen_y, radius=radius, n=n_points_circle)
		circle = PolygonRoi(xpoints, ypoints, Roi.POLYLINE)
		circle.setStrokeWidth(line_width)
		rm = get_roi_manager(new=True)
		rm.addRoi(circle)
	
		# Save the ROI
		rm.runCommand("Save", os.path.join(analysis_dir, name + "_Line_ROI.zip"))
		rm.runCommand("Reset")
	
		# Create kymograph
		kfactory = KFactory(ij.context(), z_projected, circle)
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
			'RADIUS' : radius_detection,
			'TARGET_CHANNEL' : 1,
			'THRESHOLD' : 0.,
			'DO_MEDIAN_FILTERING' : True,
		}
		
		filter1 = FeatureFilter('QUALITY', 0, True)
		#settings.addSpotFilter(filter1)
		
		trackmate = TrackMate(model, settings)
		trackmate.checkInput()
		trackmate.execDetection()
		trackmate.execInitialSpotFiltering()
		trackmate.computeSpotFeatures(True)
		trackmate.execSpotFiltering(True)
		
		# Do auto threshold
		# threshold = TMUtils.otsuThreshold( valuesMap.get( selectedFeature ) )
		
		rm = get_roi_manager(new=True)
		
		spots = []
		for spot in model.getSpots().iterator(True):
			spots.append(spot)
		
			x = spot.getFeatures()['POSITION_X']
			y = spot.getFeatures()['POSITION_Y']
			spot_radius = spot.getFeatures()['RADIUS']
		
			spot_roi = OvalRoi(x - spot_radius/2, y - spot_radius/2, spot_radius, spot_radius)
			rm.addRoi(spot_roi)
	
		spots_fname = os.path.join(analysis_dir, name + "_Comets_ROI.zip")
		rm.runCommand("Save", spots_fname)
		log.info("Saving detected spots to %s" % (spots_fname))

		# Calculate the results
		timepoints = data.dimension(data.dimensionIndex(Axes.TIME))
		duration = timepoints * dt
		events_number = len(spots)
		rate = (events_number / duration) * 60
		results.append([os.path.basename(dir_path), i+1, rate, duration, events_number])

		if close_windows:
			kymograph_imp.close()

	if close_windows:
		IJ.selectWindow("Z_Projection.tif")
		IJ.getImage().close()
	rm.runCommand("Reset")
	
	# Write results in csv
	table = ResultsTable() 
	for row in results:
		table.incrementCounter()
		table.addValue('Filename', row[0])
		table.addValue('Centrosome #', row[1])
		table.addValue('Nucleation Rate (min-1)', row[2])
		table.addValue('Time (s)', row[3])
		table.addValue('Nucleation Events', row[4])
	if show_results:
		table.show('Results Nucleation Rate')
	result_fname = os.path.join(analysis_dir, "Results.csv")
	table.save(result_fname)
	log.info("Saving final results to %s" % (result_fname))

	# Write centrosomes position in csv
	table = ResultsTable() 
	for i, row in enumerate(centrosomes):
		table.incrementCounter()
		table.addValue('Centrosome #', i+1)
		table.addValue('x', row[0])
		table.addValue('y', row[1])
	if show_results:
		table.show('Centrosomes Positions')
	cen_fname = os.path.join(analysis_dir, "Centrosomes_Position.csv")
	table.save(cen_fname)
	log.info("Saving centrosomes position to %s" % (cen_fname))

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
	if show_results:
		table.show('Parameters')
	para_fname = os.path.join(analysis_dir, "Parameters.csv")
	table.save(para_fname)
	log.info("Saving parameters to %s" % (para_fname))
	
main()
