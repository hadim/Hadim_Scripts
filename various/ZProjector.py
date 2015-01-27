# @DatasetService data
# @DisplayService display
# @ImageJ ij

from net.imagej.ops.statistics import Max
from net.imagej.ops.statistics import Sum
from net.imglib2.type.numeric import RealType

from jarray import array

fname = "/home/hadim/Documents/phd/data/test_small.ome.tif"
ds = data.open(fname)

# TODO : find dimensions in ds object (except Z dimension)
dims = array([136, 65], 'l')
out = ij.op().createimg(dims)

# Find ndim for project on Z axis
ndim = 2

op = ij.op().sum(RealType, out)
ds2 = ij.op().project(out, ds, op, ndim)

ij.ui().show(ds2.getName(), ds2)

