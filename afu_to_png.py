import argparse
import pathlib
import png
import AFU



class PNGImage:

	def __init__(self, img):
		self.transparent = img.blank
		self.img = img
		self.pixels = []
		for y in range(img.height):
			self.pixels.append([])
			for x in range(img.width):
				for colour in img[x][y]:
					self.pixels[-1].append(colour)


	def save(self, file_name):
		f = open(file_name, "wb")
		img = self.img
		self.image = png.Writer(width = img.width, height = img.height, transparent = self.transparent)
		self.image.write(f, self.pixels)



def export(name, afu_image):
	if( afu_image != None ):
		png_image = PNGImage(afu_image)
		png_image.save("{0}.png".format(name))



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("image_file",
		help="Path to the image file to be converted.",
		)
	parser.add_argument("-p", "--palette",
		help="Path to the standard.pal palette file. If not provided, standard.pal must be in the same directory as image_file.",
		)
	parser.add_argument("-b", "--background",
		help="Path to a background image on which the sprite is drawn. Only required for Sprites and Fonts.",
		required=False
		)
	args = parser.parse_args()

	if( args.palette is None ):
		AFU.Palette.standard_file_path = str(pathlib.PurePath(args.image_file).with_name("standard.pal"))
	else:
		AFU.Palette.standard_file_path = args.palette

	afu_file = AFU.File.File(args.image_file)
	output_file_name = pathlib.PurePath(args.image_file).name
	
	file_type = AFU.Utils.identify( args.image_file )
	
	if( file_type == "sprite" ):
		
		if( args.background == None ):
			print("Path to background image required for sprite but not provided.")
			parser.print_help()
			return
		
		p = AFU.Palette.FullPalette()
		p.setGlobalPalette( AFU.Palette.standard() )
		p.setLocalPalette( AFU.Palette.Palette( AFU.File.File(args.background) ) )
		
		afu_sprite = AFU.Sprite.Sprite(afu_file, p)
		for index,afu_image in afu_sprite.images.items():
			export("{0}.{1}".format(output_file_name,index), afu_image.image)
		
	elif( file_type == "background" ):
		afu_background = AFU.Background.Background(afu_file)
		export(output_file_name, afu_background.image)
	
	elif( file_type == "font" ):
		
		if( args.background == None ):
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

	elif( file_type == "texture" ):
		afu_texture = AFU.Texture.Texture(afu_file)
		export(output_file_name, afu_texture.image)



if __name__ == "__main__":
	main()
