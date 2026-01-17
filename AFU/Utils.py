from pathlib import PurePath
from json import JSONEncoder
from AFU import Image, Block, Astro, Tactic
from enum import Enum, IntEnum

# All the file extensions in AFU:
# {'', '.3dv', '.img', '.pc4', '.rm', '.pc1', '.pc6', '.db',
# '.bin', '.lbm', '.dat', '.pc5', '.pal', '.mac', '.spt',
# '.mtl', '.pic', '.dmg', '.map', '.vac', '.mrg', '.spr',
# '.pc3', '.mtr', '.rac', '.scr', '.bst', '.fvf', '.fon',
# '.3dr', '.lst', '.ast', '.anm', '.txt', '.pc2'}


class FileType (Enum):
	ADVICE = 0
	ALERT = 1
	ASTRO_STATE = 2
	AUDIO = 3
	COMPUTER_STATE = 4
	CONVERSATION = 5
	CREDITS = 6
	CURSOR = 7
	DATABASE = 8
	FONT = 9
	G3D_MATERIAL = 10
	G3D_OBJECT = 11
	ICON_MAP = 12
	IMG_BACKGROUND = 13
	IMG_GIF = 14
	IMG_LBM = 15
	IMG_MENU = 16
	LIST = 17
	MOVIE_MAP = 18
	OBJECT = 19
	PALETTE = 20
	PHASER = 21
	PHASER_MAP = 22
	POLYGONS = 23
	SAVEGAME = 24
	SECTOR_NAMES = 25
	SPRITE = 26
	TACTIC = 27
	TERMINAL = 28
	TEXT = 29
	TRIGGERS = 30
	UNKNOWN = 31
	VIDEO = 32
	WORLD = 33
	WORLD_LIST = 34
	WORLD_OBJECTS = 35
	WORLD_START = 36


def identify(file_path):
	# TODO: remove this function and use identifyFile instead
	file_path = PurePath(file_path)
	file_extension = file_path.suffix.lower()
	file_name = file_path.stem.lower()
	
	if "savegame" in file_name:
		if file_extension != "idx":
			return "savegame"
	elif file_extension == "":
		if file_name == "compstat":
			return "computer_state"
		elif file_name == "list":
			return "text"
	elif file_extension == ".txt":
		return "credits"
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
		return "image_gif"
	elif file_extension == ".lbm":
		return "image_lbm"
	elif file_extension == ".fon":
		return "font"
	elif file_extension == ".fvf":
		return "video"
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
	elif file_extension in (".mtl", ".mtr", ".dmg"):
		return "material"
	elif file_extension in [".3dv", ".3dr", ".pc1", ".pc2", ".pc3", ".pc4", ".pc5", ".pc6"]:
		return "3dobject"
	elif file_extension == ".map":
		if file_name == "icon":
			return "icon_map"
		elif file_name == "movie":
			return "movie_map"
		elif file_name == "phaser":
			return "phaser_map"
	elif file_extension == ".pic":
		if file_name == "compute1":
			return "menu"
		else:
			return "background"
	elif file_extension in (".mrg", ".anm"):
		return "menu"
	elif file_extension == ".bst":
		if file_name.startswith("o_"):
			return "object"
		elif file_name.startswith("p_"):
			return "phaser"
		elif file_name.startswith("t_"):
			return "terminal"
		elif file_name.startswith("w"):
			if( file_name.endswith("obj") ): # wXXXXobj.bst
				return "world_objects"
			elif( file_name.endswith("con") ): # w_DDDcon.bst
				return "world_list"
			elif( file_name.endswith("scrn") ):# w_DDscrn.bst
				return "world_list"
			elif( file_name.endswith("strt") ): # w_DDstrt.bst
				return "start"
			elif( file_name == "worlname" ):
				return "world_list"
			elif len(file_name) == 8 and file_name[4] == 'c': # wXXXcXXX.bst
				return "conversation"
	return "unknown"


def identifyFile(file_path):
	type_str = identify(file_path)
	type_map = {
		"advice": FileType.ADVICE,
		"alert": FileType.ALERT,
		"astro_state": FileType.ASTRO_STATE,
		"audio": FileType.AUDIO,
		"computer_state": FileType.COMPUTER_STATE,
		"conversation": FileType.CONVERSATION,
		"credits": FileType.CREDITS,
		"cursor": FileType.CURSOR,
		"database": FileType.DATABASE,
		"font": FileType.FONT,
		"material": FileType.G3D_MATERIAL,
		"3dobject": FileType.G3D_OBJECT,
		"icon_map": FileType.ICON_MAP,
		"background": FileType.IMG_BACKGROUND,
		"image_gif": FileType.IMG_GIF,
		"image_lbm": FileType.IMG_LBM,
		"menu": FileType.IMG_MENU,
		"list": FileType.LIST,
		"movie_map": FileType.MOVIE_MAP,
		"object": FileType.OBJECT,
		"palette": FileType.PALETTE,
		"phaser": FileType.PHASER,
		"phaser_map": FileType.PHASER_MAP,
		"polygons": FileType.POLYGONS,
		"savegame": FileType.SAVEGAME,
		"sector_names": FileType.SECTOR_NAMES,
		"sprite": FileType.SPRITE,
		"tactic": FileType.TACTIC,
		"terminal": FileType.TERMINAL,
		"text": FileType.TEXT,
		"triggers": FileType.TRIGGERS,
		"video": FileType.VIDEO,
		"world": FileType.WORLD,
		"world_list": FileType.WORLD_LIST,
		"world_objects": FileType.WORLD_OBJECTS,
		"start": FileType.WORLD_START,
		"unknown": FileType.UNKNOWN,
	}
	return type_map.get(type_str, FileType.UNKNOWN)


class Encoder (JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Block.BlockType) or \
				isinstance(obj, Block.ConversationResponseState) or \
				isinstance(obj, Block.ObjectWalkType) or \
				isinstance(obj, Astro.Alignment) or \
				isinstance(obj, Astro.ObjectType) or \
				isinstance(obj, SystemEnt) or \
				isinstance(obj, Tactic.TacticType):
			return obj.name
		if isinstance(obj, Block.ObjectId):
			return obj.value
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
