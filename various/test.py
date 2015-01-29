# @DatasetService dataservice
# @ImageDisplayService displayservice
# @ImageJ ij
# @DefaultLegacyService legacyservice
# @LogService log

from ij import IJ
from io.scif.config import SCIFIOConfig

fname = "/home/hadim/Documents/phd/data/test_small.ome.tif"
output = "/home/hadim/Documents/phd/data/test_small_output.ome.tif"

img = IJ.getImage()
display = legacyservice.getInstance().getImageMap().lookupDisplay(img)
dataset = displayservice.getActiveDataset(display)

print(dataset)

log.debug("SALUT")
dataservice.save(dataset, output)