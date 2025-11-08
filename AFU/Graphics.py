from AFU.File import File
from AFU.Image import Image
from PIL import Image as PIL_Image



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


def dmg(file_path):
	"""Read a .dmg Damage Material file"""
	from pathlib import Path
	f = File(file_path)

	d = {}
	d["data_size"] = f.readUInt32()
	d["n_entries"] = f.readUInt32()
	assert(f.readUInt16() == 110)
	d["txt_file"] = f.readStringBuffer(20) # Gets ignored and does not exist in the zip, so probably a dev file.
	assert(f.pos() == 30)

	assert(d["data_size"] == f.size() - 30)
	assert(d["n_entries"] * 36 == d["data_size"])

	d["entries"] = []
	for i in range(d["n_entries"]):
		entry = {}
		entry["unknown0"] = f.readUInt32() # junk, gets ignored
		assert(f.readUInt32() == 0)
		entry["type"] = f.readUInt32()
		# Usually set to 1, but two ships have an entry set to 3.
		# In these cases, the file name is partically nulled out.
		# Perhaps no damaged version of that texture?
		assert(entry["type"] in (1,3))
		assert(f.readUInt32() == 0)
		entry["img_file"] = f.readStringBuffer(13)
		for i in range(7):
			assert(f.readUInt8() == 0x3d)
		d["entries"].append(entry)	
	
	return d


#
# IMG Files
#


def imgPil(file_path):
	return PIL_Image.open(file_path, "r", "GIF")


def img(file_path):
	gif = imgPil(file_path)
	img = Image(gif.width, gif.height)
	for x in range(gif.width):
		for y in range(gif.height):
			img.set(gif.getpixel((x,y)), x, y)
	return {
		"width": gif.width,
		"height": gif.height,
		"image": img,
	}
	

#
# LBM Files
#

def _lbmReadChunk(f, compressed):
	chunk_type = f.readStringBuffer(4)
	chunk_size = f.readUInt32BE()
	chunk_start = f.pos()
	chunk = {
		"type": chunk_type,
		"size": chunk_size,
	}
	
	if chunk_type == "BMHD":
		chunk["data"] = _lbmReadChunkBMHD(f)
	elif chunk_type == "CMAP":
		chunk["data"] = _lbmReadChunkCMAP(f, chunk_size)
	elif chunk_type == "BODY":
		chunk["data"] = _lbmReadChunkBODY(f, chunk_size, compressed)
	elif chunk_type == "DPPS":
		chunk["data"] = _lbmReadChunkDPPS(f, chunk_size)
	elif chunk_type == "CRNG":
		chunk["data"] = _lbmReadChunkCRNG(f)
	elif chunk_type == "TINY":
		chunk["data"] = _lbmReadChunkTINY(f, chunk_size, compressed)
	else:
		raise ValueError("Unknown chunk type: {0}".format(chunk_type))
	assert(f.pos() == chunk_start + chunk_size)
	return chunk


def _lbmReadChunkBMHD(f):
	data = {}
	data["width"] = f.readUInt16BE()
	data["height"] = f.readUInt16BE()
	data["x_origin"] = f.readUInt16BE()
	data["y_origin"] = f.readUInt16BE()
	data["n_planes"] = f.readUInt8()
	data["masking"] = f.readUInt8()
	data["compression"] = f.readUInt8()
	data["pad1"] = f.readUInt8()
	data["transparent_color"] = f.readUInt16BE()
	data["x_aspect"] = f.readUInt8()
	data["y_aspect"] = f.readUInt8()
	data["page_width"] = f.readUInt16BE()
	data["page_height"] = f.readUInt16BE()
	return data


def _lbmReadChunkCMAP(f, chunk_size):
	end = f.pos() + chunk_size
	data = []
	while f.pos() < end:
		data.append( [f.readUInt8() for i in range(3)] )
	return data


def _lbmReadChunkBODY(f, chunk_size, compressed):
	end = f.pos() + chunk_size
	data = []
	if compressed:
		while f.pos() < end:
			n = f.readUInt8()
			if n < 128:
				data += [f.readUInt8() for i in range(n+1)]
			elif n > 128:
				data += [f.readUInt8()] * (257 - n)
			# 128 is no-op
	else:
		data = [f.readUInt8() for i in range(chunk_size)]
	return data


def _lbmReadChunkTINY(f, chunk_size, compressed):
	end = f.pos() + chunk_size
	data = {}
	data["width"] = f.readUInt16BE()
	data["height"] = f.readUInt16BE()
	data["body"] = _lbmReadChunkBODY(f, chunk_size - 4, compressed)
	assert(f.pos() == end)
	return data


def _lbmReadChunkCRNG(f):
	assert(f.readUInt16BE() == 0)
	data = {}
	data["rate"] = f.readUInt16BE()
	data["flags"] = f.readUInt16BE()
	data["low"] = f.readUInt8()
	data["high"] = f.readUInt8()
	return data


def _lbmReadChunkDPPS(f, chunk_size):
	# DPPS chunks are not documented anywhere that I can find. Best guess seems to be that they are
	# application settings to restore the state of the editor to where it was when you last edited it.
	# So we can ignore it.
	end = f.pos() + chunk_size
	data = [f.readUInt8() for i in range(chunk_size)]
	return data


def lbm(file_path):
	f = File(file_path)

	# Read the IFF header
	assert(f.readStringBuffer(4) == "FORM")
	data_size = f.readUInt32BE()
	assert(data_size == f.size() - 8)
	file_type = f.readStringBuffer(4)
	assert(file_type == "PBM ")

	# Read the PBM data
	compressed = False
	chunks = {}
	while not f.eof():
		chunk = _lbmReadChunk(f, compressed)
		chunk_type = chunk["type"]
		if chunk_type == "CRNG":
			if not chunk_type in chunks:
				chunks[chunk_type] = []
			chunks[chunk_type].append(chunk["data"])
		else:
			assert(not chunk_type in chunks)
			chunks[chunk_type] = chunk["data"]
		
		if chunk_type == "BMHD":
			if chunk["data"]["compression"] == 1:
				compressed = True

	# Create the image
	# TODO: Create animated GIF when there are CRNG bhunks
	img = Image(chunks["BMHD"]["width"], chunks["BMHD"]["height"])
	for i,px in enumerate(chunks["BODY"]):
		img.set(chunks["CMAP"][px], i)
	chunks["image"] = img
	
	if "TINY" in chunks:
		img = Image(chunks["TINY"]["width"], chunks["TINY"]["height"])
		for i,px in enumerate(chunks["BODY"]):
			img.set(chunks["CMAP"][px], i)
		chunks["TINY"]["image"] = img

	return chunks
