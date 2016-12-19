import sys
import AFU



def main():
	
	if( len(sys.argv) != 2 ):
		print("[USAGE]", __file__, "<file>")
		return

	file_path = sys.argv[1]
	file_type = AFU.Utils.identify(file_path)

	print("AFU File Type:", file_type)

	if( file_type == "unknown"):
		return

	afu_file = AFU.File.File(file_path)

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
		afu_object = AFU.Database.Database(afu_file)
	elif( file_type == "texture" ):
		afu_object = AFU.Texture.Texture(afu_file)
	elif( file_type == "world" ):
		afu_object = AFU.World.World(afu_file)
	elif( file_type == "list" ):
		afu_object = AFU.List.List(afu_file)
	elif( file_type == "menu" ):
		afu_object = AFU.Menu.Menu(file_path)

	if afu_object != None:
		print(afu_object)



if __name__ == "__main__":
	main()
