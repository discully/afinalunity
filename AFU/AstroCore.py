from enum import IntEnum, Enum


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
	# ENTERPRISE = 144


#
# Sectors
#


class Alignment (Enum):
	FEDERATION = 0
	ROMULAN = 1
	NEUTRAL = 2
	NEBULA = 3
	NONALIGNED = 4


def readSector(f):
	sector_id = f.readUInt32()
	sector_n_systems = f.readUInt32()
	sector_n_bodies = f.readUInt32()
	sector_n_stations = f.readUInt32()
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
		"_ptr_systems": sector_ptr_systems,
		"_ptr_bodies": sector_ptr_bodies,
		"_ptr_stations": sector_ptr_stations,
		"_ptr_desc": sector_ptr_description
	}


#
# Star Systems
#


class SystemFlags (IntEnum):
	WHITE_DWARF = 0x1
	BINARY = 0x2
	STATION = 0x4
	STARBASE = 0x8
	INHABITED = 0x10 # This doesn't seem to be correct in astromap.db


def readSystem(f):
	system_index = f.readUInt32()
	system_id = f.readUInt16()
	system_type = f.readUInt16()

	if ObjectType(system_type) != ObjectType.STAR_SYSTEM:
		raise ValueError("Incorrect object type (got:{}, expected:{})".format(
			system_type, ObjectType.STAR_SYSTEM.value
			))
	
	system_random_seed = f.readUInt32()
	system_x = f.readUInt32()
	system_y = f.readUInt32()
	system_z = f.readUInt32()
	system_ptr_description = f.readUInt32()
	system_ptr_name = f.readUInt32()
	system_flags = f.readUInt16()
	system_station_orbit = f.readUInt8() # In astromap.db index of the planet the station orbits. 0 in astro.db.
	system_station_type = f.readUInt8() # In astromap.db could also be either station (131) or outpost (132). 0 in astro.db.
	system_class_int = f.readUInt16()
	system_magnitude = f.readSInt16()
	system_random_seed_2 = f.readUInt32()
	system_n_planets = f.readUInt32()
	system_ptr_alias = f.readUInt32()
	system_ptr_notable_name = f.readUInt32()
	system_ptr_notable_desc = f.readUInt32()
	system_ptr_planets = f.readUInt32()
	system_ptr_station = f.readUInt32()
	
	system = {
		"index": system_index,
		"id": system_id,
		"type": ObjectType(system_type),
		"random_seed": system_random_seed,
		"coords": (system_x, system_y, system_z),
		"_ptr_desc": system_ptr_description,
		"_ptr_name": system_ptr_name,
		"flags": system_flags,
		"station_orbit": system_station_orbit,
		"station_type": system_station_type,
		"_star_class_int": system_class_int,
		"star_class": starClassFromInt(system_class_int),
		"star_mag": system_magnitude / 10.0,
		"random_seed_2": system_random_seed_2,
		"n_planets": system_n_planets,
		"_ptr_alias": system_ptr_alias,
		"_ptr_notable_name": system_ptr_notable_name,
		"_ptr_notable_desc": system_ptr_notable_desc,
		"_ptr_planets": system_ptr_planets,
		"_ptr_station": system_ptr_station,
	}

	return system


#
# Stars
#


STAR_CLASSES = "OBAFGKM"


def starClassToInt(star_class):
	upper = STAR_CLASSES.index(star_class[0])
	lower = int(star_class[1])
	return upper*10 + lower


