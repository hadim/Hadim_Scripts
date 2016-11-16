# @ImageJ ij
# @Dataset data

import sys; sys.modules.clear()

from net.imglib2.view import Views
from net.imglib2.util import Intervals
from net.imglib2.img import Img

from net.imagej import ImgPlus

from ij2_tools.ij_utils import get_axis

boundaries_strategy = "transform.extendZeroView"

intervals = {'X' : [0, 200],
			 'Y' : [0, 200]}

    
intervals_start = [data.min(d) for d in range(0, data.numDimensions())]
intervals_end = [data.max(d) for d in range(0, data.numDimensions())]

for axis_type, interval in intervals.items():
	index = data.dimensionIndex(get_axis(axis_type))
	intervals_start[index] = interval[0]
	intervals_end[index] = interval[1]

print((intervals_start + intervals_end))
intervals = Intervals.createMinMax(*(intervals_start + intervals_end))

extended = ij.op().run(boundaries_strategy, data)
extended = ij.op().run("transform.intervalView", extended, intervals)
output = ij.op().run("transform.crop", extended, intervals, False)  # Can this be removed ?

ij.ui().show("output", output)