# @Dataset dataset
# @ImageJ ij

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

from io.scif.img import SCIFIOImgPlus
from io.scif.filters import AbstractMetadataWrapper
from io.scif.ome.formats.OMETIFFFormat import Metadata
from io.scif.ome.services import DefaultOMEXMLService

from org.scijava.ui.DialogPrompt import MessageType

def main():

    imp = dataset.getImgPlus()

    # I don't really understand why sometime SCIFIO is not used
    # When it's not, we can't access to getMetadata()
    if not isinstance(imp, SCIFIOImgPlus):
        ij.ui().showDialog("This image has not been opened with SCIFIO")
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
        ij.ui().showDialog("This file does not contain OME metadata")
        return

    # Get xml string and print it with spaces indentation
    xml_string = DefaultOMEXMLService().getOMEXML(omeMeta.getRoot())

    xml_string = minidom.parseString(xml_string.encode('utf-8')).toprettyxml(indent="  ")
    ij.log().info(xml_string)

    #open("/home/hadim/md.xml", "w").write(xml_string.encode('utf-8'))

main()
