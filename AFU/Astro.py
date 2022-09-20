from enum import IntEnum, Enum
from pathlib import Path
from AFU.File import File, DatabaseFile



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


PLANET_CLASSES = "STABGMNFEDCJKLHI"
STAR_CLASSES = "OBAFGKM-."
ALIGNMENTS = ["FEDERATION", "ROMULAN", "NEUTRAL", "NEBULA", "NONALIGNED"]
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


def planetDescription(planet):
	return PLANET_DESCRIPTIONS[planet]


class Alignment (Enum):
	FEDERATION = 0
	ROMULAN = 1
	NEUTRAL = 2
	NEBULA = 3
	NONALIGNED = 4


class SectorObjects (Enum): # todo: rename to AstroObjects or similar (some of these things exist in systems)
	STAR_SYSTEM = 32
	ION_STORM = 65
	QUASAROID = 66
	BLACK_HOLE = 68
	SUBSPACE_VORTEX = 69
	UNITY_DEVICE = 72
	SPECIAL_ITEM = 73 # Alien device, Unity device, Ruinore sector, Ayers, Singelea sector
	DEEP_SPACE_STATION = 128
	COMM_RELAY = 129
	BUOY = 130
	STARBASE = 131
	OUTPOST = 132


SECTOR_OBJECTS = { # todo: remove
	32: "Star System",
	65: "Ion Storm",
	66: "Quasaroid",
	68: "Black Hole",
	69: "Subspace Vortex",
	72: "Unity Device",
	73: "Special item", # Alien device, Unity device, Ruinore sector, Ayers, Singelea sector
	128: "Deep Space Station",
	129: "Comm Relay",
	130: "Buoy",
	131: "Starbase",
	132: "Outpost",
}



#
# Sector
#



