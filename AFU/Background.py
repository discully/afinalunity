import Image
import Palette



class Background:
	
	def __init__(self, input_file = None):
		self.palette = Palette.FullPalette()
		self.palette.setGlobalPalette( Palette.standard() )
		self.width = 640
		self.height = 480
		if( input_file != None ):
			self.read(input_file)
	
	
	def __str__(self):
		return "File ({0} {1})".format(self.file_name, {
			"width":self.width,
			"height":self.height,
		})
	
	
	def read(self, f):
		self.file_name = f.name()
		local_palette = Palette.Palette(f)
		self.palette.setLocalPalette(local_palette)
		
		self.image = Image.Image(self.width, self.height)
		
		self.readImage(f)
	
	
	def readImage(self, f):
		n_pixels = self.width * self.height
		
		for pixel in range(n_pixels):
			colour = f.readUInt8()
			self.image.set(self.palette[colour], pixel)



def main():
	
	import sys
	if( len(sys.argv) != 2 ):
		print "[USAGE] Background.py <filename.rm>"
		return 0
	
	import File
	f = File.File(sys.argv[1])
	
	rm = Background(f)
	print rm


if __name__ == "__main__":
	main()
