from AFU.File import File



def mtl(file_path):
	f = File(file_path)
	m = {}
	m["data_size"] = f.readUInt32()
	m["n_entries"] = f.readUInt32()
	assert(m["data_size"] == m["n_entries"] * 36)
	format = f.readUInt16()
	assert(format == 110)
	m["format"] = format * 0.01
	[f.readUInt8() for i in range(20)] # junk bytes
	assert(f.pos() == 0x1e)
	m["entries"] = []
	for i in range(m["n_entries"]):
		entry = {}
		entry["unknown1"] =[f.readUInt32() for i in range(4)]
		entry["texture"] = f.readStringBuffer(11)
		entry["unknown3"] = [f.readUInt8() for i in range(9)]
		m["entries"].append(entry)
	assert(f.eof())
	return m
