import os

from net.imglib2.util import Intervals
from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.view import Views
from net.imglib2.img import ImgView

from .cropping import crop


def subtract_first_image(ij, data, save=False, output_dir=""):

	# Get the first frame
	first_frame = crop(ij, data, {'TIME' : [0, 0]})

	# Allocate output memory (wait for hybrid CF version of slice)
	subtracted = ij.op().create().img(data)

	# Create the op
	sub_op =  ij.op().op("math.subtract", first_frame, first_frame)

	# Setup the fixed axis
	fixed_axis = [d for d in range(0, data.numDimensions()) if d != Axes.TIME]

	# Run the op
	ij.op().slice(subtracted, data, sub_op, fixed_axis)

	# Clip image to the input type
	clipped = ij.op().create().img(subtracted, data.getImgPlus().firstElement())
	clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), subtracted.firstElement())
	ij.op().convert().imageType(clipped, subtracted, clip_op)

	output = ij.dataset().create(clipped)

	# Set the correct axes
	axes = [data.axis(d) for d in range(0, data.numDimensions())]
	output.setAxes(axes)

	if save:
		fname = os.path.join(output_dir, "Subtracted.tif")
		ij.log().info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output


def subtract_consecutive_frames(ij, data, save=False, output_dir=""):

	# Convert input
	converted = ij.op().convert().float32(data.getImgPlus())
	converted = ij.dataset().create(converted)

	stack_list = []
	for t in range(0, data.dimension(Axes.TIME) - 1):
		frame_t = crop(ij, converted, {'TIME' : [t, t]}, dropSingleDimensions=True)
		frame_t_plus_one = crop(ij, converted, {'TIME' : [t+1, t+1]}, dropSingleDimensions=True)

		sub =  ij.op().run("math.subtract", frame_t_plus_one, frame_t)
		stack_list.append(sub)

	subtracted = Views.stack(stack_list)
	subtracted = ImgView.wrap(subtracted, ij.op().run("create.imgFactory", converted))
	subtracted = ij.dataset().create(subtracted)

	# Clip image to the input type
	clipped = ij.op().create().img(subtracted, data.getImgPlus().firstElement())
	clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), subtracted.firstElement())
	ij.op().convert().imageType(clipped, subtracted, clip_op)

	output = ij.dataset().create(clipped)

	# Set the correct axes
	axes = [data.axis(d) for d in range(0, data.numDimensions())]
	output.setAxes(axes)

	# Set the correct axes
	axes = [data.axis(d) for d in range(0, data.numDimensions())]
	output.setAxes(axes)

	if save:
		fname = os.path.join(output_dir, "Subtracted.tif")
		ij.log().info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output
