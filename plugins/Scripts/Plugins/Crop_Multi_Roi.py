# @DatasetService data
# @ImageDisplayService imgdisplay
# @ImageJ ij
# @AbstractLogService log
# @DefaultLegacyService legacy

from ij import IJ
from ij.plugin.frame import RoiManager

from net.imagej.axis import Axes
from net.imagej import DefaultDataset
from net.imglib2 import FinalInterval
from io.scif.img import ImgSaver

import os

def main():

    # Get active dataset
    img = IJ.getImage()
    display = legacy.getInstance().getImageMap().lookupDisplay(img)
    active_dataset = imgdisplay.getActiveDataset(display)

    if not active_dataset:
        IJ.showMessage('No image opened.')
        return

    # Get image path
    fname = active_dataset.getSource()

    if not fname:
        IJ.showMessage('Source image needs to match a file on the system.')
        return

    IJ.log('Image filename is %s' % fname)

    # Iterate over all ROIs from ROI Manager
    rois = RoiManager.getInstance()

    if not rois:
        IJ.showMessage('No ROIs. Please use Analyze > Tools > ROI Manager...')
        return

    rois_array = rois.getRoisAsArray()
    for i, roi in enumerate(rois_array):

        crop_id = i +1
        IJ.log("Croping %i / %i" % (crop_id, len(rois_array)))

        # Get ROI bounds
        bounds = roi.getBounds()
        x = bounds.x
        y = bounds.y
        w = bounds.width
        h = bounds.height

        # Initiate dimensions
        dims = {}
        dim_names = [None] * 5
        for ax in [Axes.X, Axes.Y, Axes.Z, Axes.TIME, Axes.CHANNEL]:
            ax_index = active_dataset.dimensionIndex(ax)
            dim_names[ax_index] = str(ax)
            if int(active_dataset.dimension(ax_index)) == 1:
                dims[str(ax)] = (0, 0)
            else:
                dims[str(ax)] = (0, int(active_dataset.dimension(ax_index)) - 1)

        # Set cropped regions
        dims['X'] = (x, x + w)
        dims['Y'] = (y, y + h)

        # Set crop intervals
        begin_interval = [dims[name][0] for name in dim_names]
        end_interval = [dims[name][1] for name in dim_names]
        interval = FinalInterval(begin_interval, end_interval)

        # Get filename and basename of the current cropped image
        crop_basename = "crop%i_%s" % (crop_id, active_dataset.getName())
        crop_fname = os.path.join(os.path.dirname(fname), crop_basename)

        # Create dataset
        imp = ij.op().crop(interval, active_dataset.getImgPlus())
        ds = data.create(imp)
        ds.setName(crop_basename)

        # Show cropped image
        ij.ui().show(ds.getName(), ds)

        # Save cropped image
        IJ.log("Saving crop to %s" % crop_fname)
        #data.save(ds, crop_fname)
        
        # Hack to get save works
        imp = IJ.getImage()
        IJ.run("Properties...", "frame=5")
        IJ.run("Bio-Formats Exporter", "save=" + crop_fname + " compression=Uncompressed")
        imp.close()
        
    IJ.log('Done')

main()
