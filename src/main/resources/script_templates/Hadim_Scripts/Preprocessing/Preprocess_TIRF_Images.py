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
          "sigma1": 6,
          "sigma2": 2,
          "normalizeIntensity": True,
          "saveImage": False,
          "suffix": "-Preprocessed"}
module = runCommand(inputs, DOGFilterCommand, showOutputs=False)
filtered_dataset = module.getOutput("output")

inputs = {"input": filtered_dataset,
          "gaussianFilterSize": 50,
          "normalizeIntensity": True,
          "iteratePlane": False,
          "saveImage": False,
          "suffix": "-Preprocessed"}
module = runCommand(inputs, PseudoFlatFieldCorrectionCommand, showOutputs=True)
