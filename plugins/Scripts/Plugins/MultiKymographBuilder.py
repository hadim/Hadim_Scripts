# @Context context
# @Dataset dataset
# @ImageJ ij
# @LogService log
# @DatasetIOService io

import os

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

        io.save(kymo, os.path.join(parent_folder, title) + ".tif")

log.info("MultiKymographBuilder Finished. " + str(counter) + " ROIs processed")