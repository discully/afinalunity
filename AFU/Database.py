import AFU.File as File



class Database:
	
	def __init__(self, input_file = None):
		if( input_file != None ):
			self.read(input_file)
	
	
	def read(self, f):
		self.file_name = f.name()
		if( "astro.db" in self.file_name ):
			self.readAstro(f)
		else:
			print(self.file_name, "unsupported")
	
	
	def readAstro(self, f):
		for zi in range(8):
			for yi in range(8):
				for xi in range(8):
					try:
						coord = f.readUInt16()
						x = coord%256
						y = coord%64
						z = coord%8
						#x = f.readUInt8()
						#y = f.readUInt8()
						#z = f.readUInt8()
						data = []
						for i in range(34):
							data.append(f.readUInt8())
						print(coord, (x,y,z), (xi,yi,zi), data)
						assert(x == xi)
						assert(y == yi)
						assert(z == zi)
					except AssertionError:
						print(hex(f.pos()))
						raise AssertionError
					
