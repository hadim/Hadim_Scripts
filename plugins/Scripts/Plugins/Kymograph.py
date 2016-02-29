# @ImageJ ij
# @ImagePlus img
# @Dataset data

import math
import sys

from net.imagej.axis import Axes
from net.imagej.ops import Ops

from ij.gui import Line

# Get image processor and imgplus
imp = img.getProcessor()
imgp = data.getImgPlus()

# Get time dimension
t_dim = data.dimension(data.dimensionIndex(Axes.TIME))

# Get line ROI
line = img.getRoi()

if line == None or line.getTypeAsString() != "Straight Line":
	ij.ui().showDialog("Please use the straight line selection tool")
	sys.exit(0)

# Get line vector
dx = line.x1 - line.x2
dy = line.y1 - line.y2

# Get line length
line_length = int(round(math.sqrt(dx * dx + dy * dy), 0))

# Scale line vector
dx /= line_length
dy /= line_length

# Get line width dimension
line_width = int(line.getStrokeWidth())
line_width = max(line_width, 1)

# Create kymograph dataset
dims = [line_length, t_dim + 1, line_width]
axes = [Axes.X, Axes.Y, Axes.Z]
kymograph = ij.dataset().create(dims, "Kymograph", axes,
								data.getValidBits(),
								data.isSigned(),
								not data.isInteger())

# Get image and kymograph cursor
cursor = imgp.randomAccess()
cursor_kymo = kymograph.getImgPlus().randomAccess()

# Iterate over all parallel lines (defined by line_width)
for i in range(line_width):
    n = i - line_width / 2
    new_x1 = line.x1 + n * dy
    new_y1 = line.y1 - n * dx
    new_x2 = line.x2 + n * dy
    new_y2 = line.y2 - n * dx

    current_line = Line(new_x1, new_y1, new_x2, new_y2)
    current_line.setStrokeWidth(1)
    img.setRoi(current_line)

    xpoints = current_line.getInterpolatedPolygon().xpoints
    ypoints = current_line.getInterpolatedPolygon().ypoints

    # Iterate over every pixels defining the line
    for j, (x, y) in enumerate(zip(xpoints, ypoints)):
    
	    x = int(round(x, 0))
	    y = int(round(y, 0))

	    # Iterate over the time axis
	    for t in range(t_dim):
	    	
	        cursor.setPosition([x, y, t])
	        cursor_kymo.setPosition([j, t, i])
	        cursor_kymo.get().set(cursor.get())

# Put back the original line ROI
img.setRoi(line)

# Now create a new dataset with the projected kymograph
dims = [line_length, t_dim]
axes = [Axes.X, Axes.Y]
kymograph_projected = ij.dataset().create(dims, "Projected Kymograph", axes,
								          data.getValidBits(),
								          data.isSigned(),
								          not data.isInteger())

# Project kymograph (max or mean) with IJ Ops
max_op = ij.op().op(Ops.Stats.Max, data)
ij.op().image().project(kymograph_projected.getImgPlus().getImg(),
				        kymograph,
				        max_op,
					    kymograph.dimensionIndex(Axes.Z))

# Display dataset
ij.ui().show(kymograph)
ij.ui().show(kymograph_projected)