from enum import IntEnum
from pathlib import Path
from AFU.File import File



# Functions for handling co-ordinates
# The game space consists of an 8x8x8 grid (major co-ordinates), each cube in the grid is a "sector".
# Each sector has a 20*20*20 grid (minor co-ordinates), some of which will contain a star "system".


N_SECTORS = 512 # 8x8x8


def globalCoords(major_coords, minor_coords):
	return major_coords * 20 + minor_coords


def minorCoords(global_coords):
	return (global_coords[0] % 20, global_coords[1] % 20, global_coords[2] % 20)


def majorCoords(global_coords):
	return (global_coords[0] // 20, global_coords[1] // 20, global_coords[2] // 20)



#
# Identification
#


PLANET_CLASSES = "STABGMNFEDCJKLHI" #"ABCDEFGHIJKLMNST"
STAR_CLASSES = "OBAFGKM-."
ALIGNMENTS = ["FEDERATION", "ROMULAN", "NEUTRAL", "NEBULA", "NONALIGNED"]
DWARF_NAMES = ["black", "brown", "red", "white"]


def planetDescription(planet):
	descriptions = [
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
	return descriptions[planet]
	

class Alignment (IntEnum):
	FEDERATION = 0
	ROMULAN = 1
	NEUTRAL = 2
	NEBULA = 3
	NONALIGNED = 4


class SectorObjects (IntEnum):
	STAR_SYSTEM = 32
	ION_STORM = 65
	QUASAROID = 66
	BLACK_HOLE = 68
	SUBSPACE_VORTEX = 69
	SPECIAL_ITEM = 73
	DEEP_SPACE_STATION = 128
	COMM_RELAY = 129
	BUOY = 130
	STARBASE = 131
	OUTPOST = 132


SECTOR_OBJECTS = {
	32: "Star System",
	65: "Ion Storm",
	66: "Quasaroid",
	68: "Black Hole",
	69: "Subspace Vortex",
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
	sector_n_stations = f.readUInt32() # always 0 in astro.db, used in astromap.db
	sector_alignment = f.readUInt32()
	sector_unknown = [f.readUInt8() for x in range(16)]  # todo: astromap.db: last 4 bytes 0 for all but first system, astro.db: [0x0,0x0,0x0,0xffffffff]
	
	sector_z = (sector_id >> 6) & 0b111
	sector_x = (sector_id >> 0) & 0b111
	sector_y = (sector_id >> 3) & 0b111
	
	return {
		"id": sector_id,
		"coords": (sector_x, sector_y, sector_z),
		"n_systems": sector_n_systems,
		"n_bodies": sector_n_bodies,
		"n_stations": sector_n_stations,
		"alignment": Alignment(sector_alignment),
		
		"unknown": sector_unknown,
		
		"name": "<name unavailable>",
		"systems": [],
		"bodies": [],
		"stations": [],
	}


def sectorDescription(sector):
	d = "This sector is "
	if sector["alignment"] == Alignment.FEDERATION:
		d += "aligned with the Federation"
	elif sector["alignment"] == Alignment.ROMULAN:
		d += "aligned with the Romulans."
	elif sector["alignment"] == Alignment.NEUTRAL:
		d += "in the neutral zone"
	elif sector["alignment"] == Alignment.NEBULA:
		d += "in the Z'Tarnis Nebula"
	elif sector["alignment"] == Alignment.NONALIGNED:
		d += "nonaligned"
	else:
		raise ValueError("Invalid sector alignment: {}".format(sector["alignment"]))
	d += "."
	return d


def printSector(sector, recursive=False):
	print("""
[Sector {0[id]}] {0[name]}
	{0[coords]}
	{1}
	- u {0[unknown]}""".format(sector, sectorDescription(sector)))
	
	if recursive:
		for system in sector["systems"]:
			printSystem(system, recursive)
		for body in sector["bodies"]:
			printBody(body)
		for station in sector["stations"]:
			printStation(station)


#
# Star Systems
#


def systemInhabited(state):
	return (0b0000000000010000 & state) != 0


def systemBinary(state):
	return (0b0000000000000010 & state) != 0


def systemWhiteDwarf(state):
	return (0b0000000000000001 & state) != 0


def systemStation(state):
	return (0b0000000000000100 & state) != 0


def systemStarbase(state):
	return systemStation(state) and (0b0000000000001000 & state) != 0


def systemOutpost(state):
	return systemStation(state) and (0b0000000000001000 & state) == 0


def systemStateValidate(state):
	assert((0b1111111111100000 & state) == 0)


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
		d += " It posesses {} planets."
	else:
		d += " It posesses {} planets, ".format(system["planets"])
	
	if system["inhabited"]:
		d += "one of which"  # todo: Are there any systems with more than one inhabited planet?
	elif len(system["planets"]) == 1:
		d += "?????"  # todo: Are there any systems with only one planet?
	elif len(system["planets"]) == 2:
		d += "neither of which"
	else:
		d += "none of which"
	d += " is known to be inhabited."
	
	for station in system["stations"]:
		d += " {0[name]} orbits this system.".format(station)
	
	if not system["scanned"]:
		d += " This star is currently unscanned."
	
	if system["asteroid_belt"]:
		d += " This star system has an asteroid belt."
	
	return d


def readSystem(f):
	# Have not identified where the following information is stored:
	# - Presence of an asteroid belt
	# - Whether the system has been scanned
	# - Number of planets it contains
	
	system_index = f.readUInt32()
	system_id = f.readUInt16()
	system_type = f.readUInt16() # SectorObjects.STAR_SYSTEM
	system_unknown0 = f.readUInt8()
	system_unknown1 = f.readUInt8()
	# todo:
	# [0] 255 (x1488), 0 (x1367), 101, 173, 189, 253, 247. One-off values could indicate events on arrival at these coords?
	# [1] Lots of different values, none stand-out values
	assert(f.readUInt16() == 0)
	system_x = f.readUInt32()
	system_y = f.readUInt32()
	system_z = f.readUInt32()
	assert(f.readUInt32() == 0)
	system_name_offset = f.readUInt32() # todo: this is set in astromap.db, but not clear what it relates to
	system_state = f.readUInt16()
	system_station_orbit = f.readUInt8() # 0, or in astromap.db... 0: between first and second planet, 1: between second and third, etc.
	system_station_type = f.readUInt8() # 0, or in astromap.db... could also be either station (131) or outpost (132)
	system_class = f.readUInt16()
	system_magnitude = f.readSInt16()
	system_unknown2 = f.readUInt32()  # todo: Values between 0 and 255. No stand-out values
	assert(f.readUInt32() == 0)
	system_alias_offset = f.readUInt32()
	system_notable_offset = f.readUInt32()  # notable planet within system
	system_description_offset = f.readUInt32()
	assert(f.readUInt32() == 0)
	system_station_offset = f.readUInt32()  # todo: Only in astromap.db for systems with stations. Separation is 36bytes == sizeof(station). Offset? But what file?
	
	system_global_coords = (system_x, system_y, system_z)
	systemStateValidate(system_state)
	
	system = {
		"type": system_type,
		"index": system_index,
		"id": system_id,
		"global_coords": system_global_coords,
		"coords": minorCoords(system_global_coords),
		"class": STAR_CLASSES[system_class // 10] + str(system_class % 10),
		"state": system_state,
		"inhabited": systemInhabited(system_state),
		"binary": systemBinary(system_state),
		"white_dwarf": systemWhiteDwarf(system_state),
		"magnitude": system_magnitude / 10.0,
		"offsets": {
			"name": system_name_offset,
			"alias": system_alias_offset,
			"notable": system_notable_offset,
			"description": system_description_offset,
			"station": system_station_offset,
		},
		
		"unknown0": system_unknown0,
		"unknown1": system_unknown1,
		"unknown2": system_unknown2,
		
		"name": "<name unavailable>",
		"stations": [],
		"planets": "???",  # todo: determine how many planets there are
		"asteroid_belt": False,  # todo
		"scanned": True,  # todo: Determine how to know if a system is unscanned
	}
	
	if systemStation(system_state):
		system["stations"].append({
			"id": "<id unavailable>",
			"type": system_station_type,
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


def printSystem(system, recursive=False):
	print("""
	[System {0[id]}] {1}
		{0[global_coords]} = {3} > {0[coords]}
		{2}
		- u0 {0[unknown0]}
		- u1 {0[unknown1]:>3} {0[unknown1]:>08b}
		- u2 {0[unknown2]:>3} {0[unknown2]:>08b}""".format(system, systemTitle(system), systemDescription(system), majorCoords(system["global_coords"])))
	
	if recursive:
		for station in system["stations"]:
			printStation(station)



#
# Astronomical Bodies
#


def bodyDescription(body):
	if body["type"] == SectorObjects.SPECIAL_ITEM:  # Special item (Alien device, Unity device, Ruinore sector, Ayers, Singelea sector)
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
		"type": body_type,
		"global_coords": body_global_coords,
		"coords": minorCoords(body_global_coords),
		"zone_radius": body_zone_radius,
		"offsets": {
			"name": body_name_offset,
		},
		
		"unknown0": body_unknown0,
		
		"name": "<name unavailable>",
	}

def printBody(body):
	print("""
	[Body {0[id]}] {0[name]}
		{0[global_coords]} = {2} > {0[coords]}
		{1}""".format(body, bodyDescription(body), majorCoords(body["global_coords"])))



#
# Stations
#


def readStation(f):
	# 36 bytes long
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
		"type": station_type,
		"global_coords": station_global_coords,
		"coords": minorCoords(station_global_coords),
		"sector_id": station_sector_id,
		"orbit": station_orbit,
		"sector_index": station_sector_index,
		"offsets": {
			"name": station_name_offset
		},
		
		"name": "<name unavailable>",
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

	# 1384888:Fully Operational.
	# 1384909:Operational -- Awaiting Resupply.
	# 1384945:Partially Operational.
	# 1384970:Non-operational.
	# 1384989:Unknown -- contact lost.


def printStation(station):
	if station["type"] in [SectorObjects.STARBASE, SectorObjects.OUTPOST]:
		print("""
		[Station {0[id]}] {0[name]}
			{1}
			Orbit:{0[orbit]} Index:{0[sector_index]}""".format(station, stationDescription(station)))
	else:
		print("""
	[Station {0[id]}] {0[name]}
		{0[global_coords]} = {2} > {0[coords]}
		{1}""".format(station, stationDescription(station), majorCoords(station["global_coords"])))


#
# Files
#


def astroDb(dir):
	sector_names = sectorAst(dir)
	f = File(dir.joinpath("astro.db"))
	
	OFFSET_SECTORS = 0x0
	OFFSET_STRINGS = 0x3e3e0
	
	strings = {}
	f.setPosition(OFFSET_STRINGS)
	try:
		while True:
			offset = f.pos() - OFFSET_STRINGS
			strings[offset] = f.readString()
	except EOFError:
		pass
	f.setPosition(0)
	
	sectors = []
	for i in range(N_SECTORS):
		sector = readSector(f)
		sector["name"] = sector_names[sector["id"]]
		sectors.append(sector)
	
	ref = {}
	for sector in sectors:
		for i in range(sector["n_systems"]):
			system = readSystem(f)
			
			system["name"] = strings[system["offsets"]["name"]]
			if system["offsets"]["alias"] != 0xFFFFFFFF:  # Special name for notable (main story line) systems
				system["alias"] = strings[system["offsets"]["alias"]]
			if system["offsets"]["notable"] != 0xFFFFFFFF:  # Name of a notable (main story line) planet
				system["notable"] = strings[system["offsets"]["notable"]]
			if system["offsets"]["description"] != 0xFFFFFFFF:
				system["description"] = strings[system["offsets"]["description"]]
			
			sector["systems"].append(system)
			ref[system["id"]] = system
	
	assert (f.pos() == 0x33fb0)
	
	for sector in sectors:
		for i in range(sector["n_bodies"]):
			body = readBody(f)
			
			body["name"] = strings[body["offsets"]["name"]]
			
			sector["bodies"].append(body)
			ref[body["id"]] = body
	
	assert (f.pos() == 0x3dad8)
	
	n_stations_sector = f.readUInt32()
	n_stations_system = f.readUInt32()
	
	for i in range(n_stations_sector):
		station = readStation(f)
		
		station["name"] = strings[station["offsets"]["name"]]
		
		sectors[station["sector_id"]]["stations"].append(station)
		ref[station["id"]] = station
	
	for i in range(n_stations_system):
		station = readStation(f)
		
		station["name"] = strings[station["offsets"]["name"]]
		
		sectors[station["sector_id"]]["systems"][station["sector_index"]]["stations"].append(station)
		ref[station["id"]] = station
	
	assert (f.pos() == OFFSET_STRINGS)
	
	return sectors



def astromapDb(dir):
	sector_names = sectorAst(dir)
	f = File(dir.joinpath("astromap.db"))
	
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
		sector["name"] = sector_names[sector["id"]]
		
		for j in range(sector["n_systems"]):
			system = readSystem(f)
			sector["systems"].append(system)
		
		for j in range(sector["n_bodies"]):
			body = readBody(f)
			sector["bodies"].append(body)
		
		for j in range(sector["n_stations"]):
			station = readStation(f)
			sector["stations"].append(station)
		
		sectors.append(sector)
	
	return sectors



def sectorAst(dir):
	f = File(dir.joinpath("sector.ast"))
	return [f.readLine() for x in range(N_SECTORS)]



def astrogation(dir):
	astro_sectors = astroDb(dir)
	astromap_sectors = astromapDb(dir)
	
	for i_sector,sector in enumerate(astromap_sectors):
		assert(sector["id"] == astro_sectors[i_sector]["id"])
		assert(len(sector["systems"]) == len(astro_sectors[i_sector]["systems"]))
		assert(sector["coords"] == astro_sectors[i_sector]["coords"])
		
		for i_system,system in enumerate(sector["systems"]):
			try:
				assert(system["coords"] == astro_sectors[i_sector]["systems"][i_system]["coords"])
			except:
				printSystem(system)
				printSystem(astro_sectors[i_sector]["systems"][i_system])
	
	return astromap_sectors
