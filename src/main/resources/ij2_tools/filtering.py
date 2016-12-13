import os

from net.imagej.axis import Axes


def apply_dog_filter(ij, data, sigma1, sigma2, save=False, output_dir=""):

	ij.log().info("Applying DOG filter with sigma1 = %f and sigma2 = %f" % (sigma1, sigma2))

	converted = ij.op().convert().float32(data.getImgPlus())
	
	# Allocate output memory (wait for hybrid CF version of slice)
	dog = ij.op().create().img(converted)
	
	# Create the op
	dog_op = ij.op().op("filter.dog", converted, sigma1, sigma2)
	
	# Setup the fixed axis
	t_dim = data.dimensionIndex(Axes.TIME)
	fixed_axis = [d for d in range(0, data.numDimensions()) if d != t_dim]
	
	# Run the op
	ij.op().slice(dog, converted, dog_op, fixed_axis)

	# Clip image to the input type
	clipped = ij.op().create().img(dog, data.getImgPlus().firstElement())
	clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), dog.firstElement())
	ij.op().convert().imageType(clipped, dog, clip_op)

	output = ij.dataset().create(clipped)

	axes = [data.axis(d) for d in range(0, data.numDimensions())]
	output.setAxes(axes)

	if save:
		fname = os.path.join(output_dir, "DOG_Filtered.tif")
		ij.log().info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output