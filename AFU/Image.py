


class Image:
	
	def __init__(self, width, height):
		self.blank = (0,252,0)
		self.width = width
		self.height = height
		self.pixels = [ [self.blank for x in range(height)] for x in range(width) ]
	
	
	def __getitem__(self, x):
		if( x < 0 or x >= self.width ):
			raise IndexError( "Image x-index {0} out of range [0,{1})".format(x, self.width) )
		return self.pixels[x]
	
	
	def __len__(self):
		return self.nPixels()
	
	
	def __str__(self):
		return "Image (width={0}, height={1})".format(self.width, self.height)
	
	
	def nPixels(self):
		return self.width * self.height
	
	
	def set(self, colour, coord1, coord2 = None):
		
		if( coord2 == None ):
			if( coord1 >= len(self) ):
				raise IndexError( "Attempt to set nth pixel {0} which is out of range (0,{1}]".format( coord1, len(self) ) )
			x,y = ( coord1%self.width, coord1/self.width )
		else:
			x,y = (coord1,coord2)
		
		if( x < 0 or x >= self.width or y < 0 or y >= self.height ):
			raise IndexError( "Attempt to set pixel {0} which is out of image {1}".format( (x,y), (self.width,self.height) ) )
		
		
		self[x][y] = colour
