# @ImageJ ij
# @Dataset data

from net.imglib2.util import Intervals
from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.type.numeric.integer import UnsignedShortType
from net.imglib2.type.numeric.integer import UnsignedByteType

# Get the first frame
t_dim = data.dimensionIndex(Axes.TIME)
interval_start = []
interval_end = []
for d in range(0, data.numDimensions()):
	if d != t_dim:
		interval_start.append(0)
		interval_end.append(data.dimension(d) - 1)
	else:
		interval_start.append(0)
		interval_end.append(0)
		
intervals = interval_start + interval_end
intervals = Intervals.createMinMax(*intervals)

first_frame = ij.op().transform().crop(data.getImgPlus(), intervals)
ij.ui().show("first_frame", first_frame)

# Subtract the first frame to the stack
subtracted = ij.op().create().img(data.getImgPlus())
sub_op =  ij.op().op("math.subtract", first_frame, first_frame)

ij.op().slice(subtracted, data.getImgPlus(), sub_op, [t_dim])
ij.ui().show("subtracted", subtracted)

print(data.getImgPlus().class)
