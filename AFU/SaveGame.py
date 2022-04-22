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
	data = []
	f.setPosition(block["data_offset"])
	f.readUInt8()
	while f.pos() != block["end_offset"]:
		unknown0 = [f.readUInt8() for i in range(48)]
		x = f.readUInt32()
		y = f.readUInt32()
		z = f.readUInt32()
		orbit = f.readUInt32() # 99% sure this is correct. Index from 0-N of the bodies orbiting the star
		assert(f.readUInt32() == 0)
		assert(f.readUInt32() == 0)
		assert(f.readUInt32() == 0xffffffff)
		unknown1 = [f.readUInt8() for i in range(16)]
		name = f.readString()
		desc = f.readString()
		data.append({
			"name": name,
			"description": desc,
			"coords": [x, y, z],
			"orbit": orbit,
			"unknown0": unknown0,
			"unknown1": unknown1,
		})
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
	assert(f.readString() == "COMPSTAT")
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(3)])
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(8)])
	#fpos(f)
	#assert(f.pos() == block["end_offset"])
	return data


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

	print(blocks[0])
	data |= readBlockCompstat(f, blocks[0])
	print(blocks[1])
	data |= readBlockAststat(f, blocks[1])
	print(blocks[2])
	print(blocks[3])
	print(blocks[4])
	print(blocks[5])
	data |= readBlockTravelHistory(f, blocks[5])
	print(blocks[6])
	try:
		data |= readBlockObjects(f, blocks[6])
	except:
		print("AN ERROR OCURRED FETCHING OBJECTS - SAVEGAME SUPPORT IS A WORK IN PROGRESS")
	print(blocks[7])
	print(blocks[8])

	return data
