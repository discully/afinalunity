from pathlib import Path
from AFU.File import File
from AFU.Image import Image
from AFU.Palette import Palette
from AFU.Palette import FullPalette


class Menu:
	
	def __init__(self, file_path):
		
		self.file_path = Path(file_path)
		
		if self.file_path.suffix != ".mrg":
			raise ValueError("Menu only supports .mrg files")
		
		standard_palette = Palette(File(self.file_path.with_name("standard.pal")))
		self.palette = FullPalette()
		self.palette.setGlobalPalette(standard_palette)
		self.palette.setLocalPalette(standard_palette)
		
		self.offsets = []
		self.images = []
		
		self._read()
	
	
	def __getitem(self, item):
		return self.images[item]
	
	
	def __len__(self):
		"""The number of images in the file"""
		return len(self.images)
	
	
	def __str__(self):
		return "Menu ({0}) {} images".format(self.file_path, len(self))
	
	
	def _read(self):
		f = File(self.file_path)
		
		n_entries = f.readUInt16()
		for i in range(n_entries):
			self.offsets.append(f.readUInt32())
		
		unknown1 = f.readUInt8()
		unknown2 = f.readUInt8()
		unknown3 = f.readUInt8()
		unknown4 = f.readUInt8()
		
		for i in range(n_entries):
			print(f.pos(), self.offsets[i])
			assert(f.pos() == self.offsets[i])
			
			width = f.readUInt16()
			height = f.readUInt16()
			image = Image(width, height)
			
			for y in range(height):
				for x in range(width):
					colour = self.palette[f.readUInt8()]
					image.set(colour, x, y)
			
			self.images.append(image)
