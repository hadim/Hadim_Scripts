import math

from net.imagej.axis import Axes

from net.imglib2.realtransform import RealViews
from net.imglib2.realtransform import AffineTransform2D
from net.imglib2.interpolation.randomaccess import LanczosInterpolatorFactory

from .ij_utils import get_axis


def rotate_stack(ij, data, angle, axis_type=None):
	"""Rotate all the frames along an axis.

	Parameters
	----------
	angle : In degrees.
	axis_type : Along which axis to slice. Can be ["X", "Y", "Z", "TIME", "CHANNEL"]
	"""

	# Get the center of the images so we do the rotation according to it
	center = [int(round((data.max(d) / 2 + 1))) for d in range(0, data.numDimensions())]

	# Convert angles to radians
	angle_rad = angle * math.pi / 180

	# Build the affine transformation
	affine = AffineTransform2D()
	affine.translate([-p for p in center])
	affine.rotate(angle_rad)
	affine.translate(center)

	# Get the interpolator
	interpolator = LanczosInterpolatorFactory()

	if axis_type:
		# Iterate over all frame in the stack
		axis = get_axis(axis_type)
		output = []
		for d in range(data.dimension(axis)):

		    # Get the current frame
		    frame = corp(ij, data, {"TIME": [d, d]})

		    # Get the interpolate view of the frame
		    extended = ij.op().run("transform.extendZeroView", frame)
		    interpolant = ij.op().run("transform.interpolateView", extended, interpolator)

		    # Apply the transformation to it
		    rotated = RealViews.affine(interpolant, affine)

		    # Set the intervals
		    rotated = ij.op().run("transform.intervalView", rotated, frame)

		    output.append(rotated)

		output = Views.stack(output)

	else:
		# Get the interpolate view of the frame
		extended = ij.op().run("transform.extendZeroView", data)
		interpolant = ij.op().run("transform.interpolateView", extended, interpolator)

		# Apply the transformation to it
		rotated = RealViews.affine(interpolant, affine)

		# Set the intervals
		output = ij.op().run("transform.intervalView", rotated, data)

	return output
