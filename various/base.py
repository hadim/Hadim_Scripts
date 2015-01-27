# @DatasetService data
# @ImageDisplayService imgdisplay
# @ImageJ ij
# @DefaultLegacyService legacy

from ij import IJ

img = IJ.getImage()
display = legacy.getInstance().getImageMap().lookupDisplay(img)
d = imgdisplay.getActiveDataset(display)

#IJ.run(img, "Properties...", "frame=10")

IJ.run(img, "Bio-Formats Exporter", "save=" + "/home/hadim/test.ome.tif" + " compression=Uncompressed");
#data.save(d, "/home/hadim/test.ome.tif")

print(d)