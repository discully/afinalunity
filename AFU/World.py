from AFU.File import File
from AFU.Block import _readObjectId


def worldStrt(file_path):
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
		assert(f.readUInt32() == 0xffffffff) # unknown3
		screen["unknown4"] = f.readUInt16()
		assert(screen["unknown4"] in (0xff, 0x1, 0x0))
		assert(f.readUInt16() == 0x0) # unknown5
		assert(f.readUInt8() == 0x0) # unknown6
		for i in range(15):
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
		"polgons": screen_polygons,
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
		"difficulty_advice": [
			{"character_advice": []}
		],
	}
	
	line = f.readLine()
	if line.startswith("#"):  # unlike all the other files, w005a000.dat starts with this
		line = f.readLine()
	
	if line.startswith("EOF"):
		# no level here, end of file
		return None
	
	line = _adviceValueAndComment(line)
	level_id = int(line[0])
	if len(line) == 2:
		entry["comment"] = line[1]
	
	line = f.readLine()
	line = _adviceValueAndComment(line)
	level_sub_id = int(line[0])
	if len(line) == 2:
		entry["difficulty_advice"][0]["comment"] = line[1]
	
	entry["id"] = (level_id, level_sub_id)
	
	while True:
		line = f.readLine()
		
		if line.startswith("#"):
			# end of entry
			return entry
		
		if line.startswith("~"):
			# new difficulty
			entry["difficulty_advice"].append({"character_advice": []})
			line = line.split("//")
			assert (len(line) in (1, 2))
			if len(line) == 2:
				entry["difficulty_advice"][-1]["comment"] = line[1]
			continue
		
		character_data = line.split(",")
		if character_data[0].lower() in _ADVICE_CHARACTERS:
			print(line)
			if len(character_data) != 3:
				# There are a couple of entries where for Butler the two numbers are separated by a '.'
				assert (len(character_data) == 2)
				character_data[1:] = character_data[1].split(".")
			assert (len(character_data) == 3)
			character_name = character_data[0]
			character_adv0 = int(character_data[1].strip(" @"))
			character_adv1 = int(character_data[2])
			
			entry["difficulty_advice"][-1]["character_advice"].append({
				"name": character_name,
				"advice": (character_adv0, character_adv1)
			})
			continue
		
		raise ValueError("Unexpected value in file: '{}'".format(line))


def adviceDat(file_path):
	# Reads w{world}a000.dat files. The contain information about characters giving the player advie.
	# I'm pretty sure this file is not for the game to read.
	# There're so many typos and variations, I'm pretty sure they're developer notes.
	f = File(file_path)
	entries = []
	while not f.eof():
		level = _adviceEntry(f)
		if level is None:
			break
		entries.append(level)
	return entries
