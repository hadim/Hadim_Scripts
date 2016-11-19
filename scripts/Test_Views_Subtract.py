# @ImageJ ij
# @Dataset data

import os

from net.imglib2.util import Intervals
from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.view import Views

def get_axis(axis_type):
    return {
        'X': Axes.X,
        'Y': Axes.Y,
        'Z': Axes.Z,
        'TIME': Axes.TIME,
        'CHANNEL': Axes.CHANNEL,
    }.get(axis_type, Axes.Z)
    
    
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


# Convert input
converted = ij.op().convert().float32(data.getImgPlus())
converted = ij.dataset().create(converted)

stack_list = []
for t in range(0, data.dimension(Axes.TIME) - 1):
	frame_t = crop(ij, converted, {'TIME' : [t, t]})
	frame_t_plus_one = crop(ij, converted, {'TIME' : [t+1, t+1]})

	sub =  ij.op().run("math.subtract", frame_t_plus_one, frame_t)
	stack_list.append(sub)

subtracted = Views.stack(stack_list)
subtracted = ij.dataset().create(subtracted)

# Clip image to the input type
clipped = ij.op().create().img(subtracted, data.getImgPlus().firstElement())
clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), subtracted.firstElement())
ij.op().convert().imageType(clipped, subtracted, clip_op)

output = ij.dataset().create(clipped)

# Set the correct axes
axes = [data.axis(d) for d in range(0, data.numDimensions())]
output.setAxes(axes)

ij.ui().show(output)
