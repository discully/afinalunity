from enum import IntEnum, Enum
from pathlib import Path
from AFU.File import File, DatabaseFile, fpos



# Functions for handling co-ordinates
# The game space consists of an 8x8x8 grid (512 major co-ordinates), each cube in the grid is a "sector".
# Each sector has a 20*20*20 grid (8000 minor co-ordinates), some of which will contain a star "system".


N_SECTORS = 512 # 8x8x8

def globalCoords(major_coords, minor_coords):
	return tuple(major*20 + minor for major,minor in zip(major_coords,minor_coords))


def minorCoords(global_coords):
	return (global_coords[0] % 20, global_coords[1] % 20, global_coords[2] % 20)


def majorCoords(global_coords):
	return (global_coords[0] // 20, global_coords[1] // 20, global_coords[2] // 20)


PLANET_CLASSES = "ABCDEFGHIJKLMNST"
STAR_CLASSES = "OBAFGKM-."
DWARF_NAMES = ["black", "brown", "red", "white"]
PLANET_DESCRIPTIONS = [
		"Gas supergiant planet within its star's cold zone. Thick atmosphere of hydrogen and hydrogen compounds. High core temperature. No known lifeforms.",
		"Gas giant planet within its star's cold zone. Thick atmosphere of hydrogen and hydrogen compounds. No known lifeforms.",
		"Within its star's habitable zone. Dense carbon dioxide atmosphere. Very hot surface, water only found in vapor form. No known lifeforms.",
		"Within its star's habitable zone. Newly formed, surface still molten. Atmosphere contains many hydrogen compounds, plus reactive gases and rock vapors. No known lifeforms.",
		"Within its star's habitable zone. Newly formed, surface thin. Atmosphere contains many hydrogen compounds. No known lifeforms.",
		"Within its star's habitable zone. Young world, surface still crystallizing. Atmosphere contains small amounts of toxic gases. No known lifeforms.",
		"Within its star's hot zone. Surface very hot. Atmosphere contains heavy gases and metal vapors. No known lifeforms.",
		"Small planet within its star's cold zone. Newly formed, surface still molten. Atmosphere contains many hydrogen compounds, plus reactive gases and rock vapors. No known lifeforms.",
		"Very small planet. Low gravity, surface heavily cratered. No appreciable atmosphere. No known lifeforms.",
		"Within its star's hot zone. Surface very hot. Atmosphere tenuous, with few chemically active gases. No known lifeforms.",
		"Small planet within its star's habitable zone. Tenuous atmosphere. Some water present on the surface. No known lifeforms.",
		"Small planet within its star's cold zone. Atmosphere permanently frozen. No known lifeforms.",
		"Within its star's habitable zone. Liquid surface water. Atmosphere contains significant amounts of oxygen. No known lifeforms.",
		"Within its star's habitable zone. Liquid water covers 98% of surface. Atmosphere contains significant amounts of oxygen. No known lifeforms.",
		"Gas ultragiant within its star's cold zone. High core temperature causes it to radiate visible light. Thick atmosphere of hydrogen and hydrogen compounds. No known lifeforms.",
		"Gas supergiant within its star's cold zone. High core temperature. Some liquid water is present on surface. Thick atmosphere of hydrogen and hydrogen compounds. No known lifeforms.",
	]



class Alignment (Enum):
	FEDERATION = 0
	ROMULAN = 1
	NEUTRAL = 2
	NEBULA = 3
	NONALIGNED = 4


class ObjectType (Enum):
	STAR_SYSTEM = 32
	PLANET = 33
	MOON = 34
	# ANTIMATTER_CLOUD = 64
	ION_STORM = 65
	QUASAROID = 66
	# ROGUE_PLANET = 67
	BLACK_HOLE = 68
	SUBSPACE_VORTEX = 69
	UNITY_DEVICE = 72
	SPECIAL_ITEM = 73 # Alien device, Unity device, Ruinore sector, Ayers, Singelea sector
	DEEP_SPACE_STATION = 128
	COMM_RELAY = 129
	BUOY = 130
	STARBASE = 131
	OUTPOST = 132



#
# Sector
#



def readSector(f):
	sector_id = f.readUInt32()
	sector_n_systems = f.readUInt32()
	sector_n_bodies = f.readUInt32()
	sector_n_stations = f.readUInt32() # Only used in astromap.db, always 0 in astro.db
	sector_alignment = f.readUInt32()
	sector_ptr_systems = f.readUInt32()
	sector_ptr_bodies = f.readUInt32()
	sector_ptr_stations = f.readUInt32()
	sector_ptr_description = f.readUInt32()

	sector_x = (sector_id >> 0) & 0b111
	sector_y = (sector_id >> 3) & 0b111
	sector_z = (sector_id >> 6) & 0b111

	return {
		"id": sector_id,
		"coords_major": (sector_x, sector_y, sector_z),
		"n_systems": sector_n_systems,
		"n_bodies": sector_n_bodies,
		"n_stations": sector_n_stations,
		"alignment": Alignment(sector_alignment),
	}


def sectorDescription(sector):
	d = "This sector is {}."
	if sector["alignment"] == Alignment.FEDERATION:
		return d.format("aligned with the Federation")
	elif sector["alignment"] == Alignment.ROMULAN:
		return d.format("aligned with the Romulans")
	elif sector["alignment"] == Alignment.NEUTRAL:
		return d.format("in the neutral zone")
	elif sector["alignment"] == Alignment.NEBULA:
		return d.format("in the Z'Tarnis Nebula")
	elif sector["alignment"] == Alignment.NONALIGNED:
		return d.format("nonaligned")
	raise ValueError("Invalid sector alignment: {}".format(sector["alignment"]))


#
# Star Systems
#

# System Flags is a bitfield, but it means subtly different things in astro.db and astromap.db.
# In both files, the first two bits indicate if the system is a White Dwarf or Binary system.
# In astromap.db the third and fourth bits contains information on stations (outposts and starbases),
# but these bits are unused in astro.db.
# The fifth bit is more confusing. In astro.db it indicates is the system contains an inhabited planet.
# In astromap.db it means something else that I haven't determined (545 systems have it set).
# All the remaining bits are unused.
#
# 00000000
#        ^_ white dwarf?
#       ^__ binary?
#      ^___ contains station? - if true, check next bit to see what type (astromap.db only)
#     ^____ outpost? - if true, outpost. if false, starbase (astromap.db only)
#    ^_____ inhabited? (astro.db only), unknown state (atromap.db only)


class SystemFlags (Enum):
	WHITE_DWARF = 0x1
	BINARY = 0x2
	STATION = 0x4
	OUTPOST = 0x8
	INHABITED = 0x10


def systemInhabited(flags, is_astromap):
	# Only works in astro.db. Used for unknown-state in astromap.db
	if not is_astromap:
		return (0b0000000000010000 & flags) != 0
	else:
		return None


def systemUnknownState(flags):
	# Only works in astromap.db, and don't know what it means. Used for 'inhabited' in astro.db
	return (0b0000000000010000 & flags) != 0


def systemBinary(flags):
	return (0b0000000000000010 & flags) != 0


def systemWhiteDwarf(flags):
	return (0b0000000000000001 & flags) != 0


def systemStation(flags):
	# Only set in astromap.db
	return (0b0000000000000100 & flags) != 0


def systemStarbase(flags):
	# Only set in astromap.db
	return systemStation(flags) and (0b0000000000001000 & flags) != 0


def systemOutpost(flags):
	# Only set in astromap.db
	return systemStation(flags) and (0b0000000000001000 & flags) == 0


def systemTitle(system):
	t = system["name"]
	if "alias" in system:
		t += " (" + system["alias"] + ")"
	if "description" in system:
		t += " " + system["description"]
	return t


def systemDescription(system):
	stellar = "white dwarf" if system["white_dwarf"] else "star"
	d = "This is a class {0[class]} {1} with an absolute magnitude of {0[magnitude]}.".format(system, stellar)

	if system["binary"]:
		d += " It belongs to a binary star system, with a class ??? sister star of absolute magnitude ???.".format(
			system)

	if system["planets"] == 0:
		d += " It posesses no planets."
	elif system["planets"] == 1:
		d += " It posesses 1 planet, "
	else:
		d += " It posesses {} planets, ".format(system["planets"])

	if system["inhabited"]:
		assert(system["planets"] > 1)
		d += "one of which is known to be inhabited."  # todo: Are there any systems with more than one inhabited planet?
	elif len(system["planets"]) == 1:
		d += "which is known to be uninhabited."
	elif len(system["planets"]) == 2:
		d += "neither of which is known to be inhabited."
	else:
		d += "none of which is known to be inhabited."

	for station in system["stations"]:
		d += " {0[name]} orbits this system.".format(station)

	if not system["scanned"]:
		d += " This star is currently unscanned."

	if system["asteroid_belt"]:
		d += " This star system has an asteroid belt."

	return d


def readSystem(f):
	system_index = f.readUInt32()
	system_id = f.readUInt16()
	system_type = f.readUInt16()
	system_random_seed = f.readUInt32()
	system_x = f.readUInt32()
	system_y = f.readUInt32()
	system_z = f.readUInt32()
	system_ptr_description = f.readUInt32()
	system_name_offset = f.readUInt32()
	system_flags = f.readUInt16()
	system_station_orbit = f.readUInt8() # In astromap.db the orbit of the station (0 is between first and second planet, 1: between second and third, etc). 0 in astro.db.
	system_station_type = f.readUInt8() # In astromap.db could also be either station (131) or outpost (132). 0 in astro.db.
	system_class = f.readUInt16()
	system_magnitude = f.readSInt16()
	system_unknown2 = f.readUInt32() # Used as some kind of random variable in generating things at execution
	system_n_planets = f.readUInt32()
	system_alias_offset = f.readUInt32()
	system_notable_name_offset = f.readUInt32()
	system_notable_desc_offset = f.readUInt32()
	system_ptr_planets = f.readUInt32()
	system_ptr_station = f.readUInt32()

	assert(system_type == ObjectType.STAR_SYSTEM.value)
	assert(system_ptr_description == 0) # Set during execution
	assert(system_n_planets == 0) # Set during execution
	assert(system_ptr_planets == 0) # Set during execution
	
	system = {
		"index": system_index,
		"id": system_id,
		"type": ObjectType(system_type),
		"random_seed": system_random_seed,
		"coords": (system_x, system_y, system_z),
		"_offset_name": system_name_offset,
		"flags": system_flags,
		"station_orbit": system_station_orbit,
		"station_type": system_station_type,
		"star_class_int": system_class,
		"star_class": STAR_CLASSES[system_class // 10] + str(system_class % 10),
		"star_mag": system_magnitude / 10.0,
		"unknown2": system_unknown2,
		"_offset_alias": system_alias_offset,
		"_offset_notable_name": system_notable_name_offset,
		"_offset_notable_desc": system_notable_desc_offset,
		"_offset_station": system_ptr_station,
	}

	#if systemStation(system_flags):
	#	system["stations"] = []
	#	system["stations"].append({
	#		"type": SectorObjects(system_station_type),
	#		"coords": (system_x, system_y, system_z),
	#		"orbit": system_station_orbit,
	#		"system_index": system_index,
	#	})

	return system



#
# Astronomical Bodies
#


def bodyDescription(body):
	if body["type"] == ObjectType.SPECIAL_ITEM:  # Special item (Alien device, Unity device, Ruinore sector, USS Ayers, Singelea sector)
		return ""

	d = "{0[name]}: ".format(body)
	if body["type"] == ObjectType.ION_STORM:
		d += "Reduced sensor range, Hull Erosion danger -- use caution -- possible systems damage in high-gradient areas."
	elif body["type"] == ObjectType.QUASAROID:
		d += "Extreme Radiation & Subspace Distortion danger -- avoid!"
	elif body["type"] == ObjectType.BLACK_HOLE:
		d += "Gravity, Radiation, & Subspace Distortion danger -- avoid!"
	elif body["type"] == ObjectType.SUBSPACE_VORTEX:
		d += "Subspace Distortion danger -- use warp drive with care -- strong warp drive stress, possible coil failure."
	d += " Known zone of influence: {0[zone_radius]} light-years".format(body)
	return d


def readBody(f):
	body_index = f.readUInt32()
	body_id = f.readUInt16()
	body_type = f.readUInt16()  # Ion Storm, Quasaroid, Black Hole, Subspace Vortex, Special item
	body_random_seed = f.readUInt32()
	body_x = f.readUInt32()
	body_y = f.readUInt32()
	body_z = f.readUInt32()
	body_ptr_desc = f.readUInt32()
	body_name_offset = f.readUInt32()
	body_zone_radius = f.readUInt32()  # radius of known zone of influence, in LY
	body_unknown0 = f.readUInt32() # todo: 0 in astro.db, non-zero in astromap.db

	assert(body_random_seed == 0) # Set during execution
	assert(body_ptr_desc == 0) # Set during execution

	return {
		"index": body_index,
		"id": body_id,
		"type": ObjectType(body_type),
		"coords": (body_x, body_y, body_z),
		"_offset_name": body_name_offset,
		"zone_radius": body_zone_radius,
		"unknown0": body_unknown0,
	}



#
# Stations
#



def readStation(f):
	station_index = f.readUInt32()
	station_id = f.readUInt16()
	station_type = f.readUInt16()
	station_random_seed = f.readUInt32()
	station_x = f.readUInt32()
	station_y = f.readUInt32()
	station_z = f.readUInt32()
	station_ptr_desc = f.readUInt32()
	station_name_offset = f.readUInt32()
	station_sector_id = f.readUInt16()
	station_system_index = f.readUInt8()  # index of the system within the sector this belongs to
	station_orbit = f.readUInt8()  # location of outpost within system (0: between first and second planet, 1: between second and third, etc.)

	assert(station_index == 0)
	assert(station_random_seed == 0)
	assert(station_ptr_desc == 0)

	return {
		"id": station_id,
		"type": ObjectType(station_type),
		"coords": (station_x, station_y, station_z),
		"_offset_name": station_name_offset,
		"sector_id": station_sector_id,
		"system_index": station_system_index,
		"orbit": station_orbit,
	}


def stationDescription(station):
	d = "This is a Federation "
	if station["type"] == ObjectType.DEEP_SPACE_STATION:
		d += "Deepspace Station"
	elif station["type"] == ObjectType.COMM_RELAY:
		d += "subspace communications relay"
	elif station["type"] == ObjectType.BUOY:
		d += "navigational & scanning buoy"
	elif station["type"] == ObjectType.STARBASE:
		d += "Starbase"
	elif station["type"] == ObjectType.OUTPOST:
		d += "Outpost"
	else:
		raise ValueError("Unknown station type: {}".format(station["type"]))
	d += ". Current status of this unit is: Fully Operational"
	return d

	# In sttng.ovl, strings are found at file offsets...
	# 1384888:Fully Operational.
	# 1384909:Operational -- Awaiting Resupply.
	# 1384945:Partially Operational.
	# 1384970:Non-operational.
	# 1384989:Unknown -- contact lost.



#
# Astro State
#


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


def readLocationType(f):
	t = f.readUInt16()
	if t == 0xffff or t == 0:
		return None
	return ObjectType(t)


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
	fpos(f)
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
	
	fpos(f)
	destination_location_info  = readLocationInfo(f)
	assert(f.readUInt16() == 0x0)
	destination_location_info["location_type"] = readLocationType(f)
	
	unknown1a = [f.readUInt8() for x in range(444)]
	unknown1b = [f.readUInt16() for x in range(6)]
	
	selected_location_info = readLocationInfo(f)
	
	unknown1c = [f.readUInt16() for x in range(6)]
	
	# aststat.dat offset = 0x25c

	unknown1d = f.readUInt16()

	astrogation_speed_mode = "warp" if f.readUInt16() == 0 else "impulse"
	astrogation_speed_warp = round(float(f.readUInt32()) / 100.0, 1)
	astrogation_speed_impulse = f.readUInt32() * 10

	# all but the first of these changes when you change impulse speed, or between impulse and warp.
	# The first three don't change when you change warp speed. The second and third are 0 when in warp mode
	# If you change the selected system it also updates.
	# Perhaps some kind of estimated time to arrival? Or course information?
	
	unknown2a = [f.readUInt8() for x in range(21)]

	# aststat.dat offset = 0x2ed = 0x25c + 0x21

	unknown2b = [f.readUInt8() for x in range(7)]
	
	
	# some of these change when you change warp/impulse speed
	unknown2c = [f.readUInt16() for x in range(16)]
	selected_x = f.readUInt32()
	selected_y = f.readUInt32()
	selected_z = f.readUInt32()
	selected_system_unknown = f.readUInt32() # unknown value, changes with system selected
	assert(f.readUInt32() == 0x0)
	selected_location_unknown = f.readUInt32() # unknown value, changes with planet/moon/outpost selected
	selected_location_info["location_values"] = [f.readUInt16() for x in range(2)]
	astrogation_a_deg = f.readUInt16()
	astrogation_e_deg = f.readUInt16()
	unknown4 = [f.readUInt16() for x in range(7)]

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
	unknown5 = [f.readUInt16() for x in range(5)]
	
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

			# GHIDRA
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
	fpos(f)
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

		#Ghidra:
		# if param_5...
		# 	if status & 0x10 == 0:
		#		if starbase or outpost or comm relay:
		# 			status = "Current status of this unit is: Fully Operational.
		# 		else:
		#			status = "Current status of this unit is: "
		#	 		switch Utils_Random(4):
		#				0: "Fully Operational."
		#				1: "Operational -- Awaiting Resupply."
		#				2: "Partially Operational."
		#				3: "Non-operational."
		#				4: "Unknown -- contact lost. stardate 46254.5.  "
		# 	else if outpost:
		# 		if id == 0xf4a:
		# 			status = "Federation Outpost destroyed by alien invasion force." 
		# 		else:
		#			status = "Outpost destroyed by Romulan fleet."
		# 	else if comm relay:
		# 		status = "Relay destroyed by Romulan fleet."
		# else:
		#	
	fpos(f)
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
		"unknown1d": unknown1d,
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
				"coords": (selected_x, selected_y, selected_z),
				"system_unknown": selected_system_unknown,
				"location_unknown": selected_location_unknown,
			},
			"display": display,
		},
		"unknown2a": unknown2a,
		"unknown2b": unknown2b,
		"unknown2c": unknown2c,
		"unknown4": unknown4,
		"unknown5": unknown5,
		"systems_bodies": systems_bodies,
		"stations": stations,
	}


