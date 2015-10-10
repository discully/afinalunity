import os.path
import sys
import PIL.Image
import AFU



class PILImage:
	
	def __init__(self, img):
		
		self.transparent = (0,0,0,0)
		self.red = (255,0,0,255)
		self.green = (0,255,0,255)
		self.blue = (0,0,255,255)
		
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
		if( len(colour) == 3 ):
			colour = (colour[0], colour[1], colour[2], 255) # convert rgb to rgba
		elif( len(colour) != 4 ):
			raise ValueError("Invalid colour: {0}".format(colour))
		
		self.pixels[row, column] = colour



def export(name, afu_image):
	pil_image = PILImage( afu_image )
	pil_image.save("{0}.png".format(name))



def usage():
	print "[USAGE] {0} <file.spr> <file.pal>".format(__file__)
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
		for char,afu_character in afu_font.characters.iteritems():
			export("{0}.{1}".format(output_file_name,ord(char)), afu_character.image)
			print "Exporting {0} ({1})".format(char, ord(char))



if __name__ == "__main__":
	main()
