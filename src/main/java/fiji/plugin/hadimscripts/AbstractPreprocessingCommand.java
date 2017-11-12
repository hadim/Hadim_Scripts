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
import net.imagej.ops.OpService;

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

}
