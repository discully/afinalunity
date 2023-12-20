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

	unknown0 = [f.readUInt16() for x in range(8)]
	enterprise_warp = round(float(f.readUInt32()) / 100.0, 1)
	# aststat.dat offset = 0x14
	enterprise_current_x = f.readUInt32()
	enterprise_current_y = f.readUInt32()
	enterprise_current_z = f.readUInt32()
	enterprise_origin_x = f.readUInt32()
	enterprise_origin_y = f.readUInt32()
	enterprise_origin_z = f.readUInt32()
	enterprise_destination_x = f.readUInt32()
	enterprise_destination_y = f.readUInt32()
	enterprise_destination_z = f.readUInt32()
	#fpos(f)
	previous_location_values = [f.readUInt32() for i in range(2)]
	assert(f.readUInt32() == 0x0)
	assert(f.readUInt32() == 0x0)
	assert(f.readUInt32() == 0x0)
	assert(f.readUInt32() == 0x0)
	destination_location_values = [f.readUInt32() for i in range(2)]
	assert(f.readUInt32() == 0x0)
	
	# aststat.dat offset = 0x5c
	previous_location_info = readLocationInfo(f)
	prev_system_id = f.readUInt16()
	if prev_system_id == 255 and previous_location_info["system_index"] is None:
		prev_system_id = None
	previous_location_info["system_id"] = prev_system_id
	previous_location_info["location_type"] = readLocationType(f)
	
	#fpos(f)
	destination_location_info  = readLocationInfo(f)
	assert(f.readUInt16() == 0x0)
	destination_location_info["location_type"] = readLocationType(f)
	
	unknown1a = [f.readUInt8() for x in range(444)]
	unknown1b = [f.readUInt16() for x in range(6)]
	
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
	# 2a6 [u16] display_is_rotating ???code<-
	# 2a8 [u32] display_is_rotating ???ghidra
	# 2ac [u32] unknown_sector_id
	#

	# (astrogation)
	# ast_stat.dat offset = 2e0 = 25c + (21*4)

	astrogation_which_screen = f.readUInt8() # 0=space, 1=sector, 2=system
	#assert(f.readUInt8() == 0) # padding
	print(f.readUInt8()) # padding?

	astrogation_speed_mode = "warp" if f.readUInt16() == 0 else "impulse"
	astrogation_speed_warp = round(float(f.readUInt32()) / 100.0, 1)
	astrogation_speed_impulse = f.readUInt32() * 10
	astrogation_max_warp = f.readUInt32()
	
	unknown2a = [f.readUInt32() for x in range(6)]

	astrogation_distance1 = f.readDouble()
	astrogation_distance2 = f.readDouble()

	unknown2b = [f.readUInt32() for i in range(2)]
	
	selected_major_x = f.readUInt32()
	selected_major_y = f.readUInt32()
	selected_major_z = f.readUInt32()
	selected_minor_x = f.readUInt32()
	selected_minor_y = f.readUInt32()
	selected_minor_z = f.readUInt32()
	
	unknown2c = [f.readUInt32() for i in range(2)]
	selected_location_info["location_values"] = [f.readUInt16() for x in range(2)]

	astrogation_a_deg = f.readUInt16()
	astrogation_e_deg = f.readUInt16()
	
	unknown2d = [f.readUInt16() for x in range(7)]

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
	
	astrogation_rotating = f.readUInt16() == 1
	unknown5 = [f.readUInt32() for x in range(2)]

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
			#  4      0100 [   x1] invisible, only Lethe Beta (it has 7 planets. If you set to 5, the description doesn't inlclude the number of planets, the view shows no planets. If you set to 9, the description does)
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
		"unknown0": unknown0,
		"enterprise": {
			"current": (enterprise_current_x, enterprise_current_y, enterprise_current_z),
			"destination": (enterprise_destination_x, enterprise_destination_y, enterprise_destination_z),
			"origin": (enterprise_origin_x, enterprise_origin_y, enterprise_origin_z),
			"warp": enterprise_warp,
		},
		"previous_location_values": previous_location_values,
		"destination_location_values": destination_location_values,
		"previous_location_info": previous_location_info,
		"destination_location_info": destination_location_info,
		"unknown1a": unknown1a,
		"unknown1b": unknown1b,
		"unknown1c": unknown1c,
#		"unknown1d": unknown1d,
		"astrogation": {
			"course": {
				"speed_mode": astrogation_speed_mode,
				"speed_warp": astrogation_speed_warp,
				"speed_impulse": astrogation_speed_impulse,
			},
			"space_rotation_a": astrogation_a_deg,
			"space_rotation_e": astrogation_e_deg,
			"space_rotating": astrogation_rotating,
			"selected": {
				"info": selected_location_info,
				"major_coords": (selected_major_x, selected_major_y, selected_major_z),
				"minor_coords": (selected_minor_x, selected_minor_y, selected_minor_z),
#				"system_unknown": selected_system_unknown,
#				"location_unknown": selected_location_unknown,
			},
			"display": display,
			"which_screen": astrogation_which_screen,
		},
		"unknown2a": unknown2a,
		"unknown2c": unknown2c,
		"unknown2d": unknown2c,
		"unknown5": unknown5,
		"systems_bodies": systems_bodies,
		"stations": stations,
	}
