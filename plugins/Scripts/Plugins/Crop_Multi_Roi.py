# @DatasetService datasetservice
# @ImageDisplayService displayservice
# @ImageJ ij
# @AbstractLogService log
# @DefaultLegacyService legacy

from ij import IJ
from ij.plugin.frame import RoiManager

from net.imagej import DefaultDataset
from io.scif.img import ImgSaver

import os
import sys

sys.path.append(os.path.join(IJ.getDirectory('plugins'), "Scripts", "Plugins"))
from libtools import crop

def main():

    # Get active dataset
    img = IJ.getImage()
    display = legacy.getInstance().getImageMap().lookupDisplay(img)
    active_dataset = displayservice.getActiveDataset(display)

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

        # Get filename and basename of the current cropped image
        crop_basename = "crop%i_%s" % (crop_id, active_dataset.getName())
        crop_fname = os.path.join(os.path.dirname(fname), crop_basename)

        # Get bounds and crop
        bounds = roi.getBounds()
        dataset = crop(ij, datasetservice, active_dataset,
                       bounds.x, bounds.y, bounds.width,
                       bounds.height, crop_basename)

        # Show cropped image
        ij.ui().show(dataset.getName(), dataset)

        # Save cropped image (ugly hack)
        IJ.log("Saving crop to %s" % crop_fname)
        imp = IJ.getImage()
        IJ.run("Properties...", "frame=5")
        IJ.run("Bio-Formats Exporter", "save=" + crop_fname + " compression=Uncompressed")
        imp.close()

    IJ.log('Done')

main()
