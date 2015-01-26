# @DatasetService data
# @ImageDisplayService imgdisplay
# @ImageJ ij
# @DefaultLegacyService legacy

from ij import IJ

from net.imagej.axis import Axes
from net.imglib2 import FinalInterval


img = IJ.getImage()
display = legacy.getInstance().getImageMap().lookupDisplay(img)
d = imgdisplay.getActiveDataset(display)

# Initiate dimensions
dims = {}
dim_names = [None] * 5
for ax in [Axes.X, Axes.Y, Axes.Z, Axes.TIME, Axes.CHANNEL]:
    ax_index = d.dimensionIndex(ax)
    dim_names[ax_index] = str(ax)
    if int(d.dimension(ax_index)) == 1:
        dims[str(ax)] = (0, 0)
    else:
        dims[str(ax)] = (0, int(d.dimension(ax_index)) - 1)

# Set crop intervals
begin_interval = [dims[name][0] for name in dim_names]
end_interval = [dims[name][1] for name in dim_names]
interval = FinalInterval(begin_interval, end_interval)

# Create dataset
imp = ij.op().crop(interval, d.getImgPlus())
ds = data.create(imp)
ds.setName("New")

data.save(ds, "/home/hadim/test.ome.tif")
