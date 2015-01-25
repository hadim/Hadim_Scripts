# @DatasetService data
# @ImageJ ij

from jarray import array

from net.imglib2 import FinalInterval
from net.imglib2.img.array import ArrayImgs
from net.imagej.axis import Axes
from net.imglib2.util import Intervals

fname = "/home/hadim/Documents/phd/data/test_small.ome.tif"
ds = data.open(fname)

# Initiate dimensions
dims = {}
dim_names = [None] * 5
for ax in [Axes.X, Axes.Y, Axes.Z, Axes.TIME, Axes.CHANNEL]:
    ax_index = ds.dimensionIndex(ax)
    dim_names[ax_index] = str(ax)
    if int(ds.dimension(ax_index)) == 1:
        dims[str(ax)] = (0, 0)
    else: 
        dims[str(ax)] = (0, int(ds.dimension(ax_index)) - 1)
        
# Set cropped regions
dims['X'] = (10, 40)
dims['Y'] = (5, 20)

# Set crop intervals
begin_interval = [dims[name][0] for name in dim_names]
end_interval = [dims[name][1] for name in dim_names]
interval = FinalInterval(begin_interval, end_interval)
print(begin_interval)
print(end_interval)
print(Intervals.contains(ds, interval))

ds2 = ij.op().crop(interval, ds)
ij.ui().show(ds2.getName(), ds2)