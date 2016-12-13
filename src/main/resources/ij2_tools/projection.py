import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops

from .ij_utils import get_axis
from .ij_utils import get_projection_method


def do_projection(ij, data, axis_type="Z", method="Max", save=False, output_dir=""):

    # Select which dimension to project
    dim = data.dimensionIndex(get_axis(axis_type))

    if dim == -1:
        ij.log().info("%s dimension not found. %s Projection skipped." % (axis_type, axis_type))
        output = data.duplicate()
    elif data.dimension(dim) == 1:
        ij.log().info("%s dimension has only one frame. %s Projection skipped." % (axis_type, axis_type))
        output = data.duplicate()
    else:
        ij.log().info("Performing Z maximum projection")

        # Write the output dimensions
        projected_dimensions = [data.dimension(d) for d in range(0, data.numDimensions()) if d != dim]

        # Create the output image
        z_projected = ij.op().create().img(projected_dimensions)

        # Create the op and run it
        max_op = ij.op().op(get_projection_method(method), data)
        ij.op().transform().project(z_projected, data, max_op, dim)

        # Clip image to the input type
        clipped = ij.op().create().img(z_projected, data.getImgPlus().firstElement())
        clip_op = ij.op().op("convert.clip", data.getImgPlus().firstElement(), z_projected.firstElement())
        ij.op().convert().imageType(clipped, z_projected, clip_op)

        # Create a dataset
        output = ij.dataset().create(clipped)

        # Set the correct axes
        axes = [data.axis(d) for d in range(0, data.numDimensions()) if d != dim]
        output.setAxes(axes)

    if save:
        fname = os.path.join(output_dir, "%s_Projected_%s.tif" % (axis_type, method))
        ij.log().info("Saving at %s" % fname)
        output.setSource(fname)
        ij.io().save(output, fname)

    return output
