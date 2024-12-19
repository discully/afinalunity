from argparse import ArgumentParser
from pathlib import Path
from PIL import Image as PIL_Image
import AFU



class PILImage:

	def __init__(self, img):

		self.transparent = img.blank

		self.image = PIL_Image.new("RGBA", (img.width, img.height) )
		self.pixels = self.image.load()

		for x in range(img.width):
			for y in range(img.height):
				self.set(x, y, img[x][y])


	def get(self, row, column):
		return self.pixels[row, column]


	def save(self, file_name):
		self.image.save(file_name, "PNG")


	def set(self, row, column, colour):
		if len(colour) == 3 :
			if colour == self.transparent:
				colour = (0,0,0,0)
			else:
				colour = (colour[0], colour[1], colour[2], 255) # convert rgb to rgba
		elif len(colour) != 4:
			raise ValueError("Invalid colour: {0}".format(colour))

		self.pixels[row, column] = colour



def export(name, afu_image):
	if afu_image != None:
		png_image = PILImage(afu_image)
		png_image.save("{0}.png".format(name))


def getFilePath(file_name, image_path, argument):
	if argument is not None:
		return argument
	file_path = image_path.with_name(file_name)
	if file_path.is_file():
		return file_path
	file_path = Path(file_name)
	if file_path.is_file():
		return file_path
	return None


def main():

	parser = ArgumentParser()
	parser.add_argument("image_file", type=Path, help="Path to the image file")
	parser.add_argument("-p", "--palette", type=Path, help="Path to standard.pal")
	parser.add_argument("-b", "--background", type=Path, help="Path to a background image on which the sprite is drawn (required for Sprites and Fonts)")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place images in", default=".")
	args = parser.parse_args()

	global_palette_path = AFU.Palette.getGlobalPalettePath(args.image_file, args.palette)

	afu_file = AFU.File.File(args.image_file)
	output_file_name = args.output_dir.joinpath(args.image_file.name)

	file_type = AFU.Utils.identify( args.image_file )

	if file_type == "sprite":

		if args.background is None:
			print("Path to background image required for sprite but not provided.")
			parser.print_help()
			return

		afu_sprite = AFU.Sprite.sprite(args.image_file, args.background, args.palette)
		for offset,image in afu_sprite["images"].items():
			export("{0}.{1}".format(output_file_name, offset), image["image"])

	elif file_type == "background":
		afu_background = AFU.Background.background(args.image_file)
		export(output_file_name, afu_background["image"])

	elif file_type == "font":
		afu_font = AFU.Font.font(args.image_file, args.palette)
		for char,afu_character in afu_font.characters.items():
			export("{0}.{1}".format(output_file_name,ord(char)), afu_character.image)

	elif file_type == "texture":
		img = PIL_Image.open(args.image_file)
		img.save("{}.png".format(output_file_name), "PNG")

	elif file_type == "menu":
		afu_menu = AFU.Menu.Menu(args.image_file)
		for i in range(len(afu_menu)):
			offset = afu_menu.offsets[i]
			image = afu_menu.images[i]
			export("{}.{}".format(output_file_name, i), image)
	
	elif file_type == "cursor":
		cursors = AFU.Cursor.cursor(args.image_file, global_palette_path)
		for cursor in cursors:
			export(output_file_name.with_name(cursor.name), cursor)

	elif file_type == "database":
		if args.image_file.stem == "computer":

			background_path = getFilePath("compupnl.ast", args.image_file, args.background)
			if background_path is None:
				print("Path to background image required for computer database, but was not provided and could not be guessed.")
				parser.print_help()
				return
			
			palette = AFU.Palette.fullPalette(background_path, global_palette_path)

			computer = AFU.Computer.computerDb(args.image_file)
			for offset,entry in computer.items():
				if "image" in entry:
					image = AFU.Image.Image(entry["image"]["width"], entry["image"]["height"])
					for i,b in enumerate(entry["image"]["data"]):
						image.set(palette[b], i)
					image.export("{}.{}.png".format(output_file_name, offset))
		else:
			print("Unsupported database file: {}".format(args.image_file.name))
	elif file_type == "palette":
		# palette has 128 colours, image is 640x480px
		# draw 16x8 squares, each 40x60px
		palette = AFU.Palette.singlePalette(args.image_file)
		image = AFU.Image.Image(640,480)
		for i,colour in enumerate(palette):
			row = i % 16
			col = i // 16
			print("[{:>3}]   ({:>2},{:>2})   {}".format(i, row, col, colour))
			for dx in range(40):
				for dy in range(60):
					x = (row * 40) + dx
					y = (col * 60) + dy
					image.set(colour, x, y)
		image.export("{}.png".format(output_file_name))

	else:
		print("Unsupported file type: {}".format(file_type))



if __name__ == "__main__":
	main()
