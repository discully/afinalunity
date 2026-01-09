from pathlib import Path
from AFU.File import File, fpos
from AFU import Astro, Computer, Block, World

# [offset      ][block][size][contents             ]
#  0x0    0      Header 14
#  0xf    15     GNT    544
#                             0x13   compstat
#                             0x1a0  ?
#  0x233  563    GNT    9600         ast_stat
#  0x27b7 10167  GNT    31
#  0x27da 10202  GNT    8
#  0x27e6 10214  GNT    2177
#  0x306b 12395  GNT    5            travel history
#  0x3074 12404  GNT    5799         objects (ships, characters, away team, etc.)
#  0x471f 18207  ONT    2767         enterprise status??
#  0x51f2 20978  ONT    81           ??


def readBlockTravelHistory(f, block):
	data = []
	f.setPosition(block["data_offset"])
	assert(f.readUInt8() == 0) # padding
	
	while f.pos() != block["end_offset"]:
		
		entry = {}
		data_size = f.readUInt32()
		data_start = f.pos()

		f.readUInt32() # ptr name
		f.readUInt32() # ptr text
		assert(f.readUInt16() == 0)
		has_extra = {0: False, 0x10: True}[f.readUInt16()]
		f.readUInt32() # ptr name
		f.readUInt32() # ptr text
		assert(f.readUInt32() == 0)
		f.readUInt32() # ptr dest 2

		dest_sector_id = f.readUInt16()
		dest_system_index = f.readUInt16()
		dest_planet_index = f.readUInt16()
		dest_object_type = f.readUInt16() & 0xff # Stored in a short but only the little byte gets set
		dest_body_station_index = f.readUInt16()
		assert(f.readUInt16() == 0x0)

		if dest_system_index == 0xffff: dest_system_index = None
		if dest_planet_index == 0xffff: dest_planet_index = None
		if dest_body_station_index == 0xffff: dest_body_station_index = None
		if dest_object_type == 0xff:
			dest_object_type = None
		else:
			dest_object_type = Astro.ObjectType(dest_object_type)

		entry["destination"] = {
			"sector_id": dest_sector_id,
			"system_index": dest_system_index,
			"planet_index": dest_planet_index,
			"object_type": dest_object_type,
			"body_station_index": dest_body_station_index,
		}
		
		# Extra structure

		if has_extra:
			f.readUInt32() # ptr name
			extra_global_coords = [f.readUInt32() for i in range(3)]
			extra_system_coords = [f.readUInt32() for i in range(3)]
			assert(f.readUInt32() == 0xffffffff)

			extra_sector_id = f.readUInt16()
			extra_oject_type = f.readUInt8()
			extra_status = f.readUInt8() # TODO: Either 1 or 0. Think this is something to do with having been scanned/charterd.
			assert(f.readUInt16() == 0)
			extra_system_index = f.readUInt16()
			extra_planet_index = f.readUInt16()
			assert(f.readUInt16() == 0)
			extra_body_unknown26 = f.readUInt32()

			if extra_system_index == 0xffff: extra_system_index = None
			if extra_planet_index == 0xffff: extra_planet_index = None
			if extra_oject_type == 0xff:
				extra_oject_type = None
			else:
				extra_oject_type = Astro.ObjectType(extra_oject_type)

			entry["extra"] = {
				"global_coords": extra_global_coords,
				"system_coords": extra_system_coords,
				"sector_id": extra_sector_id,
				"object_type": extra_oject_type,
				"status": extra_status,
				"system_index": extra_system_index,
				"planet_index": extra_planet_index,
				"body_unknown26": extra_body_unknown26,
			}

		entry["name"] = f.readString()
		entry["desc"] = f.readString()
		
		data_end = f.pos()
		assert(data_end - data_start == data_size)

		data.append(entry)

	assert(f.pos() == block["end_offset"])
	return {
		"travel_history": data,
	}


