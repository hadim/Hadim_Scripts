# @Integer(label="Centrosome 1 X Position", required=true) cen1_x
# @Integer(label="Centrosome 1 Y Position", required=true) cen1_y
# @Integer(label="Centrosome 2 X Position", required=true) cen2_x
# @Integer(label="Centrosome 2 Y Position", required=true) cen2_y
# @Float(label="dt (sec)", required=true, value=3) dt
# @Integer(label="Radius", required=true, value=30) radius
# @Integer(label="Line Width for Kymo", required=true, value=4) line_width

# @ImageJ ij
# @ImagePlus img
# @Dataset data
# @StatusService status
# @LogService log
# @OpService ops
# @DatasetIOService io
# @LocationService loc

import os
import math
import csv

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
from ij import IJ

from java.awt import Polygon

## Functions

def z_project(data):
	z_dim = data.dimensionIndex(Axes.Z)
	projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != z_dim]
	z_projected = ops.create().img(projected_dimensions)
	max_op = ops.op(Ops.Stats.Max, data)
	ops.transform().project(z_projected, data, max_op, z_dim)
	return ij.dataset().create(z_projected)


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

z_projected = data

# Calculcate the radius to be between both centrosomes
if cen2_x == 0 and cen2_y == 0:
	centrosomes = [[cen1_x, cen1_y]]
else:
	centrosomes = [[cen1_x, cen1_y], [cen2_x, cen2_y]]
	cen_center_x = (cen1_x + cen2_x) / 2
	cen_center_y = (cen1_y + cen2_y) / 2
	#radius = math.sqrt((cen1_x - cen_center_x)**2 + (cen1_y - cen_center_y)**2)


results = []
for i, (cen_x, cen_y) in enumerate(centrosomes[:]):

	name = "Cen%i_Kymograph" % (i+1)

	# For now we can't use IJ2 ROI so let's use the IJ1 ROI infrastructure
	IJ.selectWindow("Z_Projection.tif")

	# Draw line around the centrosomes
	xpoints, ypoints = get_circle_points(cen_x, cen_y, radius=radius, n=50)
	circle = PolygonRoi(xpoints, ypoints, Roi.POLYLINE)
	circle.setStrokeWidth(line_width)
	rm = get_roi_manager(new=True)
	rm.addRoi(circle)
	rm.runCommand("Show All")

	# Save the ROI
	rm.runCommand("Save", os.path.join(analysis_dir, name + "_ROI.zip"))

	# Create kymograph
	kfactory = KFactory(ij.context(), data, circle)
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
		'RADIUS' : 4.0,
		'TARGET_CHANNEL' : 1,
		'THRESHOLD' : 0.,
		'DO_MEDIAN_FILTERING' : True,
	}
	
	filter1 = FeatureFilter('QUALITY', 0, True)
	settings.addSpotFilter(filter1)
	
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
	for spot in model.getSpots().iterator(False):
		spots.append(spot)
	
		x = spot.getFeatures()['POSITION_X']
		y = spot.getFeatures()['POSITION_Y']
		spot_radius = spot.getFeatures()['RADIUS']
	
		spot_roi = OvalRoi(x, y, spot_radius, spot_radius)
		rm.addRoi(spot_roi)

	spots_fname = os.path.join(analysis_dir, name + "_Comets_ROI.zip")
	rm.runCommand("Show All")
	rm.runCommand("Save", spots_fname)
	log.info("Saving detected spots to %s" % (spots_fname))

	duration = kymograph_imp.height * dt
	events_number = len(spots)
	rate = (events_number / duration) * 60
	results.append([os.path.basename(dir_path), i+1, rate, duration, events_number])

rm.runCommand("Reset")

# Write results in csv
result_fname = os.path.join(analysis_dir, "Results.csv")
columns = [['Filename', "Centrosome #", 'Nucleation Rate (min-1)', 'Time (s)', 'Nucleation Events']]

f = open(result_fname, 'wb')
w = csv.writer(f, delimiter=',')
w.writerows(columns + results)
f.close()

log.info("Saving final results to %s" % (result_fname))


