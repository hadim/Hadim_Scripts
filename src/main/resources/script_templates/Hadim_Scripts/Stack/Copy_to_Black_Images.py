# @Dataset(label="4D Stack (XYCT)") stack
# @ImageJ ij
# @OUTPUT Dataset output

# Find all images where the sum of the pixels is 0 and copy the
# last non-zero image to it from the same channels.
# Stack needs to be 4D: X, Y, C and T

import sys

dims = [stack.axis(i).type().toString() for i in range(stack.numDimensions())]

if "X" not in dims or "Y" not in dims:
    ij.status().warn("The image lacks X and/or Y dimensions.")
    sys.exit(1)

if "Time" not in dims:
    ij.status().warn("The image lacks the Time dimension.")
    sys.exit(1)

if stack.numDimensions() < 3 or stack.numDimensions() > 4:
    ij.status().warn("The stack needs to be from dimension 3 or 4.")
    sys.exit(1)

channel_dims = stack.getChannels() if "Channel" in dims else 1

output = stack.duplicate()

for channel_index in range(channel_dims):
    non_zero_image_time_index = -1

    for t in range(stack.getFrames()):
        if stack.numDimensions() == 3:
	        start_indexes = [0, 0, t]
	        end_indexes = [stack.getWidth()-1, stack.getHeight()-1, t]
        elif stack.numDimensions() == 4:
	        start_indexes = [0, 0, channel_index, t]
	        end_indexes = [stack.getWidth()-1, stack.getHeight()-1, channel_index, t]

        view = ij.op().transform().intervalView(stack, start_indexes, end_indexes)
        sum_pixels = ij.op().stats().sum(view).get()

        if sum_pixels == 0:

            if non_zero_image_time_index >= 0:
  
                viewOut = ij.op().transform().intervalView(output, start_indexes, end_indexes)
                if stack.numDimensions() == 3:
                	start = [0, 0, non_zero_image_time_index]
                	end = [stack.getWidth()-1, stack.getHeight()-1, non_zero_image_time_index]
	                viewIn = ij.op().transform().intervalView(stack, start, end)
	                
                elif stack.numDimensions() == 4:
                	start = [0, 0, channel_index, non_zero_image_time_index]
                	end = [stack.getWidth()-1, stack.getHeight()-1, channel_index, non_zero_image_time_index]
	                viewIn = ij.op().transform().intervalView(stack, start, end)

                ij.op().copy().iterableInterval(viewOut, viewIn)
        else:
            non_zero_image_time_index = t