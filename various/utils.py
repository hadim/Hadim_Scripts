# @DatasetService data
# @ImageDisplayService imgdisplay
# @ImageJ ij
# @DefaultLegacyService legacy

from ij import IJ
import os

path = "/media/thor/data/microscopy_data/ndc80-gfp-cdc11-cfp-beginning-of-mitosis/movies/wt/2015.01.23"

def process(root, f):
    print(f)
    root, f = ('/media/thor/data/microscopy_data/ndc80-gfp-cdc11-cfp-beginning-of-mitosis/movies/wt/2015.01.23/movie_9', 'crop3_movie_9_MMStack_Pos0.ome.tif')
    full_path = os.path.join(root, f)
    dest_path = os.path.join(root, "tmp", f)
    if not os.path.isdir(os.path.join(root, "tmp")):
        os.makedirs(os.path.join(root, "tmp"))
    
    IJ.open(full_path)
    imp = IJ.getImage()
    
    IJ.run("Properties...", "frame=5")
    IJ.run("Bio-Formats Exporter", "save=" + dest_path + " compression=Uncompressed")
    imp.close()

for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith("Pos0.ome.tif"):
            process(root, f)
