from AFU.File import DatabaseFile



def _readString(f, offset):
	assert(offset != 0x0)
	f.setOffset(offset)
	return f.readString().replace("\r", "\n")


def _readImage(f, offset):
	assert(offset != 0)
	f.setOffset(offset)
	image_width = f.readUInt16()
	image_height = f.readUInt16()
	image_data = f.read(image_height*image_width)
	return {
		"width": image_width,
		"height": image_height,
	#	"data": image_data,
	}


def _readAstrogation(f, offset):
	f.setOffset(offset)

	debug = f.readString()
	# A human readable string, probably used for debugging during development.
	# Depending on the destination type, has four pieces of information and finishes with a 0.
	# DS:       <sector_id> <          -1> <           -1> <    128    > <0>
	# Outpost:  <sector_id> <system_index> <station_orbit> <    132    > <0>
	# Starbase: <sector_id> <           0> <            0> <    131    > <0>

	n_data1 = f.readUInt16()
	n_data2 = f.readUInt16()

	data0 = [] if n_data1 == 0 else [f.readUInt32() for i in range(4)]
	data1 = [f.readUInt32() for i in range(n_data1)]
	data2 = [f.readUInt32() for i in range(n_data2)]

	return {
		"debug": debug,
		"data0": data0,
		"data1": data1,
		"data2": data2,
	}


def _readUnknown(f, offset):
	f.setOffset(offset)
	pos = f.pos()
	data = [f.readUInt16() for i in range(4)]
	return {
		"pos": pos,
		"offset": offset,
		"data": data,
	}


def _readEntry(f, offset):
	f.setOffset(offset)

	n_subentries = f.readUInt16()
	data_flag = f.readUInt16()
	title_offset = f.readUInt32()
	heading_offset = f.readUInt32()
	text_offset = f.readUInt32()
	data_offset = f.readUInt32()

	subentries_offsets = [f.readUInt32() for i in range(n_subentries)]
	# Subentries is a list of all possible sub-entries. compustat.dat/the game save probably indicates which are visible.

	entry = {
		"flags": data_flag,
		"title": _readString(f, title_offset).strip(),
		"heading": _readString(f, heading_offset).strip(),
		"text": _readString(f, text_offset),
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
		entry["unknown"] = _readUnknown(f, data_offset)

	return entry


def computerDb(file_path):
	f = DatabaseFile(file_path)

	n_entries = f.readUInt32()
	entries_offsets = [f.readUInt32() for i in range(n_entries)]
	offset_eof = f.readUInt32()
	f.setOffsetBase(f.pos())

	return { offset:_readEntry(f, offset) for offset in entries_offsets }
