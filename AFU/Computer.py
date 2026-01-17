from AFU.File import DatabaseFile,File
from AFU import Astro



def _readImage(f, offset):
	assert(offset != 0)
	f.setOffset(offset)
	image_width = f.readUInt16()
	image_height = f.readUInt16()
	image_data = [f.readUInt8() for i in range(image_height*image_width)]
	return {
		"offset": offset,
		"width": image_width,
		"height": image_height,
		"data": image_data,
	}


def _readAstrogation(f, offset):
	# A human readable string.
	# Depending on the destination type, has five pieces of information.
	# DS:       <sector_id> <          -1> <          -1> <object_type(128)> <body_station_index>
	# Outpost:  <sector_id> <system_index> <planet_index> <object_type(132)> <body_station_index>
	# Starbase: <sector_id> <           0> <           0> <object_type(131)> <body_station_index>
	s = f.readOffsetString(offset).replace("\r", "\n").split("\n")[0]
	a = [int(i) for i in s.split()]
	sector_id = a[0]
	system_index = a[1] if a[1] != -1 else None
	planet_index = a[2] if a[2] != -1 else None
	object_type = Astro.ObjectType(a[3])
	body_station_index = a[4] if a[4] != -1 else None
	return {
		"sector_id": sector_id,
		"system_index": system_index,
		"planet_index": planet_index,
		"object_type": object_type,
		"body_station_index": body_station_index,
	}


def _readUnknownType6(f, offset):
	# There is one entry in computer.db with this flag value. The game will intepret
	# it as having an image, but the data here is not valid and will cause the game
	# to crash, whether viewed on the computer or tricorder.
	f.setOffset(offset)
	pos = f.pos()
	data = [f.readUInt8() for i in range(8)]
	return {
		"pos": pos,
		"offset": offset,
		"data": data,
	}


def _readEntry(f, offset, index):
	f.setOffset(offset)

	n_subentries = f.readUInt16()
	data_flag = f.readUInt16()
	title_offset = f.readUInt32()
	heading_offset = f.readUInt32()
	text_offset = f.readUInt32()
	data_offset = f.readUInt32()

	subentries_offsets = [f.readUInt32() for i in range(n_subentries)]
	# Subentries is a list of all possible sub-entries.
	# The compstat section in the game save indicates which are visible at any time during the game.

	entry = {
		"index": index,
		"flags": data_flag,
		"title": f.readOffsetString(title_offset).strip(),
		"heading": f.readOffsetString(heading_offset).replace("\r", "\n").strip(),
		"text": f.readOffsetString(text_offset).replace("\r", "\n"),
		"subentries": subentries_offsets,
	}

	#     0 no additional data
	#     2 data is an image
	#     4 data is astrogation information (clicking "Astrogation" while viewing automatically engage the ship to this location
	#     6 "Dr Vi Hyunh-Foertsch" only. Unknown data type.
	if data_flag == 0:
		assert(data_offset == 0)
	elif data_flag == 2:
		entry["image"] = _readImage(f, data_offset)
	elif data_flag == 4:
		entry["astro"] = _readAstrogation(f, data_offset)
	elif data_flag == 6:
		entry["unknown"] = _readUnknownType6(f, data_offset)

	return entry


def computerDb(file_path):
	f = DatabaseFile(file_path)

	n_entries = f.readUInt32()
	entries_offsets = [f.readUInt32() for i in range(n_entries)]
	offset_eof = f.readUInt32()
	f.setOffsetBase(f.pos())
	
	return { offset:_readEntry(f, offset, index) for index,offset in enumerate(entries_offsets) }


def compstat(file_path):
	f = File(file_path)
	return readCompstat(f)


# Hardcoded in the .ovl file data section at 159348
_TRICORDER_READINGS_TO_ENTRIES = {
	20010: {'parent': 215, 'entry': 216},
	20020: {'parent': 215, 'entry': 217},
	20030: {'parent': 215, 'entry': 218},
	20040: {'parent': 215, 'entry': 219},
	20050: {'parent': 215, 'entry': 220},
	20060: {'parent': 215, 'entry': 221},
	20070: {'parent': 215, 'entry': 222},
	20080: {'parent': 215, 'entry': 223},
	20090: {'parent': 215, 'entry': 224},
	20100: {'parent': 215, 'entry': 225},
	20110: {'parent': 215, 'entry': 226},
	20120: {'parent': 215, 'entry': 227},
	20130: {'parent': 215, 'entry': 228},
	20000: {'parent': 215, 'entry': 229},
	30000: {'parent': 230, 'entry': 231},
	30001: {'parent': 230, 'entry': 232},
	30010: {'parent': 230, 'entry': 233},
	30030: {'parent': 230, 'entry': 234},
	30031: {'parent': 230, 'entry': 235},
	30032: {'parent': 230, 'entry': 236},
	30033: {'parent': 230, 'entry': 237},
	30034: {'parent': 230, 'entry': 238},
	30090: {'parent': 230, 'entry': 239},
	30100: {'parent': 230, 'entry': 240},
	30110: {'parent': 230, 'entry': 241},
	40010: {'parent': 245, 'entry': 246},
	40020: {'parent': 245, 'entry': 247},
	40030: {'parent': 245, 'entry': 248},
	40040: {'parent': 245, 'entry': 249},
	40050: {'parent': 245, 'entry': 250},
	40000: {'parent': 245, 'entry': 251},
	50010: {'parent': 242, 'entry': 243},
	50000: {'parent': 242, 'entry': 244},
	60000: {'parent': 254, 'entry': 255},
	70000: {'parent': 252, 'entry': 253}
}


def readCompstat(f):
	
	# The game stores visibility for the computer entries, as bitflags. If the bit is
	# set, the entry is hidden. It sets aside 256 bytes for this purpose, but given
	# there are only 346 computer entries, it never uses more than 44 bytes.
	visible_flags = []
	for i in range(256):
		bits = f.readBits(8)
		bits.reverse()
		visible_flags += bits
	computer_visible = {i:v == 0 for i,v in enumerate(visible_flags)}

	tricorder_n = f.readUInt32()
	tricorder_entries = []
	for i in range(16):
		assert(f.readUInt32() == 0xffffffff)
		r = f.readUInt32()
		if r != 0xffffffff:
			tricorder_entries.append({
				"reading": r,
				"world": r//10000,
				"compter_index": _TRICORDER_READINGS_TO_ENTRIES[r]["entry"],
			})
	assert(tricorder_n == len(tricorder_entries))

	return {
		"computer": computer_visible,
		"tricorder": tricorder_entries,
	}
