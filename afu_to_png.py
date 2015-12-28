import os.path
import sys
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
	png_image = PNGImage(afu_image)
	png_image.save("{0}.png".format(name))



def usage():
	print("[USAGE]",__file__,"<file.spr> <file.pal>")
	return 1



def main():
	
	if( not len(sys.argv) in range(2,5) ):
		return usage()
	
	input_file_name = sys.argv[1]
	afu_file = AFU.File.File(input_file_name)
	output_file_name = os.path.basename(input_file_name)
	
	file_type = AFU.Utils.identify( input_file_name )
	
	if( file_type == "sprite" ):
		
		if( len(sys.argv) != 3 ):
			return usage()
		
		p = AFU.Palette.FullPalette()
		p.setGlobalPalette( AFU.Palette.standard() )
		p.setLocalPalette( AFU.Palette.Palette( AFU.File.File(sys.argv[2]) ) )
		
		afu_sprite = AFU.Sprite.Sprite(p, afu_file)
		for index,afu_image in afu_sprite.images.iteritems():
			export("{0}.{1}".format(output_file_name,index), afu_image.image)
		
	elif( file_type == "background" ):
		afu_background = AFU.Background.Background(afu_file)
		export(output_file_name, afu_background.image)
	
	elif( file_type == "font" ):
		
		if( len(sys.argv) != 3 ):
			return usage()
		
		p = AFU.Palette.FullPalette()
		p.setGlobalPalette( AFU.Palette.standard() )
		p.setLocalPalette( AFU.Palette.Palette( AFU.File.File(sys.argv[2]) ) )
		
		afu_font = AFU.Font.Font(p, afu_file)
		for char,afu_character in afu_font.characters.items():
			export("{0}.{1}".format(output_file_name,ord(char)), afu_character.image)
			print("Exporting",char,ord(char))



if __name__ == "__main__":
	main()
