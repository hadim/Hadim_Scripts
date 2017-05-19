# @Dataset(label="Single Frame") singleFrame
# @Dataset(label="Stack") stack1
# @ImageJ ij
# @OUTPUT Dataset stack

from net.imglib2.view import Views
from net.imglib2.img import ImgView
from net.imglib2.img.array import ArrayImgFactory
from net.imagej.axis import Axes
from net.imagej import ImgPlus

nFrames = stack1.getFrames() if stack1.getFrames() > 1 else stack1.getDepth()

stack1 = Views.dropSingletonDimensions(stack1)

stack2_list = list([singleFrame.duplicate() for i in range(nFrames)])
stack2 = Views.stack(stack2_list)
stack2 = Views.dropSingletonDimensions(stack2)

stack = Views.stack(list([stack1, stack2]))
stack = ImgPlus(ImgView.wrap(stack, ArrayImgFactory()), "", [Axes.X, Axes.Y, Axes.TIME, Axes.CHANNEL])
stack = ij.dataset().create(stack)

ij.ui().show(stack)
