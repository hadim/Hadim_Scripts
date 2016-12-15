# @ImageJ ij
# @StatusService status

import time

from ij.gui import PolygonRoi
from ij.gui import Roi

from net.imagej.axis import Axes

data = ij.dataset().open("8bit-signed&pixelType=int8&axes=X,Y,Time&lengths=800,800,10.fake")
masked = ij.op().create().img(data)

x = [170, 270, 620, 560, 340]
y = [175, 650, 580, 190, 70]
roi = PolygonRoi(x, y, Roi.POLYGON)

x1 = roi.getBoundingRect().x
y1 = roi.getBoundingRect().y
x2 = x1 + roi.getBoundingRect().width
y2 = y1 + roi.getBoundingRect().height

nFrames = data.dimension(Axes.TIME)

start = time.time()

targetRA = masked.randomAccess()
dataRA = data.randomAccess()

# Iterate over all the frames
for t in range(0, nFrames):

	# Iterate over the bounding box of the ROI (faster that iterating over all the dataset pixels)
	for x in range(x1, x2):
		for y in range(y1, y2):
		
			# Line 1 duration = 23%
			dataRA.setPosition([x, y, t])
			# Line 2 duration = 23%
			targetRA.setPosition([x, y, t])
			# Line 3 duration = 36%
			if roi.contains(x, y):
				# Line 4 duration = 18%
				targetRA.get().set(dataRA.get())

	status.showStatus(t+1, nFrames, "Applying mask to image %i/%i" % (t+1, nFrames))


print(time.time() - start)

ij.ui().show(masked)

