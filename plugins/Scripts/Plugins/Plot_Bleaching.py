# @ImageJ ij
# @Dataset dataset
# @ImagePlus img

import java.awt.Color as Color
from ij.gui import Plot

plot = Plot("Normalized FRAP curve for ", "Time ", "NU", [], [])
plot.setLimits(0, 10, 0, 1.2 );
plot.setLineWidth(2)
 
 
plot.setColor(Color.BLACK)
plot.addPoints([0, 1, 2, 3, 4,], range(5), Plot.LINE)
 
plot.setColor(Color.black);
plot.show()

# TODO