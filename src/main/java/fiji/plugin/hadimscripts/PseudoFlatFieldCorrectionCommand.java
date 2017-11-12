package fiji.plugin.hadimscripts;

import org.scijava.ItemIO;
import org.scijava.command.ContextCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;

import net.imagej.Dataset;
import net.imagej.axis.Axes;
import net.imagej.axis.CalibratedAxis;
import net.imagej.ops.convert.RealTypeConverter;
import net.imagej.ops.special.computer.UnaryComputerOp;
import net.imglib2.IterableInterval;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.real.FloatType;

@Plugin(type = ContextCommand.class, menuPath = "Plugins>Hadim>Pseudo Flat-Field Correction")
public class PseudoFlatFieldCorrectionCommand extends AbstractPreprocessingCommand {

	@Parameter(type = ItemIO.INPUT, description = "Source Image")
	private Dataset input;

	@Parameter(type = ItemIO.INPUT, min = "0", label = "Gaussian Filter Size (pixel)", description = "The size of the Gaussian filter used to estimate the background. Higher is this value, "
			+ "bigger will be the features used to estimate the background. For example, to filter "
			+ "an uneven background in fluorescent images, you can use try a size corresponding to 10% of "
			+ "the size of your image.")
	private Integer gaussianFilterSize = 50;

	@Parameter(type = ItemIO.INPUT, label = "Normalize Intensity")
	private Boolean normalizeIntensity = true;

	@Parameter(type = ItemIO.INPUT, label = "Save result image (if possible)")
	private Boolean saveImage = false;

	@Parameter(type = ItemIO.INPUT, label = "Suffix to use for saving")
	private String suffix = "-Preprocessed";

	@Parameter(type = ItemIO.OUTPUT)
	private Dataset output;

	@Override
	public void run() {
		this.output = doPseudoFlatFieldCorrection(this.input, this.gaussianFilterSize);
		this.saveImage(this.input, this.output, this.suffix);
	}

	public <T extends RealType<T>> Dataset doPseudoFlatFieldCorrection(Dataset input, double gaussianFilterSize) {
		Dataset dataset = input.duplicate();

		// Get Gaussian filtered image and use it as a background
		status.showStatus("Apply Gaussian filter to estimate the background.");
		Dataset background = this.applyGaussianFilter(dataset, gaussianFilterSize);

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

		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i != axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(out4);
		output.setAxes(axes);
		return output;
	}

	public <T extends RealType<T>> Dataset applyGaussianFilter(Dataset input, double gaussianFilterSize) {
		Dataset dataset = input.duplicate();

		int[] fixedAxisIndices = new int[] { dataset.dimensionIndex(Axes.X), dataset.dimensionIndex(Axes.Y) };

		RandomAccessibleInterval<T> out = (RandomAccessibleInterval<T>) ops.create().img(dataset.getImgPlus());

		double[] sigmas = new double[] { gaussianFilterSize, gaussianFilterSize };
		UnaryComputerOp op = (UnaryComputerOp) ops.op("filter.gauss", dataset.getImgPlus(), sigmas);
		ops.slice(out, (RandomAccessibleInterval<T>) dataset.getImgPlus(), op, fixedAxisIndices);

		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i != axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(out);
		output.setAxes(axes);
		return output;
	}

}
