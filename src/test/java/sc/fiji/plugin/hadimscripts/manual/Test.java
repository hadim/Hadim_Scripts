
package sc.fiji.plugin.hadimscripts.manual;

import net.imagej.Dataset;
import net.imagej.ImageJ;
import net.imglib2.type.numeric.RealType;

import org.scijava.Context;

public class Test {

	// Launch ImageJ and open and Image
	public static <T extends RealType<T>> void main(final String... args) throws Exception {

		final ImageJ ij = new ImageJ();
		ij.ui().showUI();
		Context context = ij.getContext();

		final String sampleImage =
			"8bit-unsigned&pixelType=uint8&indexed=true&lengths=20,20,5&axes=X,Y,Time.fake";

		Dataset ds = (Dataset) ij.io().open(sampleImage);

		ij.ui().show(ds);
		ij.ui().showUI();
	}
}
