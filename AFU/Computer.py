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
	# Depending on the destination type, has four pieces of information and finishes with a 0.
	# DS:       <sector_id> <          -1> <          -1> <object_type(128)> <0>
	# Outpost:  <sector_id> <system_index> <planet_index> <object_type(132)> <0>
	# Starbase: <sector_id> <           0> <           0> <object_type(131)> <0>
	s = f.readOffsetString(offset).replace("\r", "\n").split("\n")[0]
	a = [int(i) for i in s.split()]
	sector_id = a[0]
	system_index = a[1] if a[1] != -1 else None
	planet_index = a[2] if a[2] != -1 else None
	object_type = Astro.ObjectType(a[3])
	return {
		"sector_id": sector_id,
		"system_index": system_index,
		"planet_index": planet_index,
		"object_type": object_type,
	}


def _readUnknown(f, offset):
	# possibly some kind of reference to an image elsewhere?
	f.setOffset(offset)
	pos = f.pos()
	data = [f.readUInt16() for i in range(4)]
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
		entry["unknown"] = _readUnknown(f, data_offset)

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


def readCompstat(f):
	visible_flags = []
	for i in range(44):
		bits = f.readBits(8)
		bits.reverse()
		visible_flags += bits
	visible = [i == 0 for i in visible_flags]
	dat_compstat = list(f.read(344))
	return {
		"visible": visible,
		"state": dat_compstat
	}
