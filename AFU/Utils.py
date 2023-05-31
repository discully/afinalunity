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
	elif file_extension == ".ast":
		if file_name == "sector":
			return "sector_names"
		else:
			return "background"
	elif file_extension == ".dat":
		if file_name == "ast_stat":
			return "astro_state"
		elif file_name.endswith("a000"):
			return "advice"
		elif file_name in ("cursor", "waitcurs"):
			return "cursor"
		elif file_name == "trigger":
			return "triggers"
		elif file_name.startswith("level"):
			return "alert"
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
	elif file_extension == ".bin":
		return "tactic"
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
		if isinstance(obj, Block.BlockType) or isinstance(obj, Block.ConversationResponseState) or isinstance(obj, Block.ObjectWalkType) or isinstance(obj, Astro.Alignment) or isinstance(obj, Astro.ObjectType) or isinstance(obj, SystemEnt):
			return obj.name
		if isinstance(obj, Enum):
			return obj.name
		if isinstance(obj, IntEnum):
			return obj.name
		if isinstance(obj, Image.Image):
			return str(obj)
		# Let the base class default method raise the TypeError
		return JSONEncoder.default(self, obj)


class SystemEnt (Enum):
	DORSAL_FORE_SHIELD	= 0x0
	VENTRAL_FORE_SHIELD	= 0x1
	NACELLE_PORT_SHIELD = 0x2
	LATERAL_SHIELD	= 0x3
	NACELLE_STARBOARD_SHIELD	= 0x4
	ENGINEERING_HULL_SHIELD	= 0x5
	DORSAL_AFT_SHIELD	= 0x6
	VENTRAL_AFT_SHIELD	= 0x7
	LATERAL_SENSOR	= 0x8
	LONG_RANGE_SENSOR	= 0x9
	E_HULL_LATERAL_SENSOR	= 0xa
	LOWER_PLATFORM_SENSOR	= 0xb
	AFT_LATERAL_SENSOR	= 0xc
	DORSAL_PHASER_ARRAY	= 0xd
	VENTRAL_PHASER_ARRAY	= 0xe
	FORE_PHASER_ARRAY	= 0xf
	AFT_PHASER_ARRAY	= 0x10
	PORT_PHASER_ARRAY	= 0x11
	STARBOARD_PHASER_ARRAY	= 0x12
	FORE_TORPEDO	= 0x13
	AFT_TORPEDO	= 0x14
	MAIN_TRACTOR	= 0x15
	FORE_TRACTOR	= 0x16
	LIFE_SUPPORT	= 0x17
	ENGINEERING_COMPUTER_CORE	= 0x18
	PORT_COMPUTER_CORE	= 0x19
	STARBOARD_COMPUTER_CORE	= 0x1a
	PORT_WARP_ENGINE	= 0x1b
	STARBOARD_WARP_ENGINE	= 0x1c
	MAIN_IMPULSE_ENGINE	= 0x1d
	PORT_IMPULSE_ENGINE	= 0x1e
	STARBOARD_IMPULSE_ENGINE	= 0x1f
	EPS_POWER_GRID	= 0x20
	FUSION_REACTOR	= 0x21
	ANTIMATTER_REACTOR	= 0x22
