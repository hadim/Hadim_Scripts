# @ImageJ ij
# @Dataset data

fname = "/home/hadim/Insync/Data/Microscopy/Misc/Fun/Microtubule_Dancing/2016.11.30/Movie_1/Microtubule.Bending_1_MMStack_Pos0.ome.tif"

#data = ij.io().open(fname)
#ij.ui().show(data)

ij.io().save(data, "/home/hadim/test.avi")