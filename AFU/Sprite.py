from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
from AFU.File import File
from AFU.Image import Image
from AFU.Palette import Palette, FullPalette


blocks = [
	"SPRT", # appears at start, indicates sprite file
	"LIST",
	"PAUS", # pause animation
	"EXIT", # pause/exit
	"STAT", # switch to static mode
	"TIME", # time (wait between frames?)
	"COMP", # compressed image data
	"MASK", # switch to mask mode
	"POSN", # change position of sprite/object?
	"SETF", # set flag (0, 1, 2, 3, 4)
	"MARK", # TODO: store info
	"RAND", # wait for a random time
	"JUMP", # a jump to an animation
	"SCOM", # compressed image data representing speech
	"DIGI", # audio?! :(
	"SNDW", # wait for sound to finish
	"SNDF", # TODO: unknown is always 75, 95 or 100. volume?
	"PLAY",
	"RPOS", # relative position change(?)
	"MPOS", # mouth position (relative to parent)
	"SILE", # stop+reset sound
	"OBJS", # set parent object state
	"RGBP", # palette (256*3 bytes, each 0-63)
	"BSON", # used only in legaleze.spr
]


def _printBlock(block):
	s = "[{:>6}] {} ".format(block["start"], block["name"])
	if block["name"] == "LIST":
		s += str(block["list"])
	if block["name"] == "SETF":
		s += str(block["flag"])
	if block["name"] == "POSN":
		s += str(block["pos"])
	if block["name"] == "JUMP":
		s += str(block["index"])
	if block["name"] in ["COMP", "SCOM"]:
		s += str(block["image"])
	if block["name"] == "SNDF":
		s += block["file"]
	return s



class Sprite:
	
	def __init__(self, palette):
		self.images = {}
		self.blocks = OrderedDict()
		self.palette = palette
	
	
	def __str__(self):
		s = "Sprite\n"
		s += "\tImages: {}\n".format(sorted(self.images.keys()))
		for block in self.blocks.values():
			s += "\t" + _printBlock(block) + "\n"
		return s



def read(sprite_path, background_path):
	f = File(sprite_path)
	p = FullPalette()
	p.setGlobalPalette(Palette(File(sprite_path.with_name("standard.pal"))))
	p.setLocalPalette(Palette(File(background_path)))
	s = Sprite(p)
	end = 0
	while True:
		block = _readBlock(f, s)
		s.blocks[block["start"]] = block
		if block["name"] == "SPRT":
			end = block["start"] + block["length"]
		if f.pos() == end:
			break
	return s


def _readBlock(f, s):
	start = f.pos()
	name = "".join(reversed([chr(c) for c in f.read(4)]))
	
	length = f.readUInt32()
	end = start + length
	
	block = {
		"start": start,
		"name": name,
		"length": length
	}
	
	if name == "SPRT":
		assert (f.readUInt32() == 0x100)
	elif name == "LIST":
		block["list"] = []
		length = f.readUInt32()
		for i in range(length):
			offset = f.readUInt32()
			block["list"].append(block["start"] + offset)
	elif name == "SETF":
		block["flag"] = f.readUInt32() # 0, 1, 2, 3 or 4
		assert (block["flag"] <= 4)
	elif name == "POSN":
		x = f.readUInt32()
		y = f.readUInt32()
		block["pos"] = (x,y)
	elif name == "COMP":
		_readImage(f, block, s)
	elif name == "TIME":
		block["time"] = f.readUInt32()
	elif name == "MARK":
		pass
	elif name == "MASK":
		pass
	elif name == "SCOM":
		_readImage(f, block, s)
	elif name == "RAND":
		extra = f.readUInt32()
		block["min"] = f.readUInt32()
		block["max"] = block["min"] + extra
	elif name == "JUMP":
		block["index"] = f.readUInt32()
	elif name == "RPOS":
		dx = f.readSInt32()
		dy = f.readSInt32()
		block["delta"] = (dx,dy)
	elif name == "SNDF":
		block["volume"] = f.readUInt32() # 75, 95 or 100. volume?
		unknown = f.readUInt32() # empty
		assert(unknown == 0)
		block["file"] = str(f.read(16))
	elif name == "MPOS":
		x = f.readUInt32()
		y = f.readUInt32()
		block["pos"] = (x,y)
	elif name == "PAUS":
		pass
	elif name == "EXIT":
		pass
	elif name == "STAT":
		pass
	elif name == "RGBP":
		s.palette.setLocalPalette(Palette(f))
	else:
		raise ValueError("Unknown block {} at {:#x}".format(name, start))
	
	return block


def _readImage(f, block, s):
	width = f.readUInt32()
	height = f.readUInt32()
	block["size"] = (width,height)
	encoding = f.readUInt16()
	image_type = f.readUInt16()
	
	if image_type == 0x3:
		offset = f.readUInt32()
		block["image"] = block["start"] - offset
		return
	
	block["image"] = block["start"]
	
	if encoding == 0xd:
		if image_type == 0x1:
			image =_readImage1(f, width, height, s.palette)
		elif image_type == 0x2:
			image = _readImage2(f, width, height, s.palette)
		else:
			raise ValueError("Unknown image type {:#x}".format(image_type))
	else:
		
		raise ValueError("Unknown image encoding {:#x}".format(encoding))
	
	s.images[block["start"]] = image

	
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



def main():
	parser = ArgumentParser()
	parser.add_argument("-f", "--file", type=Path, help="The sprite file")
	parser.add_argument("-b", "--background", type=Path, help="The scene file")
	args = parser.parse_args()
	
	sprite = read(
		Path(r"c:\users\danie\documents\data\sttng\brdgpica.spr"),
		Path(r"c:\users\danie\documents\data\sttng\bridge.rm")
	)
	
	print(sprite)
	


if __name__ == "__main__":
	main()
