import sys
import xml.dom.minidom as dom

from ij import IJ

from net.imagej.legacy import DefaultLegacyService
from net.imagej.display import DefaultImageDisplayService

from io.scif.img import SCIFIOImgPlus
from io.scif.filters import AbstractMetadataWrapper
from io.scif.ome.formats.OMETIFFFormat import Metadata
from io.scif.ome.services import DefaultOMEXMLService

def main():
    # Tricky hack to get ImagePlus from IJ1 interface
    img = IJ.getImage()
    display = DefaultLegacyService().getInstance().getImageMap().lookupDisplay(img)
    dataset = DefaultImageDisplayService().getActiveDataset(display)
    imp = dataset.getImgPlus()

    # I don't really understand why sometime SCIFIO is not used
    # When it's not, we can't access to getMetadata()
    if not isinstance(imp, SCIFIOImgPlus):
        IJ.showMessage("This image has not been opened with SCIFIO")
        return

    # Get metadata
    metadata = imp.getMetadata()

    # Why the fuck this is needed ?
    while isinstance(metadata, AbstractMetadataWrapper):
        metadata = metadata.unwrap()

    # Check if metadata are OME or not
    if isinstance(metadata, Metadata):
        omeMeta = metadata.getOmeMeta()
    else:
        IJ.showMessage("This file does not contain OME metadata")
        return

    # Get xml string and print it with spaces indentation
    xml_string = DefaultOMEXMLService().getOMEXML(omeMeta.getRoot())
    xml = dom.parseString(xml_string)
    xml_string = xml.toprettyxml(indent="  ")

    IJ.log(xml_string)

main()
