import os


def do_threshold(ij, data, method, k1=1, save=False, output_dir=""):

	histo = ij.op().run("image.histogram", data.getImgPlus())
	threshold = ij.op().run("threshold.%s" % method, histo)

	ij.log().info('Threshold found with method "%s" : %f' % (method, threshold.getRealFloat()))

	if k1 != 1:
		threshold.setReal(threshold.getRealFloat() * k1)
		ij.log().info('New threshold modified (with k1=%f) : %f' % (k1, threshold.getRealFloat()))

	thresholded = ij.op().run("threshold.apply", data.getImgPlus(), threshold)

	output = ij.op().convert().uint8(thresholded)
	output = ij.dataset().create(output)

	# Set the correct axes
	axes = [data.axis(d) for d in range(0, data.numDimensions())]
	output.setAxes(axes)

	if save:
		fname = os.path.join(output_dir, "Thresholded.tif")
		ij.log().info("Saving at %s" % fname)
		output.setSource(fname)
		ij.io().save(output, fname)

	return output
