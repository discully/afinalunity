from AFU.File import File


_PALETTE_FRAME_COUNT = 112
_MICROSECONDS_PER_FRAME = 66666 # 15fps


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
	header["bpp"] = f.readUInt16()
	assert(header["bpp"] == 0x10)
	header["width"] = f.readUInt16()
	header["height"] = f.readUInt16()
	header["micros_per_frame"] = f.readUInt32() # microseconds per frame = 66666 = 15fps
	assert(header["micros_per_frame"] == _MICROSECONDS_PER_FRAME)
	assert(f.readUInt32() == 0x0)
	header["n_frames"] = f.readUInt32()
	assert(f.readUInt32() == 0x0)
	header["unknown_4"] = f.readUInt16()
	assert(header["unknown_4"] == 0x18)
	header["palette_frame_count"] = f.readUInt8() # palette_entry_count (always 112?)
	assert(header["palette_frame_count"] == _PALETTE_FRAME_COUNT)
	header["palette_header_count"] = f.readUInt8() # header palette count (always 15?)
	header["palette_offset"] = f.readUInt32() # header palette offset
	header["unknown_5"] = [f.readUInt8() for x in range(2)]
	assert(f.readUInt32() == 0x0)
	assert(f.pos() == header["_offset"] + header["size_header"])
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

	assert(f.readUInt16() == 0x0)
	header["compression"] = f.readUInt16()
	header["n_channels"] = f.readUInt16()
	header["bits_per_sample"] = f.readUInt16()
	header["sample_rate"] = f.readUInt16()
	assert(f.readUInt16() == 0x0)
	assert(f.readUInt16() == 0x0)
	assert(f.readUInt16() == 0x0)
	header["unknown_0"] = f.readUInt16()

	assert(header["compression"] == 0x1)
	assert(header["n_channels"] == 0x1)
	assert(header["bits_per_sample"] == 0x8)
	assert(header["sample_rate"] == 22050)
	assert(header["unknown_0"] == 0x2)

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
	assert(header["size_header"] == 0x18)
	header["size"] = f.readUInt32()
	header["offset_image"] = f.readUInt32()
	header["offset_palette"] = f.readUInt32()
	header["offset_audio"] = f.readUInt32()
	assert(f.readUInt32() == 0x0)
	header["unknown_2"] = [f.readUInt8() for x in range(2)]

	assert(header["_offset"] + header["size_header"] == f.pos())
	return header


def _readFrameImageHeader(f):
	header = {}
	header["_offset"] = f.pos()
	assert(f.readUInt16() == 0x0)
	header["flags"] = f.readUInt16()
	assert(header["flags"] & 0x8 == 0)
	assert(header["flags"] in (0x0, 0x5, 0x4))
	header["motion_vector_table_size"] = f.readUInt16()
	assert(header["motion_vector_table_size"] in (0, 16))
	header["motion_vector_table"] = [f.readUInt16() for x in range(header["motion_vector_table_size"])]
	return header


def _readFrameImage(f, image):
	image["_offset_data"] = f.pos()
	image["data"] = [f.readUInt8() for i in range(image["size_data"])]



def _readFrame(f, i_block, i_frame):
	frame = {}
	# TODO: This is termporary to aid development. Remove later.
	frame["_index"] = "{:02}_{:02}".format(i_block, i_frame)

	frame |= _readFrameHeader(f)
	
	if frame["offset_image"] != 0:
		assert(f.pos() == frame["_offset"] + frame["offset_image"])
		image_size = f.readUInt16()
		frame["image"] = _readFrameImageHeader(f)
		if frame["image"]["flags"] & 0x1:
			assert(i_block == 0 and i_frame == 0)
		
		image_data_size = image_size - 6 - ( frame["image"]["motion_vector_table_size"] * 2)

		frame["image"]["size_data"] = image_data_size
		_readFrameImage(f, frame["image"])

	if frame["offset_palette"] != 0:
		assert(f.pos() == frame["_offset"] + frame["offset_palette"])
		# TODO: use _readPalette
		size_palette = _PALETTE_FRAME_COUNT * 3
		frame["palette"] = [ [f.readUInt8() for i in range(3)] for j in range(_PALETTE_FRAME_COUNT)]
	
	if frame["offset_audio"] != 0:
		assert(f.pos() == frame["_offset"] + frame["offset_audio"])
		audio_size = f.readUInt32()
		frame["audio"] = [f.readUInt8() for i in range(audio_size)]
	
	assert(f.pos() == frame["_offset"] + frame["size"])

	return frame


def _readBlock(f, i_block):
	block = _readBlockHeader(f)

	block_end = block["_offset"] + block["size_current_block"]
	block["frames"] = []

	for i in range(block["n_frames"]):

		frame = _readFrame(f, i_block, i)
		assert(f.pos() == frame["_offset"] + frame["size"])

		block["frames"].append(frame)

	unknown_extra = []
	while f.pos() < block_end:
		unknown_extra.append(f.readUInt8())
	block["_unknown_extra_size"] = len(unknown_extra)

	return block


def fvf(file_path):
	f = File(file_path)

	video = _readFileHeader(f)
	
	assert(f.pos() == video["offset_image_header"])
	video["image_header"] = _readImageHeader(f)

	assert(f.pos() == video["image_header"]["palette_offset"])
	video["palette"] = _readPalette(f, video["image_header"]["palette_header_count"])

	assert(f.pos() == video["offset_audio_header"])
	video["audio_header"] = _readAudioHeader(f)

	while f.pos() < video["offset_block_0"]:
		assert(f.readUInt8() == 0x0)

	video["blocks"] = []

	next = True
	while next:
		offset = f.pos()
		block = _readBlock(f, len(video["blocks"]))
		assert(f.pos() == offset + block["size_current_block"])
		video["blocks"].append(block)
		next = block["size_next_block"] > 0

	assert(f.eof())


	

	return video