#
# Files
#



def _addSectorNames(sectors, file_path):
	try:
		sector_names = sectorAst(file_path.with_name("sector.ast"))
		for sector in sectors:
			sector["name"] = sector_names[sector["id"]]
	except FileNotFoundError:
		pass



def astroDb(file_path):

	OFFSET_SECTORS = 0x0
	OFFSET_SYSTEMS = 0x4800
	OFFSET_BODIES = 0x33fb0
	OFFSET_STATIONS = 0x3dad8
	OFFSET_STRINGS = 0x3e3e0

	f = DatabaseFile(file_path)
	f.setOffsetBase(OFFSET_STRINGS)

	assert(f.pos() == OFFSET_SECTORS)

	sectors = []
	for i in range(N_SECTORS):
		sector = readSector(f)
		sectors.append(sector)

	assert (f.pos() == OFFSET_SYSTEMS)

	for sector in sectors:
		sector["systems"] = []
		for i in range(sector["n_systems"]):
			system = readSystem(f)
			sector["systems"].append(system)
	
	assert(f.pos() == OFFSET_BODIES)

	for sector in sectors:
		sector["bodies"] = []
		for i in range(sector["n_bodies"]):
			body = readBody(f)
			sector["bodies"].append(body)

	assert (f.pos() == OFFSET_STATIONS)

	n_stations_sector = f.readUInt32()
	n_stations_system = f.readUInt32()
	for sector in sectors:
		sector["stations"] = []
	for i in range(n_stations_sector):
		station = readStation(f)
		sectors[station["sector_id"]]["stations"].append(station)
		sectors[station["sector_id"]]["n_stations"] += 1
	for i in range(n_stations_system):
		station = readStation(f)
		sector = sectors[station["sector_id"]]
		system = sector["systems"][station["system_index"]]
		system["station"] = station

	assert (f.pos() == OFFSET_STRINGS)

	# We've read in the raw data. Now let's fix up the strings and other details.

	_addSectorNames(sectors, file_path)

	for sector in sectors:
		for system in sector["systems"]:
			offset = system.pop("_offset_name")
			if offset != 0xFFFFFFFF: system["name"] = f.readOffsetString(offset)
			offset = system.pop("_offset_alias")
			if offset != 0xFFFFFFFF: system["alias"] = f.readOffsetString(offset)
			offset = system.pop("_offset_notable_name")
			if offset != 0xFFFFFFFF:
				notable = f.readOffsetString(offset)
				notable_i = int(notable[0])
				notable_name = notable[2:]
				system["notable"] = {
					"index": notable_i,
					"name": notable_name,
				}
			offset = system.pop("_offset_notable_desc")
			if offset != 0xFFFFFFFF:
				notable = f.readOffsetString(offset)
				notable_i = int(notable[0])
				notable_desc = notable[2:]
				if "notable" in system:
					assert(notable_i == system["notable"]["index"])
				else:
					system["notable"] = {
						"index": notable_i,
					}
				system["notable"]["desc"] = notable_desc
			assert( system.pop("_offset_station") == 0 )

			if "station" in system:
				station = system["station"]
				offset = station.pop("_offset_name")
				if offset != 0xFFFFFFFF: station["name"] = f.readOffsetString(offset)
				system["station_type"] = station["type"]
				system["station_orbit"] = station["orbit"]
				system["flags"] |= SystemFlags.STATION.value
				if station["type"] == ObjectType.OUTPOST:
					system["flags"] |= SystemFlags.OUTPOST.value
				station["coords"] = system["coords"]

		for body in sector["bodies"]:
			offset = body.pop("_offset_name")
			if offset != 0xFFFFFFFF: body["name"] = f.readOffsetString(offset)

		for station in sector["stations"]:			
			offset = station.pop("_offset_name")
			if offset != 0xFFFFFFFF: station["name"] = f.readOffsetString(offset)

	return sectors



