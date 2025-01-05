from argparse import ArgumentParser
from pathlib import Path
from AFU import Block
from AFU.Utils import identify



def output(bst, path):
	print("{}    {:<24}    {}".format(path.name, "'" + bst[0]["name"] + "'", bst[0]["id"]))



def main():
	parser = ArgumentParser(description="Identifies an object file or searches a directory for object files with a given name")
	parser.add_argument("path", type=Path, help="Path to the directory to search, or an object file to identify")
	parser.add_argument("-n", "--name", type=str, help="Object name to serach for", default=None)
	
	args = parser.parse_args()

	if not args.path.exists():
		raise ValueError("Path '{}' does not exist".format(args.path))
	
	if args.path.is_dir():
		
		if args.name is None:
			raise ValueError("Path is a directory but no search term provided")
		search_name = args.name.lower()

		found = False
		for file_path in args.path.iterdir():

			if identify(file_path) != "object":
				continue
			
			bst = Block.bst(file_path)
			assert(len(bst) == 1)
			
			if bst[0]["name"].lower().find(search_name) != -1:
				found = True
				output(bst, file_path)
		
		if not found:
			print("No objects matching '{}' found in directory".format(search_name))

		return
	
	if args.path.is_file():
		
		if identify(args.path) != "object":
			raise ValueError("'{}' is not an object file".format(args.path.name))
		
		bst = Block.bst(args.path)
		assert(len(bst) == 1)

		output(bst, args.path)

		return
	
	raise ValueError("Invalid path '{}'".format(args.path))



if __name__ == "__main__":
	main()
