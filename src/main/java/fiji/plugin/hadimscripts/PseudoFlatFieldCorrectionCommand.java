package fiji.plugin.hadimscripts;

import java.util.ArrayList;
import java.util.List;

import org.scijava.ItemIO;
import org.scijava.command.ContextCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;
import org.scijava.ui.UIService;

import net.imagej.Dataset;
import net.imagej.axis.Axes;
import net.imagej.ops.convert.RealTypeConverter;
import net.imglib2.FinalInterval;
import net.imglib2.Interval;
import net.imglib2.IterableInterval;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.real.FloatType;
import net.imglib2.util.Intervals;
import net.imglib2.view.Views;

@Plugin(type = ContextCommand.class, menuPath = "Plugins>Hadim>Pseudo Flat-Field Correction")
public class PseudoFlatFieldCorrectionCommand extends AbstractPreprocessingCommand {

	@Parameter
	private UIService ui;

	@Parameter(type = ItemIO.INPUT, description = "Source Image")
	private Dataset input;

	@Parameter(type = ItemIO.INPUT, min = "0", label = "Gaussian Filter Size (pixel)", description = "The size of the Gaussian filter used to estimate the background. Higher is this value, "
			+ "bigger will be the features used to estimate the background. For example, to filter "
			+ "an uneven background in fluorescent images, you can use try a size corresponding to 10% of "
			+ "the size of your image.")
	private Integer gaussianFilterSize = 50;

	@Parameter(type = ItemIO.INPUT, label = "Normalize Intensity", required = false)
	private Boolean normalizeIntensity = true;

	@Parameter(type = ItemIO.INPUT, label = "Iterate over XY planes (reduce memory usage)", required = false)
	private Boolean iteratePlane = false;

	@Parameter(type = ItemIO.INPUT, label = "Save result image (if possible)", required = false)
	private Boolean saveImage = false;

	@Parameter(type = ItemIO.INPUT, label = "Suffix to use for saving", required = false)
	private String suffix = "-Preprocessed";

	@Parameter(type = ItemIO.OUTPUT)
	private Dataset output;

	@Override
	public void run() {

		if (this.iteratePlane) {
			this.output = doPseudoFlatFieldCorrectionXYPlaneIterate(this.input, this.gaussianFilterSize);
		} else {
			this.output = doPseudoFlatFieldCorrection(this.input, this.gaussianFilterSize);
		}

		if (this.saveImage) {
			this.saveImage(this.input, this.output, this.suffix);
		}
	}

	public <T extends RealType<T>> Dataset doPseudoFlatFieldCorrectionXYPlaneIterate(Dataset input,
			double gaussianFilterSize) {
		Dataset dataset = input.duplicate();

		if (dataset.dimension(Axes.Z) > 1) {
			log.error("The \"iterate over XY planes\" option cannot be used with more " + "than one Z stack ("
					+ dataset.dimension(Axes.Z) + " detected).");
			return null;
		}

		double[] sigmas = new double[] { gaussianFilterSize, gaussianFilterSize };

		List<FinalInterval> intervals = this.iterateOverXYPlane(dataset);

		List<RandomAccessibleInterval<T>> stack = new ArrayList<>();
		RandomAccessibleInterval plane;
		IterableInterval<FloatType> floatPlane;
		IterableInterval<FloatType> background;
		IterableInterval<FloatType> subtracted;
		RealTypeConverter converter;
		Img<T> out;

		for (int i = 0; i < intervals.size(); i++) {

			// Get the XY plane
			plane = ops.transform().crop(dataset, intervals.get(i));

			// // Convert to 32 bit
			floatPlane = (IterableInterval<FloatType>) ops.run("convert.float32", plane);

			// Estimate the background
			background = (IterableInterval<FloatType>) ops.run("filter.gauss", floatPlane, sigmas);

			// Create empty plane to store outputs
			subtracted = ops.create().img(floatPlane);
			out = ops.create().img(plane);

			// Do the subtraction
			ops.math().subtract(subtracted, (IterableInterval) floatPlane, (IterableInterval) background);

			// Convert back to the original type
			converter = (RealTypeConverter) ops.op("convert.clip", dataset.getImgPlus().firstElement(),
					subtracted.firstElement());
			ops.convert().imageType(out, subtracted, converter);

			stack.add((RandomAccessibleInterval) out);

			status.showProgress(i, intervals.size() - 1);
		}

		RandomAccessibleInterval im = ops.transform().stack(stack);

		if (dataset.numDimensions() != im.numDimensions()) {

			long middleDimension = im.dimension(2) / dataset.dimension(Axes.CHANNEL);
			Interval interval1 = Intervals.createMinMax(0, 0, 0, im.dimension(0) - 1, im.dimension(1) - 1,
					middleDimension - 1);
			Interval interval2 = Intervals.createMinMax(0, 0, middleDimension, im.dimension(0) - 1, im.dimension(1) - 1,
					im.dimension(2) - 1);

			RandomAccessibleInterval offsetInterval1 = Views.offsetInterval(im, interval1);
			RandomAccessibleInterval offsetInterval2 = Views.offsetInterval(im, interval2);

			im = Views.stack(offsetInterval1, offsetInterval2);

			if (dataset.dimension(dataset.dimensionIndex(Axes.CHANNEL)) != im
					.dimension(dataset.dimensionIndex(Axes.CHANNEL))) {
				im = Views.permute(im, 2, 3);
			}
		}

		return this.matchRAIToDataset(im, dataset);
	}

	public <T extends RealType<T>> Dataset doPseudoFlatFieldCorrection(Dataset input, double gaussianFilterSize) {
		Dataset dataset = input.duplicate();

		// Get Gaussian filtered image and use it as a background
		status.showStatus("Apply Gaussian filter to estimate the background.");
		Dataset background = this.applyGaussianFilter(dataset, gaussianFilterSize);

		status.showProgress(1, 3);

		// Convert to 32 bits
		IterableInterval<FloatType> out = (IterableInterval<FloatType>) ops.run("convert.float32",
				dataset.getImgPlus());
		IterableInterval<FloatType> original = (IterableInterval<FloatType>) ops.run("convert.float32",
				dataset.getImgPlus());
		IterableInterval<FloatType> backgroundFloat = (IterableInterval<FloatType>) ops.run("convert.float32",
				background.getImgPlus());

		// Do subtraction
		status.showStatus("Subtract image to background.");
		IterableInterval<FloatType> out2 = (IterableInterval<FloatType>) ops.create().img(out);
		ops.math().subtract(out2, original, backgroundFloat);

		status.showProgress(2, 3);

		// Clip intensities to input image type
		Img<T> out3 = (Img<T>) ops.create().img(dataset.getImgPlus());
		RealTypeConverter op2 = (RealTypeConverter) ops.op("convert.clip", dataset.getImgPlus().firstElement(),
				out2.firstElement());
		ops.convert().imageType(out3, out2, op2);

		Img<T> out4 = out3;
		if (normalizeIntensity) {
			out4 = (Img<T>) ops.create().img(out3);
			RealTypeConverter scaleOp = (RealTypeConverter) ops.op("convert.normalizeScale", out4.firstElement(),
					out3.firstElement());
			ops.convert().imageType(out4, out3, scaleOp);
		}

		status.showProgress(3, 3);

		return matchRAIToDataset(out4, dataset);
	}

}