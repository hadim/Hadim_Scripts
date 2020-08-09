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

package sc.fiji.plugin.hadimscripts;

import static org.junit.Assert.assertEquals;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;

import javax.script.ScriptException;

import net.imagej.Dataset;

import org.junit.Test;
import org.scijava.plugin.Parameter;
import org.scijava.script.ScriptModule;
import org.scijava.script.ScriptService;

public class TestScripts extends AbstractTest {

	@Parameter
	protected ScriptService ss;

	private File getScriptFile(String path) {
		final URL scriptPath = AbstractPreprocessingCommand.class.getResource(path);
		return new File(scriptPath.getPath());
	}

	@Test
	public void TestCopyoBlackImages() throws IOException, InterruptedException, ExecutionException,
		ScriptException
	{
		final String sampleImage =
			"8bit-unsigned&pixelType=uint8&lengths=10,10,2,5&axes=X,Y,Channel,Time.fake";

		Dataset dataset = (Dataset) io.open(sampleImage);

		Map<String, Object> inputs = new HashMap<>();
		inputs.put("stack", dataset);

		File scriptFile = this.getScriptFile(
			"/script_templates/Hadim_Scripts/Stack/Copy_to_Black_Images.py");
		ScriptModule module = ss.run(scriptFile, true, inputs).get();
		Dataset output = (Dataset) module.getOutput("output");

		assertEquals(output.numDimensions(), dataset.numDimensions());
	}

}
