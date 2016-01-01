from pathlib import PurePath

# All the file extensions in AFU:
# {'', '.3dv', '.img', '.pc4', '.rm', '.pc1', '.pc6', '.db',
# '.bin', '.lbm', '.dat', '.pc5', '.pal', '.mac', '.spt',
# '.mtl', '.pic', '.dmg', '.map', '.vac', '.mrg', '.spr',
# '.pc3', '.mtr', '.rac', '.scr', '.bst', '.fvf', '.fon',
# '.3dr', '.lst', '.ast', '.anm', '.txt', '.pc2'}


def identify(file_path):
	file_extension = PurePath(file_path).suffix
	if( file_extension in [".spr",".spt"] ):
		return "sprite"
	elif( file_extension in [".rm",".scr"] ):
		return "background"
	elif( file_extension in [".mac",".rac",".vac"] ):
		return "audio"
	elif( file_extension == ".img" ):
		return "texture"
	elif( file_extension == ".fon" ):
		return "font"
	elif( file_extension == ".pal" ):
		return "palette"
	elif( file_extension == ".db" ):
		return "database"
	else:
		return "unknown"


