from net.imagej.axis import Axes
from net.imglib2 import FinalInterval

def crop(ij, datasetservice, dataset, x, y, w, h, name):
    """
    """
    # Initiate dimensions
    dims = {}
    dim_names = [None] * 5
    for ax in [Axes.X, Axes.Y, Axes.Z, Axes.TIME, Axes.CHANNEL]:
        ax_index = dataset.dimensionIndex(ax)
        dim_names[ax_index] = str(ax)
        if int(dataset.dimension(ax_index)) == 1:
            dims[str(ax)] = (0, 0)
        else:
            dims[str(ax)] = (0, int(dataset.dimension(ax_index)) - 1)

    # Set cropped regions
    dims['X'] = (x, x + w)
    dims['Y'] = (y, y + h)

    # Set crop intervals
    begin_interval = [dims[name][0] for name in dim_names]
    end_interval = [dims[name][1] for name in dim_names]
    interval = FinalInterval(begin_interval, end_interval)

    # Create dataset
    imp = ij.op().crop(interval, dataset.getImgPlus())
    ds = datasetservice.create(imp)
    ds.setName(name)

    return ds
