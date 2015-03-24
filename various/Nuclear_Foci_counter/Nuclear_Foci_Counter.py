# Options

THRESHOLD_METHOD = "Default" # Huang
SHOW_SPOTS = True
SPOT_TRESHOLD = 0.68
SPOT_DIAMETER = 4
MINIMUM_AREA = 1000
MAXIMUM_AREA = 10000

#####################
# DO NOT EDIT BELOW #
#####################

from ij import IJ
from ij import WindowManager
from ij.plugin.filter import Filters
from ij.plugin.filter import EDM
from ij.measure import ResultsTable
from ij.plugin.filter import ParticleAnalyzer
from ij.plugin.frame import RoiManager
from ij.measure import Measurements

from fiji.plugin.trackmate import Spot
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.features import FeatureFilter
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate import SelectionModel

def detect_spots(imp, diameter, spot_treshold, show=True):

    # Detect spots
    model = Model()
    settings = Settings()
    settings.setFrom(imp)
    
    settings.detectorFactory = LogDetectorFactory()
    settings.detectorSettings = {'DO_SUBPIXEL_LOCALIZATION': True,
                                 'RADIUS': float(diameter / 2),
                                 'TARGET_CHANNEL': 1,
                                 'THRESHOLD': float(0),
                                 "DO_MEDIAN_FILTERING": False}
    filter1 = FeatureFilter('QUALITY', spot_treshold, True)
    settings.addSpotFilter(filter1)
    
    trackmate = TrackMate(model, settings)
    trackmate.execDetection()
    trackmate.execInitialSpotFiltering()
    trackmate.computeSpotFeatures(True)
    trackmate.execSpotFiltering(True)
    
    
    print("Found %i spots" % (trackmate.getModel().getSpots().getNSpots(True)))
    
    if show:
        selectionModel = SelectionModel(model)
        displayer= HyperStackDisplayer(model, selectionModel, imp)
        displayer.render()
        displayer.refresh()
        
        imp.updateAndDraw()

    return trackmate.getModel().getSpots()

def detect_nuclei(ori_imp, min_area, max_area, treshold_method):

    imp = ori_imp.createImagePlus()
    ip = ori_imp.getProcessor().duplicate()
    imp.setProcessor("copy", ip)
    
    # Smooth image
    filters = Filters()
    filters.setup("smooth", imp)
    filters.run(imp.getProcessor())
    
    # Threshold and watershed
    ip = imp.getProcessor().duplicate()
    imp.setProcessor("copy", ip)
    ip.setAutoThreshold("%s dark" % treshold_method)
    IJ.run(imp, "Convert to Mask", "")
    IJ.run(imp, "Watershed", "")
    
    # Analyze nuclei
    measures =  Measurements.ADD_TO_OVERLAY + Measurements.AREA + Measurements.AREA_FRACTION + \
                Measurements.CENTER_OF_MASS + Measurements.CENTROID + Measurements.CIRCULARITY + \
                Measurements.ELLIPSE + Measurements.FERET + Measurements.INTEGRATED_DENSITY + \
                Measurements.INVERT_Y + Measurements.KURTOSIS + Measurements.LABELS + Measurements.LIMIT + \
                Measurements.MAX_STANDARDS+ Measurements.MEAN + Measurements.MEDIAN + Measurements.MIN_MAX + \
                Measurements.MODE + Measurements.PERIMETER + Measurements.RECT + \
                Measurements.SCIENTIFIC_NOTATION + Measurements.SHAPE_DESCRIPTORS + Measurements.SKEWNESS + \
                Measurements.SLICE + Measurements.STACK_POSITION + Measurements.STD_DEV

    options = ParticleAnalyzer.ADD_TO_MANAGER + ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES
    
    table = ResultsTable()
    rois = RoiManager.getInstance()
    if not rois: rois = RoiManager()
    rois.reset()
    
    pa = ParticleAnalyzer(options, measures,
                          table, min_area, max_area, 0.0, 1.0)
    pa.setHideOutputImage(True)
    pa.analyze(imp)

    print("Found %i nuclei" % len(rois.getRoisAsArray()))

    return rois

def main():
    ori_imp = WindowManager.getCurrentImage()
    rois = detect_nuclei(ori_imp, MINIMUM_AREA, MAXIMUM_AREA, THRESHOLD_METHOD)
    spots = detect_spots(ori_imp, SPOT_DIAMETER, SPOT_TRESHOLD, show=SHOW_SPOTS)

    table = ResultsTable()
        
    for i, roi in enumerate(rois.getRoisAsArray()):
        n = 0
        for spot in spots.iterable(True):
            x = int(spot.getFeature(spot.POSITION_X))
            y = int(spot.getFeature(spot.POSITION_Y))
            if roi.contains(x, y):
                n += 1
    
        table.setValue("nucleus_id", i, i+1)
        table.setValue("n_foci", i, n)

    table.show("Number of foci by nuclei")

    print("Done")

main()