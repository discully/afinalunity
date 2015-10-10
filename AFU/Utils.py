


def identify(file_name):
	if( ".spr" in file_name or ".spt" in file_name ):
		return "sprite"
	elif( ".rm" in file_name or ".scr" in file_name ):
		return "background"
	elif( ".fon" in file_name ):
		return "font"
	elif( ".pal" in file_name ):
		return "palette"
	elif( ".db" in file_name ):
		return "database"
	else:
		return "unknown"


