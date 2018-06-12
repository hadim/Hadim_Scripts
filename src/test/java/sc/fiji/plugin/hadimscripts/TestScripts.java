
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
