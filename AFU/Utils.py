from pathlib import PurePath

# All the file extensions in AFU:
# {'', '.3dv', '.img', '.pc4', '.rm', '.pc1', '.pc6', '.db',
# '.bin', '.lbm', '.dat', '.pc5', '.pal', '.mac', '.spt',
# '.mtl', '.pic', '.dmg', '.map', '.vac', '.mrg', '.spr',
# '.pc3', '.mtr', '.rac', '.scr', '.bst', '.fvf', '.fon',
# '.3dr', '.lst', '.ast', '.anm', '.txt', '.pc2'}


def identify(file_path):
	file_path = PurePath(file_path)
	file_extension = file_path.suffix
	file_name = file_path.stem
	if( file_extension in [".spr",".spt"] ):
		return "sprite"
	elif( file_extension == ".rm" ):
		return "background"
	elif( file_extension == ".scr" ):
		prefix = file_name[:2]
		if( prefix == "sb" ):
			return "background"
		elif( prefix == "sl" ):
			return "world"
		elif( prefix == "st" ):
			return "polygons"
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
	elif( file_extension == ".txt" ):
		return "text"
	#elif( file_extension == ".bst" ):
		# o_XXXXXX.bst - object
		# p_XXXXXX.bst
		# t_XXXXXX.bst
		# wXXXXobj.bst - object with sprite
		# wXXXcXXX.bst - conversation
		# wXXXXXXX.bst
		# worlname.bst
		# w_DDDcon.bst
		# w_DDscrn.bst
		# w_DDstrt.bst - startup screens for world

	return "unknown"


