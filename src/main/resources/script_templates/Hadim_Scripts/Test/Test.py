# @Dataset data
# @ImagePlus imp
# @ImageJ ij

roi = imp.getRoi()
x1 = roi.getBoundingRect().x
y1 = roi.getBoundingRect().y
x2 = x1 + roi.getBoundingRect().width
y2 = y1 + roi.getBoundingRect().height

for x in range(x1, x2):
	for y in range(y1, y2):
		dataRA.setPosition([x, y, t])
		targetRA.setPosition([x, y, t])
		if roi.contains(x, y):
			targetRA.get().set(dataRA.get())
