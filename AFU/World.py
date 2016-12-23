from pathlib import Path
from AFU.File import File



class World:

	def __init__(self, file_path):
		
		self.file_path = Path(file_path)
		
		if( self.file_path.suffix != ".scr" or self.file_path.name[:2] != "sl" ):
			raise ValueError("World only supports sl*.scr files")
		
		self.id = int(self.file_path.stem[2:])
		self._screens = []
		
		self._read()
	
	
	def __getitem__(self, item):
		return self._screens[item]
	
	
	def __len__(self):
		return len(self._screens)


	def __str__(self):
		s = "World {0}:\n".format(self.id)
		s += "  File: {0}\n".format(self.file_path.name)
		s += "  Screens ({0}):\n".format(len(self))
		for screen in self._screens:
			s += "    Screen {0}:\n".format(screen["screen_id"])
			s += "      Background: {0}\n".format(screen["background"])
			s += "      Polygons:   {0}\n".format(screen["polygons"])
			s += "      Entrances:  {0}\n".format(len(screen["entrances"]))
		return s


	def _read(self):
		f = File(self.file_path)

		n_screens = f.readUInt16()

		screens = []
		for i in range(n_screens):
			screen_id = f.readUInt32()
			offset = f.readUInt32()
			screens.append({"screen_id":screen_id, "offset":offset})

		unknown = f.readUInt32()
		unknown = f.readUInt32()

		for screen in screens:
			if( f.pos() != screen["offset"] ):
				raise RuntimeError("Expected to start block at {0} not {1}".format(screen["offset"], f.pos()))

			background_file_name_length = f.readUInt8()
			background_file_name = ""
			screen["background"] = f.readString()

			polygons_file_nane_length = f.readUInt8()
			polygons_file_name = ""
			screen["polygons"] = f.readString()

			n_entrances = f.readUInt8()
			entrances = []
			for i in range(n_entrances):
				entrance_id = f.readUInt8()

				# unknown is 0x1 for every single screen in every world except
				# screen 11 in world 2, where it's 0x8d.
				# If you don't unwind by one byte then, you end up overrunning
				# the block, and the entrance positions are nonsense.
				unknown = f.readUInt8()
				if( unknown != 0x1 ):
					f.setPosition(f.pos() - 1)

				position = []
				for j in range(4):
					position.append( (f.readUInt16(), f.readUInt16()) )
				entrance = {"entrance_id":entrance_id, "unknown":unknown, "position":position}
				entrances.append(entrance)

			screen["entrances"] = entrances

		self._screens = screens
