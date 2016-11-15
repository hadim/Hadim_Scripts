# @File(label='Choose a directory', style='directory') data_dir
# @String(label="Result Folder Name", choices={"Analysis_Nucleation", "Analysis_Comet"}) result_folder
# @String(label="Result filename", value="Results.csv") result_filename

import os
import csv
from collections import defaultdict

data_dir_path = data_dir.getAbsolutePath()

results_files = []
for root, folder, files in os.walk(data_dir_path):

	parent = os.path.basename(root)

	if parent == result_folder:

		for fname in files:
			if fname == result_filename:
				results_files.append(os.path.join(root, fname))

rows = []
headers = []
for fname in results_files:
	print(fname)

	reader = csv.DictReader(open(fname))
	for row in reader:
		del row[' ']
		rows.append(row)

headers = reader.fieldnames[1:]

f = open(os.path.join(data_dir_path, result_filename), 'wb')
w = csv.DictWriter(f, headers)

w.writerow(dict((col, col) for col in headers))
for row in rows:
	w.writerow(row)
f.close()