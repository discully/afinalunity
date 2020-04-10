import AFU.Image as Image
import AFU.Palette as Palette
import AFU.File as File



class Character:
	
	def __init__(self, width, image):
		self.width = width
		self.image = image



class Font:
	
	def __init__(self, palette, input_file = None):
		self.palette = palette
		
		self.characters = {}
		
		self.height = 0 # the height in pixels of each character's image
		self.width = 0  # the width in pixels of each character's image
		self.pitch = 0  # the distance between where the start of each character is drawn
		self.start = 0  # the integer representation of the first character included in the font
		self.end = 0    # the integer representation of the last character included in the font
		
		if( input_file != None ):
			self.read(input_file)
	
	
	def __getitem__(slef, int_char):
		return self.integer(int_char)
	
	
	def __len__(self):
		return len(self.characters)
	
	
	def __str__(self):
		return "Font: {0}".format({
			"height":self.height,
			"start":self.start,
			"end":self.end,
			"size":len(self),
			"width":self.width,
			"pitch":self.pitch,
		})
	
	
	def character(self, char):
		if( not char in self.characters ):
			raise IndexError("Character {0} not in font.".format(char))
		return self.characters[char]
	
	
	def integer(self, int_char):
		if( int_char < self.start or int_char > self.end ):
			raise IndexError("Character represented by {0:d} ({0:c}) not in font.".format(int_char))
		return self.character(chr(int_char))
	
	
	def read(self, f):
		
		unknown = f.readUInt8()
		if( unknown != 0x1 ):
			raise ValueError("Expected 0x1 as first byte of font file, got {0:#x}".format(unknown))
		
		self.height = f.readUInt8()
		self.start = f.readUInt8()
		self.end = f.readUInt8()
		size = f.readUInt16() - 1
		
		if( size % self.height ):
			raise ValueError("Size ({0}) is not an integer multiple of height ({1}).".format(size, self.height))
		self.width = size / self.height
		
		unknown2 = f.readUInt8()
		if( unknown2 != 0x0 ):
			raise ValueError("Expected 0x0 at end of font file header, got {0:#x}".format(unknown2))
		
		unknown3 = f.readUInt8()
		if( unknown3 not in (0x0,0x1) ):
			raise ValueError("Expected one of {0} at end of font file header, got {1:#x}".format((0x0,0x1), unknown3))
		elif( unknown3 == 0x0 ):
			raise ValueError("Font type {0:#x} not currently supported".format(unknown3))
		
		self.pitch = f.readUInt8()
		
		if( unknown3 == 0 ):
			expected_size = 1
		else:
			expected_size = self.pitch * self.height
		
		if( size != expected_size ):
			raise ValueError("Size reported in file ({0}) does not match that expected ({1}).".format(size, expected_size))
		
		#print(self)
		
		for char_int in range(self.start, self.end+1):
			char_character = chr(char_int)
			char_width =  f.readUInt8()
			#print(char_width)
			char_image = Image.Image(self.pitch, self.height)
			
			for y in range(self.height):
				for x in range(self.pitch):
					colour = f.readUInt8()
					char_image.set(self.palette[colour], x, y)
			
			self.characters[char_character] = Character(char_width, char_image)
		
		#if( f.pos() != f.size() ):
		#	raise ValueError("Not at EOF: pos({0}) size({1})".format(f.pos(), f.size()))
	
	
	def string(self, string):
		chars = [ self.character(char) for char in string ]
