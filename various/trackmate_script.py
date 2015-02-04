from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

from ij import WindowManager

import sys
  
imp = WindowManager.getCurrentImage()
imp.show()
   
model = Model()
model.setLogger(Logger.IJ_LOGGER)
      
settings = Settings()
settings.setFrom(imp)

settings.detectorFactory = LogDetectorFactory()
settings.detectorSettings = { 
    'DO_SUBPIXEL_LOCALIZATION' : True,
    'RADIUS' : 0.22,
    'TARGET_CHANNEL' : 2,
    'THRESHOLD' : 0.,
    'DO_MEDIAN_FILTERING' : False,
}  

filter1 = FeatureFilter('QUALITY', 1, True)
settings.addSpotFilter(filter1)
 
trackmate = TrackMate(model, settings)

# Process
#ok = trackmate.checkInput()
#if not ok:
#    sys.exit(str(trackmate.getErrorMessage()))
   
trackmate.execDetection()
trackmate.execInitialSpotFiltering()
trackmate.computeSpotFeatures(True)

# Display 
selectionModel = SelectionModel(model)
displayer =  HyperStackDisplayer(model, selectionModel, imp)
displayer.render()
displayer.refresh()
   
# Echo results with the logger we set at start:
model.getLogger().log(str(model))