# @Integer(label="Zoom to apply to kymograph", value=400, required=false) zoom_level
# @Context context
# @Dataset dataset
# @ImageJ ij
# @LogService log
# @DatasetIOService io

import os

from ij import IJ
from ij.plugin.frame import RoiManager

import fiji.plugin.kymographbuilder.KymographFactory as KFactory

rm = RoiManager.getInstance()
counter = 0

parent_folder = os.path.dirname(dataset.getSource())
kymo_folder = os.path.join(parent_folder, "Kymographs-" + os.path.splitext(dataset.getName())[0])
if not os.path.isdir(kymo_folder):
	os.makedirs(kymo_folder)

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
        IJ.run("Set... ", "zoom=%i" % int(zoom_level))

        io.save(kymo, os.path.join(parent_folder, kymo_folder, title + ".tif"))

roi_path = os.path.join(parent_folder, os.path.splitext(dataset.getName())[0] + ".zip")
rm.runCommand("Save", roi_path)

log.info("MultiKymographBuilder Finished. " + str(counter) + " ROIs processed")