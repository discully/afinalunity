from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
from AFU.File import File
from AFU.Image import Image
from AFU.Palette import Palette, FullPalette


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
#	MARK - TODO: store info
#	RAND - wait for a random time
#	JUMP - Jump to another place in the sprite. Specifies an index into the array of offsets in LIST.
#	SCOM - compressed image data representing speech
#	DIGI - audio?! :(
#	SNDW - wait for sound to finish
#	SNDF - TODO: unknown is always 75, 95 or 100. volume?
#	PLAY -
#	RPOS - relative position change(?)
#	MPOS - mouth position (relative to parent)
#	SILE - stop+reset sound
#	OBJS - set parent object state
#	RGBP - palette (256*3 bytes, each 0-63)
#	BSON - used only in legaleze.spr


def sprite(sprite_path, background_path, palette_path=None):
	f = File(sprite_path)

	if palette_path is None:
		palette_path = sprite_path.with_name("standard.pal")

	p = FullPalette()
	p.setGlobalPalette(Palette(File(palette_path)))
	p.setLocalPalette(Palette(File(background_path)))

	s = {
		"blocks": OrderedDict(),
		"images": {},
	}

	block = _readBlockHeader(f)
	assert(block["name"] == "SPRT")
	assert(f.readUInt32() == 0x100)
	eof = block["start"] + block["length"]

	while f.pos() < eof:
		block = _readBlockHeader(f)

		if block["name"] == "LIST":
			block["offsets"] = []
			length = f.readUInt32()
			for i in range(length):
				offset = f.readUInt32()
				block["offsets"].append(block["start"] + offset)

		elif block["name"] == "SETF":
			block["flag"] = f.readUInt32() # 0, 1, 2, 3 or 4

		elif block["name"] == "POSN":
			x = f.readUInt32()
			y = f.readUInt32()
			block["data"] = {
				"x": x,
				"y": y,
			}

		elif block["name"] == "COMP":
			image = _readImage(f, block, p)
			offset = image.pop("offset")
			block["offset"] = offset
			if image["image"] is not None:
				s["images"][offset] = image

		elif block["name"] == "TIME":
			block["time"] = f.readUInt32()

		elif block["name"] == "MARK":
			pass

		elif block["name"] == "MASK":
			pass

		elif block["name"] == "SCOM":
			image = _readImage(f, block, p)
			offset = image.pop("offset")
			block["offset"] = offset
			if image["image"] is not None:
				s["images"][offset] = image

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
			p.setLocalPalette(Palette(f))
			p.setGlobalPalette(Palette(f))

		else:
			raise ValueError("Unknown block {} at {:#x}".format(block["name"], block["start"]))

		offset = block.pop("start")
		block.pop("length")
		s["blocks"][offset] = block

	return s


def _readBlockHeader(f):
	start = f.pos()
	name = "".join(reversed([chr(c) for c in f.read(4)]))
	length = f.readUInt32()
	return {
		"start": start,
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
		image_offset = block["start"] - offset
		image_image = None
	else:
		image_offset = block["start"]

		if image_encoding == 0xd:
			if image_type == 0x1:
				image_image =_readImage1(f, image_width, image_height, palette)
			elif image_type == 0x2:
				image_image = _readImage2(f, image_width, image_height, palette)
			else:
				raise ValueError("Unknown image type {:#x}".format(image_type))
		else:
			raise ValueError("Unknown image encoding {:#x}".format(encoding))

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
			if ((offset & 0x2) == 0):
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
	colour = 0

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
