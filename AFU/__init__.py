from enum import Enum


from . import Astro
from . import Background
from . import Block
from . import Computer
from . import Cursor
from . import Data
from . import File
from . import Font
from . import Image
from . import Graphics
from . import Menu
from . import Map
from . import Palette
from . import SaveGame
from . import Sprite
from . import Tactic
from . import Terminal
from . import Utils
from . import Video
from . import World


__all__ = [
	"FileType", "handler", "identify"
	"Astro",
	"Background",
	"Block",
	"Computer",
	"Cursor",
	"Data",
	"File",
	"Font",
	"Image",
	"Graphics",
	"Menu",
	"Map",
	"Palette",
	"SaveGame",
	"Sprite",
	"Tactic",
	"Terminal",
	"Utils",
	"Video",
	"World",
	]


class FileType (Enum):
	ADVICE = 0
	ALERT = 1
	ASTRO_STATE = 2
	AUDIO = 3
	COMPUTER_STATE = 4
	CONVERSATION = 5
	CREDITS = 6
	CURSOR = 7
	DATABASE_ASTRO = 8
	DATABASE_ASTROMAP = 9
	DATABASE_COMPUTER = 10
	FONT = 11
	G3D_MATERIAL = 12
	G3D_OBJECT = 13
	ICON_MAP = 14
	IMG_BACKGROUND = 15
	IMG_GIF = 16
	IMG_LBM = 17
	IMG_MENU = 18
	LIST = 19
	MOVIE_MAP = 20
	OBJECT = 21
	PALETTE = 22
	PHASER = 23
	PHASER_MAP = 24
	POLYGONS = 25
	SAVEGAME = 26
	SECTOR_NAMES = 27
	SPRITE = 28
	TACTIC = 29
	TERMINAL = 30
	TEXT = 31
	TRIGGERS = 32
	UNKNOWN = 33
	VIDEO = 34
	WORLD = 35
	WORLD_LIST = 36
	WORLD_OBJECTS = 37
	WORLD_START = 38


_FILE_HANDLERS = {
	FileType.DATABASE_ASTRO:      Astro.astroDb,
	FileType.DATABASE_ASTROMAP:   Astro.astromapDb,
	FileType.ASTRO_STATE:         Astro.astStatDat,
	FileType.DATABASE_COMPUTER:   Computer.computerDb,
	FileType.COMPUTER_STATE:      Computer.compstat,
	FileType.WORLD:               World.worldSlScr,
	FileType.POLYGONS:            World.worldStScr,
	FileType.SPRITE:              Sprite.sprite,
	FileType.SECTOR_NAMES:        Astro.sectorAst,
	FileType.CONVERSATION:        Block.bst,
	FileType.OBJECT:              Block.bst,
	FileType.PHASER:              Block.bst,
	FileType.LIST:                Sprite.lst,
	FileType.ADVICE:              World.adviceDat,
	FileType.TERMINAL:            Terminal.terminal,
	FileType.WORLD_START:         World.worldStrt,
	FileType.WORLD_LIST:          World.worldList,
	FileType.WORLD_OBJECTS:       World.worldObj,
	FileType.TRIGGERS:            Data.triggers,
	FileType.ICON_MAP:            Map.icon,
	FileType.MOVIE_MAP:           Map.movie,
	FileType.PHASER_MAP:          Map.phaser,
	FileType.SAVEGAME:            SaveGame.savegame,
	FileType.TACTIC:              Tactic.bin,
	FileType.ALERT:               Data.alert,
	FileType.FONT:                Font.font,
	FileType.IMG_MENU:            Menu.mrg,
	FileType.PALETTE:             Palette.pal,
	FileType.TEXT:                Data.txt,
	FileType.CREDITS:             Data.credits,
	FileType.G3D_MATERIAL:        Graphics.material,
	FileType.IMG_GIF:             Graphics.img,
	FileType.IMG_LBM:             Graphics.lbm,
	FileType.G3D_OBJECT:          Graphics.model,
	FileType.VIDEO:               Video.fvf,
}


def handler(file_type):
	if not file_type in _FILE_HANDLERS:
		raise ValueError(f"{file_type} is currently unsupported")
	return _FILE_HANDLERS[file_type]


def identify(file_path):
	type_str = Utils.identify(file_path)
	type_map = {
		"advice": FileType.ADVICE,
		"alert": FileType.ALERT,
		"astro_state": FileType.ASTRO_STATE,
		"audio": FileType.AUDIO,
		"computer_state": FileType.COMPUTER_STATE,
		"conversation": FileType.CONVERSATION,
		"credits": FileType.CREDITS,
		"cursor": FileType.CURSOR,
		"database_astro": FileType.DATABASE_ASTRO,
		"database_astromap": FileType.DATABASE_ASTROMAP,
		"database_computer": FileType.DATABASE_COMPUTER,
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
