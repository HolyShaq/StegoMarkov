import os

base_dir = f"corpora"
folder = "neg"
files = os.listdir(f"{base_dir}/{folder}")
open(f"{base_dir}/clean_{folder}.txt", "w").close()  # Clear file

count = 1
for file in files:
	with open(f"{base_dir}/{folder}/{file}", "r", encoding="utf8") as f:
		text = f.read().replace("<br /><br />", " ")
	with open(f"{base_dir}/clean_{folder}.txt", "a", encoding="utf8") as f:
		f.write(" " + text)

	if count % 50 == 0:
		print(f"Progress: {count * 100 / len(files)}%")
	count += 1
