
package sc.fiji.plugin.hadimscripts;

import io.scif.services.DatasetIOService;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import net.imagej.Dataset;
import net.imagej.DatasetService;
import net.imagej.axis.Axes;
import net.imagej.axis.CalibratedAxis;
import net.imagej.ops.OpService;
import net.imagej.ops.special.computer.UnaryComputerOp;
import net.imglib2.FinalInterval;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;

import org.apache.commons.io.FilenameUtils;
import org.scijava.app.StatusService;
import org.scijava.command.Command;
import org.scijava.log.LogService;
import org.scijava.plugin.Parameter;

public abstract class AbstractPreprocessingCommand implements Command {

	@Parameter
	protected LogService log;

	@Parameter
	protected OpService ops;

	@Parameter
	protected DatasetService ds;

	@Parameter
	protected StatusService status;

	@Parameter
	protected DatasetIOService dsio;

	protected void saveImage(Dataset input, Dataset output, String suffix) {

		// Check if input is saved on disk
		if (input != null && input.getSource() != null && input.getSource() != "") {

			String newFilename = this.suffixPath(input.getSource(), suffix);

			// Save output image
			try {
				dsio.save(output, newFilename);
				print("Preprocessed image saved at " + newFilename);
			}
			catch (IOException e) {
				log.error("Cannot save the output image to disk because : " + e
					.getLocalizedMessage());
			}
		}
		else {
			status.showStatus(
				"Output image cannot be saved on disk because the input " +
					"image is not saved on disk.");
		}
	}

	protected String suffixPath(String path, String suffix) {
		String extension = FilenameUtils.getExtension(path);
		String newFilename = FilenameUtils.removeExtension(path) + suffix + "." +
			extension;

		return newFilename;
	}

	protected <T extends RealType<T>> Dataset matchRAIToDataset(
		RandomAccessibleInterval<T> rai, Dataset dataset)
	{
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i < axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(rai);
		output.setAxes(axes);
		return output;
	}

	protected <T extends RealType<T>> Dataset matchRAIToDataset(Img<T> rai,
		Dataset dataset)
	{
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i < axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(rai);
		output.setAxes(axes);
		return output;
	}

	protected <T extends RealType<T>> Dataset matchRAIToDataset(Dataset original,
		Dataset dataset)
	{
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i < axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		original.setAxes(axes);
		return original;
	}

	protected List<FinalInterval> iterateOverXYPlane(Dataset dataset) {
		List<FinalInterval> intervals = new ArrayList<>();
		FinalInterval interval;
		long[] min = new long[dataset.numDimensions()];
		long[] max = new long[dataset.numDimensions()];

		min[dataset.dimensionIndex(Axes.X)] = dataset.min(dataset.dimensionIndex(
			Axes.X));
		min[dataset.dimensionIndex(Axes.Y)] = dataset.min(dataset.dimensionIndex(
			Axes.Y));

		max[dataset.dimensionIndex(Axes.X)] = dataset.max(dataset.dimensionIndex(
			Axes.X));
		max[dataset.dimensionIndex(Axes.Y)] = dataset.max(dataset.dimensionIndex(
			Axes.Y));

		int index1 = dataset.dimensionIndex(Axes.CHANNEL);
		int index2 = -1;
		if (index1 == -1) {
			index1 = dataset.dimensionIndex(Axes.TIME);
		}
		else {
			index2 = dataset.dimensionIndex(Axes.TIME);
		}

		for (int i = 0; i < dataset.dimension(index1); i++) {
			min[index1] = i;
			max[index1] = i;
			if (index2 != -1) {
				for (int j = 0; j < dataset.dimension(index2); j++) {
					min[index2] = j;
					max[index2] = j;
					interval = new FinalInterval(min, max);
					intervals.add(interval);
				}
			}
			else {
				interval = new FinalInterval(min, max);
				intervals.add(interval);
			}

		}
		return intervals;
	}

	protected <T extends RealType<T>> Dataset applyGaussianFilter(Dataset input,
		double gaussianFilterSize)
	{
		Dataset dataset = input.duplicate();

		int[] fixedAxisIndices = new int[] { dataset.dimensionIndex(Axes.X), dataset
			.dimensionIndex(Axes.Y) };

		RandomAccessibleInterval<T> out = (RandomAccessibleInterval<T>) ops.create()
			.img(dataset.getImgPlus());

		double[] sigmas = new double[] { gaussianFilterSize, gaussianFilterSize };
		UnaryComputerOp op = (UnaryComputerOp) ops.op("filter.gauss", dataset
			.getImgPlus(), sigmas);
		ops.slice(out, (RandomAccessibleInterval<T>) dataset.getImgPlus(), op,
			fixedAxisIndices);

		return matchRAIToDataset(out, dataset);
	}

}
