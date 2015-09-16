# @DatasetService datasetservice
# @ImageDisplayService displayservice
# @ImageJ ij
# @AbstractLogService log

from ij import IJ
from ij import Macro
from ij.io import FileSaver
from ij.plugin.frame import RoiManager

from io.scif.img import ImgSaver
from net.imagej import DefaultDataset

from loci.plugins import BF
from loci.plugins import LociExporter
from loci.plugins.out import Exporter
from loci.plugins.in import ImporterOptions
from loci.common import Region

from net.imglib2.img import ImagePlusAdapter

import os
import sys
import glob

sys.path.append(os.path.join(IJ.getDirectory('plugins'), "Scripts", "Plugins"))
from libtools import crop
from libtools.utils import get_dt


def main():

    # Get image path
    fname = "/media/thor/data/microscopy_data/soumya/movies/wt/2015.05.29/cgc_spd_1_mII_crop.ims"

    basename = os.path.basename(fname)
    dir_path = os.path.dirname(fname)

    if not fname:
        IJ.showMessage('Source image needs to match a file on the system.')
        return

    # Open ROIs
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

    rois_array = rois.getRoisAsArray()
    for i, roi in enumerate(rois_array):

        crop_id = i + 1
        IJ.log("Crop region %i / %i" % (crop_id, len(rois_array)))

        # Get filename and basename of the current cropped image
        crop_basename = "crop%i_%s" % (crop_id, basename)
        crop_basename = os.path.splitext(crop_basename)[0] + ".ome.tif"
        crop_fname = os.path.join(os.path.dirname(fname), "crop", crop_basename)

        # Get bounds and crop
        bounds = roi.getBounds()

        x = bounds.x
        y = bounds.y
        w = bounds.width
        h = bounds.height

        # Import only cropped region of the image
        options = ImporterOptions()
        options.setCrop(True)
        options.setCropRegion(0, Region(x, y, w, h))
        options.setId(fname)
        imps = BF.openImagePlus(options)

        imp = imps[0]
        #imp.show()

        # Save cropped image as raw Tiff
        IJ.run(imp, "Save", "save=" + crop_fname + "");

        imp.close()

    IJ.log('Done')

main()
