from ij import IJ
from ij.plugin.frame import RoiManager

from io.scif.config import SCIFIOConfig
from io.scif.img import ImageRegion
from io.scif.img import ImgOpener
from io.scif.img import ImgSaver
from net.imagej.axis import Axes

import os

def main():
    # Get current image filename
    imp = IJ.getImage()
    f = imp.getOriginalFileInfo()
    fname = os.path.join(f.directory, f.fileName)

    # Iterate over all ROIs from ROI Manager
    rois = RoiManager.getInstance()

    if not rois:
        IJ.showMessage('No ROIs. Please use Analyze > Tools > ROI Manager...')
        return

    IJ.log('Image filename is %s' % fname)
    
    for i, roi in enumerate(rois.getRoisAsArray()):
    
        crop_id = i +1
        IJ.log("Opening crop %i / %i" % (crop_id, len(rois)))
    
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
        crop_basename = "crop%i_%s" % (crop_id, f.fileName)
        crop_fname = os.path.join(f.directory, crop_basename)
        IJ.log("Saving crop to %s" % crop_fname)
    
        # Save cropped image
        saver = ImgSaver()
        saver.saveImg(crop_fname, imp)
    
    IJ.log('Done')

main()
