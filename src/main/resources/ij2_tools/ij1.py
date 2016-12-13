from ij.plugin.frame import RoiManager


def get_roi_manager(new=False):
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm