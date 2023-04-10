from pathlib import Path
from AFU.File import File, fpos
from AFU import Astro, Computer, Block

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
	print("Travel History:")
	data = []
	f.setPosition(block["data_offset"])
	f.readUInt8()
	while f.pos() != block["end_offset"]:

		# Some kind of type info?
		#   - Moons >= 200
		#   - Planets,stations >= 100
		#   - Sectors < 100.
		# Except Cymkoe IV is 99? Because this is actually mertens orbital station??
		unknown_location_number = f.readUInt32() 

		addrs = []
		addrs.append(f.readUInt32())
		addrs.append(f.readUInt32())
		assert(f.readUInt16() == 0)
		assert(f.readUInt16() == 16)
		addrs.append(f.readUInt32())
		addrs.append(f.readUInt32())
		assert(f.readUInt32() == 0)
		addrs.append(f.readUInt32())

		ua_sector_id = f.readUInt16()
		ua_system_index = f.readUInt16()
		ua_planet_index = f.readUInt16()
		ua_location_type = f.readUInt8()
		ua_unknown1 = f.readUInt8() 			# 0xFF for stations,sectors,systems. 0 otherwise.
		ua_unknown2 = f.readUInt16()			# 0xFFFF for stations. 0 otherwise.
		assert(f.readUInt16() == 0x0)
		
		addrs.append(f.readUInt32())

		x = f.readUInt32()
		y = f.readUInt32()
		z = f.readUInt32()

		unknown_location_values = [f.readUInt32() for i in range(2)] # [0,0] for sectors,systems,stations. Two integer values for planets,moons. Values seem less than ~60. Colour information???
		assert(f.readUInt32() == 0x0)
		assert(f.readUInt32() == 0xffffffff)

		# There is a second set of information here (differs in that location_type is not set for star systems)
		# Ordinarily, it gets set to the same place as the first set.
		# But if you go to a Deep Space Station, it will be the previous location.
		# Ocasionally, that also happens for an Outpost, but not always??

		ub_sector_id = f.readUInt16()
		ub_location_type = f.readUInt8()
		ub_unknown = f.readUInt8() 				# 0 for moons,sectors. 1 for systems,planets,stations.
		assert(f.readUInt16() == 0)
		ub_system_index = f.readUInt16() 		# index of system within sector, or 0xff if not in system
		ub_planet_index = f.readUInt16()		# index of planet within system. moon gets planets' index. 0xff if not in system.
		assert(f.readUInt16() == 0)
		assert(f.readUInt16() == 0)
		assert(f.readUInt16() == 0)

		if ua_system_index == 0xffff:
			ua_system_index = None
		if ua_planet_index == 0xffff:
			ua_planet_index = None

		if ua_location_type == 0xff:			# Empty location in a sector.
			ua_location_type = None
		else:
			ua_location_type = Astro.ObjectType(ua_location_type)
		
		if ub_location_type == 0xff:			# Empty location in a sector.
			ub_location_type = None
		else:
			ub_location_type = Astro.ObjectType(ub_location_type)
		
		if ub_system_index == 0xffff:
			ub_system_index = None
		if ub_planet_index == 0xffff:
			ub_planet_index = None
		
		assert(ua_unknown1 in (0x0,0xff))
		assert(ua_unknown2 in (0x0,0xffff))
		assert(ub_unknown in (1,0))

		name = f.readString()
		desc = f.readString()
		data.append({
			"name": name,
			"description": desc,
			"coords": [x, y, z],
			"info_a" : {
				"sector_id": ua_sector_id,
				"system_index": ua_system_index,
				"planet_index": ua_planet_index,
				"location_type": ua_location_type,
				"unknown": [ua_unknown1, ua_unknown2],
			},
			"info_b" : {
				"sector_id": ub_sector_id,
				"system_index": ub_system_index,
				"planet_index": ub_planet_index,
				"location_type": ub_location_type,
				"unknown": ub_unknown,
			},
			"addrs": addrs,
			"unknown_location_number": unknown_location_number,
			"unknown_location_values": unknown_location_values,
		})

		print("    {0:<25} {1:>3} ({2[0]:>3},{2[1]:>3})".format(name,unknown_location_number,unknown_location_values))

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
	assert(f.readStringBuffer(8) == "COMPSTAT")

	assert(f.readUInt32() == 0)

	unknown = []
	for j in range(5):
		unknowna = [f.readUInt32() for i in range(3)]
		unknownb = [f.readUInt8() for i in range(8)]
		unknownc = [f.readUInt8() for i in range(8)]
		unknown.append([unknowna, unknownb, unknownc])
	data["computer_unknown"] = unknown

	assert(f.pos() == block["end_offset"])
	return data


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
		conversation_buffer([f.readUInt32() for j in range(3)])
	
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
		"conversation_buffer": conversation_buffer,
		"situation_buffer": situation_buffer,
		"action_buffer": action_buffer,
		"conversation_history": conversation_history,
		"recent_vacs": recent_vacs,
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

	print(block)
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
	return blocks


def savegame(input_path):
	f = File(input_path)
	data = {}

	# Header
	assert(f.readString() == "STTNG_GAME")

	blocks = readBlockHeaders(f)
	assert(len(blocks) == 9)

	print(blocks[0]) # compstat
	data |= readBlockCompstat(f, blocks[0])
	print(blocks[1]) # aststat
	data |= readBlockAststat(f, blocks[1])
	print(blocks[2]) # videos
	print(blocks[3]) # unknown
	print(blocks[4])
	data |= readBlockConverations(f, blocks[4])
	print(blocks[5])
	data |= readBlockTravelHistory(f, blocks[5])
	print(blocks[6]) # chunks
	try:
		data |= readBlockObjects(f, blocks[6])
	except:
		print("AN ERROR OCURRED FETCHING OBJECTS - SAVEGAME SUPPORT IS A WORK IN PROGRESS")
	print(blocks[7]) # enterprise
	print(blocks[8]) # unknown

	return data
