import struct
from collections import deque



def fpos(f, comment=""):
	print(f.pos(), hex(f.pos()), comment)



class File:

	def __init__(self, file_name):
		self.file_name = str(file_name)
		self.f = open(self.file_name, "rb")
		self.start = self.pos()
		self.bits = deque()
		self._size = None


	def __len__(self):
		return self.size()


	def clearBits(self):
		self.bits.clear()


	def name(self):
		return self.file_name


	def eof(self):
		return not self.pos() < self.size()


	def peek(self):
		value = self.readUInt8()
		self.setPosition(self.pos() - 1)
		return value


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
		if len(self.bits) < n_bits:
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
		if len(got) != length: raise EOFError("End of file {}".format(self.pos()))
		return got


	def readLine(self):
		"""Read string up to a \n"""
		s = ""
		c = self.readUInt8()
		while c != 0x0A:
			s += chr(c)
			c = self.readUInt8()
		return s.strip()


	def readString(self):
		"""Read string up to a null byte"""
		s = ""
		c = self.readUInt8()
		while c != 0x0:
			s += chr(c)
			c = self.readUInt8()
		return s


	def readStringBuffer(self, length):
		b = self.read(length)
		s = ""
		for x in b:
			if x == 0:
				break
			s += chr(x)
		return s


	def size(self):
		if self._size is None:
			current_position = self.pos()
			self.f.seek(0,2) # go to the end of the file
			self._size = self.pos()
			self.f.seek(current_position, 0) # go back to where we were
		return self._size


	def setPosition(self, pos):
		self.f.seek(pos, 0)



class DatabaseFile(File):

	def __init__(self, file_path):
		self._offset_base = 0
		File.__init__(self, file_path)

	def setOffsetBase(self, offset):
		self._offset_base = offset

	def offset(self):
		return self.pos() - self._offset_base

	def offsetBase(self):
		return self._offset_base

	def setOffset(self, offset):
		self.setPosition(self._offset_base + offset)

	def readToOffset(self, offset, allow_content=True):
		count = offset - self.offset()
		assert (count >= 0)
		x = self.read(count).replace(b"\0", b"")
		if not allow_content and x:
			raise ValueError("Invalid content: {}".format(x))
		return x

	def offsetToPos(self, offset):
		return offset + self._offset_base

	def posToOffset(self, pos):
		return pos - self._offset_base

	def readOffsetString(self, offset):
		pos = self.pos()
		self.setOffset(offset)
		s = self.readString()
		self.setPosition(pos)
		return s
