# @ImageJ ij
# @Dataset data

from net.imglib2.util import Intervals
from net.imagej.axis import Axes
from net.imagej.ops import Ops
from net.imglib2.type.numeric.integer import UnsignedShortType
from net.imglib2.type.numeric.integer import ShortType
from net.imglib2.type.numeric.integer import IntType
from  net.imglib2.type.numeric.real import FloatType
from net.imagej.ops.convert.clip import ClipRealTypes

# Convert input
pixel_type = data.getImgPlus().firstElement().class
converted = ij.op().convert().float32(data.getImgPlus())

# Get the first frame (TODO: find a faser way !)
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

first_frame = ij.op().transform().crop(converted, intervals)

# Allocate output memory (wait for hybrid CF version of slice)
subtracted = ij.op().create().img(converted)

# Create the op
sub_op =  ij.op().op("math.subtract", first_frame, first_frame)

# Setup the fixed axis
fixed_axis = [d for d in range(0, data.numDimensions()) if d != t_dim]

# Run the op
ij.op().slice(subtracted, converted, sub_op, fixed_axis)

# Remove values below 0 and above maximum type value by clipping
clip_op = ij.op().op("convert.clip", pixel_type(), subtracted.firstElement().class())
clipped = ij.op().create().img(subtracted)
ij.op().map(clipped, subtracted, clip_op)

# Show it
#subtracted = ij.op().convert().uint8(subtracted)
ij.ui().show("subtracted", clipped)