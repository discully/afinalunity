from pathlib import PurePath



class World:

	def __init__(self, input_file = None):
		self.world_id = None
		self.file_name = ""
		self.screens = []

		if( input_file != None ):
			self.read(input_file)


	def __str__(self):
		s = "World {0}:\n".format(self.world_id)
		s += "  File: {0}\n".format(self.file_name)
		s += "  Screens ({0}):\n".format(len(self.screens))
		for screen in self.screens:
			s += "    Screen {0}:\n".format(screen["screen_id"])
			s += "      Background: {0}\n".format(screen["background"])
			s += "      Polygons:   {0}\n".format(screen["polygons"])
			s += "      Entrances:  {0}\n".format(len(screen["entrances"]))
		return s


	def read(self, f):
		fname = PurePath(f.name())
		self.file_name = fname.name
		if( fname.suffix == ".scr" and len(fname.stem) == 5 and fname.stem[:2] == "sl" ):
			self.world_id = int(fname.stem[2:])

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

				unknown = f.readUInt8()
				if( unknown != 0x1 ):
					f.setPosition(f.pos() - 1)

				position = []
				for j in range(4):
					position.append( (f.readUInt16(), f.readUInt16()) )
				entrance = {"entrance_id":entrance_id, "unknown":unknown, "position":position}
				entrances.append(entrance)

			screen["entrances"] = entrances

		self.screens = screens
