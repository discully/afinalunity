from AFU.File import File, fpos
from enum import IntEnum

class TacticType (IntEnum):
	UNKNOWN_0 = 0x0
	UNKNOWN_1 = 0x1
	UNKNOWN_2 = 0x2
	PAGE = 0x3


def _readEntryHeader(f):
	p = f.pos()
	entry_type = TacticType(f.readUInt32())
	entry_unknown = f.readUInt32()
	entry_length = f.readUInt32()
	return {
		"type": entry_type,
		"subtype": entry_unknown,
		"length": entry_length,
		"offset": p,
		"offset_end": f.pos() + entry_length,
	}


def _readPage(f, entry):
	assert(entry["type"] == TacticType.PAGE)
	assert(entry["subtype"] == 31)
	assert(entry["length"] == 88)
	page_unknown = [f.readUInt32() for i in range(2)]
	page_name = f.readString()
	data_length = entry["length"] - 0x8 - (len(page_name) + 1)
	data = [f.readUInt8() for i in range(data_length)]
	return {
		"entry": entry,
		"name": page_name,
		"unknown": page_unknown,
		"data": data,
		"entries": [],
	}


def _readEntry1(f, entry):
	if entry["length"] > 0:
		entry["e1_type"] = f.readUInt32()
		entry["data"] = [f.readUInt8() for i in range(entry["length"] - 4)]
		
	else:
		entry["e1_type"] = 0
		entry["data"] = [f.readUInt8() for i in range(entry["length"] - 4)]
	print("{:>3} {:>3} {}".format(entry["subtype"], entry["e1_type"], entry["length"]))



def bin(file_path):
	f = File(file_path)
	tactics = []
	assert(f.readStringBuffer(7) == "TACTICS")
	while not f.eof():
		p = f.pos()
		entry = _readEntryHeader(f)
		#print(entry)
		if entry["type"] == TacticType.PAGE:
			page = _readPage(f, entry)
			tactics.append(page)
			#print(page["name"])
		elif entry["type"] == TacticType.UNKNOWN_1:
			_readEntry1(f, entry)
			page["entries"].append(entry)
		else:
			entry["data"] = [f.readUInt8() for i in range(entry["length"])]
			page["entries"].append(entry)
		
		assert(f.pos() == entry["offset_end"])
	return tactics
