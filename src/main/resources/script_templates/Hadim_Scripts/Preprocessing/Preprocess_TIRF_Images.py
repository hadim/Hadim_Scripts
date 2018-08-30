# @Float(label="Sigma 1", value=6) sigma1
# @Float(label="Sigma 2", value=2) sigma2
# @Float(label="Gaussian Filter Size", value=50) gaussian_filter_size
# @Boolean(label="Iterate XY plane (reduce memory usage)", value=False) iterate_plane
# @Boolean(label="Save Preprocessed Image", value=False) save_image
# @Dataset data

# @CommandService cs
# @ModuleService ms
# @PluginService ps

from sc.fiji.plugin.hadimscripts import DOGFilterCommand
from sc.fiji.plugin.hadimscripts import PseudoFlatFieldCorrectionCommand

def runCommand(inputs, command, showOutputs=False):
	from org.scijava.module.process import PreprocessorPlugin
	from org.scijava.module.process import PostprocessorPlugin
	command = cs.getCommand(command)
	pre = ps.createInstancesOfType(PreprocessorPlugin)
	post = ps.createInstancesOfType(PostprocessorPlugin)
	if showOutputs:
		module = ms.waitFor(ms.run(command, pre, post, inputs))
	else:
		module = ms.waitFor(ms.run(command, pre, None, inputs))
	return module

inputs = {"input": data,
          "sigma1": sigma1,
          "sigma2": sigma2,
          "normalizeIntensity": True,
          "saveImage": False,
          "suffix": ""}
module = runCommand(inputs, DOGFilterCommand, showOutputs=False)
filtered_dataset = module.getOutput("output")

inputs = {"input": filtered_dataset,
          "gaussianFilterSize": gaussian_filter_size,
          "normalizeIntensity": True,
          "iteratePlane": iterate_plane,
          "saveImage": save_image,
          "suffix": "-Preprocessed"}
module = runCommand(inputs, PseudoFlatFieldCorrectionCommand, showOutputs=True)
