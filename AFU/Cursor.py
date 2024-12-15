from AFU import File, Image, Palette


def cursor(file_path, palette_path=None):
	f = File.File(file_path)
	
	palette_path = Palette.getGlobalPalettePath(file_path, palette_path)
	palette = Palette.fullPalette(palette_path, palette_path)
	
	cursors = []
	try:
		while True:
			width = f.readUInt16()
			height = f.readUInt16()
			cursor_image = Image.Image(width, height)
			cursor_image.name = "{}.{}".format(file_path.name, len(cursors))
			for y in range(height):
				for x in range(width):
					i = f.readUInt8()
					if i == 13:
						cursor_image.set((0,0,0,0), x, y)
					else:
						cursor_image.set(palette[i], x, y)
			cursors.append(cursor_image)
	except EOFError:
		pass
	
	return cursors


DEFAULT_CURSOR = [
	0,0,3,3,3,3,3,3,3,3,3,
	0,1,0,3,3,3,3,3,3,3,3,
	0,1,1,0,3,3,3,3,3,3,3,
	0,1,1,1,0,3,3,3,3,3,3,
	0,1,1,1,1,0,3,3,3,3,3,
	0,1,1,1,1,1,0,3,3,3,3,
	0,1,1,1,1,1,1,0,3,3,3,
	0,1,1,1,1,1,1,1,0,3,3,
	0,1,1,1,1,1,1,1,1,0,3,
	0,1,1,1,1,1,1,1,1,1,0,
	0,1,1,1,1,1,0,3,3,3,3,
	0,1,0,3,0,1,1,0,3,3,3,
	0,0,3,3,0,1,1,0,3,3,3,
	3,3,3,3,3,0,1,1,0,3,3,
	3,3,3,3,3,0,1,1,0,3,3,
	3,3,3,3,3,3,0,1,1,0,3
]
DEFAULT_CURSOR_WIDTH = 11
DEFAULT_CURSOR_HEIGHT = 16
DEFAULT_CURSOR_COLOURS = {
	0: (255, 255, 255, 255),
	1: (0, 0, 0, 255),
	3: (255, 255, 255, 0)
}


def default():
	img = Image.Image(DEFAULT_CURSOR_WIDTH, DEFAULT_CURSOR_HEIGHT)
	for y in range(DEFAULT_CURSOR_HEIGHT):
		for x in range(DEFAULT_CURSOR_WIDTH):
			img.set( DEFAULT_CURSOR_COLOURS[DEFAULT_CURSOR[x + DEFAULT_CURSOR_WIDTH*y]], x, y)
	return img
	
