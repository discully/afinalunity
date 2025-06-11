from AFU.File import File


def _readFileHeader(f):
	header = {}
	header["_size"] = f.size()
	header["_offset_header"] = f.pos()
	assert(f.readStringBuffer(4) == "FVF ")
	header["unknown_0"] = [f.readUInt32() for x in range(3)]
	header["offset_block_0"] = f.readUInt32()
	header["offset_block_n"] = f.readUInt32()
	header["offset_image_header"] = f.readUInt32()
	header["offset_audio_header"] = f.readUInt32()
	header["unknown_1"] = [f.readUInt8() for x in range(64)]
	return header


def _readImageHeader(f):
	header = {}
	header["_offset"] = f.pos()
	header["size_header"] = f.readUInt16()
	assert(header["size_header"] == 0x28)
	header["unknown_0"] = f.readUInt16()
	assert(header["unknown_0"] == 0x1)
	header["unknown_1"] = f.readUInt16()
	assert(header["unknown_1"] == 0x10)
	header["width"] = f.readUInt16()
	header["height"] = f.readUInt16()
	header["delay"] = f.readUInt32()
	header["unknown_2"] = f.readUInt32()
	header["n_frames"] = f.readUInt32()
	header["unknown_3"] = f.readUInt32()
	header["unknown_4"] = f.readUInt16()
	header["palette_unknown_0"] = f.readUInt8()
	header["palette_n_entries"] = f.readUInt8()
	header["palette_offset"] = f.readUInt32()
	header["unknown_5"] = [f.readUInt8() for x in range(2)]
	assert(f.readUInt32() == 0x0)
	return header


def _readPalette(f, n_entries):
	palette = []
	for i in range(n_entries):
		r = f.readUInt8() * 4
		g = f.readUInt8() * 4
		b = f.readUInt8() * 4
		palette.append((r, g, b))
	return palette


def _readAudioHeader(f):
	header = {}
	header["_offset"] = f.pos()
	header["compression"] = f.readUInt16()
	header["n_channels"] = f.readUInt16()
	header["bits_per_sample"] = f.readUInt16()
	header["sample_rate"] = f.readUInt32()
	header["unknown_0"] = [f.readUInt8() for x in range(8)]
	return header


def _readBlockHeader(f):
	header = {}
	header["_offset"] = f.pos()
	header["size_header"] = f.readUInt16()
	assert(header["size_header"] == 0x10)
	header["n_frames"] = f.readUInt16()
	header["size_previous_block"] = f.readUInt32()
	header["size_current_block"] = f.readUInt32()
	header["size_next_block"] = f.readUInt32()
	return header


def _readFrameHeader(f):
	header = {}
	header["_offset"] = f.pos()

	header["size_header"] = f.readUInt16()
	assert(header["size_header"] == 24)
	header["size"] = f.readUInt32()
	header["unknown_0"] = f.readUInt32()
	assert(header["unknown_0"] == 24)
	header["size_audio"] = f.readUInt32()
	header["size_video"] = f.readUInt32()
	header["_size_extra"] = header["size"] - header["size_header"] - header["size_audio"] - header["size_video"]
	assert(f.readUInt32() == 0x0)
	header["unknown_2"] = [f.readUInt8() for x in range(2)]

	assert(header["_offset"] + header["size_header"] == f.pos())
	return header


def _readBlock(f):
	block = _readBlockHeader(f)

	block_end = block["_offset"] + block["size_current_block"]
	block["frames"] = []

	for i in range(block["n_frames"]):
		#print("    Frame", i, "    ", f.pos())

		frame = _readFrameHeader(f)

		# Skip the data until we know how to read it
		f.setPosition(frame["_offset"] + frame["size"])

		block["frames"].append(frame)

	unknown_extra = []
	while f.pos() < block_end:
		unknown_extra.append(f.readUInt8())
	block["_unknown_extra_size"] = len(unknown_extra)

	return block


def fvf(file_path):
	f = File(file_path)

	data = _readFileHeader(f)
	
	assert(f.pos() == data["offset_image_header"])
	data["image_header"] = _readImageHeader(f)

	assert(f.pos() == data["image_header"]["palette_offset"])
	data["palette"] = _readPalette(f, data["image_header"]["palette_n_entries"])

	assert(f.pos() == data["offset_audio_header"])
	data["audio_header"] = _readAudioHeader(f)

	while f.pos() < data["offset_block_0"]:
		assert(f.readUInt8() == 0x0)

	data["blocks"] = []

	next = True
	while next:
		offset = f.pos()
		#print("Block", len(data["blocks"]), "        ", offset)

		block = _readBlock(f)

		assert(f.pos() == offset + block["size_current_block"])

		data["blocks"].append(block)

		next = block["size_next_block"] > 0

	assert(f.eof())

	return data