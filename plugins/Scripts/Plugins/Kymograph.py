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

    zIdx = dataset.dimensionIndex(Axes.Z)
    timeIdx = dataset.dimensionIndex(Axes.TIME)
    
    t_dim = dataset.dimension(timeIdx)
    z_dim = dataset.dimension(zIdx)
    
    if t_dim < z_dim:
        yes_no = ij.ui().showDialog("It appears this image has %i timepoints and %i Z slices.\n"
                                    "Do you want to swap Z and T axes ?"%(t_dim, z_dim),
                                    MessageType.QUESTION_MESSAGE,
                                    OptionType.YES_NO_OPTION)
                                    
        if yes_no == Result.YES_OPTION:
            if zIdx != -1:
                dataset.axis(zIdx).setType(Axes.TIME)
            if timeIdx != -1:
                dataset.axis(timeIdx).setType(Axes.Z)

def fill_kymograph(line, vector, t_dim, line_width, img, cursor_image, cursor_kymo, offset):
    """
    """

    dx = vector[0]
    dy = vector[1]

    (x1, y1), (x2, y2) = line
    
    # Iterate over all parallel lines (defined by line_width)
    for i in range(line_width):
        
        n = i - line_width / 2
        new_x1 = x1 + n * dy
        new_y1 = y1 - n * dx
        new_x2 = x2 + n * dy
        new_y2 = y2 - n * dx
    
        current_line = Line(new_x1, new_y1, new_x2, new_y2)
        current_line.setStrokeWidth(1)
        img.setRoi(current_line)
        
        xpoints = current_line.getInterpolatedPolygon().xpoints
        ypoints = current_line.getInterpolatedPolygon().ypoints
        
        # Iterate over every pixels defining the line
        for j, (x, y) in enumerate(zip(xpoints[:-1], ypoints[:-1])):
        
            x = int(round(x, 0))
            y = int(round(y, 0))
    
            # Iterate over the time axis
            for t in range(t_dim):
                cursor_image.setPosition([x, y, 0, t])
                cursor_kymo.setPosition([t, offset + j, i])
                cursor_kymo.get().set(cursor_image.get())

        """while cursor_image.hasNext():
            cursor_image.next()"""


def create_kymograph(dataset, lines, roi):
    """
    """

    timeIdx = dataset.dimensionIndex(Axes.TIME)
    t_dim = dataset.dimension(timeIdx)
    print(dataset.dimensionIndex(Axes.Z))
    # Get ImgPlus
    imgp = dataset.getImgPlus()

    # Get lines width
    line_width = int(roi.getStrokeWidth())
    line_width = max(line_width, 1)

    # Get lines length
    lines_length = []
    lines_vector_scaled = []

    for (x1, y1), (x2, y2) in lines:
        dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

        dx = (x1 - x2) / dist
        dy = (y1 - y2) / dist
        
        lines_length.append(int(round(dist, 0)))
        lines_vector_scaled.append([dx, dy])
        
    total_length = sum(lines_length)

    ij.log().info("Get %i lines with a width of %i and a "
                  "total length of %i to process." % (len(lines), line_width, total_length))

    # Create kymograph dataset
    dims = [t_dim, total_length - len(lines) + 1, line_width]
    axes = [Axes.X, Axes.Y, Axes.Z]
    title = dataset.getName() + " (Kymograph)"
    kymograph = ij.dataset().create(dims, title, axes,
                                    dataset.getValidBits(),
                                    dataset.isSigned(),
                                    not dataset.isInteger())
    kymo_img = kymograph.getImgPlus()

    # Get image and kymograph cursor
    cursor_image = imgp.randomAccess()
    cursor_kymo = kymo_img.randomAccess()
    
    offset = 0
    for line, vector, length in zip(lines, lines_vector_scaled, lines_length):

        fill_kymograph(line, vector, t_dim, line_width, img,
                       cursor_image, cursor_kymo, offset)

        offset += length - 1
    
     # Put back the original line ROI
    img.setRoi(roi)

    return kymograph


def project_kymograph(kymograph):
    """
    """

    # Create a new dataset with the projected kymograph
    x_dim = kymograph.dimension(kymograph.dimensionIndex(Axes.X))
    y_dim = kymograph.dimension(kymograph.dimensionIndex(Axes.Y))
    dims = [x_dim, y_dim]
    axes = [Axes.X, Axes.Y]
    title = dataset.getName() + " (Projected Kymograph)"
    kymograph_projected = ij.dataset().create(dims, title, axes,
                                              dataset.getValidBits(),
                                              dataset.isSigned(),
                                              not dataset.isInteger())
    
    # Project kymograph (max or mean) with IJ Ops
    max_op = ij.op().op(Ops.Stats.Max, kymograph)
    ij.op().transform().project(kymograph_projected.getImgPlus().getImg(),
                                kymograph,
                                max_op,
                                kymograph.dimensionIndex(Axes.Z))

    return kymograph_projected


# Main functions

def main():
    print(dataset.dimensionIndex(Axes.TIME))
    ask_swap_dimensions(dataset)
    print(dataset.dimensionIndex(Axes.TIME))

    # Get line ROI
    roi = img.getRoi()

    if(not roi):
        ij.ui().showDialog("Please define a line in order to build the kymograph.")
        return False
    
    # Check roi and convert it to a list of line
    if roi.getTypeAsString() == "Straight Line":
        lines = [[[roi.x1, roi.y1], [roi.x2, roi.y2]]]
        
    elif roi.getTypeAsString() == "Polyline":
        polygon = roi.getPolygon()
        n_lines = polygon.npoints - 1
        xpoints = polygon.xpoints
        ypoints = polygon.ypoints
    
        lines = []
        for i in range(n_lines):
            line = [[xpoints[i], ypoints[i]], [xpoints[i+1], ypoints[i+1]]]
            lines.append(line)
            
    else:
        ij.ui().showDialog("Please use the Straight Line or Segmented Line selection tool.")
        return False

    print(lines)

    kymograph = create_kymograph(dataset, lines, roi)
    kymograph_projected = project_kymograph(kymograph)
    
    # Display dataset
    ij.ui().show(kymograph)
    ij.ui().show(kymograph_projected)

main()