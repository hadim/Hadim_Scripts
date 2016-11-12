# @ImageJ ij
# @Dataset data
# @ImagePlus imp

from ij.plugin.filter import DifferenceOfGaussians
from ij.plugin import ContrastEnhancer
from ij.plugin import Duplicator

sigma1 = 4.2
sigma2 = 1.25

# IJ Ops version
pixel_type = data.getImgPlus().firstElement().__class__
dog = ij.op().create().img(data.getImgPlus(), pixel_type())

ij.op().run("filter.dog", dog, data.getImgPlus(), sigma1, sigma2)
ij.ui().show("dog", dog)

# GDSC Plugin version
out = Duplicator().run(imp)
f = DifferenceOfGaussians()
f.setup("", out)

for i in range(1, out.getNFrames()+1):
	out.setPosition(i)
	f.run(out.getProcessor(), sigma1, sigma2)

out.show()