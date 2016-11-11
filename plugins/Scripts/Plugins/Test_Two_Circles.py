# @ImageJ ij
# @ImagePlus imp

import math
import operator

from net.imglib2.img.display.imagej import ImageJFunctions

from ij.plugin.frame import RoiManager
from ij.gui import PointRoi
from ij.gui import Roi
from ij.gui import PolygonRoi

def get_roi_manager(new=False):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm

def get_closest_point_index(points, ref):
	closest_index = 0
	distances = []
	for i, point in enumerate(points):
		d = math.sqrt((point[0] - ref[0])**2 + (point[1] - ref[1])**2)
		distances.append(d)
	return min(xrange(len(distances)), key=distances.__getitem__)

def get_circle_points(x_center, y_center, radius, n=20):
	xpoints = []
	ypoints = []
	points = []
	for i in range(0, n+1):
		x = math.cos(2*math.pi/n*i) * radius + x_center
		y =  math.sin(2*math.pi/n*i) * radius + y_center
		xpoints.append(x)
		ypoints.append(y)
		points.append([x, y])
	return xpoints[:-1], ypoints[:-1], points[:-1]
	
black = ij.op().create().img([800, 600])
ij.ui().show(black)

x1, y1 = 260, 260
x2, y2 = 460, 400

rm = get_roi_manager(new=True)
centers = PointRoi([x1, x2], [y1, y2])
rm.addRoi(centers)
rm.runCommand("Show All")

xcen, ycen = (x1 + x2) / 2, (y1 + y2) / 2
rm.addRoi(PointRoi([xcen], [ycen]))

radius = math.sqrt((x1 - xcen)**2 + (y1 - ycen)**2)
radius *= 1.1

xpoints, ypoints, points = get_circle_points(x1, y1, radius, n=30)
closest_point_index = get_closest_point_index(points, [xcen, ycen])
xpoints = xpoints[closest_point_index:] + xpoints[:closest_point_index]
ypoints = ypoints[closest_point_index:] + ypoints[:closest_point_index]
circle = PolygonRoi(xpoints, ypoints, Roi.POLYLINE)
rm.addRoi(circle)

xpoints, ypoints, points = get_circle_points(x2, y2, radius, n=30)
closest_point_index = get_closest_point_index(points, [xcen, ycen])
xpoints = xpoints[closest_point_index:] + xpoints[:closest_point_index]
ypoints = ypoints[closest_point_index:] + ypoints[:closest_point_index]
circle = PolygonRoi(xpoints, ypoints, Roi.POLYLINE)
rm.addRoi(circle)