def starClassFromInt(star_class_int):
	return STAR_CLASSES[star_class_int // 10] + str(star_class_int % 10)


#
# Planets
#


PLANET_CLASSES = "ABCDEFGHIJKLMNST"


class PlanetFlags (IntEnum):
	ASTEROIDS = 0x1
	UNKNOWN = 0x2 # Set in _planetInit. Possibly set if no outpost. Never checked?
	INHABITED = 0x10


def readPlanet(f):
	planet_index = f.readUInt32()
	planet_unknown4 = f.readUInt32()
	planet_random_seed = f.readUInt32()
	planet_x = f.readUInt32()
	planet_y = f.readUInt32()
	planet_z = f.readUInt32()
	planet_ptr_desc = f.readUInt32()
	planet_ptr_name = f.readUInt32()
	planet_flags = f.readUInt16()
	planet_nth = f.readUInt16()
	planet_class = f.readUInt32()
	planet_n_moons = f.readUInt32()
	planet_ptr_alias = f.readUInt32()
	planet_ptr_moons = f.readUInt32()

	assert(planet_unknown4 == 0)
	return {
		"index": planet_index,
		"unknown4": planet_unknown4,
		"random_seed": planet_random_seed,
		"coords": (planet_x,planet_y,planet_z),
		"_ptr_desc": planet_ptr_desc,
		"_ptr_name": planet_ptr_name,
		"flags": planet_flags,
		"nth_created": planet_nth,
		"class": PLANET_CLASSES[planet_class],
		"n_moons": planet_n_moons,
		"_ptr_alias": planet_ptr_alias,
		"_ptr_moons": planet_ptr_moons,
	}


#
# Moons
#


def readMoon(f):
	moon_unknown0 = f.readUInt32()
	moon_unknown4 = f.readUInt32()
	moon_random_seed = f.readUInt32()
	moon_x = f.readUInt32()
	moon_y = f.readUInt32()
	moon_z = f.readUInt32()
	moon_ptr_desc = f.readUInt32()
	moon_ptr_name = f.readUInt32()
	moon_unknown32 = f.readUInt8()
	moon_unknown33 = f.readUInt8()
	moon_class = f.readUInt8()
	moon_unknown35 = f.readUInt8()
	moon_ptr_alias = f.readUInt32()
	
	assert(moon_unknown32 == 0)
	assert(moon_unknown33 == 0)
	assert(moon_unknown35 == 0)

	return {
		"unknown0": moon_unknown0,
		"unknown4": moon_unknown4,
		"random_seed": moon_random_seed,
		"coords": (moon_x, moon_y, moon_z),
		"_ptr_desc": moon_ptr_desc,
		"_ptr_name": moon_ptr_name,
		"unknown": (moon_unknown32, moon_unknown33, moon_unknown35),
		"_class_int": moon_class,
		"_ptr_alias": moon_ptr_alias,
	}


#
# Astronomical Bodies
#


BODY_TYPES = (
	ObjectType.ION_STORM,
	ObjectType.QUASAROID,
	ObjectType.BLACK_HOLE,
	ObjectType.SUBSPACE_VORTEX,
	ObjectType.UNITY_DEVICE,
	ObjectType.SPECIAL_ITEM
	)


def readBody(f):
	body_index = f.readUInt32()
	body_id = f.readUInt16()
	body_type = f.readUInt16()

	if ObjectType(body_type) not in BODY_TYPES:
		raise ValueError("Incorrect object type (got:{}, expected:{})".format(
			body_type, [b.value for b in BODY_TYPES]
			))

	body_random_seed = f.readUInt32()
	body_x = f.readUInt32()
	body_y = f.readUInt32()
	body_z = f.readUInt32()
	body_ptr_desc = f.readUInt32()
	body_ptr_name = f.readUInt32()
	body_zone_radius = f.readUInt32()  # radius of known zone of influence, in LY
	body_unknown0 = f.readUInt32() # todo: 0 in astro.db, non-zero in astromap.db

	assert(body_random_seed == 0) # Set during execution
	assert(body_ptr_desc == 0) # Set during execution

	return {
		"index": body_index,
		"id": body_id,
		"type": ObjectType(body_type),
		"coords": (body_x, body_y, body_z),
		"_ptr_desc": body_ptr_desc,
		"_ptr_name": body_ptr_name,
		"zone_radius": body_zone_radius,
		"unknown0": body_unknown0,
	}


#
# Stations
#


STATION_TYPES = (
	ObjectType.COMM_RELAY,
	ObjectType.DEEP_SPACE_STATION,
	ObjectType.OUTPOST,
	ObjectType.BUOY,
	ObjectType.STARBASE
	)


def readStation(f):
	station_index = f.readUInt32()
	station_id = f.readUInt16()
	station_type = f.readUInt16()

	if ObjectType(station_type) not in STATION_TYPES:
		raise ValueError("Incorrect object type (got:{}, expected:{})".format(
			station_type, [s.value for s in STATION_TYPES]
			))

	station_random_seed = f.readUInt32()
	station_x = f.readUInt32()
	station_y = f.readUInt32()
	station_z = f.readUInt32()
	station_ptr_desc = f.readUInt32()
	station_ptr_name = f.readUInt32()
	station_sector_id = f.readUInt16()
	station_system_index = f.readUInt8()  # index of the system within the sector this belongs to
	station_orbit = f.readUInt8()  # index of the planet within the system the station orbits

	assert(station_index == 0)
	assert(station_random_seed == 0)
	assert(station_ptr_desc == 0)

	return {
		"index": station_index,
		"id": station_id,
		"type": ObjectType(station_type),
		"random_seed": station_random_seed,
		"coords": (station_x, station_y, station_z),
		"_ptr_desc": station_ptr_desc,
		"_ptr_name": station_ptr_name,
		"sector_id": station_sector_id,
		"system_index": station_system_index,
		"orbit": station_orbit, # todo: rename to planet index?
	}
