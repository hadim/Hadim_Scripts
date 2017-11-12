package fiji.plugin.hadimscripts;

import org.scijava.ItemIO;
import org.scijava.command.ContextCommand;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;

import net.imagej.Dataset;
import net.imagej.axis.Axes;
import net.imagej.ops.convert.RealTypeConverter;
import net.imagej.ops.special.computer.UnaryComputerOp;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.real.FloatType;

@Plugin(type = ContextCommand.class, menuPath = "Plugins>Hadim>DOG Filter")
public class DOGFilterCommand extends AbstractPreprocessingCommand {

	@Parameter(type = ItemIO.INPUT, description = "Source Image")
	private Dataset input;

	@Parameter(type = ItemIO.INPUT, min = "1", label = "Sigma 1")
	private Integer sigma1 = 6;

	@Parameter(type = ItemIO.INPUT, min = "1", label = "Sigma 2")
	private Integer sigma2 = 2;

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
		this.output = applyDOGFilter(this.input, this.sigma1, this.sigma2);
		if (this.saveImage) {
			this.saveImage(this.input, this.output, this.suffix);
		}
	}

	public <T extends RealType<T>> Dataset applyDOGFilter(Dataset input, int sigma1, int sigma2) {

		if (sigma1 < sigma2) {
			int tmp = sigma1;
			sigma1 = sigma2;
			sigma2 = tmp;
		}

		Dataset dataset = input.duplicate();

		int[] fixedAxisIndices = new int[] { dataset.dimensionIndex(Axes.X), dataset.dimensionIndex(Axes.Y) };

		// Convert to 32 bits
		Img<FloatType> out = (Img<FloatType>) ops.run("convert.float32", dataset.getImgPlus());

		// Apply filter
		Img<FloatType> out2 = ops.create().img(out);
		UnaryComputerOp op = (UnaryComputerOp) ops.op("filter.dog", out, sigma1, sigma2);
		ops.slice(out2, out, op, fixedAxisIndices);

		// Clip intensities
		Img<T> out3 = (Img<T>) ops.create().img(dataset.getImgPlus());
		RealTypeConverter op2 = (RealTypeConverter) ops.op("convert.clip", dataset.getImgPlus().firstElement(),
				out2.firstElement());
		ops.convert().imageType(out3, out2, op2);

		return matchRAIToDataset(out3, dataset);
	}

}
