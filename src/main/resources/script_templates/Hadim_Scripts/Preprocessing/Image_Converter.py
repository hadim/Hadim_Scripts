# @String(label="Input Extension", value=".lsm") input_extension
# @String(label="Output Extension", value=".tif") output_extension
# @File(label="Select a directory", style="directory") dir_path
# @DatasetIOService io

import os

for fname in os.listdir(dir_path.toString()):
	if fname.endswith(input_extension):

		dataset = io.open(os.path.join(dir_path.toString(), fname))
		filename = dataset.getName()
		# getSource() returns a weird path. I need to use replace().
		parent_folder = dataset.getSource().replace(filename, "")
		new_path = os.path.join(parent_folder, os.path.splitext(filename)[0] + output_extension)

		io.save(dataset, new_path)
		print(new_path)
