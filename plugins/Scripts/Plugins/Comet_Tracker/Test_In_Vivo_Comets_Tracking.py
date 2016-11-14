# @Float(label="Sigma 1", required=true, value=4.2) sigma1
# @Float(label="Sigma 2", required=true, value=1.25) sigma2
# @Boolean(label="Do thresholding ?", required=true, value=true) do_thresholding
# @Boolean(label="Show intermediates images (for debugging)", required=true, value=true) show_images

# @ImageJ ij
# @ImagePlus imp

# Script TODO are :
#
# - Preprocess Image : DOG + Rosin thresholding
# - Create Comet Average from ROIs or TrackMate file
# - Template Matching with TrackMate spots and Comet Average

from ij.plugin.filter import DifferenceOfGaussians
from ij.plugin import ContrastEnhancer
from ij.plugin import Duplicator
from ij.plugin import ZProjector
from ij.plugin import Thresholder
from ij.process import AutoThresholder
from ij import ImageStack
from ij import ImagePlus
from ij.process import ImageProcessor
from ij.plugin import ImageCalculator

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.img.display.imagej import ImageJFunctions


# Do Z Projection

proj = ZProjector(imp)
proj.setMethod(ZProjector.MAX_METHOD)
proj.setStartSlice(1)
proj.setStopSlice(imp.getNChannels())
proj.doHyperStackProjection(True)
imp = proj.getProjection()
if show_images:
	imp.show()


# Apply DOG filtering

f = DifferenceOfGaussians()
f.setup("", imp)

for i in range(1, imp.getNFrames()+1):
	imp.setPosition(i)
	f.run(imp.getProcessor(), sigma1, sigma2)

final_imp = imp

# Apply unimodal compatible thresholding (IJ1 default method)

if do_thresholding:

	binary_stack = ImageStack.create(imp.getWidth(), imp.getHeight(), imp.getType(), imp.getBitDepth())

	for i in range(1, imp.getNFrames() + 1):
		imp.setPosition(i)
		ip = imp.getProcessor().duplicate()

		ip = ip.convertToShort(False)
		ip.setAutoThreshold(AutoThresholder.Method.Otsu, False)
		ip.threshold(ip.getAutoThreshold())

		ip = ip.convertToByteProcessor(True)
		ip.invert()

		binary_stack.addSlice(ip)

	binary_stack.deleteSlice(1)
	binary_imp = ImagePlus("Binary", binary_stack)
	if show_images:
		binary_imp.show()

	# Subtract binary stack to DOG filtered stack

	calc = ImageCalculator()
	subtracted_imp = calc.run("subtract create stack", imp, binary_imp)
	subtracted_imp.show()

	final_imp = binary_imp

final_imp.show()
