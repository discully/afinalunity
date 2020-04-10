from AFU import Image, File, Palette


WIDTH = 640
HEIGHT = 480


def background(input_path, palette_path=None):
	
	palette_path = Palette.getGlobalPalettePath(input_path, palette_path)
	global_palette = Palette.singlePalette(palette_path)

	f = File.File(input_path)
	local_palette = Palette.readSinglePalette(f)
	palette = Palette.combinePalettes(local_palette, global_palette)
	
	image = Image.Image(WIDTH, HEIGHT)
	image.name = input_path.name + ".png"
	
	n_pixels = WIDTH * HEIGHT
	for pixel in range(n_pixels):
		colour_index = f.readUInt8()
		image.set(palette[colour_index], pixel)
	
	return {
		"name": input_path.name,
		"image": image,
	}