def astromapDb(file_path):
	f = File(file_path)

	eof = len(f)
	offsets = []
	while True:
		offset = f.readUInt32()
		if offset == eof:
			break
		offsets.append(offset)

	sectors = []
	for offset in offsets:
		assert (f.pos() == offset)

		sector = readSector(f)

		sector["systems"] = []
		for i in range(sector["n_systems"]):
			system = readSystem(f)
			system.pop("_offset_name")
			system.pop("_offset_alias")
			system.pop("_offset_notable_name")
			assert( system.pop("_offset_notable_desc") == 0 )
			system.pop("_offset_station")
			sector["systems"].append(system)

		sector["bodies"] = []
		for i in range(sector["n_bodies"]):
			body = readBody(f)
			body.pop("_offset_name")
			sector["bodies"].append(body)

		sector["stations"] = []
		for i in range(sector["n_stations"]):
			station = readStation(f)
			station.pop("_offset_name")
			sector["stations"].append(station)

		sectors.append(sector)

	_addSectorNames(sectors, file_path)

	return sectors



def sectorAst(file_path):
	f = File(file_path)
	return { i: f.readLine() for i in range(N_SECTORS) }



def astStatDat(file_path):
	f = File(file_path)
	state = readAstroState(f)
	assert(f.eof())
	return state



