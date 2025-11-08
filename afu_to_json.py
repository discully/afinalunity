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



def main():
	parser = ArgumentParser()
	parser.add_argument("file", type=Path, help="Path to the file to be converted")
	parser.add_argument("-i", "--image_data", action="store_true", help='Include image data in export of computer.db', default=False)
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place json in", default=".")
	args = parser.parse_args()

	file_type = AFU.Utils.identify( args.file )

	if file_type == "database":
		if args.file.stem == "computer":
			data = AFU.Computer.computerDb(args.file)
			if not args.image_data: # Strip image data out
				for value in data.values():
					if "image" in value:
						value["image"].pop("data")
		elif args.file.stem == "astro":
			data = AFU.Astro.astroDb(args.file)
		elif args.file.stem == "astromap":
			data = AFU.Astro.astromapDb(args.file)
		else:
			print("Unsupported database file: {}".format(args.file.name))
			return
	elif file_type == "astro_state":
		data = AFU.Astro.astStatDat(args.file)
	elif file_type == "computer_state":
		data = AFU.Computer.compstat(args.file)
	elif file_type == "world":
		data = AFU.World.worldSlScr(args.file)
	elif file_type == "polygons":
		data = AFU.World.worldStScr(args.file)
	elif file_type == "sprite":
		data = AFU.Sprite.sprite(args.file, args.file.with_name("standard.pal"), args.file.with_name("standard.pal"))
		AFU.Sprite.combine(data)
	elif file_type == "sector_names":
		data = AFU.Astro.sectorAst(args.file)
	elif file_type in ["conversation", "object", "phaser"]:
		data = AFU.Block.bst(args.file)
		_stripDebugElements(data)
		_stripUnknownElements(data)
	elif file_type == "list":
		data = AFU.Sprite.lst(args.file)
	elif file_type == "advice":
		data = AFU.World.adviceDat(args.file)
	elif file_type == "terminal":
		data = AFU.Terminal.terminal(args.file)
	elif file_type == "start":
		data = AFU.World.worldStrt(args.file)
	elif file_type == "world_list":
		data = AFU.World.worldList(args.file)
	elif file_type == "world_objects":
		data = AFU.World.worldObj(args.file)
	elif file_type == "triggers":
		data = AFU.Data.triggers(args.file)
	elif file_type == "icon_map":
		data = AFU.Map.icon(args.file)
	elif file_type == "movie_map":
		data = AFU.Map.movie(args.file)
	elif file_type == "phaser_map":
		data = AFU.Map.phaser(args.file)
	elif file_type == "savegame":
		data = AFU.SaveGame.savegame(args.file)
	elif file_type == "tactic":
		data = AFU.Tactic.bin(args.file)
	elif file_type == "alert":
		data = AFU.Data.alert(args.file)
	elif file_type == "font":
		data = AFU.Font.font(args.file)
	elif file_type == "menu":
		data = AFU.Menu.mrg(args.file)
	elif file_type == "palette":
		data = AFU.Palette.pal(args.file)
	elif file_type == "text":
		data = AFU.Data.txt(args.file)
	elif file_type == "credits":
		data = AFU.Data.credits(args.file)
	elif file_type == "material":
		data = AFU.Graphics.mtl(args.file)
	elif file_type == "image_gif":
		data = AFU.Graphics.img(args.file)
	elif file_type == "image_lbm":
		data = AFU.Graphics.lbm(args.file)
	elif file_type == "damage_material":
		data = AFU.Graphics.dmg(args.file)
	elif file_type == "video":
		data = AFU.Video.fvf(args.file)
		_stripVideoData(data)
	else:
		print("Unsupported file type: {}".format(file_type))
		return

	output_path = "{}.json".format(args.output_dir.joinpath(args.file.name))
	json.dump(data, open(output_path, "w"), indent="\t", cls=AFU.Utils.Encoder)


if __name__ == "__main__":
	main()
