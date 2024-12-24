from PIL import Image as PIL_Image


class Image:
	
	def __init__(self, width, height):
		self.blank = (0,252,0)
		self.width = width
		self.height = height
		self.pixels = [ [self.blank for x in range(height)] for y in range(width) ]
		self.name = None
	
	
	def __getitem__(self, x):
		if( x < 0 or x >= self.width ):
			raise IndexError( "Image x-index {0} out of range [0,{1})".format(x, self.width) )
		return self.pixels[x]
	
	
	def __len__(self):
		return self.nPixels()
	
	
	def __str__(self):
		if self.name:
			return self.name
		else:
			return "Image (width={0}, height={1})".format(self.width, self.height)
	
	
	def nPixels(self):
		return self.width * self.height
	
	
	def set(self, colour, coord1, coord2 = None):
		
		if( coord2 == None ):
			if( coord1 >= len(self) ):
				raise IndexError( "Attempt to set nth pixel {0} which is out of range (0,{1}]".format( coord1, len(self) ) )
			x,y = ( coord1%self.width, coord1//self.width )
		else:
			x,y = (coord1,coord2)
		
		if( x < 0 or x >= self.width or y < 0 or y >= self.height ):
			raise IndexError( "Attempt to set pixel {0} which is out of image {1}".format( (x,y), (self.width,self.height) ) )
		
		
		self[x][y] = colour
	

	def paste(self, image, x, y):
		for i_x in range(image.width):
			for i_y in range(image.height):
				self[x+i_x][y+i_y] = image[i_x][i_y]

	
	def pilImage(self):
		class PILImage:
			
			def __init__(self, img):
				
				self.transparent = img.blank
				
				self.image = PIL_Image.new("RGBA", (img.width, img.height))
				self.pixels = self.image.load()
				
				for x in range(img.width):
					for y in range(img.height):
						self.set(x, y, img[x][y])
			
			def get(self, row, column):
				return self.pixels[row, column]
			
			def save(self, file_name):
				self.image.save(file_name, "PNG")
			
			def set(self, row, column, colour):
				if len(colour) == 3:
					if colour == self.transparent:
						colour = (0, 0, 0, 0)
					else:
						colour = (colour[0], colour[1], colour[2], 255)  # convert rgb to rgba
				elif len(colour) != 4:
					raise ValueError("Invalid colour: {0}".format(colour))
				
				self.pixels[row, column] = colour
		return PILImage(self)
	
	
	def export(self, name):
		png_image = self.pilImage()
		png_image.save(name)
