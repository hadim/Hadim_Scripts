# @Dataset dataset
# @ImageJ ij

from __future__ import division
import sys

from io.scif.filters import AbstractMetadataWrapper

imp = dataset.getImgPlus()

# Get metadata
metadata = imp.getMetadata()

# Why the fuck this is needed ?
while isinstance(metadata, AbstractMetadataWrapper):
    metadata = metadata.unwrap()

omeMeta = metadata.getOmeMeta()
omeMeta = omeMeta.getRoot()

times = []
for i in range(0, omeMeta.getPlaneCount(0)):
    dt = omeMeta.getPlaneDeltaT(0, i).value() 
    times.append(dt)

delta_times = [j-i for i, j in zip(times[:-1], times[1:])]

mean_time = sum(delta_times) / len(delta_times)
print("Mean time between each plane : %f" % mean_time)
