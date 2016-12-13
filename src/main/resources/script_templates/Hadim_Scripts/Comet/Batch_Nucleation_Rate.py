# @File(label="Path to Nucleation_Rate.py script") scriptFile
# @File(label="Path to the dataset", style="directory") dataPath
# @Float(label="dt (sec)", required=true, value=3, stepSize=0.1) dt
# @Float(label="Pixel Size (um)", required=true, value=0.089, stepSize=0.01) pixel_size
# @Float(label="PREPROCESSING | DOG Sigma 1 (um)", required=false, value=0.400, stepSize=0.01) sigma1_um
# @Float(label="PREPROCESSING | DOG Sigma 2 (um)", required=true, value=0.120, stepSize=0.01) sigma2_um
# @Float(label="KYMOGRAPH | Circle Diameter (um)", required=true, value=4.5, stepSize=0.1) diameter_kymograph_um
# @Float(label="DETECTION | Spot Diameter", required=true, value=0.400, stepSize=0.01) diameter_spot_detection_um
# @Float(label="DETECTION | Threshold", required=true, value=15, stepSize=1) threshold_detection
# @Boolean(label="Save intermediates images ?", value=True) save_images

# @ImageJ ij
# @ScriptService scriptService

import os

params = {}
params['dt'] = dt
params['pixel_size'] = pixel_size
params['sigma1_um'] = sigma1_um
params['sigma2_um'] = sigma2_um
params['diameter_kymograph_um'] = diameter_kymograph_um
params['diameter_spot_detection_um'] = diameter_spot_detection_um
params['threshold_detection'] = threshold_detection
params['show_images'] = "None"
params['save_images'] = save_images
params['show_results'] = False


for root, dirs, files in os.walk(str(dataPath)):
	for fname in files:
		if fname.endswith(".nd"):
			print("Running script for %s" % os.path.join(root, fname))
			params['show_results'] = ij.dataset().open(os.path.join(root, fname))
			scriptModule = scriptService.run(str(scriptFile), bool(1), params).get()

print(scriptModule)