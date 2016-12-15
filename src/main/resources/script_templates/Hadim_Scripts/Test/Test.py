# @Dataset data
# @ImagePlus imp
# @ImageJ ij
# @StatusService status

from net.imagej.axis import Axes

masked = ij.op().create().img(data)
	
targetRA = masked.randomAccess()
dataRA = data.randomAccess()

nFrames = data.dimension(Axes.TIME)

for t in range(0, nFrames):

	roi = imp.getRoi()
	
	x1 = roi.getBoundingRect().x
	y1 = roi.getBoundingRect().y
	x2 = x1 + roi.getBoundingRect().width
	y2 = y1 + roi.getBoundingRect().height
	
	for x in range(x1, x2):
		for y in range(y1, y2):
			dataRA.setPosition([x, y, t])
			targetRA.setPosition([x, y, t])
			#if roi.contains(x, y):
			#	targetRA.get().set(dataRA.get())

	status.showStatus(t+1, nFrames, "Applying mask to image %i/%i" % (t+1, nFrames))


ij.ui().show(masked)
