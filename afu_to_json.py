from argparse import ArgumentParser
from pathlib import Path
import AFU
import json


def main():
	parser = ArgumentParser()
	parser.add_argument("file", type=Path, help="Path to the file to be converted")
	args = parser.parse_args()

	file_type = AFU.Utils.identify( args.file )

	if file_type == "database":
		if args.file.stem == "computer":
			data = AFU.Computer.computerDb(args.file)
		elif args.file.stem == "astro":
			data = AFU.Astro.astroDb(args.file)
		elif args.file.stem == "astromap":
			data = AFU.Astro.astromapDb(args.file)
		else:
			print("Unsupported database file: {}".format(args.file.name))
	else:
		print("Unsupported file type: {}".format(file_type))

	json.dump(data, open("{}.json".format(args.file.name), "w"), indent="\t")


if __name__ == "__main__":
	main()
