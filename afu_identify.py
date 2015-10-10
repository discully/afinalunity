import sys
import AFU



def supported(is_supported, message =""):
	if( is_supported ):
		return ""
	else:
		return message



def main():
	
	if( len(sys.argv) != 2 ):
		print "[USAGE]", __file__, "<file>"
		return
		
	f_name = sys.argv[1]
	f_type = AFU.Utils.identify(f_name)
	f_file = AFU.File.File(f_name)
	f_msg = "supported"
	
	try:
		if( f_type == "sprite" ):
			AFU.Sprite.SpriteFile(AFU.Palette.standard(), f_file)
		elif( f_type == "background" ):
			AFU.Background.Background()
		elif( f_type == "font" ):
			AFU.Font.Font(AFU.Palette.standard(), f_file)
		elif( f_type == "palette" ):
			AFU.Palette.Palette(f_file)
		elif( f_type == "database" ):
			AFU.Database.Database(f_file)
		else:
			f_msg = "Unknown file type"
	except ValueError as e:
		f_msg = str(e)
	
	print "[{0}] {1} ".format(f_type, f_msg)



if __name__ == "__main__":
	main()
