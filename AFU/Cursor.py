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
					cursor_image.set(palette[f.readUInt8()], x, y)
			cursors.append(cursor_image)
	except EOFError:
		pass
	
	return cursors
