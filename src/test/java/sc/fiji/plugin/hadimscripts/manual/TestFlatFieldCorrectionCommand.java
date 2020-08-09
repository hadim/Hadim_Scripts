/*-
 * #%L
 * A set of plugins/macros/script for Fiji.
 * %%
 * Copyright (C) 2016 - 2020 Hadrien Mary
 * %%
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 * #L%
 */

package sc.fiji.plugin.hadimscripts.manual;

import java.util.HashMap;
import java.util.Map;

import net.imagej.Dataset;
import net.imagej.ImageJ;
import net.imglib2.type.numeric.RealType;

import org.scijava.Context;
import org.scijava.command.CommandModule;

import sc.fiji.plugin.hadimscripts.PseudoFlatFieldCorrectionCommand;

public class TestFlatFieldCorrectionCommand {

	// Launch the PseudoFlatFieldCorrection command
	public static <T extends RealType<T>> void main(final String... args)
		throws Exception
	{

		final ImageJ ij = net.imagej.Main.launch(args);
		Context context = ij.getContext();

		String fpath =
			"/home/hadim/.doc/Code/Postdoc/ij/testdata/7,5uM_emccd_lapse1-small-8bit.tif";
		Dataset dataset = (Dataset) ij.io().open(fpath);
		ij.ui().show(dataset);

		Map<String, Object> parameters = new HashMap<>();
		parameters.put("input", dataset);
		parameters.put("gaussianFilterSize", 50);
		parameters.put("normalizeIntensity", false);
		parameters.put("iteratePlane", true);
		parameters.put("saveImage", true);
		parameters.put("suffix", "-PPSOSOS");

		CommandModule module = ij.command().run(
			PseudoFlatFieldCorrectionCommand.class, true, parameters).get();
		Dataset output = (Dataset) module.getOutput("output");
	}

}
