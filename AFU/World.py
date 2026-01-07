from AFU.File import File
from AFU.Block import _readObjectId
from enum import Enum


class WorldId (Enum):
	UNSET	= 		0x0
	ALLANOR =		0x2
	MORASSIA =		0x3
	MERTENS =		0x4
	FRIGIS =		0x5
	UNITY_DEVICE =	0x6
	HORST_III =		0x7
	FRIGIS_2 =		0x8
	PLANETS_MAX =	0xa
	COMBAT =		0x10
	ENTERPRISE =	0x5f
	NONE =			0xffffffff


class ScreenRegionType (Enum):
	TILE_INACTIVE = 0x0
	TILE = 0x1
	UNKNOWN_3 = 0x3
	SCENE = 0x4


def worldStrt(file_path):
	""""w_##strt.bst"""
	f = File(file_path)
	data = []
	while not f.eof():
		screen = {}
		screen["advice_id"] = f.readUInt16()
		screen["advice_timer"] = f.readUInt16()
		screen["unknown1"] = f.readUInt8()
		screen["unknown2"] = f.readUInt8()
		screen["id"] = f.readUInt16()
		assert (screen["id"] == len(data))
		screen["target"] = _readObjectId(f)
		screen["action_type"] = f.readUInt8()
		screen["who"] = _readObjectId(f)
		screen["other"] = _readObjectId(f)
		assert(f.readUInt16() == 0xffff) # unknown3
		assert(f.readUInt16() == 0xffff) # unknown4
		screen["unknown5"] = f.readUInt8()
		assert(screen["unknown5"] in (0xff, 0x1, 0x0))
		assert(f.readUInt8() == 0x0)
		assert(f.readUInt16() == 0x0)
		for i in range(16):
			assert (f.readUInt8() == 0)
		data.append(screen)
	return data


def worldList(file_path):
	f = File(file_path)
	data = {}
	while not f.eof():
		scene_id = f.readUInt16()
		assert(f.readUInt16() == scene_id)
		assert(f.readUInt16() == 0)
		comment = f.readStringBuffer(21)
		data[scene_id] = comment
	return data


def worldSlScr(file_path):
	"""Screen Entrances File"""
	f = File(file_path)

	n_screens = f.readUInt16()
	screens = []
	for i in range(n_screens):
		screen_id = f.readUInt32()
		screen_offset = f.readUInt32()
		screens.append( (screen_id,screen_offset) )

	assert( f.readUInt32() == 0xFF )
	eof = f.readUInt32()

	world_screens = []
	for screen_id,screen_offset in screens:
		assert( f.pos() == screen_offset )

		screen = {
			"id": screen_id,
			"entrances": [],
		}

		background_file_length = f.readUInt8()
		background_file = f.readString()
		assert(len(background_file) + 1 == background_file_length)
		screen["background"] = background_file

		polygons_file_length = f.readUInt8()
		polygons_file = f.readString()
		assert(len(polygons_file) + 1 == polygons_file_length)
		screen["polygons"] = polygons_file

		n_entrances = f.readUInt8()
		for i in range(n_entrances):
			entrance_id = f.readUInt8()

			# unknown is 0x1 for every single screen in every world except
			# screen 11 in world 2, where it's 0x8d.
			# If you don't unwind by one byte then, you end up overrunning
			# the block, and the entrance positions are nonsense.
			entrance_unknown = f.readUInt8()
			if( entrance_unknown != 0x1 ):
				f.setPosition(f.pos() - 1)

			entrance_vertices = []
			for j in range(4):
				entrance_vertices.append({"x": f.readUInt16(), "y": f.readUInt16()})
			entrance = {
				"entrance_id": entrance_id,
				"unknown": entrance_unknown,
				"vertices": entrance_vertices,
			}
			screen["entrances"].append(entrance)
		world_screens.append(screen)

	assert(f.pos() == eof)

	return { "screens": world_screens }


