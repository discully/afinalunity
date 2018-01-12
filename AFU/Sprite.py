import AFU.Image as Image
import AFU.Palette as Palette
from collections import Counter



blocks = [
	"SPRT", # appears at start, indicates sprite file
	"LIST",
	"PAUS", # pause animation
	"EXIT", # pause/exit
	"STAT", # switch to static mode
	"TIME", # time (wait between frames?)
	"COMP", # compressed image data
	"MASK", # switch to mask mode
	"POSN", # change position of sprite/object?
	"SETF", # set flag (0, 1, 2, 3, 4)
	"MARK", # TODO: store info
	"RAND", # wait for a random time
	"JUMP", # a jump to an animation
	"SCOM", # compressed image data representing speech
	"DIGI", # audio?! :(
	"SNDW", # wait for sound to finish
	"SNDF", # TODO: unknown is always 75, 95 or 100. volume?
	"PLAY",
	"RPOS", # relative position change(?)
	"MPOS", # mouth position (relative to parent)
	"SILE", # stop+reset sound
	"OBJS", # set parent object state
	"RGBP", # palette (256*3 bytes, each 0-63)
	"BSON", # used only in legaleze.spr
]



"""Given a list of integers, returns a tuple of hexadecimal strings"""
def hext(int_list):
	str_list = [hex(i) for i in int_list]
	return tuple(str_list)



