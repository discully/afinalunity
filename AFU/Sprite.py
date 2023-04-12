from AFU.File import File
from AFU.Image import Image
from AFU import Palette


#	SPRT - appears at start, indicates sprite file
#	LIST - a list of offsets into the sprite, used for JUMP blocks
#	PAUS - pause animation
#	EXIT - pause/exit
#	STAT - switch to static mode
#	TIME - time (wait between frames?)
#	COMP - compressed image data
#	MASK - switch to mask mode
#	POSN - change position of sprite/object?
#	SETF - set flag (0, 1, 2, 3, 4)
#	MARK - store the current position
#	RAND - wait for a random time
#	JUMP - jump to another place in the sprite. Specifies an index into the array of offsets in LIST.
#	SCOM - compressed image data representing speech
#	DIGI - unknown. audio?!
#	SNDW - wait for sound to finish
#	SNDF - unknown. is always 75, 95 or 100. could be volume?
#	PLAY - play sound? or play sprite after sound wait?
#	RPOS - relative position change(?)
#	MPOS - mouth position (relative to parent)
#	SILE - stop+reset sound
#	OBJS - set parent object state
#	RGBP - palette (256*3 bytes, each 0-63)
#	BSON - used only in legaleze.spr


def lst(file_path):
	f = File(file_path)
	n = f.readUInt32()
	entries = []
	while not f.eof():
		entries.append(f.readString())
	assert(n == len(entries))
	return entries


def combine(spr):
	
	# Create a single image
	combined_image = Image(0,0)
	for offset,image in spr["images"].items():
		offset_x = combined_image.width
		offset_y = 0
		combined_width = combined_image.width + image["width"]
		combined_height = max(combined_image.height, image["height"])
		new_combined_image = Image(combined_width, combined_height)
		for x in range(combined_image.width):
			for y in range(combined_image.height):
				new_combined_image.set(combined_image[x][y], x, y)
		for x in range(image["width"]):
			for y in range(image["height"]):
				new_combined_image.set(image["image"][x][y], offset_x + x, offset_y + y)
		combined_image = new_combined_image
		image["offset_x"] = offset_x
		image["offset_y"] = offset_y
		image.pop("image")
	combined_image.name = spr["name"]
	spr["image"] = combined_image
	
	# Put the image info directly into the blocks
	for block in spr["blocks"]:
		if "image_offset" in block:
			block.update(spr["images"][block["image_offset"]])


def sprite(sprite_path, background_path, palette_path=None):
	
	palette_path = Palette.getGlobalPalettePath(sprite_path, palette_path)
	global_palette = Palette.singlePalette(palette_path)
	local_palette = Palette.singlePalette(background_path)
	palette = Palette.combinePalettes(local_palette, global_palette)
	
	f = File(sprite_path)

	spr = {
		"name": sprite_path.name,
		"blocks": [],
		"images": {},
	}

	block = _readBlockHeader(f)
	assert(block["name"] == "SPRT")
	assert(f.readUInt32() == 0x100)
	eof = block["offset"] + block["length"]
	
	block_offsets = []

	while f.pos() < eof:
		block = _readBlockHeader(f)
		
		if block["name"] == "LIST":
			block["entries"] = []
			length = f.readUInt32()
			for i in range(length):
				offset = f.readUInt32()
				block["entries"].append({"offset": block["offset"] + offset})

		elif block["name"] == "SETF":
			block["flag"] = f.readUInt32() # 0, 1, 2, 3 or 4

		elif block["name"] == "POSN":
			block["x"] = f.readUInt32()
			block["y"] = f.readUInt32()

		elif block["name"] == "COMP":
			image = _readImage(f, block, palette)
			offset = image.pop("offset")
			block["image_offset"] = offset
			if image["image"] is not None:
				image["image"].name = _imageName(sprite_path, offset)
				spr["images"][offset] = image

		elif block["name"] == "TIME":
			block["time"] = f.readUInt32()

		elif block["name"] == "MARK":
			pass

		elif block["name"] == "MASK":
			pass

		elif block["name"] == "SCOM":
			image = _readImage(f, block, palette)
			offset = image.pop("offset")
			block["image_offset"] = offset
			if image["image"] is not None:
				image["image"].name = _imageName(sprite_path, offset)
				spr["images"][offset] = image

		elif block["name"] == "RAND":
			rand_extra = f.readUInt32()
			block["min"] = f.readUInt32()
			block["max"] = block["min"] + rand_extra

		elif block["name"] == "JUMP":
			block["index"] = f.readUInt32()

		elif block["name"] == "RPOS":
			block["dx"] = f.readSInt32()
			block["dy"] = f.readSInt32()

		elif block["name"] == "SNDF":
			sound_volume = f.readUInt32() # 75, 95 or 100. volume?
			assert(f.readUInt32() == 0)
			sound_file = str(f.read(16))
			block["volume"] = sound_volume
			block["file"] = sound_file

		elif block["name"] == "MPOS":
			block["x"] = f.readUInt32()
			block["y"] = f.readUInt32()

		elif block["name"] == "PAUS":
			pass

		elif block["name"] == "EXIT":
			pass

		elif block["name"] == "STAT":
			pass

		elif block["name"] == "RGBP":
			palette = Palette.readFullPalette(f)
		
		elif block["name"] == "DIGI":
			block["data"] = f.read(block["length"] - 8)
		
		elif block["name"] == "SNDW":
			pass
			
		elif block["name"] == "PLAY":
			pass

		else:
			raise ValueError("Unknown block {} at {:#x}".format(block["name"], block["offset"]))
		
		block_offsets.append(block["offset"])
		block.pop("length") # we don't need this any more
		spr["blocks"].append(block)
	
	for block in spr["blocks"]:
		if block["name"] == "LIST":
			for entry in block["entries"]:
				entry["index"] = block_offsets.index(entry["offset"])

	return spr


