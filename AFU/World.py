from AFU.File import File



def worldSlScr(file_path):
	f = File(file_path)

	n_screens = f.readUInt16()
	screens = []
	for i in range(n_screens):
		screen_id = f.readUInt32()
		screen_offset = f.readUInt32()
		screens.append( (screen_id,screen_offset) )

	assert( f.readUInt32() == 0xFF )
	eof = f.readUInt32()

	world_screens = []
	for screen_id,screen_offset in screens:
		assert( f.pos() == screen_offset )

		screen = {
			"id": screen_id,
			"entrances": [],
		}

		background_file_length = f.readUInt8()
		background_file = f.readString()
		assert(len(background_file) + 1 == background_file_length)
		screen["background"] = background_file

		polygons_file_length = f.readUInt8()
		polygons_file = f.readString()
		assert(len(polygons_file) + 1 == polygons_file_length)
		screen["polygons"] = polygons_file

		n_entrances = f.readUInt8()
		for i in range(n_entrances):
			entrance_id = f.readUInt8()

			# unknown is 0x1 for every single screen in every world except
			# screen 11 in world 2, where it's 0x8d.
			# If you don't unwind by one byte then, you end up overrunning
			# the block, and the entrance positions are nonsense.
			entrance_unknown = f.readUInt8()
			if( entrance_unknown != 0x1 ):
				f.setPosition(f.pos() - 1)

			entrance_vertices = []
			for j in range(4):
				entrance_vertices.append({"x": f.readUInt16(), "y": f.readUInt16()})
			entrance = {
				"entrance_id": entrance_id,
				"unknown": entrance_unknown,
				"vertices": entrance_vertices,
			}
			screen["entrances"].append(entrance)
		world_screens.append(screen)

	assert(f.pos() == eof)

	return { "screens": world_screens }



def worldStScr(file_path):
	f = File(file_path)

	n_entries = f.readUInt16()
	entries = []
	for i in range(n_entries):
		id = f.readUInt32()
		offset = f.readUInt32()
		entries.append( (id,offset) )

	assert(f.readUInt32() == 0xFF)
	eof = f.readUInt32()

	n_screen_unknown = f.readUInt8()
	screen_unknown = [f.readUInt16() for x in range(n_screen_unknown)]

	screen_polygons = []
	for id,offset in entries:
		assert(f.pos() == offset)

		poly_type = f.readUInt8()
		assert(poly_type in [0,1,3,4])

		assert(f.readUInt16() == 0)

		n_vertices = f.readUInt8()
		poly_vertices = []
		for i in range(n_vertices):
			x = f.readUInt16()
			y = f.readUInt16()
			distance = f.readUInt16()
			poly_vertices.append({
				"x": x,
				"y": y,
				"distance": distance,
				})

		n_poly_unknown = f.readUInt8()
		poly_unknown = []
		for i in range(n_poly_unknown):
			poly_unknown.append((f.readUInt8(), f.readUInt8()))

		assert(f.readUInt16() == 0)

		screen_polygons.append({
			"type": poly_type,
			"vertices": poly_vertices,
			"unknown": poly_unknown,
		})

	assert(f.pos() == eof)

	screen = {
		"unknown": screen_unknown,
		"polgons": screen_polygons,
	}

	return screen