def worldObj(file_path):
	f = File(file_path)
	screen = []
	while not f.eof():
		counter = f.readUInt16()
		object_id = _readObjectId(f)
		assert(object_id["id"] == counter)
		name = f.readStringBuffer(30).strip()
		description = f.readStringBuffer(260).strip()
		screen.append({
			"id": object_id,
			"name": name,
			"description": description,
		})
	return screen


def worldStScr(file_path):
	"""Polys/Tile/Region File st######.scr"""
	f = File(file_path)

	n_entries = f.readUInt16()
	entries = []
	for i in range(n_entries):
		id = f.readUInt32()
		offset = f.readUInt32()
		entries.append( (id,offset) )

	assert(f.readUInt32() == 0xFF)
	eof = f.readUInt32()

	n_screen_unknown = f.readUInt8()
	screen_unknown = [f.readUInt16() for x in range(n_screen_unknown)]

	screen_polygons = []
	for id,offset in entries:
		assert(f.pos() == offset)

		poly_type = f.readUInt8()
		assert(poly_type in [0,1,3,4])

		assert(f.readUInt16() == 0)

		n_vertices = f.readUInt8()
		poly_vertices = []
		for i in range(n_vertices):
			x = f.readUInt16()
			y = f.readUInt16()
			distance = f.readUInt16()
			poly_vertices.append({
				"x": x,
				"y": y,
				"distance": distance,
				})

		n_poly_unknown = f.readUInt8()
		poly_unknown = []
		for i in range(n_poly_unknown):
			poly_unknown.append((f.readUInt8(), f.readUInt8()))

		assert(f.readUInt16() == 0)

		screen_polygons.append({
			"type": poly_type,
			"vertices": poly_vertices,
			"unknown": poly_unknown,
		})

	assert(f.pos() == eof)

	screen = {
		"unknown": screen_unknown,
		"polygons": screen_polygons,
	}

	return screen


_ADVICE_CHARACTERS = ["picard", "riker", "data", "troi", "laforge", "beverly", "crusher", "worf", "butler", "carlstrom"]


def _adviceValueAndComment(s):
	vc = s.split("//")
	assert (len(vc) in (2, 1))
	if len(vc) == 2:
		return vc
	
	vc = vc[0].split("/")
	assert (len(vc) in (2, 1))
	return vc


def _adviceEntry(f):
	
	entry = {
		"advice": {
			"easy": {},
			"hard": {},
		},
	}
	
	line = f.readLine()
	if line.startswith("#"):  # unlike all the other files, w005a000.dat starts with this
		line = f.readLine()
	
	if line.startswith("EOF"):
		# no entry here, end of file
		return None
	
	line = _adviceValueAndComment(line)
	entry["id"] = int(line[0])
	if len(line) == 2:
		entry["comment"] = line[1]
	else:
		entry["comment"] = ""
	
	line = f.readLine()
	line = _adviceValueAndComment(line)
	entry["wait"] = int(line[0])
	difficulty = "easy"
	# the comment is just 'Easy level'
	
	while True:
		line = f.readLine()
				
		if line.startswith("#"):
			# end of entry
			return entry
		
		if line.startswith("~"):
			# hard difficulty
			difficulty = "hard"
			continue
		
		character,hail = line.split(",", 1)

		character = character.lower().strip()
		assert(character in _ADVICE_CHARACTERS)
		
		hail = hail.strip()
		assert(hail[0] == '@')

		advice = hail[1:].split(',')
		if len(advice) != 2:
			advice = hail[1:].split('.')
		assert(len(advice) == 2)
		advice = [int(a) for a in advice]

		#entry["advice"][difficulty][character] = hail
		entry["advice"][difficulty][character] = advice


def adviceDat(file_path):
	# Reads w{world}a000.dat files. The contain information about characters giving the player advice.
	f = File(file_path)
	entries = {}
	while not f.eof():
		entry = _adviceEntry(f)
		if entry is None:
			break
		entries[entry["id"]] = entry
	return entries
