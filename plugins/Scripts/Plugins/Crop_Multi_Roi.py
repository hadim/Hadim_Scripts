# @DatasetService datasetservice
# @ImageDisplayService displayservice
# @ImageJ ij
# @AbstractLogService log
# @DefaultLegacyService legacyservice

from ij import IJ
from ij import Macro
from ij.plugin.frame import RoiManager

from net.imagej import DefaultDataset
from loci.plugins import LociExporter
from loci.plugins.out import Exporter

import os
import sys
import glob

sys.path.append(os.path.join(IJ.getDirectory('plugins'), "Scripts", "Plugins"))
from libtools import crop
from libtools.utils import get_dt


def main():

    # Get active dataset
    img = IJ.getImage()
    display = legacyservice.getInstance().getImageMap().lookupDisplay(img)
    active_dataset = displayservice.getActiveDataset(display)

    if not active_dataset:
        IJ.showMessage('No image opened.')
        return

    # Get image path
    fname = active_dataset.getSource()
    dir_path = os.path.dirname(fname)

    if not fname:
        IJ.showMessage('Source image needs to match a file on the system.')
        return

    # Open ROIs
    rois = RoiManager.getInstance()
    if not rois:
        roi_path = os.path.join(dir_path, "RoiSet.zip")
        if not os.path.isfile(roi_path):
            try:
                roi_path = glob.glob(os.path.join(dir_path, "*.roi"))[0]
            except:
                roi_path = None

        if not roi_path:
            IJ.showMessage('No ROIs. Please use Analyze > Tools > ROI Manager...')
            return

        rois = RoiManager(True)
        rois.reset()
        rois.runCommand("Open", roi_path)

    IJ.log('Image filename is %s' % fname)
    dt = get_dt(active_dataset)

    rois_array = rois.getRoisAsArray()
    for i, roi in enumerate(rois_array):

        crop_id = i + 1
        IJ.log("Croping %i / %i" % (crop_id, len(rois_array)))

        # Get filename and basename of the current cropped image
        crop_basename = "crop%i_%s" % (crop_id, active_dataset.getName())
        crop_basename = os.path.splitext(crop_basename)[0] + ".ome.tif"
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
        bfExporter = LociExporter()
        macroOpts = "save=[" + crop_fname + "]"
        bfExporter.setup(None, imp)
        Macro.setOptions(macroOpts)
        bfExporter.run(None)

        imp.close()

    IJ.log('Done')

main()
