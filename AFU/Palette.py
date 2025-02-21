from pathlib import Path
from AFU.File import File


_LENGTH_SINGLE = 128
_LENGTH_FULL = 2*_LENGTH_SINGLE


def readFullPalette(f):
	"""Read a full (256 colour) palette from the current position in an open file"""
	return readSinglePalette(f) + readSinglePalette(f)


def readSinglePalette(f):
	"""Read a single (128 colour) palette from the current position in an open file"""
	palette = []
	for i in range(_LENGTH_SINGLE):
		r = f.readUInt8() * 4
		g = f.readUInt8() * 4
		b = f.readUInt8() * 4
		palette.append( (r, g, b) )
	return palette


def fullPalette(local_path, global_path):
	"""Read a full (256 colour) palette, getting the local and global parts from two separate files"""
	local_palette = readSinglePalette(File(local_path))
	global_palette = readSinglePalette(File(global_path))
	return local_palette + global_palette


def singlePalette(palette_path):
	"""Read a single (128 colour) palette from a file"""
	return readSinglePalette(File(palette_path))


def combinePalettes(local_palette, global_palette):
	"""Combine two single (128 colour) palettes into one full (256 colour) palette"""
	return local_palette + global_palette


def replaceLocalPalette(full_palette, new_local_palette):
	if not len(new_local_palette) == _LENGTH_SINGLE:
		raise ValueError("New local palette's length ({}) does not match the required size ({})", len(new_local_palette), _LENGTH_SINGLE)
	full_palette[:_LENGTH_SINGLE] = new_local_palette


def replaceGlobalPalette(full_palette, new_global_palette):
	if not len(new_global_palette) == _LENGTH_SINGLE:
		raise ValueError("New global palette's length ({}) does not match the required size ({})", len(new_global_palette), _LENGTH_SINGLE)
	full_palette[_LENGTH_SINGLE:] = new_global_palette


def getGlobalPalettePath(image_path, palette_path=None):
	# First, if a palette path was explicitly provided, check that
	if not palette_path is None:
		if palette_path.is_file():
			return palette_path
		else:
			raise ValueError("Palette provided is not a file: {}".format(palette_path))
	
	# Second, look alongside the image for the usual standard palette
	palette_path = image_path.with_name("standard.pal")
	if palette_path.is_file():
		return palette_path
	
	# Finally, look in the working directory for the usual standard palette
	palette_path = Path("standard.pal")
	if palette_path.is_file():
		return palette_path
	
	raise RuntimeError("Could not find the palette standard.pal and no alternative was provided")