def fixDarienBeta(astro_db):
	for sector in astro_db:
		for system in sector["systems"]:
			if system["name"] == "Darien Beta":
				system["coords"] = (55,82,52)


def _combineKey(a, am, key):
	return {
		"astro": a[key],
		"astromap": am[key]
	}



def combine(astro_path, astromap_path, aststat_path):
	data_a = astroDb(astro_path)
	fixDarienBeta(data_a)
	data_am = astromapDb(astromap_path)
	data_as = astStatDat(aststat_path)

	for i_sector,sector_a in enumerate(data_a):
		print(sector_a["name"])
		sector_am = data_am[i_sector]
		assert(sector_a["coords"] == sector_am["coords"])

		sector_a["unknown"] = _combineKey(sector_a, sector_am, "unknown")

		for i_system,system_a in enumerate(sector_a["systems"]):
			print(system_a["name"])
			if system_a["name"] == "Shonoisho Epsilon":
				continue

			system_am = sector_am["systems"][i_system]
			assert(system_a["coords"] == system_am["coords"])

			system_a["flags"] = _combineKey(system_a, system_am, "flags")
			system_a["unknown0"] = _combineKey(system_a, system_am, "unknown0")
			system_a["unknown1"] = _combineKey(system_a, system_am, "unknown1")
			system_a["unknown2"] = _combineKey(system_a, system_am, "unknown2")

			for i_station,station_a in enumerate(system_a["stations"]):
				if station_a["name"] == "Outpost Delta-0-8":
					continue
				station_am = system_am["stations"][i_station]
				assert(station_a["coords"] == station_am["coords"])

				station_a["ids"] = _combineKey(station_a, station_am, "id")

		for i_body,body_a in enumerate(sector_a["bodies"]):
			print(i_body, len(sector_am["bodies"]), body_a["type"])
			if body_a["type"] == ObjectType.SPECIAL_ITEM and i_body >= len(sector_am["bodies"]):
				print("bingo")
				continue
			body_am = sector_am["bodies"][i_body]
			assert(body_a["coords"] == body_am["coords"])

			body_a["unknown0"] = _combineKey(body_a, body_am, "unknown0")

		for i_station,station_a in enumerate(sector_a["stations"]):
			station_am = sector_am["stations"][i_station]
			assert(station_a["coords"] == station_am["coords"])

			station_a["ids"] = _combineKey(station_a, station_am, "id")

	return data_a
