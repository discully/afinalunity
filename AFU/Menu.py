from pathlib import Path
from AFU import Palette, Image, File



def mrg(mrg_path, background_path=None, palette_path=None):
	
	if background_path is None: background_path = mrg_path.with_name("bridge.rm")
	palette_path = Palette.getGlobalPalettePath(mrg_path, palette_path)
	palette = Palette.fullPalette(background_path, palette_path)

	f = File.File(mrg_path)
	mrg = []

	n_entries = f.readUInt16()

	offsets = [f.readUInt32() for i in range(n_entries)]

	eof = f.readUInt32()
	for i in range(n_entries):
		
		assert(f.pos() <= offsets[i])
		while f.pos() < offsets[i]:
			assert(f.readUInt8() == 0)

		width = f.readUInt16()
		height = f.readUInt16()
		image = Image.Image(width, height)

		for y in range(height):
			for x in range(width):
				c = f.readUInt8()
				if c == 13:
					colour = (0,0,0,0)
				else:
					colour = palette[c]
				image.set(colour, x, y)

		mrg.append(image)

	assert(f.pos() == eof)

	return mrg
