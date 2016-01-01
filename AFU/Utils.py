from pathlib import PurePath



def identify(file_path):
	file_extension = PurePath(file_path).suffix
	if( file_extension in [".spr",".spt"] ):
		return "sprite"
	elif( file_extension in [".rm",".scr"] ):
		return "background"
	elif( file_extension in [".mac",".rac",".vac"] ):
		return "audio"
	elif( file_extension == ".fon" ):
		return "font"
	elif( file_extension == ".pal" ):
		return "palette"
	elif( file_extension == ".db" ):
		return "database"
	else:
		return "unknown"


