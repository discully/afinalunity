from AFU.File import DatabaseFile,File
from AFU.Image import Image
from PIL import Image as PIL_Image



def material(file_path):
	"""Reads .mtl, .mtr, .dmg material files."""
	f = File(file_path)

	m = {}
	m["_data_size"] = f.readUInt32()
	m["n_entries"] = f.readUInt32()
	assert(m["_data_size"] == m["n_entries"] * 36)
	format = f.readUInt16()
	assert(format == 110)
	m["format"] = "1.10"

	m["txt_file"] = f.readStringBuffer(20) # Gets ignored and does not exist in the zip, so probably a dev file.
	assert(f.pos() == 0x1e)

	m["entries"] = []
	for i in range(m["n_entries"]):

		# All this data gets ignored, except for the "img_file" name.
		# The type of texture is inferred from the "img_file" extension, not the "type" field.
		# The "type" field is:
		#     1    - .IMG
		#     2    - .LBM (except STATW.IMG in station.mtl - probably a mistype)
		#     3    - no file (only in .mtr files)
		#     2561 - .img files, and only in *x.mtl files which are for testing. So type 1 with some flag???

		entry = {}
		entry["unknown_0"] = f.readUInt32() # Junk
		entry["unknown_1"] = f.readUInt32() # Always 0x0, except in shield_*.mtl.
		entry["type"] = f.readUInt32()
		assert(entry["type"] in (1,2,3,2561))
		assert(f.readUInt32() == 0)
		entry["img_file"] = f.readStringBuffer(13)
		entry["obj_name"] = f.readStringBuffer(7)

		m["entries"].append(entry)
	
	return m



#
# IMG Files
#


def imgPil(file_path):
	return PIL_Image.open(file_path, "r", ("GIF",))


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
	# TODO: Create animated GIF when there are CRNG chunks
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



#
# 3D Files
#


def _modelReadHeader(f):
	header_size = 0x1e
	assert(f.pos() == 0x0)
	header = {}
	header["_data_size"] = f.readUInt32()
	assert(f.size() == header["_data_size"] + header_size)
	fmt = f.readUInt16()
	assert(fmt == 110)
	header["format"] = "1.10"
	header["max_vertices_per_mesh"] = f.readUInt16()
	assert(header["max_vertices_per_mesh"] <= 5000)
	header["max_faces_per_mesh"] = f.readUInt16()
	assert(header["max_faces_per_mesh"] <= 5000)
	header["name"] = f.readString()

	header["_unused"] = []
	while f.pos() < header_size:
		header["_unused"].append(f.readUInt8())

	assert(f.pos() == header_size)
	return header



def _modelReadMesh(f):
	import math
	mesh = {}
	n = f.readSInt32()
	mesh["vertices_flag"] = n < 0
	mesh["vertices_n"] = abs(n)
	mesh["faces_n"] = f.readUInt32()
	assert(f.readUInt32() == 2)
	
	mesh["_vertices_offset"] = f.readUInt32()
	mesh["_uvs_offset"] = f.readUInt32()
	assert(f.readUInt32() == 0)
	assert(f.readUInt32() == 0)
	mesh["_faces_offset"] = f.readUInt32()
	mesh["_vertices_normals_offset"] = f.readUInt32()
	mesh["_faces_normals_offset"] = f.readUInt32()
	mesh["_faces_distances_offset"] = f.readUInt32()

	p = f.pos()
	
	f.setOffset(mesh["_vertices_offset"])
	mesh["vertices"] = [ (f.readFloat(),f.readFloat(),f.readFloat()) for j in range(abs(mesh["vertices_n"]))]

	if mesh["_uvs_offset"] > 0:
		assert(f.offset() == mesh["_uvs_offset"])
		mesh["uvs"] = [ (f.readUInt32(),f.readUInt32()) for j in range(abs(mesh["vertices_n"]))]
	
	if mesh["_faces_offset"] > 0:
		assert(f.offset() == mesh["_faces_offset"])
		mesh["faces"] = []
		for i in range(mesh["faces_n"]):
			face = {}
			x = f.readUInt16()
			face["material"] = x & 0x7fff
			face["flag"] = (x & 0x8000) != 0
			face["vertices"] = (f.readUInt16(), f.readUInt16(), f.readUInt16())
			mesh["faces"].append(face)
	
	if mesh["_vertices_normals_offset"] > 0:
		assert(f.offset() == mesh["_vertices_normals_offset"])
		mesh["vertices_normals"] = [ (f.readFloat(),f.readFloat(),f.readFloat()) for j in range(abs(mesh["vertices_n"]))]

	if mesh["_faces_normals_offset"] > 0:
		assert(f.offset() == mesh["_faces_normals_offset"])
		mesh["faces_normals"] = [ [f.readFloat() for k in range(3)] for j in range(mesh["faces_n"])]

	if mesh["_faces_distances_offset"] > 0:
		assert(f.offset() == mesh["_faces_distances_offset"])
		mesh["faces_distances"] = [ f.readFloat() for j in range(mesh["faces_n"])]

	f.setPosition(p)
	return mesh


def model(file_name):
	"""Reads .3dv .3dr and .pc* 3D model files."""
	f = DatabaseFile(file_name)

	pcn = {}
	pcn["header"] = _modelReadHeader(f)

	data_start = f.pos()
	pcn["_data_offset_base"] = data_start
	f.setOffsetBase(data_start)

	model = {}
	assert(f.readUInt32() == 0)
	model["meshes_n"] = f.readUInt32()
	model["_meshes_offset"] = f.readUInt32()
	assert(f.readUInt32() == 0) # stores a pointer to the material when loaded
	model["size"] = [f.readFloat() for i in range(3)]
	model["centre"] = [f.readFloat() for i in range(3)]
	off = f.readUInt32()
	assert(f.offset() == off)
	pcn["model"] = model

	while f.offset() < model["_meshes_offset"]:
		assert(f.readUInt8() == 0) # padding
	
	pcn["meshes"] = []
	for i in range(model["meshes_n"]):
		pcn["meshes"].append(_modelReadMesh(f))

	return pcn
