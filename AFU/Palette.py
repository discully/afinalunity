import os.path



class Palette:
	
	def __init__(self, input_file = None):
		self._palette = [None for i in range(128)]
		if( input_file != None ):
			self.read(input_file)
	
	
	def __getitem__(self, index):
		if( index < 0 or index >= len(self) ):
			raise IndexError( "Palette index {0} out of range [0,{1})".format(index, len(self)) )
		return self._palette[index]
	
	
	def __len__(self):
		return len(self._palette)
	
	
	def __str__(self):
		s = "Palette:\n"
		for i in range(len(self)):
			s += "  {0} {1}\n".format(i, self[i])
		return s
	
	
	def read(self, f):
		for i in range(len(self)):
			r = f.readUInt8() * 4
			g = f.readUInt8() * 4
			b = f.readUInt8() * 4
			self._palette[i] = (r,g,b)



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
			print(i, self[i])
	
	
	def setGlobalPalette(self, global_palette):
		self.global_palette = global_palette
	
	
	def setLocalPalette(self, local_palette):
		self.local_palette = local_palette



def standard():
	global standard_file_path
	global _standard_palette

	if( standard_file_path == None ):
		if( os.path.isfile("standard.pal") ):
			standard_file_path = "standard.pal"
		else:
			raise RuntimeError("The location of the palette file standard.pal is not set and it cannot be found.")

	if( _standard_palette == None ):
		import AFU.File as File
		f = File.File(standard_file_path)
		_standard_palette = Palette(f)

	return _standard_palette

standard_file_path = None
_standard_palette = None



def main():
	
	import sys
	if( len(sys.argv) != 2 ):
		print("[USAGE]",__file__,"<filename.pal>")
		return 0
	
	import AFU.File as File
	f = File.File(sys.argv[1])
	
	pal = Palette(f)
	print(pal)


if __name__ == "__main__":
	main()



