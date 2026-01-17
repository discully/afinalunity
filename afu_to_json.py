from argparse import ArgumentParser
from pathlib import Path
import AFU
import json


def _stripDebugElements(x):
	if type(x) is list:
		for y in x:
			_stripDebugElements(y)
	elif type(x) is dict:
		for k in list(x.keys()):
			if k.startswith("_"):
				x.pop(k)
			else:
				_stripDebugElements(x[k])

def _stripUnknownElements(x):
	if type(x) is dict:
		for k in list(x.keys()):
			if k.startswith("unknown_"):
				x.pop(k)
			else:
				_stripUnknownElements(x[k])
	elif type(x) is list:
		for y in x:
			_stripUnknownElements(y)

def _stripVideoData(x):
	for block in x["blocks"]:
		for frame in block["frames"]:
			if "image" in frame and "data" in frame["image"]:
				frame["image"].pop("data")
			if "audio" in frame:
				frame.pop("audio")
			if "palette" in frame:
				frame.pop("palette")

def _stripTacticMetadata(x):
	for page in x:
		page.pop("data")
		for entry in page["entries"]:
			if "data" in entry: entry.pop("data")

def _stripSpriteAudio(file_path, x):
	for block in x["blocks"]:
		if block["name"] in ["DIGI"]:
			block.pop("audio")
			block["audio"] = f"{file_path.name}.{block["offset"]}.mac"



def main():
	parser = ArgumentParser()
	parser.add_argument("file", type=Path, help="Path to the file to be converted")
	parser.add_argument("-i", "--image_data", action="store_true", help='Include image data in export of computer.db', default=False)
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place json in", default=".")
	args = parser.parse_args()

	file_type = AFU.identify( args.file )
	file_handler = AFU.handler(file_type)

	if file_type == AFU.FileType.SPRITE:
		data = file_handler(args.file, args.file.with_name("standard.pal"), args.file.with_name("standard.pal"))
	else:
		data = file_handler(args.file)
	
	if file_type == AFU.FileType.DATABASE_COMPUTER:
		if not args.image_data:
				for value in data.values():
					if "image" in value:
						value["image"].pop("data")
	elif file_type == AFU.FileType.SPRITE:
		_stripSpriteAudio(args.file, data)
	elif file_type in [AFU.FileType.CONVERSATION, AFU.FileType.OBJECT, AFU.FileType.PHASER]:
		_stripDebugElements(data)
		_stripUnknownElements(data)
	elif file_type == AFU.FileType.TACTIC:
		_stripDebugElements(data)
		_stripTacticMetadata(data)
	elif file_type == AFU.FileType.VIDEO:
		_stripVideoData(data)

	output_path = "{}.json".format(args.output_dir.joinpath(args.file.name))
	json.dump(data, open(output_path, "w"), indent="\t", cls=AFU.Utils.Encoder)


if __name__ == "__main__":
	main()
