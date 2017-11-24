import java.util.stream.IntStream;
import java.util.stream.LongStream;

import org.scijava.Context;
import org.scijava.log.LogService;

import net.imagej.Dataset;
import net.imagej.DatasetService;
import net.imagej.ImageJ;
import net.imagej.axis.CalibratedAxis;
import net.imagej.ops.OpService;
import net.imglib2.cache.img.DiskCachedCellImgFactory;
import net.imglib2.cache.img.DiskCachedCellImgOptions;
import net.imglib2.cache.img.DiskCachedCellImgOptions.CacheType;
import net.imglib2.img.Img;
import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.real.DoubleType;

public class TestCache {

	// Launch ImageJ and open and Image
	public static <T extends RealType<T>> void main(final String... args) throws Exception {

		final ImageJ ij = net.imagej.Main.launch(args);
		Context context = ij.getContext();

		LogService log = ij.log();
		OpService ops = ij.op();
		DatasetService ds = ij.dataset();

		String fpath = "/home/hadim/.doc/Code/Postdoc/ij/testdata/7,5uM_emccd_lapse1-small-8bit.tif";
		Dataset dataset = ij.dataset().open(fpath);
		ij.ui().show(dataset);

		// ----------

		int cellCacheSize = 64;
		int maxCacheSize = 100;
		CacheType cachType = CacheType.BOUNDED;

		long[] dims = LongStream.range(0, dataset.numDimensions()).map(i -> dataset.dimension((int) i)).toArray();

		// Print dimensions
		LongStream.range(0, dims.length).forEach(i -> System.out.print(dims[(int) i] + ", "));

		// Create cell dimensions for cached data
		int[] cellDimensions = IntStream.range(0, dims.length).map(i -> cellCacheSize).toArray();

		// Setup options for the cached image
		final DiskCachedCellImgOptions options = new DiskCachedCellImgOptions().cellDimensions(cellDimensions)
				.cacheType(cachType).maxCacheSize(maxCacheSize);

		DiskCachedCellImgFactory factory = new DiskCachedCellImgFactory(options);

		Img<T> img = factory.create(dims, new DoubleType());
				
		Dataset output = ds.create(img);
		output = matchRAIToDataset(output, dataset);
		
		output.copyDataFrom(dataset);
		
		ij.ui().show(output);
	}
	
	protected static <T extends RealType<T>> Dataset matchRAIToDataset(Dataset original, Dataset dataset) {
		CalibratedAxis[] axes = new CalibratedAxis[dataset.numDimensions()];
		for (int i = 0; i < axes.length; i++) {
			axes[i] = dataset.axis(i);
		}
		original.setAxes(axes);
		return original;
	}
}
