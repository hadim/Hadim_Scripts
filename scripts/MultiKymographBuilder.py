# @Context context
# @Dataset dataset
# @ImageJ ij
# @LogService log
# @DatasetIOService io

import os

from ij import IJ
from ij.plugin.frame import RoiManager
import fiji.plugin.kymographbuilder.KymographFactory as KFactory
from java.io import File

rm = RoiManager.getInstance()
counter = 0

parent_folder = File(dataset.getSource()).getParent()

for roi in rm.getRoisAsArray():
    if roi.isLine():

        counter += 1
        title = "Kymograph" + "_" + str(counter).zfill(3) + "_" + roi.getName()

        kfactory = KFactory(context, dataset, roi)
        kfactory.build()
        
        kymo = kfactory.getKymograph()
        ij.ui().show(title, kymo)

        # Make the display prettier (IJ1 way)
        IJ.getImage().setDisplayMode(IJ.COMPOSITE)
        IJ.run("Set... ", "zoom=600")
        #IJ.getImage().setActiveChannel("100")
        #IJ.run("Enhance Contrast", "saturated=0.35 equalize")
        #IJ.getImage().setActiveChannel("010")
        #IJ.run("Enhance Contrast", "saturated=0.35 equalize")

        io.save(kymo, os.path.join(parent_folder, title) + ".tif")

roi_path = os.path.join(parent_folder, os.path.splitext(dataset.getName())[0] + ".zip")
rm.runCommand("Save", roi_path)

log.info("MultiKymographBuilder Finished. " + str(counter) + " ROIs processed")