def readBlockAststat(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	data["astro_state"] = Astro.readAstroState(f)
	assert(f.pos() == block["end_offset"])
	return data


def readBlockCompstat(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	data["computer_state"] = Computer.readCompstat(f)

	# Pretty sure what follows is just junk grabbed from reading too
	# many bytes from memory. The COMPSTAT file is 388 bytes. But
	# the game copies 540 bytes in/out of memory. That means the last
	# 152 bytes of this section are just junk.
	f.setPosition(f.pos() + 152)

	assert(f.pos() == block["end_offset"])
	return data


def readVideos(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	i = 0
	videos = []
	while f.pos() < block["end_offset"]:
		visible = (False, True)[f.readUInt8()]
		videos.append({"index": i, "visible": visible})
		i += 1
	data["videos"] = videos

	assert(f.pos() == block["end_offset"])
	return data


def readScreenRegions(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	screen_regions = []
	while True:
		n = f.readUInt32()
		if n == 0xffffffff: break

		world_id = World.WorldId(f.readUInt32())
		screen_id = f.readUInt32()
		n_regions = f.readUInt32()
		region_types = [World.ScreenRegionType(f.readUInt8()) for i in range(n_regions)]

		[f.readUInt8() for i in range(3)] # either padding or an error in the game's arithmetic

		screen_regions.append({
			"world_id": world_id,
			"screen_id": screen_id,
			"n_regions": n_regions,
			"region_types": region_types
		})
	
	assert(f.pos() == block["end_offset"])
	return {
		"screen_regions": screen_regions,
	}


def readBlockConverations(f, block):
	f.setPosition(block["data_offset"])

	assert(f.readUInt8() == 0)

	conversation_buffer_n = f.readUInt32() # entries in the buffer
	conversation_buffer_size = f.readUInt32() # allocated size of the buffer
	situation_buffer_n = f.readUInt32()
	situation_buffer_size = f.readUInt32()
	action_buffer_n = f.readUInt32()
	action_buffer_size = f.readUInt32()
	
	conversation_buffer = []
	for i in range(conversation_buffer_n):
		conversation_buffer.append([f.readUInt32() for j in range(3)])
	
	situation_buffer = []
	for i in range(situation_buffer_n):
		situation_buffer.append([f.readUInt32() for j in range(3)])
	
	action_buffer = [f.readUInt8() for j in range(action_buffer_n)]

	conversation_history_n = f.readUInt32()
	conversation_history = []
	for i in range(conversation_history_n):
		conversation = []
		c_size = f.readUInt32()
		c_start = f.pos()
		assert(f.readUInt32() == c_size)
		while True:
			c_world = f.readUInt8()
			c_index = f.readUInt8()
			if c_world == 0xff:
				assert(c_index == 0xff)
				break
			elif c_world == 0:
				assert(c_index == 0xff)
				c_line = f.readString()
			else:
				c_id = f.readUInt8()
				c_state = f.readUInt8()
				c_unknown1 = f.readUInt8()
				c_unknown2 = f.readUInt8()
				c_line = {
					"world": c_world, "index": c_index,
					"id": c_id, "state": c_state, "unknown1": c_unknown1, "unknown2": c_unknown2
					}
			conversation.append(c_line)
		assert(f.pos() == c_start + c_size)
		conversation_history.append(conversation)
	
	#print("Conversation History")
	#for i,conversation in enumerate(conversation_history):
	#	if i == 0:
	#		print("    Previous Conversation")
	#	else:
	#		print("    Conversation", i)
	#	for line in conversation:
	#		print("       ", line)

	recent_vacs = [f.readStringBuffer(14) for j in range(3)]

	return {
		"conversations": {
			"conversation_buffer": conversation_buffer,
			"situation_buffer": situation_buffer,
			"action_buffer": action_buffer,
			"conversation_history": conversation_history,
			"recent_vacs": recent_vacs,
		}
	}


def readBlockObjectHeader(f):
	addr = f.readUInt32()
	type_1 = f.readUInt32()
	id = Block._readObjectId(f)
	type_2 = f.readUInt32()
	assert(type_1 == type_2)
	assert(f.readUInt32() == 0x0)
	next = f.readUInt32()
	return {
		"addr": addr,
		"type_1": type_1,
		"id": id,
		"type_2": type_2,
		"next": next,
	}


def readBlockObjectType4(f):
	unknown = []
	unknown.append([f.readUInt8() for i in range(8)])
	unknown.append([f.readUInt32() for i in range(7)])
	unknown.append([f.readUInt8() for i in range(4)])
	unknown.append(f.readUInt32())
	unknown.append(f.readUInt32())
	for u in unknown:
		print("**4**", u)
	return {
		"unknown": unknown
	}
def readBlockObjectType4B(f):
	unknown = []
	unknown.append([f.readUInt8() for i in range(8)])
	n4 = f.readUInt32()
	unknown.append(n4)
	for j in range(n4):
		unknown.append([f.readUInt8() for i in range(6)])
	unknown.append([f.readUInt8() for i in range(78)])
	fpos(f, "here")
	#unknown.append([f.readUInt8() for i in range(14)])
	name = f.readStringBuffer(20)
	desc = f.readStringBuffer(100)
	unknown_5 = f.readUInt16()
	unknown_6 = f.readUInt32()
	unknown_7 = [f.readUInt32(), f.readUInt32(), f.readUInt16(), f.readUInt16(), f.readUInt32(), f.readUInt32()]
	for u in unknown:
		print("**4**", u)
	print("**44**", name)
	return {
		"unknown": unknown,
		"name": name,
		"desc": desc,
	}


def readBlockObjectType1(f, obj_type):
	flags = f.readUInt32()
	state = f.readUInt8()
	anim_index = f.readUInt8()
	y_adjust = f.readSInt16()
	region_id = f.readUInt16()
	sprite_id = f.readUInt16()
	xyz = [f.readSInt32() for i in range(3)]
	universe_xyz = [f.readSInt32() for i in range(3)]
	unknown_1 = [f.readUInt32() for i in range(2)]
	curr_screen = f.readUInt32()
	voice_id = Block._readVoiceId(f)
	unknown_2 = [f.readUInt8() for i in range(4)]

	unknown_3 = None
	unknown_4 = None
	if obj_type == 16:
		unknown_3 = [f.readUInt16() for i in range(2)]
	if obj_type == 16 or obj_type == 1:
		unknown_4 = [f.readUInt8() for i in range(56)]

	name = f.readStringBuffer(20)
	desc = f.readStringBuffer(100)

	unknown_5 = f.readUInt16()
	unknown_6 = f.readUInt32()
	unknown_7 = [f.readUInt32(), f.readUInt32(), f.readUInt16(), f.readUInt16(), f.readUInt32(), f.readUInt32()]

	unknown_8 = None
	if obj_type == 16 and unknown_1[1] == 16: # this is a complete guess as to what's signalling the extra data, or if this is where it is
		unknown_8 = [f.readUInt8() for i in range(8)]

	data = {
		"flags": flags,
		"state": state,
		"anim_index": anim_index,
		"y_adjust": y_adjust,
		"region_id": region_id,
		"sprite_id": sprite_id,
		"xyz": xyz,
		"universe_xyz": universe_xyz,
		"curr_screen": curr_screen,
		"voice_id": voice_id,
		"name": name,
		"desc": desc,
		"unknown": [unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8]
	}

	return data



def readBlockObjects2(f):
	# The Away Team ?

	data = []
	id = None
	for i in range(7):
		fpos(f)

		# Some characters have multiple (identical?) entries.
		# The first entry has their ID, the subsequent ones have ID of 0xffffffff.
		new_id = f.readUInt32()
		if new_id != 0xffffffff:
			id = new_id

		type = f.readUInt32()
		#assert(type == 2)

		unknown1 = []
		unknown1.append([f.readUInt32() for i in range(3)]) #
		unknown1.append([f.readUInt16() for i in range(4)]) #
		unknown1.append([f.readUInt32() for i in range(8)]) #
		unknown1.append([f.readUInt16() for i in range(9)]) # 78
		name = f.readStringBuffer(9) # todo: check this with Carlstrom in the team
		unknown2 = [f.readUInt8() for i in range(141)] # almost looks like bocks of four, but not quite

		print(id, type, name)

		data.append({
			"id": id,
			"type": type,
			"name": name,
			"unknown1": unknown1,
			"unknown2": unknown2
		})
	return data


def readBlockObjects1(f):
	data = {}
	next = 0xffffffff
	while next != 0x0:
		p = f.pos()
		obj = readBlockObjectHeader(f)

		if obj["type_1"] == 4:
			#obj |= readBlockObjectType4(f)
			#key = ""
			obj |= readBlockObjectType4B(f)
			key = obj["name"]
		elif obj["type_1"] in (1, 2, 16):
			obj |= readBlockObjectType1(f, obj["type_1"])
			key = obj["name"]
		else:
			raise ValueError("Unknown object type: {}".format(obj["type_1"]))

		if key == "":
			key = "{0[id]}-{0[screen]}-{0[world]}".format(obj["id"])

		if key in data:
			raise ValueError("Key already exists in data: {}".format(key))

		obj_size = f.pos() - p
		obj_delta_next = obj["next"] - next

		data[key] = obj
		next = obj["next"]

		print("{} {:>2} {:<25} {}".format(hex(p), obj["type_1"], key, hex(p + obj_delta_next + 4)))

	return data


def readBlockObjects(f, block):

	dat = Path("../../data/STTNG/")

	data = {}
	f.setPosition(block["data_offset"])

	fpos(f)

	while f.pos() <= block["end_offset"]:
		section = [f.readUInt8() for i in range(4)]

		print("===========", section, "===========")
		if section[0] == 1: # Lots of objects
			data |= readBlockObjects1(f)
			unknown_addr = f.readUInt32()
			assert(f.readUInt32() == 0xffffffff)
		elif section[0] == 64:
			n64 = f.readUInt32()
			assert(n64 == 0)
		elif section[0] == 16:
			assert(f.readUInt8() == 0)
			# e.g. [2, 4, 4294967295, 7, 4, 0, 4294967295, 1, 4, 0]
			# Is the '7' the number of away team members under '2,2,2,2' ???
			# Todo: try an away team with fewer than four members
			print([f.readUInt32() for i in range(10)])
		elif section[0] == 4:
			n4 = f.readUInt32()
			assert(n4 == 0)
		elif section[0] == 2: # Away team
			readBlockObjects2(f)
		elif section[0] == 32:
			s32 = [f.readUInt32()]
			while s32[-1] != 17:
				s32.append(f.readUInt32())
			s32u = [f.readUInt8() for i in range(46)]
			print(s32)
			print(s32u)
		elif section[0] == 48:
			n48 = f.readUInt32()
			print(n48)
			print([f.readUInt32() for i in range(2*n48)])
		elif section[0] == 6:
			pass
		elif section[0] == 3:
			print([f.readUInt8() for i in range(92)])
			name3 = f.readString()
			print(name3)
		elif section[0] == 0xff:
			break
		else:
			assert(False)

	return data



def readEnterprise(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	assert(f.readUInt32() == 0x08080808)
	combat = {}
	combat["unknown_1"] = f.readUInt32()
	combat["screen"] = f.readUInt32()
	if combat["screen"] == 0xffffffff: combat["screen"] = None
	
	assert(f.readUInt32() == 0x0a0a0a0a)
	enterprise = {}
	enterprise["name"] = f.readStringBuffer(30)
	enterprise["n_systems"] = f.readUInt32()
	enterprise["type"] = f.readUInt32()
	# Power
	power = {"generators":[]}
	for i in range(2):
		generator = {}
		generator["unknown_g1"] = f.readUInt32()
		generator["power_free"] = f.readUInt32()
		generator["unknown_g2"] = f.readUInt32()
		generator["time_last_power_update"] = f.readUInt32()
		generator["time_normal_operation_update"] = f.readUInt32()
		generator["unknown_g3"] = f.readUInt32()
		generator["ptr_system"] = f.readUInt32()
		power["generators"].append(generator)
	power["total_power_free"] = f.readUInt32()
	power["unknown_1"] = f.readUInt32()
	power["time_repair_update"] = f.readUInt32()
	power["ptr_battery_system"] = f.readUInt32()
	power["unknown_2"] = [f.readUInt32() for i in range(6)]
	power["total_power_requested"] = f.readUInt32()
	power["total_power_applied"] = f.readUInt32()
	enterprise["power"] = power
	
	enterprise["h"] = [f.readUInt32() for i in range(14)]

	enterprise["systems"] = []
	for i in range(enterprise["n_systems"]):
		system = {}
		system["charge_current"] = f.readUInt32()
		system["charge_target"] = f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		system["rate_usage"] = f.readUInt32() # not sure this is the right label
		system["health_damage"] = f.readUInt32()
		system["unknown_64"] = f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		system["charge_requested_min"] = f.readUInt32() # not sure this is the right label
		system["charge_requested"] = f.readUInt32()
		system["unknown_94"] = f.readUInt32()
		system["readout_power_target"] = f.readUInt32()
		system["readout_power_current"] = f.readUInt32()
		system["readout_repair_target"] = f.readUInt32()
		system["readout_repair_current"] = f.readUInt32()
		enterprise["systems"].append(system)
	assert(f.readUInt32() == 0xa0a0a0a0)

	assert(f.readUInt32() == 0x0b0b0b0b)
	tactical = {}
	tactical["weapons_lock"] = (False, True)[f.readUInt8()]
	tactical["torpedo_spread"] = f.readUInt32() / 46
	tactical["shields_raised"] = (False, True)[f.readUInt8()]
	tactical["deletgate_on"] = (False, True)[f.readUInt8()]
	f.readUInt8()
	tactical["unknown_74"] = f.readUInt8()
	tactical["alert_level"] = f.readUInt32()
	assert(f.readUInt32() == 0xb0b0b0b0)

	assert(f.readUInt32() == 0x80808080)

	assert(f.pos() == block["end_offset"])
	return { "ncc1701d": {
		"combat": combat,
		"enterprise": enterprise,
		"tactical": tactical,
	}}


def readGlobalSettings(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	
	while True:
		x = f.readUInt32()
		if x == 0:
			data["dialogue_scrollable_pos"] = (f.readUInt16(), f.readUInt16())
		elif x == 1:
			data["dialogue_talking_pos"] = (f.readUInt16(), f.readUInt16())
		elif x == 2:
			data["unknown"] = [f.readUInt8() for i in range(0x20)]
			#for i in range(0x20):
			#	assert(f.readUInt8() == 0x0)
		elif x == 3:
			data["astrogation_location_updated"] = (False, True)[f.readUInt8()]
		elif x == 4:
			data["warpout_video_state"] = f.readUint8()
		elif x == 5:
			data["phaser_setting"] = f.readUInt32()
		elif x == 0xffffffff:
			break

	assert(f.pos() == block["end_offset"])
	return {"globals": data}


def readBlockHeader(f):
	block_offset = f.pos()
	block_type = f.readStringBuffer(4)
	assert(block_type in ["GNT", "ONT"])
	block_data_size = f.readUInt32() - 4
	block_data_offset = f.pos()
	block_end_offset = block_data_offset + block_data_size
	return {
		"type": block_type,
		"offset": block_offset,
		"data_offset": block_data_offset,
		"data_size": block_data_size,
		"end_offset": block_end_offset,
	}


def readBlockHeaders(f):
	blocks = []
	while not f.eof():
		blocks.append(readBlockHeader(f))
		f.setPosition(blocks[-1]["end_offset"])
	
	assert(len(blocks) == 9)
	names = ["compstat", "aststat", "videos", "screen_regions", "converations", "travel_history", "objects", "enterprise", "globals"]
	for i,name in enumerate(names):
		blocks[i]["name"] = name

	return blocks


def savegame(input_path):
	f = File(input_path)
	data = {}

	# Header
	assert(f.readString() == "STTNG_GAME")

	blocks = readBlockHeaders(f)
	assert(len(blocks) == 9)

	print(blocks[0])
	data |= readBlockCompstat(f, blocks[0])
	print(blocks[1])
	data |= readBlockAststat(f, blocks[1])
	print(blocks[2])
	data |= readVideos(f, blocks[2])
	print(blocks[3])
	data |= readScreenRegions(f, blocks[3])
	print(blocks[4])
	data |= readBlockConverations(f, blocks[4])
	print(blocks[5])
	data |= readBlockTravelHistory(f, blocks[5])
	print(blocks[6])
	try:
		data |= readBlockObjects(f, blocks[6])
	except:
		print("AN ERROR OCURRED FETCHING OBJECTS - SAVEGAME SUPPORT IS A WORK IN PROGRESS")
	print(blocks[7]) # enterprise
	data |= readEnterprise(f, blocks[7])
	print(blocks[8])
	data |= readGlobalSettings(f, blocks[8])

	return data
