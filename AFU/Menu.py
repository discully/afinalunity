from pathlib import Path
from AFU import Palette, Image, File


class Menu:

	def __init__(self, file_path):

		self.file_path = Path(file_path)

		if self.file_path.suffix not in (".mrg", ".anm", ".pic"):
			raise ValueError("Menu only supports .mrg, .anm and .pic files")

		global_palette_path = Palette.getGlobalPalettePath(file_path)
		self.palette = Palette.fullPalette(global_palette_path, global_palette_path) # todo: This is certainly the wrong local pallette.

		self.offsets = []
		self.images = []

		self._read()


	def __getitem__(self, item):
		return self.images[item]


	def __len__(self):
		"""The number of images in the file"""
		return len(self.images)


	def __str__(self):
		return "Menu ({}) {} images".format(self.file_path, len(self))


	def _read(self):
		f = File.File(self.file_path)

		n_entries = f.readUInt16()
		for i in range(n_entries):
			self.offsets.append(f.readUInt32())

		eof = f.readUInt32()
		for i in range(n_entries):
			
			assert(f.pos() <= self.offsets[i])
			while f.pos() < self.offsets[i]:
				assert(f.readUInt8() == 0)

			width = f.readUInt16()
			height = f.readUInt16()
			image = Image.Image(width, height)

			for y in range(height):
				for x in range(width):
					c = f.readUInt8()
					if c == 13:
						colour = (0,0,0,0)
					else:
						colour = self.palette[c]
					image.set(colour, x, y)

			self.images.append(image)

		assert(f.pos() == eof)


def mrg(mrg_path, background_path=None, palette_path=None):
	
	if background_path is None: background_path = mrg_path.with_name("bridge.rm")
	palette_path = Palette.getGlobalPalettePath(mrg_path, palette_path)
	palette = Palette.fullPalette(background_path, palette_path)

	f = File.File(mrg_path)
	mrg = []

	n_entries = f.readUInt16()

	offsets = [f.readUInt32() for i in range(n_entries)]

	eof = f.readUInt32()
	for i in range(n_entries):
		
		assert(f.pos() <= offsets[i])
		while f.pos() < offsets[i]:
			assert(f.readUInt8() == 0)

		width = f.readUInt16()
		height = f.readUInt16()
		image = Image.Image(width, height)

		for y in range(height):
			for x in range(width):
				c = f.readUInt8()
				if c == 13:
					colour = (0,0,0,0)
				else:
					colour = palette[c]
				image.set(colour, x, y)

		mrg.append(image)

	assert(f.pos() == eof)

	return mrg