def _imageName(sprite_path, image_offset):
	return "{}.{}{}".format(sprite_path.stem, image_offset, sprite_path.suffix)


def _readBlockHeader(f):
	offset = f.pos()
	name = "".join(reversed([chr(c) for c in f.read(4)]))
	length = f.readUInt32()
	return {
		"offset": offset,
		"name": name,
		"length": length
	}


def _readImage(f, block, palette):
	image_width = f.readUInt32()
	image_height = f.readUInt32()
	image_encoding = f.readUInt16()
	image_type = f.readUInt16()

	if image_type == 0x3:
		offset = f.readUInt32()
		image_offset = block["offset"] - offset
		image_image = None
	else:
		image_offset = block["offset"]

		if image_encoding == 0xd:
			if image_type == 0x1:
				image_image =_readImage1(f, image_width, image_height, palette)
			elif image_type == 0x2:
				image_image = _readImage2(f, image_width, image_height, palette)
			else:
				raise ValueError("Unknown image type {:#x}".format(image_type))
		else:
			raise ValueError("Unknown image encoding {:#x}".format(image_encoding))

	return {
		"offset": image_offset,
		"width": image_width,
		"height": image_height,
		"encoding": image_encoding,
		"type": image_type,
		"image": image_image,
	}


def _setPixel(image, pixel, colour):
	image.set(colour, pixel)
	return pixel + 1


def _setNPixels(image, pixel, n, colour):
	for i in range(n):
		pixel = _setPixel(image, pixel, colour)
	return pixel


def _readImage1(f, width, height, palette):
	f.clearBits()

	image = Image(width, height)
	n_pixels = len(image)
	curr_pixel = 0
	colour = 0

	while curr_pixel < n_pixels:
		if f.readBitsToInt(1) == 0:
			# bit 0 set: single pixel, 3 bit colour offset
			offset = f.readBitsToInt(3)
			if (offset & 0x4) == 0:
				colour = colour + 1 + offset
			else:
				colour = colour - 1 - (offset & 0x3)
			curr_pixel = _setPixel(image, curr_pixel, palette[colour])

		elif f.readBitsToInt(1) == 0:
			# bit 1 set: 2 bit colour offset, 3 bit length (+1)
			offset = f.readBitsToInt(2)
			length = f.readBitsToInt(3) + 1
			if (offset & 0x2) == 0:
				colour = colour + 1 + offset
			else:
				colour = colour + 1 - offset
			curr_pixel = _setNPixels(image, curr_pixel, length, palette[colour])

		elif f.readBitsToInt(1) == 0:
			# bit 2 set: 7 bit colour (+128 for global palette), 1 bit length (+1)
			colour = f.readBitsToInt(7) + 128
			length = f.readBitsToInt(1) + 1
			curr_pixel = _setNPixels(image, curr_pixel, length, palette[colour])

		elif f.readBitsToInt(1) == 0:
			# bit 3 set: 5 bit length (+1), use previous colour
			length = f.readBitsToInt(5) + 1
			# curr_pixel = _setNPixels(image, curr_pixel, length, palette[colour]) # I've changed this to blank to make picard.spr work
			curr_pixel = _setNPixels(image, curr_pixel, length, image.blank)         # I've changed this to blank to make picard.spr work

		elif f.readBitsToInt(1) == 0:
			# bit 4 set: 7 bit colour (+128 for global palette), 4 bit length (+1)
			colour = f.readBitsToInt(7) + 128
			length = f.readBitsToInt(4) + 1
			curr_pixel = _setNPixels(image, curr_pixel, length, palette[colour])

		elif f.readBitsToInt(1) == 0:
			# bit 5 set: 8 bit colour, 8 bit length
			colour = f.readBitsToInt(8)
			length = f.readBitsToInt(8) + 1
			curr_pixel = _setNPixels(image, curr_pixel, length, palette[colour])

		else:
			# otherwise: do a pixel run of blank(?) for a whole width, then drop 1 bit
			curr_pixel = _setNPixels(image, curr_pixel, image.width, image.blank)
			f.readBitsToInt(1)  # probably always 1?

	return image


def _readImage2(f, width, height, palette):
	f.clearBits()

	image = Image(width, height)
	n_pixels = len(image)
	curr_pixel = 0

	while curr_pixel < n_pixels:

		draw_command = f.readBits(2)

		if draw_command == [0, 0]:
			# the next 8 bits are a number n, run of (n + 1) blank(?) pixels
			n = f.readBitsToInt(8)
			curr_pixel = _setNPixels(image, curr_pixel, n + 1, image.blank)
		elif draw_command == [0, 1]:
			# the next 8 bits represent data for a single pixel
			palette_index = f.readBitsToInt(8)
			curr_pixel = _setPixel(image, curr_pixel, palette[palette_index])
		elif draw_command == [1, 0]:
			# 8 bits pixel data, followed by 3 bits n, run of (n + 1) of those pixels
			palette_index = f.readBitsToInt(8)
			n = f.readBitsToInt(3)
			curr_pixel = _setNPixels(image, curr_pixel, n + 1, palette[palette_index])
		elif draw_command == [1, 1]:
			# 8 bits pixel data, followed by 8 bits n, run of (n + 1) of those pixels
			palette_index = f.readBitsToInt(8)
			n = f.readBitsToInt(8)
			curr_pixel = _setNPixels(image, curr_pixel, n + 1, palette[palette_index])
		else:
			# this isn't possible
			raise ValueError("SpriteImage2 encountered unknown draw command {0:#x}".format(draw_command))

	return image
