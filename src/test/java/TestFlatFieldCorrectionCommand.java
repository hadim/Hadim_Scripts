import java.util.HashMap;
import java.util.Map;

import org.scijava.Context;
import org.scijava.command.CommandModule;

import sc.fiji.plugin.hadimscripts.PseudoFlatFieldCorrectionCommand;

import net.imagej.Dataset;
import net.imagej.ImageJ;
import net.imglib2.type.numeric.RealType;

public class TestFlatFieldCorrectionCommand {

	// Launch the PseudoFlatFieldCorrection command
	public static <T extends RealType<T>> void main(final String... args) throws Exception {

		final ImageJ ij = net.imagej.Main.launch(args);
		Context context = ij.getContext();

		String fpath = "/home/hadim/.doc/Code/Postdoc/ij/testdata/7,5uM_emccd_lapse1-small-8bit.tif";
		Dataset dataset = ij.dataset().open(fpath);
		ij.ui().show(dataset);

		Map<String, Object> parameters = new HashMap<>();
		parameters.put("input", dataset);
		parameters.put("gaussianFilterSize", 50);
		parameters.put("normalizeIntensity", false);
		parameters.put("iteratePlane", true);
		parameters.put("saveImage", false);
		parameters.put("suffix", "");

		CommandModule module = ij.command().run(PseudoFlatFieldCorrectionCommand.class, true, parameters).get();
		Dataset output = (Dataset) module.getOutput("output");
	}

}
