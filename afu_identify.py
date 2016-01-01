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
	f_msg = ""
	try:
		if( file_type == "sprite" ):
			afu_object = AFU.Sprite.Sprite(afu_file) #AFU.Palette.standard(), afu_file)
		elif( file_type == "background" ):
			afu_object = AFU.Background.Background()
		elif( file_type == "font" ):
			afu_object = AFU.Font.Font(AFU.Palette.standard(), afu_file)
		elif( file_type == "palette" ):
			afu_object = AFU.Palette.Palette(afu_file)
		elif( file_type == "database" ):
			afu_object = AFU.Database.Database(afu_file)
		else:
			f_msg = "Unknown file type"
	except ValueError as e:
		f_msg = str(e)

	if afu_object != None:
		print(afu_object)
	else:
		print("[{0}] {1} ".format(file_type, f_msg))



if __name__ == "__main__":
	main()
