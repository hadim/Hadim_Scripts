from net.imagej.axis import Axes
from net.imglib2.util import Intervals

from .ij_utils import get_axis


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