class Sprite:
	
	def __init__(self, input_file=None, palette=None):
		self.file_name = ""
		self.images = {}
		self.main_list = []
		self.steps = []
		
		self.palette = palette
		
		if( input_file != None ):
			self.read(input_file)
	
	
	def __str__(self):
		return "Sprite: {0} {1})".format(self.file_name, {
			"key image frames": len(self.main_list),
			"images": len(self.images),
			"steps": len(self.steps),
			"image formats": Counter([(info["type"],info["encoding"]) for block,info in self.steps if block in ["COMP","SCOM"]]),
		} )
	
	
	def read(self, f):
		self.file_name = f.name()
		
		self.images = {}
		self.steps = []
		
		try:
			self.readBlocks(f)
		except EOFError:
			pass
	
	
	def readBlocks(self, f):
		while True:
			self.readBlock(f)
	
	
	def readBlock(self, f):
		
		block_start = f.pos()
		
		block_name = self.readBlockName(f)
		if not block_name in blocks:
			raise ValueError( "Block at {0:#x} has invalid block type: {1}".format(block_start, block_name) )
		
		block_length = f.readUInt32()
		block_end = block_start + block_length
		
		if(   block_name == "SPRT" ): self.readBlockSPRT(f)
		elif( block_name == "LIST" ): self.readBlockLIST(f)
		elif( block_name == "SETF" ): self.readBlockSETF(f)
		elif( block_name == "POSN" ): self.readBlockPOSN(f)
		elif( block_name == "COMP" ): self.readBlockCOMP(f)
		elif( block_name == "TIME" ): self.readBlockTIME(f)
		elif( block_name == "MARK" ): self.readBlockMARK(f)
		elif( block_name == "MASK" ): self.readBlockMASK(f)
		elif( block_name == "SCOM" ): self.readBlockSCOM(f)
		elif( block_name == "RAND" ): self.readBlockRAND(f)
		elif( block_name == "JUMP" ): self.readBlockJUMP(f)
		elif( block_name == "RPOS" ): self.readBlockRPOS(f)
		elif( block_name == "SNDF" ): self.readBlockSNDF(f)
		elif( block_name == "MPOS" ): self.readBlockMPOS(f)
		elif( block_name == "PAUS" ): self.readBlockPAUS(f)
		elif( block_name == "EXIT" ): self.readBlockEXIT(f)
		elif( block_name == "STAT" ): self.readBlockSTAT(f)
		elif( block_name == "RGBP" ): self.readBlockRGBP(f)
		else:
			raise ValueError("Block at {0:#x} has invalid type: {1}".format(block_start, block_name))
		
		if( f.pos() > block_end ):
			raise ValueError("{0} block at {1:#x} over ran by {2} bytes".format(block_name, block_start, (f.pos() - block_end) ) )
		elif( f.pos() < block_end ):
			# TODO:
			# For the moment we'll ignore this and jump ahead
			# Once image reading is being done, this should raise an exception
			f.setPosition(block_end)
	
	
	def readBlockName(self, f):
		name = ""
		for i in range(4):
			name = chr(f.readUInt8()) + name
		return name
	
	
	def readBlockCOMP(self, f):
		block_start = f.pos() - 8
		info = self.readImage(f)
		self.steps.append( ("COMP", info) )
	
	
	def readBlockEXIT(self, f):
		self.steps.append( ("EXIT", {}) )
	
	
	def readBlockJUMP(self, f):
		target = f.readUInt32()
		self.steps.append( ("JUMP", {"target":target}) )
	
	
	def readBlockLIST(self, f):
		block_start = f.pos() - 8
		
		n_entries = f.readUInt32()
		
		self.main_list = []
		for i in range(n_entries):
			self.main_list.append(block_start + f.readUInt32())
		
		self.readBlocks(f)
	
	
	def readBlockMARK(self, f):
		self.steps.append( ("MARK", {}) )
	
	
	def readBlockMASK(self, f):
		self.steps.append( ("MASK", {}) )
	
	
	def readBlockMPOS(self, f):
		x = f.readUInt32()
		y = f.readUInt32()
		self.steps.append( ("MPOS", {"x":x, "y":y}) )
	
	
	def readBlockPAUS(self, f):
		self.steps.append( ("PAUS", {}) )
		
	
	def readBlockPOSN(self, f):
		x = f.readUInt32()
		y = f.readUInt32()
		self.steps.append( ("POSN", {"x":x, "y":y}) )
	
	
	def readBlockRAND(self, f):
		rand_amt =  f.readUInt32()
		rand_base = f.readUInt32()
		self.steps.append( ("RAND", {"amount":rand_amt, "base":rand_base}) )
	
	
	def readBlockRPOS(self, f):
		dx = f.readSInt32()
		dy = f.readSInt32()
		self.steps.append( ("RPOS", {"x":dx, "y":dy}) )
	
	
	def readBlockSCOM(self, f):
		block_start = f.pos() - 8
		info = self.readImage(f)
		self.steps.append( ("SCOM", info) )
	
	
	def readBlockSETF(self, f):
		flag = f.readUInt32()
		self.steps.append( ("SETF", {"flag":flag}) )
	
	
	def readBlockSNDF(self, f):
		unknown1 = f.readUInt32() # 75, 95 or 100. Volume?
		unknown2 = f.readUInt32() # Empty
		sound_file_name = str(f.read(16))
		self.steps.append( ("SNDF", {"volume":unknown1, "empty":unknown2, "file":sound_file_name}) )
	
	
	def readBlockSPRT(self, f):
		unknown = f.readUInt32()
		if( unknown != 0x100 ):
			raise ValueError("SPRT expected 0x100, got " + hex(unknown))
		self.readBlocks(f)
	
	
	def readBlockSTAT(self, f):
		self.steps.append( ("STAT", {}) )
	
	
	def readBlockRGBP(self, f):
		self.palette.local_palette = Palette.Palette(f)
	
	
	def readBlockTIME(self, f):
		time = f.readUInt32()
		self.steps.append( ("TIME", {"time":time}) )
	
	
	def readImage(self, f, process_image=False):
		
		block_start = f.pos() - 12 - 8
		
		image_width  = f.readUInt32()
		image_height = f.readUInt32()
		image_encoding = f.readUInt16()
		image_type   = f.readUInt16() # 0x1 = SpriteType1, 0x2 = SpriteType2, 0x3 = copy of previous sprite

		if( image_type == 0x3 ):
			# Reference to an image which has already been passed
			relative_position = f.readUInt32()
			image_position = block_start - relative_position
			if( not image_position in self.images ):
				raise ValueError("Image at {0} references image at {1} which is not present".format(block_start, image_position))
		else:
			image_position = block_start

		image_info = {
			"width":image_width,
			"height":image_height,
			"encoding":image_encoding,
			"type":image_type,
			"image":image_position
		}

		if( image_type != 0x3 ):
			# A new image
			self.images[block_start] = None
			if( self.palette != None ):
				# Note that not all format/type combinations are currently supported
				if( image_encoding == 0xd ):
					if( image_type == 0x1 ):
						img = SpriteImage1(image_width, image_height, self.palette, f)
						img.read(f)
						self.images[image_position] = img
					elif( image_type == 0x2 ):
						img = SpriteImage2(image_width, image_height, self.palette, f)
						img.read(f)
						self.images[image_position] = img

		return image_info



class SpriteImage:
	
	def __init__(self, width, height, palette, input_file = None):
		
		self.image = Image.Image(width, height)
		self.palette = palette
		self.n_pixels_drawn = 0
		
		if( input_file != None ):
			self.read(input_file)
	
	
	def setNPixels(self, colour, n):
		for i in range(n):
			self.setPixel(colour)
	
	
	def setPixel(self, colour):
		self.image.set(colour, self.n_pixels_drawn)
		self.n_pixels_drawn += 1



