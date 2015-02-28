# @ImageDisplayService displayservice
# @DefaultLegacyService legacyservice

from io.scif.filters import AbstractMetadataWrapper
from io.scif.img import SCIFIOImgPlus
from ij import IJ


def get_dt(dataset):

    imp = dataset.getImgPlus()
    metadata = imp.getMetadata()

    while isinstance(metadata, AbstractMetadataWrapper):
        metadata = metadata.unwrap()

    try:
        metadata = metadata.getOmeMeta()
        dt = metadata.getRoot().getPixelsTimeIncrement(0)
    except:
        dt = 1

    return dt
