from argparse import ArgumentParser
from pathlib import Path
import AFU
import json


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
	elif file_type == "list":
		data = AFU.List.lst(args.file)
	else:
		print("Unsupported file type: {}".format(file_type))

	output_path = "{}.json".format(args.output_dir.joinpath(args.file.name))
	json.dump(data, open(output_path, "w"), indent="\t", cls=AFU.Utils.Encoder)


if __name__ == "__main__":
	main()