def readSector(f):
	sector_id = f.readUInt32()
	sector_n_systems = f.readUInt32()
	sector_n_bodies = f.readUInt32()
	sector_n_stations = f.readUInt32() # Only used in astromap.db, always 0 in astro.db
	sector_alignment = f.readUInt32()
	sector_unknown = [f.readUInt32() for x in range(4)]  # todo: astromap.db: last value 0 for all but first system, astro.db: [0x0,0x0,0x0,0xffffffff]

	sector_x = (sector_id >> 0) & 0b111
	sector_y = (sector_id >> 3) & 0b111
	sector_z = (sector_id >> 6) & 0b111

	return {
		"id": sector_id,
		"coords": (sector_x, sector_y, sector_z),
		"n_systems": sector_n_systems,
		"n_bodies": sector_n_bodies,
		"n_stations": sector_n_stations,
		"alignment": Alignment(sector_alignment),
		"unknown": sector_unknown,
		"systems": [],
		"bodies": [],
		"stations": [],
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

# System State is a bitfield, but it means subtly different things in astro.db and astromap.db.
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
#     ^____ starbase? - if false, then outpost (astromap.db only)
#    ^_____ inhabited? (astro.db only), unknown state (atromap.db only)


def systemInhabited(state, file_name):
	# Only works in astro.db. Used for unknown-state in astromap.db
	if "astro.db" in file_name:
		return (0b0000000000010000 & state) != 0
	else:
		return False


def systemUnknownState(state):
	# Only works in astromap.db, and don't know what it means. Used for 'inhabited' in astro.db
	return (0b0000000000010000 & state) != 0


def systemBinary(state):
	return (0b0000000000000010 & state) != 0


def systemWhiteDwarf(state):
	return (0b0000000000000001 & state) != 0


def systemStation(state):
	# Only set in astromap.db
	return (0b0000000000000100 & state) != 0


def systemStarbase(state):
	# Only set in astromap.db
	return systemStation(state) and (0b0000000000001000 & state) != 0


def systemOutpost(state):
	# Only set in astromap.db
	return systemStation(state) and (0b0000000000001000 & state) == 0


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
	elif systemp["planets"] == 1:
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
	system_file_offset = f.pos()

	# Have not identified where the following information is stored:
	# - Presence of an asteroid belt
	# - Number of planets it contains

	system_index = f.readUInt32()
	system_id = f.readUInt16()
	system_type = f.readUInt16() # SectorObjects.STAR_SYSTEM

	# Unknown Values seem to have something to do with the layout of the system.
	# astro.db and astromap.db are in strong agreement, with only a handful of differences
	#
	# Unknown0:
	#   If unknown1 <= 127, unknown0 is 0
	#   If unknown1 >= 129, unknown0 is 255
	#   If unknown1 == 128, unknown0 is either 0 or 255
	#   There are five systems which deviate from this in astro.db, and one in astromap.db:
	#                                     astro.db  astromap.db
	#     - Darien Beta                   101         0
	#     - Byrn Beta                     173       255
	#     - Shonoisho Epsilon 5 (Frigis)  189       255
	#     - Polynya Delta                 253         0
	#     - Cashat Delta (Joward)         247       247           Go to Joward III in search of Ferengi trader. Upon arrival, crew advises going to Nigold System.
	#
	# Unknown1 values range from 0 to 255, covering all values, with the systems
	# distributed relatively evenly across that range.
	#
	# Unknown2 also ranges between 0 and 255.
	#
	# Systems with the same combination of unknown1 and unknown2 almost always have
	# the same planets/moons (though not exclusively).
	# Changing either of the values changes the planets/moons in the system.
	#
	# Astro.db and astromap.db are largely in agreement with nine exceptions, five
	# of which were already mentioned above:
	#                                 astro.db          astromap.db
	#                                 <u0> <u1> <u2>    <u0> <u1> <u2>
	# Euterpe Epsilon (55,50,101)	     0   71  175       0   87  177    Contains "Morassia", location of the zoo mission
	# Polynya Delta (62,6,127)         253  100  139       0  101  139
	# Darien Beta (55,82,52)           101   87  224       0   16  224
	# Byrn Beta (61, 99, 43)           173  115  241     255  202  241
	# Linore Iota (82, 84, 63)           0   29   49       0   20   49
	# Shonoisho Epsilon (88, 45, 105)  189    0   18     255  189   68    Contains "Frigis", location of the Garidian colony
	# Shonoisho Eta (93, 56, 111)      255  189   68       0   62   53
	# Steger Delta (92, 76, 56)          0   29   49       0   29  140    Contains "Cymkoe IV", location of the Mertens Orbital Station
	# Tothe Delta (106, 84, 99)        255  171  104       0   33  231    Contains "Horst III", where you visit Shanok


	system_unknown0 = f.readUInt8()
	system_unknown1 = f.readUInt8()

	assert(f.readUInt16() == 0)
	system_x = f.readUInt32()
	system_y = f.readUInt32()
	system_z = f.readUInt32()
	assert(f.readUInt32() == 0)
	system_name_offset = f.readUInt32() # todo: this is set in astromap.db, but isn't an offset within the file
	system_state = f.readUInt16()
	system_station_orbit = f.readUInt8() # In astromap.db the orbit of the station (0 is between first and second planet, 1: between second and third, etc). 0 in astro.db.
	system_station_type = f.readUInt8() # In astromap.db could also be either station (131) or outpost (132). 0 in astro.db.
	system_class = f.readUInt16()
	system_magnitude = f.readSInt16()

	system_unknown2 = f.readUInt32()

	assert(f.readUInt32() == 0)
	system_alias_offset = f.readUInt32()
	system_notable_offset = f.readUInt32()  # notable planet within system
	system_description_offset = f.readUInt32()
	assert(f.readUInt32() == 0)
	system_station_offset = f.readUInt32()  # todo: Only in astromap.db for systems with stations. Separation is 36bytes == sizeof(station).

	system_global_coords = (system_x, system_y, system_z)

	system = {
		"type": SectorObjects(system_type),
		"index": system_index,
		"id": system_id,
		"global_coords": system_global_coords,
		"coords": minorCoords(system_global_coords),
		"class": STAR_CLASSES[system_class // 10] + str(system_class % 10),
		"state": system_state,
		"inhabited": systemInhabited(system_state, f.name()),
		"binary": systemBinary(system_state),
		"white_dwarf": systemWhiteDwarf(system_state),
		"magnitude": system_magnitude / 10.0,

		"name_offset": system_name_offset,
		"alias_offset": system_alias_offset,
		"notable_offset": system_notable_offset,
		"description_offset": system_description_offset,
		"station_offset": system_station_offset,

		"unknown0": system_unknown0,
		"unknown1": system_unknown1,
		"unknown2": system_unknown2,

		"name": None,
		"stations": [],
		"planets": None,  # todo: determine how many planets there are
		"asteroid_belt": None,  # todo: determine where asteroid belt is specified
		"scanned": None,  # This is specified in ast_stat
	}

	if systemStation(system_state):
		system["stations"].append({
			"id": "<id unavailable>",
			"type": SectorObjects(system_station_type),
			"global_coords": system_global_coords,
			"coords": minorCoords(system_global_coords),
			#"sector_id": system_sector_id,
			"orbit": system_station_orbit,
			"sector_index": system_index,
			"offsets": {
				"name": system_station_offset, # todo: not sure this is correct
			},
			"name": "<name unavailable>",
		})

	return system



#
# Astronomical Bodies
#


def bodyDescription(body):
	if body["type"] == SectorObjects.SPECIAL_ITEM:  # Special item (Alien device, Unity device, Ruinore sector, USS Ayers, Singelea sector)
		return ""

	d = "{0[name]}: ".format(body)
	if body["type"] == SectorObjects.ION_STORM:
		d += "Reduced sensor range, Hull Erosion danger -- use caution -- possible systems damage in high-gradient areas."
	elif body["type"] == SectorObjects.QUASAROID:
		d += "Extreme Radiation & Subspace Distortion danger -- avoid!"
	elif body["type"] == SectorObjects.BLACK_HOLE:
		d += "Gravity, Radiation, & Subspace Distortion danger -- avoid!"
	elif body["type"] == SectorObjects.SUBSPACE_VORTEX:
		d += "Subspace Distortion danger -- use warp drive with care -- strong warp drive stress, possible coil failure."
	d += " Known zone of influence: {0[zone_radius]} light-years".format(body)
	return d


def readBody(f):
	body_index = f.readUInt32()
	body_id = f.readUInt16()
	body_type = f.readUInt16()  # Ion Storm, Quasaroid, Black Hole, Subspace Vortex, Special item
	assert(f.readUInt32() == 0)
	body_x = f.readUInt32()
	body_y = f.readUInt32()
	body_z = f.readUInt32()
	assert(f.readUInt32() == 0)
	body_name_offset = f.readUInt32()
	body_zone_radius = f.readUInt32()  # radius of known zone of influence, in LY
	body_unknown0 = f.readUInt32() # todo: 0 in astro.db, non-zero in astromap.db

	body_global_coords = (body_x, body_y, body_z)

	return {
		"index": body_index,
		"id": body_id,
		"type": SectorObjects(body_type),
		"global_coords": body_global_coords,
		"coords": minorCoords(body_global_coords),
		"zone_radius": body_zone_radius,
		"unknown0": body_unknown0,
		"name_offset": body_name_offset,
	}



#
# Stations
#



def readStation(f):
	assert (f.readUInt32() == 0)
	station_id = f.readUInt16()
	station_type = f.readUInt16()
	assert (f.readUInt32() == 0)
	station_x = f.readUInt32()
	station_y = f.readUInt32()
	station_z = f.readUInt32()
	assert (f.readUInt32() == 0)
	station_name_offset = f.readUInt32()
	station_sector_id = f.readUInt16()
	station_sector_index = f.readUInt8()  # index of the system within the sector this belongs to
	station_orbit = f.readUInt8()  # location of outpost within system (0: between first and second planet, 1: between second and third, etc.)

	station_global_coords = (station_x, station_y, station_z)

	return {
		"id": station_id,
		"type": SectorObjects(station_type),
		"global_coords": station_global_coords,
		"coords": minorCoords(station_global_coords),
		"sector_id": station_sector_id,
		"orbit": station_orbit,
		"sector_index": station_sector_index,
		"name_offset": station_name_offset,
	}


def stationDescription(station):
	d = "This is a Federation "
	if station["type"] == SectorObjects.DEEP_SPACE_STATION:
		d += "Deepspace Station"
	elif station["type"] == SectorObjects.COMM_RELAY:
		d += "subspace communications relay"
	elif station["type"] == SectorObjects.BUOY:
		d += "navigational & scanning buoy"
	elif station["type"] == SectorObjects.STARBASE:
		d += "Starbase"
	elif station["type"] == SectorObjects.OUTPOST:
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


def readAstroState(f):

	unknown0 = [f.readUInt16() for x in range(8)]
	enterprise_warp = round(float(f.readUInt32()) / 100.0, 1)
	enterprise_location_x = f.readUInt32()
	enterprise_location_y = f.readUInt32()
	enterprise_location_z = f.readUInt32()
	enterprise_origin_x = f.readUInt32()
	enterprise_origin_y = f.readUInt32()
	enterprise_origin_z = f.readUInt32()
	enterprise_destination_x = f.readUInt32()
	enterprise_destination_y = f.readUInt32()
	enterprise_destination_z = f.readUInt32()
	unknown1a = [f.readUInt8() for x in range(512)]
	unknown1b = [f.readUInt16() for x in range(19)]
	astrogation_speed_mode = "warp" if f.readUInt16() == 0 else "impulse"
	astrogation_speed_warp = round(float(f.readUInt32()) / 100.0, 1)
	astrogation_speed_impulse = f.readUInt32() * 10

	# all but the first of these changes when you change impulse speed, or between impulse and warp.
	# The first three don't change when you change warp speed. The second and third are 0 when in warp mode
	# If you change the selected system it also updates.
	# Perhaps some kind of estimated time to arrival? Or course information?
	unknown2a = [f.readUInt32() for x in range(7)]

	# some of these change when you change warp/impulse speed
	unknown2b = [f.readUInt16() for x in range(16)]
	astrogation_selected_x = f.readUInt32()
	astrogation_selected_y = f.readUInt32()
	astrogation_selected_z = f.readUInt32()
	unknown3 = [f.readUInt16() for x in range(8)]
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

	systems_bodies = {}
	for sector_id,end in enumerate(sector_end):
		while object_id < end:
			state = f.readUInt16()

			# What does this value mean...
			#  0      0000 invisible, unscanned
			#  1      0001 visible,  unscanned
			#  4      0100 invisible, only Lethe Beta
			#  5      0101 Only stellar bodies (no star systems)
			#  6      0110 invisible, only Lethe Zeta
			#  9      1001
			# 13      1101
			# 29 0001 1101 13 + story planet  (x5: M'kyru Zeta (Palmyra), Tothe Delta (horst), Euterpe Epsilon (Morassia), Steger Delta (Cymkoe), Kamyar Delta)

			#  0000 0000
			#          ^---- visible?
			#         ^----- 4: Lethe Zeta only
			#        ^------ 5,6: ???
			#       ^------- scanned?
			#     ^--------- story point?

			# M'kyru Zeta (Palmyra)      - If you don't fight the original Garidian warbird, the scout ship self destructs, and you detect escape pods here
			# Tothe Delta (Horst)        - Where Vulcan archeologist Shanok is based
			# Euterpe Epsilon (Morassia) - Location where Vie Hunfrsch goes missing
			# Steger Delta (Cymkoe IV)   - Location of Mertens Orbital Station (video on arrival)
			# Kamyar Delta               - ?????

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
		# What does this value mean...
		# Each station type has only one value:
		# starbase: 0
		# outpost: 0
		# buoy: 1
		# comm relay: 13
		# deep space station: 1

	return {
		"unknown0": unknown0,
		"enterprise": {
			"location": (enterprise_location_x, enterprise_location_y, enterprise_location_z),
			"destination": (enterprise_destination_x, enterprise_destination_y, enterprise_destination_z),
			"origin": (enterprise_origin_x, enterprise_origin_y, enterprise_origin_z),
			"warp": enterprise_warp,
		},
		"unknown1a": unknown1a,
		"unknown1b": unknown1b,
		"astrogation": {
			"speed_mode": astrogation_speed_mode,
			"speed_warp": astrogation_speed_warp,
			"speed_impulse": astrogation_speed_impulse,
			"selected": (astrogation_selected_x, astrogation_selected_y, astrogation_selected_z),
			"space_rotation_a": astrogation_a_deg,
			"space_rotation_e": astrogation_e_deg,
			"space_rotating": astrogation_rotating,
			"display": display,
		},
		"unknown2a": unknown2a,
		"unknown2b": unknown2b,
		"unknown3": unknown3,
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

	sectors = []
	for i in range(N_SECTORS):
		sector = readSector(f)
		sectors.append(sector)

	assert (f.pos() == OFFSET_SYSTEMS)

	for sector in sectors:
		for i in range(sector["n_systems"]):
			system = readSystem(f)

			offset = system.pop("name_offset")
			if offset != 0xFFFFFFFF: system["name"] = f.readOffsetString(offset)
			offset = system.pop("alias_offset")
			if offset != 0xFFFFFFFF: system["alias"] = f.readOffsetString(offset)
			offset = system.pop("notable_offset")
			if offset != 0xFFFFFFFF: system["notable"] = f.readOffsetString(offset)
			offset = system.pop("description_offset")
			if offset != 0xFFFFFFFF: system["description"] = f.readOffsetString(offset)
			assert( system.pop("station_offset") == 0 )

			sector["systems"].append(system)

	assert (f.pos() == OFFSET_BODIES)

	for sector in sectors:
		for i in range(sector["n_bodies"]):
			body = readBody(f)

			offset = body.pop("name_offset")
			if offset != 0xFFFFFFFF: body["name"] = f.readOffsetString(offset)

			sector["bodies"].append(body)

	assert (f.pos() == OFFSET_STATIONS)

	n_stations_sector = f.readUInt32()
	n_stations_system = f.readUInt32()
	for i in range(n_stations_sector):
		station = readStation(f)

		offset = station.pop("name_offset")
		if offset != 0xFFFFFFFF: station["name"] = f.readOffsetString(offset)

		sectors[station["sector_id"]]["stations"].append(station)
		sectors[station["sector_id"]]["n_stations"] += 1

	for i in range(n_stations_system):
		station = readStation(f)

		offset = station.pop("name_offset")
		if offset != 0xFFFFFFFF: station["name"] = f.readOffsetString(offset)

		system = sectors[station["sector_id"]]["systems"][station["sector_index"]]
		station["global_coords"] = system["global_coords"]
		station["coords"] = system["coords"]
		system["stations"].append(station)

	assert (f.pos() == OFFSET_STRINGS)

	_addSectorNames(sectors, file_path)

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

		for j in range(sector["n_systems"]):
			system = readSystem(f)
			system.pop("name_offset")
			system.pop("alias_offset")
			system.pop("notable_offset")
			assert( system.pop("description_offset") == 0 )
			system.pop("station_offset")
			sector["systems"].append(system)

		for j in range(sector["n_bodies"]):
			body = readBody(f)
			body.pop("name_offset")
			sector["bodies"].append(body)

		for j in range(sector["n_stations"]):
			station = readStation(f)
			station.pop("name_offset")
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
