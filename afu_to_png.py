from argparse import ArgumentParser
from pathlib import Path
import PIL
import AFU



class PILImage:

	def __init__(self, img):

		self.transparent = img.blank

		self.image = PIL.Image.new("RGBA", (img.width, img.height) )
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



def main():

	parser = ArgumentParser()
	parser.add_argument("image_file", type=Path, help="Path to the image file")
	parser.add_argument("-p", "--palette", type=Path, help="Path to standard.pal")
	parser.add_argument("-b", "--background", type=Path, help="Path to a background image on which the sprite is drawn (required for Sprites and Fonts)")
	args = parser.parse_args()

	if args.palette is None:
		AFU.Palette.standard_file_path = args.image_file.with_name("standard.pal")
	else:
		AFU.Palette.standard_file_path = args.palette

	afu_file = AFU.File.File(args.image_file)
	output_file_name = args.image_file.name
	
	file_type = AFU.Utils.identify( args.image_file )
	
	if file_type == "sprite":
		
		if args.background is None:
			print("Path to background image required for sprite but not provided.")
			parser.print_help()
			return
		
		afu_sprite = AFU.Sprite.read(args.image_file, args.background)
		for index,image in afu_sprite.images.items():
			export("{0}.{1}".format(output_file_name, index), image)
		
	elif file_type == "background":
		afu_background = AFU.Background.Background(afu_file)
		export(output_file_name, afu_background.image)
	
	elif file_type == "font":
		
		if args.background is None:
			print("Path to background image required for font but not provided.")
			parser.print_help()
			return
		
		p = AFU.Palette.FullPalette()
		p.setGlobalPalette( AFU.Palette.standard() )
		p.setLocalPalette( AFU.Palette.Palette( AFU.File.File(args.background) ) )
		
		afu_font = AFU.Font.Font(p, afu_file)
		for char,afu_character in afu_font.characters.items():
			export("{0}.{1}".format(output_file_name,ord(char)), afu_character.image)
			print("Exporting",char,ord(char))

	elif file_type == "texture":
		afu_texture = AFU.Texture.Texture(afu_file)
		export(output_file_name, afu_texture.image)
		
	elif file_type == "menu":
		path = args.image_file
		afu_menu = AFU.Menu.Menu(path)
		for i in range(len(afu_menu)):
			offset = afu_menu.offsets[i]
			image = afu_menu.images[i]
			output_file_name = "{}_{}".format(path.stem, offset)
			export(output_file_name, image)
	
	else:
		print("Unsupported file type: {}".format(file_type))



if __name__ == "__main__":
	main()
