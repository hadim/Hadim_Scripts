# @Dataset data
# @ImagePlus imp
# @ImageJ ij

import os
import sys

from java.io import File

from ij.gui import Roi
from ij.plugin.frame import RoiManager

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking.sparselap import SimpleSparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.features.track import TrackDurationAnalyzer
from fiji.plugin.trackmate.features.track import TrackIndexAnalyzer
from fiji.plugin.trackmate.features.track import TrackLocationAnalyzer
from fiji.plugin.trackmate.features.track import TrackSpeedStatisticsAnalyzer
from fiji.plugin.trackmate.features.track import TrackSpotQualityFeatureAnalyzer
from fiji.plugin.trackmate.features.edges import EdgeTargetAnalyzer
from fiji.plugin.trackmate.features.edges import EdgeTimeLocationAnalyzer
from fiji.plugin.trackmate.features.edges import EdgeVelocityAnalyzer

from fiji.plugin.trackmate.io import TmXmlWriter

dir_path = os.path.dirname(data.getSource())
all_roi_path = os.path.join(dir_path, "AllRoiSet.zip")
trackmate_path = os.path.join(dir_path, "Trajectories.xml")

## Find the minimal bounding box for detection and tracking

# Open all ROIs
rm = RoiManager.getInstance()
if not rm:
	rm = RoiManager()
rm.runCommand("Deselect")
rm.runCommand("Reset")

rm.runCommand("Open", all_roi_path)

# Find the biggest bounding box possible
xx1, yy1, xx2, yy2 = [], [], [], []
for roi in rm.getRoisAsArray():
	rect = roi.getBounds()
	x1 = roi.getBoundingRect().x
	y1 = roi.getBoundingRect().y
	x2 = x1 + roi.getBoundingRect().width
	y2 = y1 + roi.getBoundingRect().height

	xx1.append(x1)
	yy1.append(y1)
	xx2.append(x2)
	yy2.append(y2)

x1 = min(xx1)
y1 = min(yy1)
x2 = max(xx2)
y2 = max(yy2)

rect = Roi(x1, y1, x2 - x1, y2 - y1)
imp.setRoi(rect)

# Clear ROIs
rm.runCommand("Deselect")
rm.runCommand("Reset")
rm.close()

print("Bounding box generated")

## Do the tracking

model = Model()
model.setLogger(Logger.IJ_LOGGER)
   
settings = Settings()
settings.setFrom(imp)
       
# Configure detector - We use the Strings for the keys
settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = { 
    'DO_SUBPIXEL_LOCALIZATION' : True,
    'RADIUS' : 15.0,
    'TARGET_CHANNEL' : 0,
    'THRESHOLD' : 0.63,
    'DO_MEDIAN_FILTERING' : False,
}  
     
settings.trackerFactory = SparseLAPTrackerFactory()
settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
settings.trackerSettings['LINKING_MAX_DISTANCE'] = float(80)
settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = float(80)
settings.trackerSettings['MAX_FRAME_GAP'] = 5

settings.addTrackAnalyzer(TrackDurationAnalyzer())
settings.addTrackAnalyzer(TrackIndexAnalyzer())
settings.addTrackAnalyzer(TrackLocationAnalyzer())
settings.addTrackAnalyzer(TrackSpeedStatisticsAnalyzer())
settings.addTrackAnalyzer(TrackSpotQualityFeatureAnalyzer())

settings.addEdgeAnalyzer(EdgeTargetAnalyzer())
settings.addEdgeAnalyzer(EdgeTimeLocationAnalyzer())
settings.addEdgeAnalyzer(EdgeVelocityAnalyzer())
    
filter2 = FeatureFilter('NUMBER_SPOTS', 8, True)
settings.addTrackFilter(filter2)
filter3 = FeatureFilter('TRACK_MEAN_SPEED', 3, True)
settings.addTrackFilter(filter3)
filter4 = FeatureFilter('TRACK_MEAN_SPEED', 50, False)
settings.addTrackFilter(filter4)
    
trackmate = TrackMate(model, settings)

ok = trackmate.checkInput()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))
    
ok = trackmate.process()
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))

selectionModel = SelectionModel(model)
displayer =  HyperStackDisplayer(model, selectionModel, imp)
displayer.render()
displayer.refresh()

### Save the tracks in XML file
writer = TmXmlWriter(File(trackmate_path))
writer.appendModel(model)
writer.appendSettings(settings)
writer.writeToFile()

print("Tracking is done and saved at %s" % trackmate_path)