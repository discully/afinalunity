from AFU import Image, File, Palette


WIDTH = 640
HEIGHT = 480


def background(input_path, palette_path=None):

	# TODO: Will not work for sb002004.scr, sb002007.scr, sb002009.scr, sb002016.scr, sb002018.scr, sb005012.scr, sb006015.scr,sb006016.scr, sb007004.scr

	f = File.File(input_path)

	n_palettes = (len(f) - (WIDTH * HEIGHT)) // (Palette._LENGTH_SINGLE * 3)

	if n_palettes < 1 or n_palettes > 2:
		raise ValueError("Background file contains an unexpected number of palettes: {}".format(n_palettes))

	local_palette = Palette.readSinglePalette(f)
	if n_palettes == 1:
		palette_path = Palette.getGlobalPalettePath(input_path, palette_path)
		global_palette = Palette.singlePalette(palette_path)
	else:
		global_palette = Palette.readSinglePalette(f)
	palette = Palette.combinePalettes(local_palette, global_palette)
	
	image = Image.Image(WIDTH, HEIGHT)
	image.name = input_path.name + ".png"
	
	n_pixels = WIDTH * HEIGHT
	for pixel in range(n_pixels):
		colour_index = f.readUInt8()
		image.set(palette[colour_index], pixel)

	assert(f.eof())
	
	return {
		"name": input_path.name,
		"image": image,
	}
