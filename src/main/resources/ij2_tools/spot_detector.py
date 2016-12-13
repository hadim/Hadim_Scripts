from fiji.plugin.trackmate import SpotCollection
from fiji.plugin.trackmate.util import TMUtils
from fiji.plugin.trackmate.features import FeatureFilter
from fiji.plugin.trackmate import Spot
from fiji.plugin.trackmate.detection import DogDetector

from net.imglib2.img.display.imagej import ImageJFunctions

from ij.gui import OvalRoi


def dog_detector(ij, data, radius, relative_threshold=None, absolute_threshold=None,
				 doSubpixel=True, doMedian=False, calibration=None):

	img = data.getImgPlus()

	# Set the parameters for DogDetector
	interval = img

	if not calibration:
		imp = ImageJFunctions.wrap(img, "imp_spot_detector")
		cal = imp.getCalibration()
		calibration = [cal.pixelWidth, cal.pixelHeight, cal.pixelDepth]

	detector = DogDetector(img, interval, calibration, radius, 0, doSubpixel, doMedian)

	spots = []

	# Start processing and display the results
	if detector.process():

		peaks = detector.getResult()

		# Otsu filtering by quality features
		qualities = [peak.getFeatures()['QUALITY'] for peak in peaks]
		if not absolute_threshold:
			threshold = TMUtils.otsuThreshold(qualities)
			if relative_threshold:
				threshold *= relative_threshold
		else:
			threshold = absolute_threshold
		peaks = [peak for peak in peaks if peak.getFeatures()['QUALITY'] > threshold]

		ij.log().info("%i peaks were found." % len(peaks))

		# Loop through all the peak that were found
		for peak in peaks:

			x = peak.getDoublePosition(0) / calibration[0]
			y = peak.getDoublePosition(1) / calibration[1]
			z = int(peak.getDoublePosition(2) / calibration[2])

			spot_roi = OvalRoi(x - radius/2, y - radius/2, radius * 2, radius * 2)
			spot_roi.setPosition(z)
			spots.append(spot_roi)

	else:
		ij.log().info("The detector could not process the data.")

	return spots
