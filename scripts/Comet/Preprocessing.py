# @ImageJ ij
# @Dataset data
# @LogService log

import math
import os

from net.imagej.axis import Axes
from net.imagej.ops import Ops

from ij2_tools import do_z_projection
from ij2_tools import apply_dog_filter
from ij2_tools import do_threshold


# Parameters
show_images = False
save_images = False

sigma1 = 4.2
sigma2 = 1.25
threshold_method = "otsu"
k1 = 1

output_dir = os.path.join(os.path.dirname(data.getSource()), "Analysis_Comets")
if not os.path.exists(output_dir):
	os.makedirs(output_dir)


## Z Projection
z_projected = do_z_projection(ij, data, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("z_projected", z_projected)

## DOG Filtering
dog = apply_dog_filter(ij, z_projected, sigma1, sigma2, save=save_images, output_dir=output_dir)
if show_images:
	ij.ui().show("dog", dog)

## Segmentation
thresholded = do_threshold(ij, dog, threshold_method, k1, save=save_images, output_dir=output_dir)
ij.ui().show("thresholded", thresholded)
