from argparse import ArgumentParser
from difflib import SequenceMatcher
from json import dump as json_dump
from pathlib import Path
from AFU import Block,Utils,Terminal


# Some of the files are hardcoded into the executable with no subtitles.
hardcoded = {
	"fe000287.vac": "Engage!",
	"fe0004ea.vac": "Argh!",
	"fe010330.vac": "Argh!",
	"fe0203bf.vac": "The ship is de-cloaking",
	"fe0302aa.vac": "Argh!",
	"fe0402ff.vac": "Argh!",
	"fe05024a.vac": "Argh!",
	"fe06032f.vac": "Argh!",
	"fe0702c1.vac": "Argh!",
	"fe0802e7.vac": "Argh!",
	"fe09006e.vac": "Warning! Selected destination is a quasaroid.",
	"fe09006f.vac": "Warning! Selected destination is a subspace vortex.",
	"fe090070.vac": "Warning! Selected destination is a ionstorm.",
	"fe090071.vac": "Warning! Selected destination is a black hole.",
}


def getHardcodedName(input_dir, speakers, vac):
	if vac.startswith("cm_"):
		return "Computer Voice"
	
	assert(vac.startswith("fe"))
	sid = int(vac[2:4], 16)
	return getSpeakerName(input_dir, speakers, {"world": 0, "screen": 0, "id": sid})
	
	#if vac == "feff1401.vac" or "feff0801.vac":
	#	return "alien"
	#if vac.startswith("feff050"):
	#	return "SPEAKER: Chodak Terminal"
	#raise ValueError("Cannot identify speaker for file {}".format(vac))



def getSpeakerName(input_dir, speakers, speaker):
	speaker_id = speaker["id"]
	# 0x20 - 0x28 indicate the speaker is on the Enterprise speaking over comms
	if speaker["world"] == 0 and speaker["screen"] == 0 and (speaker["id"] >= 0x20 and speaker["id"] <= 0x28):
		speaker_id -= 0x20
	elif speaker["world"] == 0 and speaker["screen"] == 0 and (speaker["id"] >= 0x30 and speaker["id"] <= 0x38):
		speaker_id -= 0x30

	sid = "{:02x}{:02x}{:02x}".format(speaker["world"], speaker["screen"], speaker_id)

	if not sid in speakers:
		file_name = "o_{}.bst".format(sid)
		file_path = input_dir.joinpath(file_name)
		if file_path.exists():
			data = Block.bst(file_path)
			assert(len(data) == 1)
			speakers[sid] = data[0]["name"]
		else:
			speakers[sid] = "unknown-" + sid

	return speakers[sid]


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



def subtitles(input_dir, output_dir, names=False):
	speakers = {}
	subs = { vac.name:{"text":[]} for vac in input_dir.glob("*.vac") }
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
				print("Error: Non existant file", vac["file"], vac["text"])
				continue

			vac["name"] = getSpeakerName(input_dir, speakers, vac["speaker"])
			
			if not "name" in subs[vac["file"]]:
				subs[vac["file"]]["name"] = vac["name"]

			if subs[vac["file"]]["name"].startswith("unknown-"):
				print("Error: Non existant speaker", vac["file"], vac["text"])
			
			if len(subs[vac["file"]]["text"]) == 0:
				subs[vac["file"]]["text"].append(vac["text"])

			if SequenceMatcher(None, subs[vac["file"]]["text"][0], vac["text"]).ratio() < 0.8:
				subs[vac["file"]]["text"].append(vac["text"])

	for vac,s in subs.items():
		if len(s["text"]) == 0:
			if vac in hardcoded:
				subs[vac] = {
					"text": hardcoded[vac],
					"name": getHardcodedName(input_dir, speakers, vac),
				}
				if subs[vac]["name"].startswith("unknown-"):
					print("Error: Non existant speaker", vac, subs[vac]["text"])
			else:
				print("Error: Missing subtitle for", vac)
				subs[vac] = None
		if len(s["text"]) == 1:
			subs[vac]["text"] = s["text"][0]

	if not names:
		for vac in subs.keys():
			if subs[vac] is not None:
				subs[vac] = subs[vac]["text"]

	output_path = output_dir.joinpath("subtitles.json")

	print("Writing subtitles file to", output_path)

	json_dump(subs, open(output_path, "w"), indent="\t")



def main():
	parser = ArgumentParser(description="Reads .bst files to determine the subtitles for .vac voice files")
	parser.add_argument("input_dir", type=Path, help="Input directory containing 'vac' and 'bst' files")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place json in", default=".")
	parser.add_argument("--names", action="store_true", help="Include the speaker's name in the output data")
	args = parser.parse_args()
	subtitles(args.input_dir, args.output_dir, args.names)


if __name__ == "__main__":
	main()
