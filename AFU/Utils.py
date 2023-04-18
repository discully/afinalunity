from pathlib import PurePath
from json import JSONEncoder
from AFU import Image, Block, Astro
from enum import Enum, IntEnum

# All the file extensions in AFU:
# {'', '.3dv', '.img', '.pc4', '.rm', '.pc1', '.pc6', '.db',
# '.bin', '.lbm', '.dat', '.pc5', '.pal', '.mac', '.spt',
# '.mtl', '.pic', '.dmg', '.map', '.vac', '.mrg', '.spr',
# '.pc3', '.mtr', '.rac', '.scr', '.bst', '.fvf', '.fon',
# '.3dr', '.lst', '.ast', '.anm', '.txt', '.pc2'}


def identify(file_path):
	file_path = PurePath(file_path)
	file_extension = file_path.suffix.lower()
	file_name = file_path.stem.lower()
	
	if "savegame" in file_name:
		if file_extension != "idx":
			return "savegame"
	elif file_name == "compstat":
		return "computer_state"
	elif file_extension in [".spr",".spt"]:
		return "sprite"
	elif file_extension == ".rm":
		return "background"
	elif file_extension == ".dat":
		if file_name == "ast_stat":
			return "astro_state"
	elif file_extension == ".ast":
		if file_name == "sector":
			return "sector_names"
		else:
			return "background"
	elif file_extension == ".dat":
		if file_name.endswith("a000"):
			return "advice"
		elif file_name in ("cursor", "waitcurs"):
			return "cursor"
		elif file_name == "trigger":
			return "triggers"
		# todo	ast_stat.dat, level#.dat, trigger.dat
	elif file_extension == ".scr":
		prefix = file_name[:2]
		if prefix == "sb":
			return "background"
		elif prefix == "sl":
			return "world"
		elif prefix == "st":
			return "polygons"
	elif file_extension in [".mac", ".rac", ".vac"]:
		return "audio"
	elif file_extension == ".img":
		return "texture"
	elif file_extension == ".fon":
		return "font"
	elif file_extension == ".pal":
		return "palette"
	elif file_extension == ".db":
		return "database"
	elif file_extension == ".txt":
		return "text"
	elif file_extension == ".lst":
		return "list"
	elif file_extension == ".map":
		if file_name == "icon":
			return "icon_map"
		elif file_name == "movie":
			return "movie_map"
		elif file_name == "phaser":
			return "phaser_map"
	elif file_extension in (".mrg", ".anm", ".pic"):
		return "menu"
	elif file_extension == ".bst":
		if file_name.startswith("o_"):
			return "object"
		elif file_name.startswith("p_"):
			return "phaser"
		elif file_name.startswith("t_"):
			return "terminal"
		elif file_name.startswith("w"):
			if len(file_name) == 8 and file_name[4] == 'c': # wXXXcXXX.bst
				return "conversation"
			elif( file_name.endswith("obj") ): # wXXXXobj.bst
				return "world_objects"
			elif( file_name.endswith("con") ): # w_DDDcon.bst
				return "world_list"
			elif( file_name.endswith("scrn") ):# w_DDscrn.bst
				return "world_list"
			elif( file_name.endswith("strt") ): # w_DDstrt.bst
				return "start"
			elif( file_name == "worlname" ):
				return "world_list"
	return "unknown"



class Encoder (JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Block.BlockType) or isinstance(obj, Block.ConversationResponseState) or isinstance(obj, Block.ObjectWalkType) or isinstance(obj, Astro.Alignment) or isinstance(obj, Astro.ObjectType):
			return obj.name
		if isinstance(obj, Enum):
			return obj.name
		if isinstance(obj, IntEnum):
			return obj.name
		if isinstance(obj, Image.Image):
			return str(obj)
		# Let the base class default method raise the TypeError
		return JSONEncoder.default(self, obj)
