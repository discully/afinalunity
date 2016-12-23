from pathlib import Path
from AFU.Image import Image
import PIL.Image



class Texture:

	def __init__(self, file_path):
		self.file_path = Path(file_path)
		self.width = None
		self.height = None
		self.image = None
		self._read()


	def __str__(self):
		return "Texture ({0} {1})".format(self.file_path.name, {
			"width":self.width,
			"height":self.height,
		})


	def _read(self):
		
		pil_image = PIL.Image.open(str(self.file_path))
		pil_image = pil_image.convert(mode="RGB")
		pil_pixels = pil_image.load()
		
		self.image = Image(pil_image.width, pil_image.height)
		for x in range(pil_image.width):
			for y in range(pil_image.height):
				self.image.set(pil_pixels[x,y], x, y)
		self.width = pil_image.width
		self.height = pil_image.height
