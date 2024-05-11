import os
import markovify
import json

for file in os.listdir("corpora"):
	with open(f"corpora/{file}", "r", encoding="utf8") as f:
		print(f"Constructing model from {file[:-4]}...")

		text = f.read()
		model = markovify.Text(text)

	with open(f"models/{file[6:-4]}.json", "w") as f:
		f.write(model.to_json())

# for k, v in model.chain.model.items():
# 	v = sorted(v.items(), key=lambda kv: (kv[1]), reverse=True)
# 	v = [i[0] for i in v]
# 	print(f"{k} : {v}")

entry_points = [key[1] for key in model.chain.model.keys() if "___BEGIN__" in key][1:]
print(entry_points)
