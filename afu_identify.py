from argparse import ArgumentParser
from pathlib import Path
import AFU



def main():

	parser = ArgumentParser()
	parser.add_argument("file", help="Path to the file to be identified", type=Path)
	args = parser.parse_args()

	file_type = AFU.Utils.identify(args.file)

	print("AFU File Type:", file_type)

	if( file_type == "unknown"):
		return

	afu_file = AFU.File.File(args.file)

	afu_object = None
	if( file_type == "sprite" ):
		afu_object = AFU.Sprite.Sprite(afu_file) #AFU.Palette.standard(), afu_file)
	elif( file_type == "background" ):
		afu_object = AFU.Background.Background(afu_file)
	elif( file_type == "font" ):
		afu_object = AFU.Font.Font(AFU.Palette.standard(), afu_file)
	elif( file_type == "palette" ):
		afu_object = AFU.Palette.Palette(afu_file)
	elif( file_type == "database" ):
		afu_object = None
	elif( file_type == "texture" ):
		afu_object = AFU.Texture.Texture(file_path)
	elif( file_type == "world" ):
		afu_object = None
	elif( file_type == "list" ):
		afu_object = AFU.List.List(afu_file)
	elif( file_type == "menu" ):
		afu_object = AFU.Menu.Menu(file_path)

	if afu_object != None:
		print(afu_object)



if __name__ == "__main__":
	main()
