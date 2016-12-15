# @Float(label="Pixel Size (um)", required=false, value=1) pixel_size
# @Float(label="Duration between Two Frames (s)", required=false, value=1) dt
# @Dataset data
# @ImagePlus imp
# @ImageJ ij

import os
import sys

from java.io import File

from ij.measure import ResultsTable

from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate.providers import DetectorProvider
from fiji.plugin.trackmate.providers import TrackerProvider
from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
from fiji.plugin.trackmate.providers import TrackAnalyzerProvider
from fiji.plugin.trackmate.visualization import PerTrackFeatureColorGenerator

logger = Logger.IJ_LOGGER

### Open and display tracks

dir_path = os.path.dirname(data.getSource())
trackmate_path = os.path.join(dir_path, "Trajectories.xml")
stats_path = os.path.join(dir_path, "Statistics.csv")

reader = TmXmlReader(File(trackmate_path))
if not reader.isReadingOk():
    sys.exit(reader.getErrorMessage())

model = reader.getModel()

spots = model.getSpots()
trackIDs = model.getTrackModel().trackIDs(True)
  
settings = Settings()
  
detectorProvider = DetectorProvider()
trackerProvider = TrackerProvider()
spotAnalyzerProvider = SpotAnalyzerProvider()
edgeAnalyzerProvider = EdgeAnalyzerProvider()
trackAnalyzerProvider = TrackAnalyzerProvider()
 
reader.readSettings(settings, detectorProvider, trackerProvider,
			        spotAnalyzerProvider, edgeAnalyzerProvider,
			        trackAnalyzerProvider)
 
logger.log(str(settings))

sm = SelectionModel(model)
displayer =  HyperStackDisplayer(model, sm, imp)
color = PerTrackFeatureColorGenerator(model, 'TRACK_INDEX')
displayer.setDisplaySettings('TrackDisplaymode', 0)
displayer.setDisplaySettings('TrackDisplayDepth', 20)
displayer.setDisplaySettings('TrackColoring', color)
displayer.render()

### Build stats table

fm = model.getFeatureModel()

table = ResultsTable()

for id in model.getTrackModel().trackIDs(True):
	table.incrementCounter()
	track = model.getTrackModel().trackSpots(id)

	table.addValue('Track ID', id)
	table.addValue('TRACK_DURATION', fm.getTrackFeature(id, 'TRACK_DURATION') * dt)
	table.addValue('TRACK_DISPLACEMENT', fm.getTrackFeature(id, 'TRACK_DISPLACEMENT') * pixel_size)
	table.addValue('TRACK_MEAN_SPEED', fm.getTrackFeature(id, 'TRACK_MEAN_SPEED') * pixel_size / dt)
	table.addValue('TRACK_MIN_SPEED', fm.getTrackFeature(id, 'TRACK_MIN_SPEED') * pixel_size / dt)
	table.addValue('TRACK_MAX_SPEED', fm.getTrackFeature(id, 'TRACK_MAX_SPEED') * pixel_size / dt)
	table.addValue('TRACK_STD_SPEED', fm.getTrackFeature(id, 'TRACK_STD_SPEED') * pixel_size / dt)
	

table.save(stats_path)
table.show("Statistics")