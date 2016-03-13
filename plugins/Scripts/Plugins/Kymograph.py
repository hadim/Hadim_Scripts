# @ImageJ ij
# @ImagePlus img
# @Dataset dataset

import math
import sys

from net.imagej.axis import Axes
from net.imagej.ops import Ops

from ij.gui import Line

# Functions

def ask_swap_dimensions(dataset):
    """Ask the user to swap Z and T axes dimensions if needed.
    """
    from org.scijava.ui.DialogPrompt import MessageType
    from org.scijava.ui.DialogPrompt import OptionType
    from org.scijava.ui.DialogPrompt import Result
    
    t_dim = dataset.dimension(dataset.dimensionIndex(Axes.TIME))
    z_dim = dataset.dimension(dataset.dimensionIndex(Axes.Z))
    
    if t_dim < z_dim:
        yes_no = ij.ui().showDialog("It appears this image has %i timepoints and %i Z slices.\n"
                                    "Do you want to swap Z and T axes ?"%(t_dim, z_dim),
                                    MessageType.QUESTION_MESSAGE,
                                    OptionType.YES_NO_OPTION)
                                    
        if yes_no == Result.YES_OPTION:
            z_dim, t_dim = t_dim, z_dim

    return z_dim, t_dim

def create_kymograph(dataset, line, t_dim, debug=False):
    """
    """
    # Get ImgPlus
    imgp = dataset.getImgPlus()
    
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
    dims = [t_dim, line_length + 1000, line_width]
    axes = [Axes.X, Axes.Y, Axes.Z]
    kymograph = ij.dataset().create(dims, "Kymograph", axes,
                                    dataset.getValidBits(),
                                    dataset.isSigned(),
                                    not dataset.isInteger())
    kymo_img = kymograph.getImgPlus()

    # Get image and kymograph cursor
    cursor = imgp.randomAccess()
    cursor_kymo = kymo_img.randomAccess()

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
                cursor_kymo.setPosition([t, j, i])
                cursor_kymo.get().set(cursor.get())
    
     # Put back the original line ROI
    img.setRoi(line)

    # Now create a new dataset with the projected kymograph
    dims = [t_dim, line_length]
    axes = [Axes.X, Axes.Y]
    kymograph_projected = ij.dataset().create(dims, "Projected Kymograph", axes,
                                              dataset.getValidBits(),
                                              dataset.isSigned(),
                                              not dataset.isInteger())
    
    # Project kymograph (max or mean) with IJ Ops
    max_op = ij.op().op(Ops.Stats.Max, kymograph)
    ij.op().image().project(kymograph_projected.getImgPlus().getImg(),
                            kymograph,
                            max_op,
                            kymograph.dimensionIndex(Axes.Z))
    
    # Display dataset
    ij.ui().show(kymograph)
    ij.ui().show(kymograph_projected)

# Main functions

def main():

    z_dim, t_dim = ask_swap_dimensions(dataset)

    # Get line ROI
    line = img.getRoi()
    
    if line == None or line.getTypeAsString() != "Straight Line":
        ij.ui().showDialog("Please use the straight line selection tool")
        return False

    # Create kymograph
    create_kymograph(dataset, line, t_dim)
    
main()