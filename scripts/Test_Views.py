# @ImageJ ij
# @Dataset data
# @LogService log

import sys; sys.modules.clear()

import math
import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.util import Intervals

from net.imglib2.algorithm.labeling.ConnectedComponents import StructuringElement
from net.imglib2.roi.labeling import LabelRegions
from net.imglib2.view import Views


def get_axis(axis_type):
    return {
        'X': Axes.X,
        'Y': Axes.Y,
        'Z': Axes.Z,
        'TIME': Axes.TIME,
        'CHANNEL': Axes.CHANNEL,
    }.get(axis_type, Axes.Z)


def get_projection_method(method):
    return {
        'Max': Ops.Stats.Max,
        'Mean': Ops.Stats.Mean,
        'Median': Ops.Stats.Median,
        'Min': Ops.Stats.Min,
        'StdDev': Ops.Stats.StdDev,
        'Sum': Ops.Stats.Sum,
    }.get(method, Ops.Stats.Max)
    
    
def crop(ij, data, intervals, dropSingleDimensions=False, boundaries_strategy="transform.extendZeroView"):
	"""Crop along a one or more axis.

	Parameters
	----------
	intervals : Dict specifying which axis to crop and with what intervals.
				Example :
				intervals = {'X' : [0, 50],
				             'Y' : [0, 50]}
	"""

	intervals_start = [data.min(d) for d in range(0, data.numDimensions())]
	intervals_end = [data.max(d) for d in range(0, data.numDimensions())]

	for axis_type, interval in intervals.items():
		index = data.dimensionIndex(get_axis(axis_type))
		intervals_start[index] = interval[0] 
		intervals_end[index] = interval[1] + 1
	finalIntervals = Intervals.createMinMax(*(intervals_start + intervals_end))

	extended = ij.op().run(boundaries_strategy, data)
	extended = ij.op().run("transform.intervalView", extended, finalIntervals)

	intervals_start = [data.min(d) for d in range(0, data.numDimensions())]
	intervals_end = [data.max(d) for d in range(0, data.numDimensions())]

	for axis_type, interval in intervals.items():
		index = data.dimensionIndex(get_axis(axis_type))
		intervals_start[index] = interval[0] 
		intervals_end[index] = interval[1]
	finalIntervals = Intervals.createMinMax(*(intervals_start + intervals_end))

	output = ij.op().run("transform.crop", extended, finalIntervals, dropSingleDimensions)
	return output


def do_projection(ij, data, axis_type="Z", method="Max"):

    # Select which dimension to project
    dim = data.dimensionIndex(get_axis(axis_type))

    # Write the output dimensions
    projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != dim]

    # Create the output image
    z_projected = ij.op().create().img(projected_dimensions)

    # Create the op and run it
    max_op = ij.op().op(get_projection_method(method), data)
    ij.op().transform().project(z_projected, data.getImgPlus(), max_op, dim)

    # Clip image to the input type
    clipped = ij.op().create().img(z_projected, data.getImgPlus().firstElement())
    clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), z_projected.firstElement())
    ij.op().convert().imageType(clipped, z_projected, clip_op)

    # Create a dataset
    output = ij.dataset().create(clipped)

    # Set the correct axes
    axes = [data.axis(d) for d in range(0, data.numDimensions()) if d != dim]
    output.setAxes(axes)

    return output
    

positions = [[27, 8], [81, 44], [65, 75], [38, 94]]
patch_size = 10

patches_list = []
for position in positions:
	# Define the rectangle coordinates according to the center and the size of the patch
	rect = [[int(round(p - (patch_size//2))), int(round((p + patch_size//2)))] for p in position]
	intervals = {'X' : rect[0],
	             'Y' : rect[1]}
	patch = crop(ij, data, intervals)
	patches_list.append(patch)

# Stack the patches
patches = Views.stack(patches_list)
print(patches)
patches = ij.dataset().create(patches)
print(patches)
ij.ui().show("patches", patches)

# Do the mean of all the patches
mean_patch = do_projection(ij, patches, axis_type="TIME", method="Mean")
ij.ui().show("mean_patch", mean_patch)