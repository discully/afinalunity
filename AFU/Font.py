import AFU.Image as Image
import AFU.Palette as Palette
from AFU.File import File



def font(font_path, background_path=None, palette_path=None):
	
	if background_path is None: background_path = font_path.with_name("bridge.rm")
	palette_path = Palette.getGlobalPalettePath(font_path, palette_path)
	palette = Palette.fullPalette(background_path, palette_path)

	f = File(font_path)

	assert(f.readUInt8() == 0x1)
	height = f.readUInt8()
	start = f.readUInt8()
	end = f.readUInt8()
	size = f.readUInt16()
	assert(f.readUInt8() == 0x0)
	font_type = f.readUInt8()
	assert(font_type in (0x0, 0x1))
	data_width = f.readUInt8()

	font = {
		"height": height,
		"start": start,
		"end": end,
		"size": size,
		"type": font_type,
		"width": data_width,
		"chars": {},
	}

	if font_type == 0x0:
		assert(font["width"] == 0)
		font["width"] = 8

		for char_int in range(start, end+1):
			char = chr(char_int)
			char_width = f.readUInt8()
			image = Image.Image(char_width, height)

			data = [f.readUInt8() for d in range(font["height"])]
			for y in range(font["height"]):
				for x in range(char_width):
					mask = 0x80 >> x
					if data[y] & mask:
						image[x][y] = (0,0,255)
					else:
						image[x][y] = (0,0,0,0)
			
			if char_width == 0:
				continue

			font["chars"][char] = {
				"width": char_width,
				"image": image
			}

			if f.eof(): break

		return font

	elif font_type == 0x1:
		for char_int in range(start, end+1):
			char = chr(char_int)
			char_width = f.readUInt8()
			if char_width == 0xff: char_width = data_width
			
			image = Image.Image(char_width, height)
			for y in range(height):
				for x in range(data_width):
					colour = f.readUInt8()
					if x < char_width:
						image.set(palette[colour], x, y)
			
			if char_width == 0:
				continue

			font["chars"][char] = {
				"width": char_width,
				"image": image
			}

			# Todo: Sometimes fonts contain an extra character. Most of them have non-zero char widths.
	else:
		raise ValueError("Invalid font type {}".format(font_type))
	
	return font


def text_width(font, txt):
	try:
		return sum([ font["chars"][c]["width"] for c in txt ])
	except KeyError:
		raise ValueError("Font does not contain all characters in text")


def text(font, txt):
	width = text_width(font, txt)
	image = Image.Image(width, font["height"])
	x = 0
	for c in txt:
		image.paste(font["chars"][c]["image"], x, 0)
		x += font["chars"][c]["width"]
	return image
