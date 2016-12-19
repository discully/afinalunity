import struct
from collections import deque



class File:
	
	def __init__(self, file_name):
		self.file_name = str(file_name)
		self.f = open(self.file_name, "rb")
		self.start = self.pos()
		self.bits = deque()
	
	
	def __len__(self):
		return self.size()
	
	
	def clearBits(self):
		self.bits.clear()
	
	
	def name(self):
		return self.file_name
	
	
	def pos(self):
		return self.f.tell()
	
	
	def readSInt32(self):
		"""Read a 32-bit Signed Integer"""
		return struct.unpack_from('i', self.read(4))[0]
	
	
	def readUInt32(self):
		"""Read a 32-bit Unsigned Integer"""
		return struct.unpack_from('I', self.read(4))[0]
	
	
	def readSInt16(self):
		"""Read a 16-bit Signed Integer"""
		return struct.unpack_from('h', self.read(2))[0]
	
	
	def readUInt16(self):
		"""Read a 16-bit Unsigned Integer"""
		return struct.unpack_from('H', self.read(2))[0]
	
	
	def readSInt8(self):
		"""Read an 8-bit Signed Integer"""
		return struct.unpack_from('b', self.read(1))[0]
	
	
	def readUInt8(self):
		"""Read an 8-bit Unsigned Integer"""
		return struct.unpack_from('B', self.read(1))[0]
	
	
	def read32(self):
		"""Read 32-bits"""
		return self.read(4)
	
	
	def read16(self):
		"""Read 16-bits"""
		return self.read(2)
	
	
	def read8(self):
		"""Read 8-bits"""
		return self.read(1)
	
	
	def readBits(self, n_bits):
		if( len(self.bits) < n_bits):
			self.bits += list("{0:08b}".format(self.readUInt8()))
		bits = []
		for i in range(n_bits):
			bits.append(int(self.bits.popleft()))
		return bits
	
	
	def readBitsToInt(self, n_bits):
		bits = self.readBits(n_bits)
		char_bits = [str(b) for b in bits]
		binary_string = "".join(char_bits)
		return int(binary_string, 2)
	
	
	def read(self, length):
		"""Read `length` bytes from the file"""
		got = self.f.read(length)
		if( len(got) != length ): raise EOFError("End of file")
		return got
	
	
	def readString(self):
		"""Read string up to a null byte"""
		s = ""
		c = self.readUInt8()
		while( c != 0x0 ):
			s += chr(c)
			c = self.readUInt8()
		return s
	
	
	def size(self):
		current_position = self.pos()
		self.f.seek(0,2) # go to the end of the file
		size = self.pos()
		self.f.seek(current_position, 0) # go back to where we were
		return size
	
	
	def setPosition(self, pos):
		self.f.seek(pos, 0)
