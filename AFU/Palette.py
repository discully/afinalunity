


class Palette:
	
	def __init__(self, input_file = None):
		self.size = 128
		self.palette = []
		if( input_file != None ):
			self.read(input_file)
	
	
	def __getitem__(self, index):
		if( index < 0 or index >= len(self) ):
			raise IndexError( "Palette index {0} out of range [0,{1})".format(index, len(self)) )
		return self.palette[index]
	
	
	def __len__(self):
		return len(self.palette)
	
	
	def __str__(self):
		s = "Palette:\n"
		for i in range(palette_size):
			s += "  {0} {1}\n".format(i, self[i])
		return s
	
	
	def read(self, f):
		palette = []
		for i in range(self.size):
			r = f.readUInt8() * 4
			g = f.readUInt8() * 4
			b = f.readUInt8() * 4
			colour = (r,g,b)
			palette.append(colour)
		self.palette = palette



class FullPalette:
	
	def __init__(self):
		self.global_palette = None
		self.local_palette   = None
	
	def __getitem__(self, index):
		if( index < 0 or index >= len(self) ):
			raise IndexError( "Palette index {0} out of range [0,{1})".format(index, len(self)) )
		elif( index >= len(self.local_palette) ):
			return self.global_palette[index-len(self.local_palette)]
		else:
			return self.local_palette[index]
	
	
	def __len__(self):
		return len(self.global_palette) + len(self.local_palette)
	
	
	def __str__(self):
		for i in range(len(self)):
			print i, self[i]
	
	
	def setGlobalPalette(self, global_palette):
		self.global_palette = global_palette
	
	
	def setLocalPalette(self, local_palette):
		self.local_palette = local_palette



def standard(file_path = None):
	if( file_path == None ):
		import os
		file_path = os.getenv("STTNG_PAL")
		if( file_path == None ):
			raise EnvironmentError("Environment variable 'STTNG_PAL' should be the path to standard.pal")
	
	import File
	f = File.File(file_path)
	
	p = Palette(f)
	return p



def main():
	
	import sys
	if( len(sys.argv) != 2 ):
		print "[USAGE] Palette.py <filename.pal>"
		return 0
	
	import File
	f = File.File(sys.argv[1])
	
	pal = Palette(f)
	print pal


if __name__ == "__main__":
	main()



