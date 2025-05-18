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
	assert(header["size_header"] == 40)
	assert(f.readUInt16() == 0x1)
	assert(f.readUInt16() == 0x10)
	header["width"] = f.readUInt16()
	header["height"] = f.readUInt16()
	header["delay"] = f.readUInt32()
	header["unknown_0"] = f.readUInt32()
	header["n_frames"] = f.readUInt32()
	header["unknown_1"] = f.readUInt32()
	header["unknown_2"] = f.readUInt16()
	header["palette_unknown_0"] = f.readUInt8()
	header["palette_n_entries"] = f.readUInt8()
	header["palette_offset"] = f.readUInt32()
	header["unknown_3"] = [f.readUInt8() for x in range(6)]
	return header


def _readPalette(f, imgae_header):
	# TODO: replace with Palette.readSinglePalette() ??
	palette = []
	for i in range(imgae_header["palette_n_entries"]):
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
	assert(header["size_header"] == 16)
	header["flags"] = f.readUInt16()
	header["previous_block_size"] = f.readUInt32()
	header["current_block_size"] = f.readUInt32()
	header["next_block_size"] = f.readUInt32()
	return header


def _readFrameHeader(f):
	header = {}
	header["_offset"] = f.pos()

	header["size_header"] = f.readUInt16()
	if header["size_header"] == 0x0:
		return None
	elif header["size_header"] != 24:
		print("Unknown frame header size: {}".format(header["size_header"]))
		#assert(header["size_header"] == 24)
		return None

	header["size"] = f.readUInt32()
	header["unknown_0"] = f.readUInt32()
	assert(header["unknown_0"] == 24)
	header["size_video"] = f.readUInt32()
	header["size_audio"] = f.readUInt32()
	assert(f.readUInt32() == 0x0)
	header["unknown_2"] = f.readUInt16()

	assert(header["_offset"] + header["size_header"] == f.pos())
	return header


def _readFrame(f):
	offset = f.pos()
	frame = _readFrameHeader(f)
	if frame is None:
		return frame
	
	#print(frame)


	size_1 = f.readUInt16()
	data_1 = [f.readUInt8() for x in range(size_1)]
	#data_1 = _readImage(f)
	#size_1 = data_1["size"]
	
	size_pad = -4
	size_2 = 0
	while size_2 == 0:
		size_pad += 4
		size_2 = f.readUInt32()
	#data_2 = [f.readUInt8() for x in range(size_2)]
	data_2 = _readImage(f, size_2)
	
	frame["size_1"] = size_1
	frame["size_2"] = size_2
	frame["size_pad"] = size_pad

	f.setPosition(offset + frame["size"])
	return frame


def _readBlock(f):
	block = _readBlockHeader(f)
	
	"""block_end = block["_offset"] + block["current_block_size"]
	print("    block end", block_end)
	block["frames"] = []
	while f.pos() < block_end:
		
		frame = _readFrame(f)
		if frame is None:
			break

		print("        Frame {}".format(len(block["frames"])))
		print("            end pos    ", f.pos())
		print("            offset+size", frame["_offset"] + frame["size"])
		print(frame)
		
		block["frames"].append(frame)
	
	extra = []
	while f.pos() < block_end:
		extra.append(f.readUInt8())
	block["size_extra"] = len(extra)
	print("    block extra size:", block["size_extra"])"""

	return block



def _readImage(f, size):
	img = {}
	
	#img["_offset"] = f.pos()
	#img["size"] = f.readUInt32()
	img["_offset"] = f.pos() - 4
	img["size"] = size

	img["palette_change"] = f.readUInt16()
	img["motion_vector_table_size"] = f.readUInt16()

	# TODO: this is a guess
	img["motion_vector_table"] = [f.readUInt8() for x in range(img["motion_vector_table_size"])]

	end = img["_offset"] + img["size"]
	#print("end", end)
	while f.pos() < end:
		#print(f.pos())
		op = f.readBitsToInt(3)
		if op == 0:
			pal = f.readBitsToInt(7)
			off = f.readBitsToInt(14)
			flip_horz = False
			flip_vert = False
		elif op == 1:
			pal = f.readBitsToInt(7)
			off = f.readBitsToInt(14)
			flip_horz = True
			flip_vert = False
		elif op == 2:
			pal = f.readBitsToInt(7)
			off = f.readBitsToInt(14)
			flip_horz = False
			flip_vert = True
		elif op == 3:
			pal = f.readBitsToInt(7)
			off = f.readBitsToInt(14)
			flip_horz = True
			flip_vert = True
		elif op == 4:
			run = f.readBitsToInt(5)
		elif op == 5:
			run = f.readBitsToInt(1)
			mvi = f.readBitsToInt(4)
			n = 1 if run == 0 else f.readBitsToInt(8)
		elif op == 6:
			skip = f.readBits(5)
			copy = [f.readUint8() for i in range(16)]
		elif op == 7:
			op2 = f.readBitsToInt(4)
			if op2 >= 0 and op2 <= 7:
				skip = f.readBits(1)
				pal = f.readBitsToInt(7)
				flag = f.readBitsToInt(1)
				off = f.readBitsToInt(16) # TODO: should be 14 or 16?
				# TODO: flipping modes
			elif op2 == 12:
				flag = f.readBitsToInt(1)
				# TODO: not sure which way around the flag works
				if flag:
					n = f.readBitsToInt(8) + 32
				else:
					n = f.readBitsToInt(16) + 288
			elif op2 == 15:
				# TODO: this is a guess how this works
				tile = [f.readUInt8() for i in range(4)]
			else:
				raise ValueError("Unknown op2: {}".format(op2))
		else:
			raise ValueError("Unknown op: {}".format(op))
	#print("done")
	return img
			



def fvf(file_path):
	f = File(file_path)

	data = _readFileHeader(f)
	
	assert(f.pos() == data["offset_image_header"])
	data["image_header"] = _readImageHeader(f)

	assert(f.pos() == data["image_header"]["palette_offset"])
	data["palette"] = _readPalette(f, data["image_header"])

	assert(f.pos() == data["offset_audio_header"])
	data["audio_header"] = _readAudioHeader(f)

	while f.pos() < data["offset_block_0"]:
		assert(f.readUInt8() == 0x0)
	
	data["blocks"] = []
	next = True
	while next:
		#print("Block {}".format(len(data["blocks"])))
		start = f.pos()
		block = _readBlock(f)
		size = block["current_block_size"]
		end = start + size
		next = block["next_block_size"] > 0

		
		#print("    start:", start)
		#print("    size :", size)
		#print("    end  :", end)
		#print("    pos  :", f.pos())

		#assert(f.pos() == end)
		data["blocks"].append(block)
		#n_frames = sum([len(b["frames"]) for b in data["blocks"]])
		#print("Total frames: {}".format(n_frames))
		
		if next:
			f.setPosition(block["_offset"] + block["current_block_size"])
			while f.pos() % 2048:
				assert(f.readUInt8() == 0x0)

	

	return data