# @ImageJ ij
# @Dataset data
# @LogService log

import math
import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops

# Parameters
show_images = False
save_images = False

sigma1 = 4.2
sigma2 = 1.25
threshold_method = "otsu"
k1 = 1

output_dir = os.path.join(os.path.dirname(data.getSource()), "Analysis_Comets")
if not os.path.exists(output_dir):
	os.makedirs(output_dir)
	

# Functions

def do_z_projection(data, save=False, output_dir=""):
	# Select which dimension to project
	z_dim = data.dimensionIndex(Axes.Z)

	if z_dim == -1:
		log.info("Z dimension not found. Z Projection skipped.")
		output = data.duplicate()
	elif data.dimension(z_dim) == 1:
		log.info("Z dimension has only one frame. Z Projection skipped.")
		output = data.duplicate()
	else:
		log.info("Performing Z maximum projection")
	
		# Write the output dimensions
		projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != z_dim]
	
		# Create the output image
		z_projected = ij.op().create().img(projected_dimensions)
	
		# Create the op and run it
		max_op = ij.op().op(Ops.Stats.Max, data)
		ij.op().transform().project(z_projected, data, max_op, z_dim)
	
		# Create a dataset
		output = ij.dataset().create(z_projected)
	
		# Set the correct axes (is that needed ?)
		axes = [data.axis(d) for d in range(0, data.numDimensions()) if d != z_dim]
		output.setAxes(axes)

	if save:
		fname = os.path.join(output_dir, "Z_Projected.tif")
		log.info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output


def apply_dog_filter(data, sigma1, sigma2, save=False, output_dir=""):

	log.info("Applying DOG filter with sigma1 = %f and sigma2 = %f" % (sigma1, sigma2))

	pixel_type = data.getImgPlus().firstElement().class
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

	output = ij.dataset().create(dog)

	if save:
		fname = os.path.join(output_dir, "DOG_Filtered.tif")
		log.info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output


def do_threshold(data, method, k1, save=False, output_dir=""):

	histo = ij.op().run("image.histogram", data.getImgPlus())
	threshold = ij.op().run("threshold.%s" % method, histo)

	log.info('Threshold found with method "%s" : %f' % (method, threshold.getRealFloat()))

	threshold.setReal(threshold.getRealFloat() * k1)
	log.info('New threshold modified (with k1=%f) : %f' % (k1, threshold.getRealFloat()))
	
	thresholded = ij.op().run("threshold.apply", data.getImgPlus(), threshold)

	output = ij.op().convert().uint8(thresholded)
	output = ij.dataset().create(output)

	if save:
		fname = os.path.join(output_dir, "Thresholded.tif")
		log.info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)
		
	return output


# Main Function

## Z Projection
z_projected = do_z_projection(data, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("z_projected", z_projected)

## DOG Filtering
dog = apply_dog_filter(z_projected, sigma1, sigma2, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("dog", dog)

## Segmentation
thresholded = do_threshold(dog, threshold_method, k1, save=save_images, output_dir=output_dir)
ij.ui().show("thresholded", thresholded)
