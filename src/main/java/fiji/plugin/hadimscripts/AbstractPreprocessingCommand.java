package fiji.plugin.hadimscripts;

import java.io.IOException;

import org.apache.commons.io.FilenameUtils;
import org.scijava.app.StatusService;
import org.scijava.command.Command;
import org.scijava.log.LogService;
import org.scijava.plugin.Parameter;

import io.scif.services.DatasetIOService;
import net.imagej.Dataset;
import net.imagej.DatasetService;
import net.imagej.axis.CalibratedAxis;
import net.imagej.ops.OpService;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;

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
		if (input.getSource() != null) {
			// Create new filename
			String extension = FilenameUtils.getExtension(input.getSource());
			String newFilename = FilenameUtils.removeExtension(input.getSource()) + suffix + "." + extension;

			// Save output image
			try {
				dsio.save(output, newFilename);
			} catch (IOException e) {
				log.error("Cannot save the output image to disk because : " + e.getLocalizedMessage());
			}
		} else {
			status.showStatus(
					"Output image cannot be saved on disk because the input " + "image is not saved on disk.");
		}
	}

	protected <T extends RealType<T>> Dataset matchRAIToDataset(RandomAccessibleInterval<T> rai, Dataset dataset) {
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i != axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(rai);
		output.setAxes(axes);
		return output;
	}

	protected <T extends RealType<T>> Dataset matchRAIToDataset(Img<T> rai, Dataset dataset) {
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i != axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		Dataset output = ds.create(rai);
		output.setAxes(axes);
		return output;
	}

}
