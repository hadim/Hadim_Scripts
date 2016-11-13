# @ImageJ ij
# @Dataset data
# @ImagePlus imp

from ij.plugin.filter import DifferenceOfGaussians
from ij.plugin import ContrastEnhancer
from ij.plugin import Duplicator

from net.imagej.axis import Axes

sigma1 = 4.2
sigma2 = 1.25

# IJ Ops version

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

# Show it
ij.ui().show("dog", dog)

# GDSC Plugin version
out = Duplicator().run(imp)
f = DifferenceOfGaussians()
f.setup("", out)

for i in range(1, out.getNFrames()+1):
	out.setPosition(i)
	f.run(out.getProcessor(), sigma1, sigma2)

out.show()