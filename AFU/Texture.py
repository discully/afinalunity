from pathlib import PurePath
import PIL.Image
import AFU.Image



class Texture:

	def __init__(self, input_file = None):
		self.width = None
		self.height = None
		self.image = None
		self.file_name = ""

		if( input_file != None ):
			self.read(input_file)


	def __str__(self):
		return "Texture ({0} {1})".format(self.file_name, {
			"width":self.width,
			"height":self.height,
		})


	def read(self, f):
		self.file_name = PurePath(f.name()).name
		pil_image = PIL.Image.open(f.file_name)
		pil_image = pil_image.convert(mode="RGB")
		pil_pixels = pil_image.load()
		afu_image = AFU.Image.Image(pil_image.width, pil_image.height)
		for x in range(pil_image.width):
			for y in range(pil_image.height):
				afu_image.set(pil_pixels[x,y], x, y)
		self.image = afu_image
		self.width = pil_image.width
		self.height = pil_image.height
