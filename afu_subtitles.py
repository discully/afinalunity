from argparse import ArgumentParser
from difflib import SequenceMatcher
from json import dump as json_dump
from pathlib import Path
from AFU import Block,Utils,Terminal


# Some of the files are hardcoded into the executable with no subtitles.
hardcoded = {
	# Computer
	"cm_183.vac": "Warning, life support system at 50%",
	"cm_184.vac": "Warning, life support system at 25%",
	"cm_185.vac": "Warning, life support system failure imminent",
	"cm_186.vac": "Life support system down. Switching to emergency life support system",
	"cm_246.vac": "Warning, fusion reactor at 50%",
	"cm_247.vac": "Warning, fusion reactor at 25%",
	"cm_248.vac": "Warning, fusion reactor failure imminent",
	"cm_249.vac": "Fusion reactor down",
	"cm_254.vac": "Warning, matter-antimatter reactor at 50%",
	"cm_255.vac": "Warning, matter-antimatter reactor at 25%",
	"cm_256.vac": "Warning, matter-antimatter reactor failure imminent",
	"cm_258.vac": "Matter-antimatter reactor down",
	"cm_269.vac": "Targeting area",
	"cm_270.vac": "Targeting Romulan warbird",
	"cm_271.vac": "Targeting Chodak ship",
	"cm_272.vac": "Targeting Chodak drone",
	"cm_273.vac": "Targeting Ferengi marauder",
	"cm_274.vac": "Targeting Klingon bird of prey",
	"cm_275.vac": "Targeting Garidian warbird",
	"cm_282.vac": "Alert level 2",
	"cm_283.vac": "Yellow alert",
	"cm_284.vac": "Alert level 4",
	"cm_286.vac": "Alert cancelled, condition green",
	# Picard
	"fe00027d.vac": "Disengage tactical maneuver",
	"fe00027e.vac": "Engage tactical maneuver",
	"fe000281.vac": "Fire!",
	"fe000287.vac": "Engage!",
	"fe00028c.vac": "Full stop",
	"fe000294.vac": "Mr Worf, you have tactical",
	"fe00029d.vac": "Mr LaForge, you have engineering",
	"fe0004ea.vac": "Argh!",
	# Riker
	"fe0102d0.vac": "Alert, level 2",
	"fe0102d1.vac": "Go to yellow alert",
	"fe0102d5.vac": "Go to red alert",
	"fe0102df.vac": "The ship is drifting",
	"fe010330.vac": "Argh!",
	# Data
	"fe0203bf.vac": "The ship is de-cloaking",
	# Troi
	"fe0302aa.vac": "Argh!",
	# Worf
	"fe040222.vac": "Damage to warp engines",
	"fe040227.vac": "Damage to torpedo bay",
	"fe040229.vac": "The shields are damaged",
	"fe04022a.vac": "Damage to the sensor array",
	"fe04022b.vac": "The tractor array has been damaged",
	"fe04022c.vac": "The life support systems have been damaged",
	"fe04022d.vac": "Damage to the computer core",
	"fe040240.vac": "Our phaser fire hit the target",
	"fe040241.vac": "Our phaser fire missed",
	"fe040243.vac": "Photon tubes are empty",
	"fe040244.vac": "Torpedo spread maximum",
	"fe040245.vac": "Torpedo spread minimum",
	"fe040248.vac": "Torpedo away",
	"fe04024b.vac": "Torpedo fire missed the target",
	"fe04024e.vac": "Torpedo has reaquired the target",
	"fe04024f.vac": "Target is out of range",
	"fe040250.vac": "Locking weapons",
	"fe040256.vac": "Intercepting the target",
	"fe040258.vac": "Direct hit",
	"fe040259.vac": "Captain, if we fire now we will be caught in the blast radius",
	"fe04025a.vac": "We have been hit",
	"fe04025b.vac": "We are under attack",
	"fe040261.vac": "Raising shields",
	"fe040263.vac": "Lowering shields",
	"fe040265.vac": "The shields are holding",
	"fe040268.vac": "A Chodak ship is on sensors",
	"fe040269.vac": "A Romulan warbird is on sensors",
	"fe04026a.vac": "A Ferengi ship is on sensors",
	"fe04026b.vac": "A Garidian ship is on sensors",
	"fe04026c.vac": "A Klingon bird of prey is on sensors",
	"fe04026d.vac": "A Chodak probe is on sensors",
	"fe04026e.vac": "The Chodak ship has been destroyed",
	"fe04026f.vac": "The Romulan warbird has been destroyed",
	"fe040270.vac": "The Ferengi ship has been destroyed",
	"fe040272.vac": "The Garidian ship has been destroyed",
	"fe040273.vac": "The Chodak probe has been destroyed",
	"fe040276.vac": "The enemy has engaged its self-destruct sequence",
	"fe040278.vac": "The enemy ship has sustained major damage",
	"fe040279.vac": "Their shields are failing",
	"fe04027a.vac": "Enemy ship is firing",
	"fe04029a.vac": "They are raising their shields",
	"fe0402a8.vac": "There is no response to our hail",
	"fe0402ff.vac": "Argh!",
	"fe04043f.vac": "Captain, I am honoured",
	"fe040446.vac": "The ship has sustained major damage",
	"fe040447.vac": "The ship is trying to hail us",
	"fe040448.vac": "Target lowering shields",
	"fe040449.vac": "Target raising shields",
	"fe04044a.vac": "Torpedo locked",
	"fe04044b.vac": "Klingon destroyed",
	"fe04044c.vac": "The target is out of phaser range",
	"fe04044d.vac": "The target is out of photon torpedo range",
	# Crusher
	"fe05024a.vac": "Argh!",
	# Laforge
	"fe060200.vac": "Damage to main impulse engine",
	"fe060203.vac": "The batteries are damaged",
	"fe060204.vac": "Damage to electro plasma system",
	"fe060205.vac": "Damage to matter-antimatter reactor",
	"fe060212.vac": "Damage to the long-range sensor array",
	"fe0602c0.vac": "We don't have enough power",
	"fe0602c3.vac": "Captain, we've got a problem here",
	"fe0602c4.vac": "Captain, we've got an emergency here",
	"fe0602c7.vac": "Yes, sir!",
	"fe0602cb.vac": "Photon tubes empty",
	"fe0602d9.vac": "All phaser banks are destroyed",
	"fe0602db.vac": "Our shields have failed",
	"fe06032f.vac": "Argh!",
	# Carlstrom
	"fe0702c1.vac": "Argh!",
	# Butler
	"fe0802e7.vac": "Argh!",
	# Computer
	"fe09001a.vac": "Reactors failing",
	"fe09001b.vac": "Reactors critical",
	"fe09001c.vac": "Warp core breech imminent",
	"fe090021.vac": "Initiating core ejection sequence",
	"fe090022.vac": "Safety interlocks enabled",
	"fe090023.vac": "Core ejection in 30 seconds",
	"fe090026.vac": "Core ejection underway",
	"fe09002f.vac": "Auto-destruct sequence initiated",
	"fe090032.vac": "15 seconds to auto-destruct",
	"fe090033.vac": "10 seconds to auto-destruct",
	"fe090042.vac": "5 seconds to auto-destruct",
	"fe090048.vac": "Auto-destruct sequence disengaged",
	"fe090055.vac": "Stars displayed",
	"fe090057.vac": "Stars not displayed",
	"fe090058.vac": "Grid displayed",
	"fe090059.vac": "Grid not displayed",
	"fe09005a.vac": "Federation space displayed",
	"fe09005b.vac": "Federation space not displayed",
	"fe09005c.vac": "Romulan space displayed",
	"fe09005d.vac": "Romulan space not displayed",
	"fe09005e.vac": "Neutral zone displayed",
	"fe09005f.vac": "Neutral zone not displayed",
	"fe090060.vac": "Nebulas displayed",
	"fe090061.vac": "Nebulas not displayed",
	"fe090062.vac": "Non-aligned space displayed",
	"fe090063.vac": "Non-aligned space not displayed",
	"fe090064.vac": "Inhabited space displayed",
	"fe090065.vac": "Inhabited space not displayed",
	"fe090068.vac": "Starbases displayed",
	"fe090069.vac": "Starbases not displayed",
	"fe09006e.vac": "Warning! Selected destination is a quasaroid.",
	"fe09006f.vac": "Warning! Selected destination is a subspace vortex.",
	"fe090070.vac": "Warning! Selected destination is a ionstorm.",
	"fe090071.vac": "Warning! Selected destination is a black hole.",
	"fe090072.vac": "Warning! Selected destination is an antimatter cloud",
	"fe090077.vac": "Warning! Entering nebula, reducing speed",
	"fe090078.vac": "Entering Federation space",
	"fe090079.vac": "Warning! Entering Romulan space",
	"fe09007a.vac": "Warning! Entering the neutral zone",
	"fe09007b.vac": "Entering non-aligned space",
	"fe090081.vac": "Primary core access enabled",
	"fe090082.vac": "Systems online",
	"fe090090.vac": "Warp engines unable to sustain current speed. Reducing speed to maximum warp",
	"fe090092.vac": "Impulse engines unable to sustain current speed. Suggest using warp drive",
	"fe090093.vac": "Warning",
	"fe090094.vac": "Switching to manual control",
	"fe090098.vac": "The system is down",
	"fe0900aa.vac": "Online, partically operational",
	"fe0900ac.vac": "Warning! Computer core failure imminent",
	"fe0900ad.vac": "Warning! Entering nebula",
	"fe0900b0.vac": "There are no valid beamdown coordinates at this location",
	"fe0900b1.vac": "No beamdown coordinates have been entered",
	"fe0900b2.vac": "Select beamdown coordinates",
	"fe0900b3.vac": "Beamdown coordinates selected",
	"fe0900b4.vac": "Captain Picard, please report to the transporter room",
	"fe0900b5.vac": "Commander Riker, please report to the transporter room",
	"fe0900b6.vac": "Lieutenant Commander Data, please report to the transporter room",
	"fe0900b7.vac": "Counsellor Troi, please report to the transporter room",
	"fe0900b8.vac": "Lieutenant Worf, please report to the transporter room",
	"fe0900b9.vac": "Doctor Crusher, please report to the transporter room",
	"fe0900ba.vac": "Lieutenant Commander LaForge, please report to the transporter room",
	"fe0900bb.vac": "Ensign Butler, please report to the transporter room",
	"fe0900bc.vac": "Ensign Carlstrom, please report to the transporter room",
	"fe0900bd.vac": "Warning! Quasaroid",
	"fe0900be.vac": "Warning! Subspace vortex",
	"fe0900bf.vac": "Warning! Ion storm",
	"fe0900c0.vac": "Warning! Black hole",
	"fe0900c1.vac": "Warning! Antimatter cloud",
	"fe0900c2.vac": "Impulse engines unable to sustain current speed",
	"fe09106e.vac": "Warning! Selected destination is a quasaroid",
	"fe09106f.vac": "Warning! Selected destination is a subspace vortex",
	"fe091070.vac": "Warning! Selected destination is an ion storm",
	"fe091071.vac": "Warning! Selected destination is a black hole",
	# Chodak scientist
	#"feff0501.vac": None,
	#"feff0502.vac": None, # Some long speeches...
	#"feff0503.vac": None,
	# 
	"feff0801.vac": "We must not speak, our master is here",
	# 
	"feff1401.vac": "Can you not see that we are superceded?",
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
				if "file" in description:
					output.append(description)
			for action in ["uses", "gets", "looks", "timers"]:
				for action_set in entry[action]:
					for action_item in action_set:
						t = action_item[0]["type"] if type(action_item) is list else action_item["type"]
						if t == Block.BlockType.ALTER:
							for action_block in action_item:
								if "vac" in action_block:
									output.append(action_block["vac"])
		elif entry["type"] == Block.BlockType.CONV_RESPONSE:
			for say in entry["whocansay"]:
				if "vac" in say:
					output.append(say["vac"])
			for text in entry["text"]:
				if "file" in text:
					output.append(text)
			for result in entry["results"]:
				for result_set in result["entries"]:
					for result_item in result_set:
						t = result_item[0]["type"] if type(result_item) is list else result_item["type"]
						if t == Block.BlockType.ALTER:
							for action_block in result_item: #["blocks"]:
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
