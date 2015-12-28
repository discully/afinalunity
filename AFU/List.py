


class List:
	
	def __init__(self, input_file = None):
		self._entries = []
		if( input_file != None ):
			self.read(input_file)
	
	
	def __len__(self):
		return len(self._entries)
	
	
	def __str__(self):
		s = "List:\n"
		for i in range(len(self)):
			s += "  {0} {1}\n".format(i, self[i])
		return s
	
	
	def __getitem__(self, index):
		if( index < 0 or index >= len(self) ):
			raise IndexError( "List index {0} out of range [0,{1})".format(index, len(self)) )
		return self._entries[index]
	
	
	def read(self, f):
		n = f.readUInt32()
		for i in range(n):
			s = f.readString()
			self._entries.append(s)



def main():
	
	import sys
	if( len(sys.argv) != 2 ):
		print("[USAGE]",__file__,"<filename.lst>")
		return 0
	
	import AFU.File as File
	f = File.File(sys.argv[1])
	
	lst = List(f)
	print(lst)


if __name__ == "__main__":
	main()
