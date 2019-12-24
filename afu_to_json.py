from argparse import ArgumentParser
from pathlib import Path
import AFU
import json


def main():
	parser = ArgumentParser()
	parser.add_argument("file", type=Path, help="Path to the file to be converted")
	parser.add_argument("--image_data", "-i", action="store_true", default=False, help='Include image data in export of computer.db')
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
	else:
		print("Unsupported file type: {}".format(file_type))

	json.dump(data, open("{}.json".format(args.file.name), "w"), indent="\t", cls=AFU.Utils.Encoder)


if __name__ == "__main__":
	main()