class SpriteImage1 (SpriteImage):
	
	def __init__(self, width, height, palette, input_file = None):
		SpriteImage.__init__(self, width, height, palette, input_file)
	
	
	def read(self, f):
		palette = self.palette
		img = self.image
		
		n_pixels_target = len(img)
		
		colour = 0
		f.clearBits()
		
		while( self.n_pixels_drawn < n_pixels_target ):
			if( f.readBitsToInt(1) == 0 ):
				# bit 0 set: single pixel, 3 bit colour offset
				offset = f.readBitsToInt(3)
				if ((offset & 0x4) == 0):
					colour = colour + 1 + offset;
				else:
					colour = colour - 1 - (offset & 0x3)
				self.setPixel( palette[colour] )
				
			elif( f.readBitsToInt(1) == 0 ):
				# bit 1 set: 2 bit colour offset, 3 bit length (+1)
				offset = f.readBitsToInt(2)
				length = f.readBitsToInt(3) + 1
				if((offset & 0x2) == 0):
					colour = colour + 1 + offset
				else:
					colour = colour + 1 - offset
				self.setNPixels( palette[colour], length )
				
			elif( f.readBitsToInt(1) == 0 ):
				# bit 2 set: 7 bit colour (+128 for global palette), 1 bit length (+1)
				colour = f.readBitsToInt(7) + 128
				length = f.readBitsToInt(1) + 1
				self.setNPixels( palette[colour], length )
				
			elif( f.readBitsToInt(1) == 0 ):
				# bit 3 set: 5 bit length (+1), use previous colour
				length = f.readBitsToInt(5) + 1
				#self.setNPixels( palette[colour], length ) # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! I've changed this to blank to make picard.spr work
				self.setNPixels( img.blank, length )        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! I've changed this to blank to make picard.spr work
				
			elif( f.readBitsToInt(1) == 0 ):
				# bit 4 set: 7 bit colour (+128 for global palette), 4 bit length (+1)
				colour = f.readBitsToInt(7) + 128
				length = f.readBitsToInt(4) + 1
				self.setNPixels( palette[colour], length )
				
			elif( f.readBitsToInt(1) == 0 ):
				# bit 5 set: 8 bit colour, 8 bit length
				colour = f.readBitsToInt(8)
				length = f.readBitsToInt(8) + 1
				self.setNPixels( palette[colour], length )
				
			else:
				# otherwise: do a pixel run of blank(?) for a whole width, then drop 1 bit
				self.setNPixels( img.blank, img.width )
				f.readBitsToInt(1) # probably always 1?



class SpriteImage2 (SpriteImage):
	
	def __init__(self, width, height, palette, input_file = None):
		SpriteImage.__init__(self, width, height, palette, input_file)
	
	
	def read(self, f):
		f.clearBits()
		
		palette = self.palette
		img = self.image
		
		n_pixels_target = len(img)
		
		while( self.n_pixels_drawn < n_pixels_target ):
			
			draw_command = f.readBits(2)
			
			if( draw_command == [0,0] ):
				# the next 8 bits are a number n, run of (n + 1) blank(?) pixels
				n = f.readBitsToInt(8)
				self.setNPixels(img.blank, n+1)
			elif( draw_command == [0,1] ):
				# the next 8 bits represent data for a single pixel
				pixel = f.readBitsToInt(8)
				self.setPixel( palette[pixel] )
			elif( draw_command == [1,0] ):
				# 8 bits pixel data, followed by 3 bits n, run of (n + 1) of those pixels
				pixel = f.readBitsToInt(8)
				n = f.readBitsToInt(3)
				self.setNPixels( palette[pixel], n+1 )
			elif( draw_command == [1,1] ):
				# 8 bits pixel data, followed by 8 bits n, run of (n + 1) of those pixels
				pixel = f.readBitsToInt(8)
				n = f.readBitsToInt(8)
				self.setNPixels( palette[pixel], n+1 )
			else:
				# this isn't possible
				raise ValueError( "SpriteImage2 encountered unknown draw command {0:#x}".format(draw_command) )



def main():
	
	import sys
	if( len(sys.argv) != 3 ):
		print("[USAGE]",__file__,"<spritefile.spr> <palettefile.rm>")
		return 0
	
	import AFU.File as File
	f = File.File(sys.argv[1])
	
	import AFU.Palette as Palette
	p = Palette.FullPalette()
	p.setGlobalPalette( Palette.standard() )
	p.setLocalPalette( Palette.Palette( File.File(sys.argv[2]) ) )
	
	s = Sprite(p, f)
	print(s)


if __name__ == "__main__":
	main()
