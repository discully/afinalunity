from AFU.Astro import ObjectType
from AFU.AstroUtils import N_SECTORS
from AFU.File import fpos


def readLocationType(f):
	t = f.readUInt16()
	if t == 0xffff or t == 0:
		return None
	return ObjectType(t)


def readLocationInfo(f):
	sector_id = f.readUInt16()
	system_index = f.readUInt16()
	if system_index == 0xffff:
		system_index = None
	planet_index = f.readUInt16()
	if planet_index == 0xffff:
		planet_index = None
	moon_index = f.readUInt16()
	if moon_index == 0xffff:
		moon_index = None
	station_index = f.readUInt16()
	if station_index == 0xffff:
		station_index = None
	body_index = f.readUInt16()
	if body_index == 0xffff:
		body_index = None
	return {
		"sector_id": sector_id,
		"system_index": system_index,
		"planet_index": planet_index,
		"moon_index": moon_index,
		"station_index": station_index,
		"body_index": body_index,
	}


def readAstroState(f):

	# Definitions:
	# 	current = where the enterprise is at that moment
	# 	origin = where the enterprise set off from, last time you pressed 'engage'
	# 	destination = where the enterprise is going to when travelling, or 'current' when not travelling
	# 	previous = 'origin' when travelling, 'current' when not travelling
	#	selected = the most recent object chosen in the astrogation menu

	journey_time_start = f.readUInt32()
	journey_time_total = f.readFloat()
	journey_progress = f.readFloat()
	journey_is_moving = (False, True)[f.readUInt32()]

	#current_warp = round(float(f.readUInt32()) / 100.0, 1) # TODO: Think this is just 'speed' and won't work if at Impulse
	speed = f.readUInt32()
	#if speed <= 10:
	#	speed *= 100
	#else:
	#	speed = round(float(f.readUInt32()) / 100.0, 1)
	# aststat.dat offset = 0x14
	current_space_coords = [f.readUInt32() for i in range(3)]
	origin_space_coords = [f.readUInt32() for i in range(3)]
	destination_space_coords = [f.readUInt32() for i in range(3)]
	current_system_coords = [f.readUInt32() for i in range(3)]
	origin_system_coords = [f.readUInt32() for i in range(3)]
	destination_system_coords = [f.readUInt32() for i in range(3)]
	
	# aststat.dat offset = 0x5c
	origin_location_info = readLocationInfo(f) # 6 ushorts
	prev_system_id = f.readUInt16()
	if prev_system_id == 255 and origin_location_info["system_index"] is None:
		prev_system_id = None
	origin_location_info["system_id"] = prev_system_id
	origin_location_info["location_type"] = readLocationType(f)
	
	destination_location_info  = readLocationInfo(f)
	assert(f.readUInt16() == 0x0)
	destination_location_info["location_type"] = readLocationType(f)

	destination_name = f.readStringBuffer(64)
	unknown_graphic_data = [f.readUInt8() for i in range(384)]
	unknown_flags = [f.readUInt8() for i in range(2)]
	is_impulse = (False, True)[f.readUInt8()]

	if is_impulse:
		speed *= 10
	else:
		speed = round(float(speed) / 100.0, 1)

	unknown_flags.append(f.readUInt8())
	journey_distance_space = f.readFloat() # not sure about what this is yet
	
	selected_location_info = readLocationInfo(f)
	
	unknown1c = [f.readUInt16() for x in range(6)]
	
	# aststat.dat offset = 0x25c
	#
	# 25c [u8 ] which_screen (0=space, 1=sector, 2=system)
	# 25d [u8 ]
	# 25e [u16] current_speed_mode (0=warp, 1=impulse)
	# 260 [u32] current_warp
	# 264 [u32] current_impulse
	# ---------------------------------------u2a
	# 268 [u32] maximum_warp
	# 26c [u32]
	# 270 [u32]
	# 274 [u32]
	# 278 [u32]
	# 27c [u32]
	# 280 [u32]
	# ---------------------------------------u2c
	# 284 [dbl] distance_to_dest_sys ?
	# 28c [dbl] distance_to_dest
	# 294 [u32]
	# 298 [u32]


	# ---------------------------------------end u2c
	# 29c [u32] selected_major_x
	# 270 [u32] selected_major_y
	# 274 [u32] selected_major_z
	# 278 [u32] selected_minor_x
	# 27c [u32] selected_minor_y
	# 280 [u32] selected_minor_z
	# 284 [u32]  ??? selected_system_z
	# 288 [u32]  ??? selected_system_y
	# 28c [u16]  ??? selecteed_system_x
	# 28e [u16] 
	# 290 [u16] a_deg
	# 292 [u16] e_deg
	# 294 [u16]*5
	# 29e [u16]
	# 2a0 [u16]
	# 2a2 [u16] display_which_systems
	# 2a4 [u16] display_which_features
	# 2a6 [u16] display_is_rotating -
	# 2a8 [u32] display_is_rotating 
	# 2ac [u32] unknown_sector_id
	#

	# (astrogation)
	# ast_stat.dat offset = 2e0 = 25c + (21*4)

	astrogation_which_screen = ("space", "sector", "system")[f.readUInt8()]
	astrogation_which_panel = ("info", "course", "display")[f.readUInt8()]

	astrogation_speed_mode = ("warp", "impulse")[f.readUInt16()]
	astrogation_speed_warp = round(float(f.readUInt32()) / 100.0, 1)
	astrogation_speed_impulse = f.readUInt32() * 10
	astrogation_max_warp = round(float(f.readUInt32()) / 100.0, 1)
	
	astrogation_dist = {}
	astrogation_dist["light_years"] = f.readUInt32()
	astrogation_dist["light_months"] = f.readUInt32()
	astrogation_dist["light_days"] = f.readUInt32()
	astrogation_dist["light_hours"] = f.readUInt32()
	astrogation_dist["light_minutes"] = f.readUInt32()
	astrogation_dist["light_seconds"] = f.readUInt32()

	astrogation_distance1 = f.readDouble()
	astrogation_distance2 = f.readDouble()
	astrogation_x1 = f.readUInt32()
	astrogation_x2 = f.readUInt32()
	
	selected_major_coords = [f.readUInt32() for i in range(3)]
	selected_minor_coords = [f.readUInt32() for i in range(3)]
	selected_system_coords = [f.readUInt32() for i in range(3)]

	astrogation_a_deg = f.readUInt16()
	astrogation_e_deg = f.readUInt16()

	assert(f.readUInt16() == 0) # Game sets this to zero, but never reads it.
	
	for i in range(10): # Unused
		assert(f.readUInt8() == 0)
	
	# Tested but not set by the game.
	# Will only draw certain systems/planets if this value matches some flags which are set.
	# Those flags are:
	# When drawing the Space screen:
	#     * 0x1 if  Inhabited and UNKNOWN_SCAN is set
	#     * 0x2 if  UNKNOWN_LETHE is set
	# When drawing thje System screen
	#     * 0x1 if  Inhabited
	#     * 0x2 if  UNKNOWN_LETHE is set
	#     * 0x4 if  Starbase
	assert(f.readUInt16() == 0) # Could be a series of flags, shwowing what to disply, but never set.

	d0 = f.readUInt16()
	d1 = f.readUInt16()
	display = {
		"federation": (d0 & 0b00000001) != 0,
		"romulan": (d0 & 0b00000010) != 0,
		"neutral": (d0 & 0b00000100) != 0,
		"nebula": (d0 & 0b00001000) != 0,
		"nonaligned": (d0 & 0b00010000) != 0,
		"grid": (d1 & 0b00000001) != 0,
		"stars": (d1 & 0b00000010) != 0,
		"inhabited": (d1 & 0b00000100) != 0,
		"starbases": (d1 & 0b00001000) != 0,
	}
	
	astrogation_rotating = (False,True)[f.readUInt16()]
	unknown5 = f.readUInt32()
	astrogation_selected_sector_id = f.readUInt32()

	assert(f.readUInt16() == 0)

	sector_end = []
	for i in range(N_SECTORS):
		sector_end.append(f.readUInt16())

	object_id = 0
	
	# aststat.dat offset = 0x6e2 = 0x25c + 0x486

	systems_bodies = {}
	for sector_id,end in enumerate(sector_end):
		while object_id < end:
			state = f.readUInt16()

			# What does this value mean...
			#              [x3853]
			#  0      0000 [x1123] invisible, unscanned
			#  1      0001 [x1322] visible,  unscanned
			#  4      0100 [   x1] invisible, only Lethe Beta (it has 7 planets. If you set to 5 (101), the description doesn't inlclude the number of planets, the view shows no planets. If you set to 9 (1001), the description does)
			#  5      0101 [ x263] Only stellar bodies (no star systems). No obvious difference from 1.
			#  6      0110 [   x1] invisible, only Lethe Zeta
			#  9      1001 [ x392] visible, scanned (but if there's no planets, the system view says 'unscanned', even though the description suggests sanned). One body, all the rest are systems.
			# 13      1101 [ x746] visible, scanned (if there's no planets, the system view is correct - but some of these systems have multiple planets too). Five bodies, all the rest are systems.
			# 29 0001 1101 [   x5] 13 + story planet  (x5: M'kyru Zeta (Palmyra), Tothe Delta (horst), Euterpe Epsilon (Morassia), Steger Delta (Cymkoe), Kamyar Delta (Yajj))

			#  0000 0000
			#          ^---- visible? "uncharted"
			#         ^----- 4: Lethe Zeta only
			#        ^------ 5,6: ???
			#       ^------- scanned?
			#     ^--------- story point?

			# M'kyru Zeta (Palmyra)      - If you don't fight the original Garidian warbird, the scout ship self destructs, and you detect escape pods here
			# Tothe Delta (Horst)        - Where Vulcan archeologist Shanok is based
			# Euterpe Epsilon (Morassia) - Location where Vie Hunfrsch goes missing
			# Steger Delta (Cymkoe IV)   - Location of Mertens Orbital Station (video on arrival)
			# Kamyar Delta (Yajj)        - Location of Outpost Delta-0-8

			# x & 1 != 1     -> Uncharted
			# x & 4 == 0     -> Unscanned
			# (x & 4 == 0) && (x & 8 == 0)    =Unscanned

			state_visible = (state & 0b00000001) != 0
			state_scanned = (state & 0b00001000) != 0
			systems_bodies[object_id] = {
				"sector_id": sector_id,
				"object_id": object_id,
				"state": state,
				"visible": state_visible,
				"scanned": state_scanned,
			}
			object_id += 1
	
	stations = {}
	for i in range(64):
		stations[object_id] = f.readUInt16()
		object_id += 1
		# What does this value mean?
		# Each station type has only one value:
		#     starbase: 0
		#     outpost: 0
		#     buoy: 1
		#     comm relay: 13
		#     deep space station: 1
		# I suspect the states might vary more after the Chodak invasion, when a
		# a lot of the comm relays etc. become destroyed. Will need to investigate.
	
	return {
		"ship": {
			"journey_time_start": journey_time_start,
			"journey_time_total": journey_time_total,
			"journey_progress": journey_progress,
			"journey_is_moving": journey_is_moving,
			
			"current_space_coords": current_space_coords,
			"destination_space_coords": destination_space_coords,
			"origin_space_coords": origin_space_coords,
			"current_system_coords": current_system_coords,
			"destination_system_coords": destination_system_coords,
			"origin_system_coords": origin_system_coords,
			"current_speed": speed, #current_warp,
			"previous_location_info": origin_location_info,
			"destination_location_info": destination_location_info,
			"destination_name": destination_name,
			"unknown_graphic_data": unknown_graphic_data,
			"unknown_flags": unknown_flags,
			"is_impulse": is_impulse,
			"journey_distance_space": journey_distance_space,
			"unknown1c": unknown1c,
		},
		"astrogation": {
			"course": {
				"speed_mode": astrogation_speed_mode,
				"speed_warp": astrogation_speed_warp,
				"speed_impulse": astrogation_speed_impulse,
				"speed_warp_max": astrogation_max_warp,
				"distance": astrogation_dist,
				"distance_1": astrogation_distance1,
				"distance_2": astrogation_distance2,
				"x1": astrogation_x1,
				"x2": astrogation_x2,
			},
			"space_rotation_a": astrogation_a_deg,
			"space_rotation_e": astrogation_e_deg,
			"space_rotating": astrogation_rotating,
			"selected": {
				"info": selected_location_info,
				"major_coords": selected_major_coords,
				"minor_coords": selected_minor_coords,
				"system_coords": selected_system_coords,
			},
			"selected_sector_id": astrogation_selected_sector_id,
			"display": display,
			"which_screen": astrogation_which_screen,
			"which_panel": astrogation_which_panel,
		},
		"unknown5": unknown5,
		"systems_bodies": systems_bodies,
		"stations": stations,
	}
