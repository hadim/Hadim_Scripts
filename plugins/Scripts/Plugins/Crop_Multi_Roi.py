# @DatasetService data
# @ImageDisplayService imgdisplay
# @ImageJ ij
# @AbstractLogService log

from ij import IJ
from ij.plugin.frame import RoiManager

from io.scif.config import SCIFIOConfig
from io.scif.img import ImageRegion
from io.scif.img import ImgOpener
from io.scif.img import ImgSaver
from net.imagej.axis import Axes

import os

def main():

    # Get active dataset
    active_dataset = imgdisplay.getActiveDataset()
    
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
        IJ.log("Opening crop %i / %i" % (crop_id, len(rois_array)))
    
        # Get ROI bounds
        bounds = roi.getBounds()
        x = bounds.x
        y = bounds.y
        w = bounds.width
        h = bounds.height  
    
        # Import only cropped region of the image
        axes = [Axes.X, Axes.Y]
        ranges = ["%i-%i" % (x, x+w), "%i-%i" % (y, y+h)]
        config = SCIFIOConfig()
        config.imgOpenerSetRegion(ImageRegion(axes, ranges))
        
        opener = ImgOpener()
        imps = opener.openImgs(fname, config)
        imp = imps[0]
        
        # Get filename and basename of the current cropped image
        crop_basename = "crop%i_%s" % (crop_id, active_dataset.getName())
        crop_fname = os.path.join(os.path.dirname(fname), crop_basename)
        imp.setName(crop_basename)

        # Create dataset
        ds = data.create(imp)
    
        # Save cropped image
        IJ.log("Saving crop to %s" % crop_fname)
        data.save(ds, crop_fname)

        # Show cropped image
        ij.ui().show(ds.getName(), ds)
    
    IJ.log('Done')

main()
