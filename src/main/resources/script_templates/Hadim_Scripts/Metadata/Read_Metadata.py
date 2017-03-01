# @ImageJ ij

from io.scif import FieldPrinter

filePath = "/home/hadim/.data/Test/IM000556.Tif"
format = ij.scifio().format().getFormat(filePath)

metadata = format.createParser().parse(filePath)
#print(FieldPrinter(metadata))

imageMeta = metadata.get(0)
print(imageMeta)