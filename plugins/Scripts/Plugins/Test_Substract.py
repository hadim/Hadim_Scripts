# @ImageJ ij
# @Dataset data

from net.imglib2.util import Intervals
from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.type.numeric.integer import UnsignedByteType, ByteType

# Get the first frame (ugly code)
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

# Get the type of the image
pixel_type = data.getImgPlus().firstElement().__class__

# Allocate memory for the output
subtracted = ij.op().create().img(data.getImgPlus(), pixel_type())

# Setup the op
sub_op =  ij.op().op("math.subtract", first_frame, first_frame)

# Calculate the fixed axes
fixed_axis = [d for d in range(0, data.numDimensions()) if d != t_dim]

# Do the subtraction
ij.op().slice(subtracted, data.getImgPlus(), sub_op, fixed_axis)

# Display image
ij.ui().show("subtracted", subtracted)
