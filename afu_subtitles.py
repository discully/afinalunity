from argparse import ArgumentParser
from difflib import SequenceMatcher
from json import dump as json_dump
from pathlib import Path
from AFU import Block,Utils,Terminal



def getVoiceFilesFromBst(path):
	output = []
	data = Block.bst(path)
	for entry in data:
		if entry["type"] == Block.BlockType.OBJECT:
			if "vac" in entry:
				output.append(entry["vac"])
			for description in entry["descriptions"]:
				if "vac" in description:
					output.append(description["vac"])
			for action in ["uses", "gets", "looks", "timers"]:
				for action_set in entry[action]:
					for action_item in action_set:
						if action_item["type"] == Block.BlockType.ALTER:
							for action_block in action_item["blocks"]:
								if "vac" in action_block:
									output.append(action_block["vac"])
		elif entry["type"] == Block.BlockType.CONV_RESPONSE:
			for say in entry["whocansay"]:
				if "vac" in say:
					output.append(say["vac"])
			for text in entry["text"]:
				if "vac" in text:
					output.append(text["vac"])
			for result in entry["results"]:
				for result_set in result["entries"]:
					for result_item in result_set:
						if result_item["type"] == Block.BlockType.ALTER:
							for action_block in result_item["blocks"]:
								if "vac" in action_block:
									output.append(action_block["vac"])
	return output



def subtitles(input_dir, output_dir):
	subs = { vac.name:[] for vac in input_dir.glob("*.vac") }
	for i,bst in enumerate(input_dir.glob("*.bst")):

		if i % 300 == 0:
			print("{}%".format(i // 30))

		if bst.stem == "worlname":
			continue
		if bst.name.startswith("t_"):
			continue
		if bst.stem.endswith("obj") or bst.stem.endswith("con") or bst.stem.endswith("scrn") or bst.stem.endswith("strt"):
			continue

		for vac in getVoiceFilesFromBst(bst):
			if not vac["file"] in subs:
				continue

			if len(subs[vac["file"]]) == 0:
				subs[vac["file"]].append(vac["text"])

			if SequenceMatcher(None, subs[vac["file"]][0], vac["text"]).ratio() < 0.8:
				subs[vac["file"]].append(vac["text"])

	for vac,s in subs.items():
		if len(s) == 0:
			subs[vac] = None
		if len(s) == 1:
			subs[vac] = s[0]

	output_path = output_dir.joinpath("subtitles.json")

	print("Writing subtitles file to", output_path)

	json_dump(subs, open(output_path, "w"), indent="\t")



def main():
	parser = ArgumentParser(description="Reads .bst files to determine the subtitles for .vac voice files")
	parser.add_argument("input_dir", type=Path, help="Input directory containing 'vac' and 'bst' files")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place json in", default=".")
	args = parser.parse_args()
	subtitles(args.input_dir, args.output_dir)


if __name__ == "__main__":
	main()
