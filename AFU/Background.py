from AFU import Image, File, Palette


WIDTH = 640
HEIGHT = 480


def background(input_path, palette_path=None):

	f = File.File(input_path)

	f_size = len(f)
	if f_size == 256384:
		rows = 400
		extra_palette = False
	elif f_size == 307584:
		rows = 480
		extra_palette = False
	elif f_size == 307968:
		rows = 480
		extra_palette = True
	else:
		raise ValueError("Unsupported background file size: {}".format(f_size))

	local_palette = Palette.readSinglePalette(f)
	if extra_palette:
		global_palette = Palette.readSinglePalette(f)
	else:
		palette_path = Palette.getGlobalPalettePath(input_path, palette_path)
		global_palette = Palette.singlePalette(palette_path)
	palette = Palette.combinePalettes(local_palette, global_palette)
	
	image = Image.Image(WIDTH, HEIGHT)
	image.name = input_path.name + ".png"
	
	n_pixels = WIDTH * rows
	for pixel in range(n_pixels):
		colour_index = f.readUInt8()
		image.set(palette[colour_index], pixel)
	
	for row in range(rows, HEIGHT):
		for col in range(WIDTH):
			image.set((0, 0, 0), row * WIDTH + col)

	assert(f.eof())
	
	return {
		"name": input_path.name,
		"image": image,
	}
