from AFU.File import File, DatabaseFile
from AFU.AstroCore import *
from AFU.AstroUtils import N_SECTORS
from AFU.AstroState import readAstroState
from AFU.AstroGen import BODY_UNKNOWN0, systemGenerate
from AFU.Utils import identify
from AFU.SaveGame import savegame


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
		offset = sector.pop("_ptr_systems")
		assert(offset == 0)
		offset = sector.pop("_ptr_bodies")
		assert(offset == 0)
		offset = sector.pop("_ptr_stations")
		assert(offset == 0)
		offset = sector.pop("_ptr_desc")
		assert(offset == 0xffffffff)

		for system in sector["systems"]:
			offset = system.pop("_ptr_desc")
			assert(offset == 0)
			offset = system.pop("_ptr_name")
			if offset != 0xFFFFFFFF: system["name"] = f.readOffsetString(offset)
			offset = system.pop("_ptr_alias")
			if offset != 0xFFFFFFFF: system["alias"] = f.readOffsetString(offset)
			offset = system.pop("_ptr_notable_name")
			if offset != 0xFFFFFFFF:
				notable = f.readOffsetString(offset)
				notable_i = int(notable[0])
				notable_name = notable[2:]
				system["notable"] = {
					"index": notable_i,
					"name": notable_name,
				}
			offset = system.pop("_ptr_planets")
			assert(offset == 0)
			offset = system.pop("_ptr_notable_desc")
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
			assert( system.pop("_ptr_station") == 0 )

			if "station" in system:
				station = system["station"]
				offset = station.pop("_ptr_desc")
				assert(offset == 0)
				offset = station.pop("_ptr_name")
				if offset != 0xFFFFFFFF: station["name"] = f.readOffsetString(offset)
				system["station_type"] = station["type"]
				system["station_planet_index"] = station["planet_index"]
				system["flags"] |= SystemFlags.STATION
				if station["type"] == ObjectType.STARBASE:
					system["flags"] |= SystemFlags.STARBASE
				station["coords"] = system["coords"]
			else:
				system["station_type"] = None
				system["station_planet_index"] = None

		for body in sector["bodies"]:
			offset = body.pop("_ptr_desc")
			assert(offset == 0)
			offset = body.pop("_ptr_name")
			if offset != 0xFFFFFFFF: body["name"] = f.readOffsetString(offset)
			assert(body["unknown0"] == 0)
			body["unknown0"] = BODY_UNKNOWN0[body["type"]]

		for station in sector["stations"]:			
			offset = station.pop("_ptr_desc")
			assert(offset == 0)
			offset = station.pop("_ptr_name")
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
			sector["systems"].append(system)

		sector["bodies"] = []
		for i in range(sector["n_bodies"]):
			body = readBody(f)
			sector["bodies"].append(body)

		sector["stations"] = []
		for i in range(sector["n_stations"]):
			station = readStation(f)
			sector["stations"].append(station)

		sectors.append(sector)

	_addSectorNames(sectors, file_path)

	for sector in sectors:
		sector.pop("_ptr_desc")
		sector.pop("_ptr_bodies")
		sector.pop("_ptr_stations")
		sector.pop("_ptr_systems")
		for system in sector["systems"]:
			system.pop("_ptr_desc")
			system.pop("_ptr_name")
			system.pop("_ptr_alias")
			system.pop("_ptr_notable_name")
			system.pop("_ptr_notable_desc")
			system.pop("_ptr_station")
			system.pop("_ptr_planets")
			if system["station_type"] == 0:
				system["station_type"] = None
				system["station_planet_index"] = None
			else:
				system["station_type"] = ObjectType(system["station_type"])
		for body in sector["bodies"]:
			body.pop("_ptr_desc")
			body.pop("_ptr_name")
		for station in sector["stations"]:
			station.pop("_ptr_desc")
			station.pop("_ptr_name")

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
	"""In astro.db, the co-ordinates of Darien Beta are set to (0,0,0).
	This looks to be an error, and it results in Darien Beta not being
	visible in the game. This function will correct that with the
	co-ordinates found in astromap.db."""
	for sector in astro_db:
		for system in sector["systems"]:
			if system["name"] == "Darien Beta":
				system["coords"] = (55,82,52)


def astrogation(astro_db_path, astro_stat_path):

	stat_type = identify(astro_stat_path)
	stat = None
	if stat_type == "savegame":
		stat = savegame(astro_stat_path)["astro_state"]
	elif stat_type == "astro_state":
		stat = astStatDat(astro_stat_path)
	else:
		raise ValueError("Astro state file not recognised ({})".format(astro_stat_path.name))

	astro = astroDb(astro_db_path)
	fixDarienBeta(astro)

	for sector in astro:
		for system in sector["systems"]:
			system["state"] = stat["systems_bodies"][system["id"]]["state"]
			if "station" in system:
				system["station"]["state"] = stat["stations"][system["station"]["id"]]
		for body in sector["bodies"]:
			body["state"] = stat["systems_bodies"][body["id"]]["state"]
		for station in sector["stations"]:
			station["state"] = stat["stations"][station["id"]]
	
	for sector in astro:
		for system in sector["systems"]:
			systemGenerate(system)
	
	for sector in astro:
		for system in sector["systems"]:
			flags = system["flags"]
			#system["flags"] = [f.name for f in SystemFlags if f & flags == f]
			if "notable" in system:
				n = system["notable"]
				if "name" in n:
					system["planets"][n["index"]]["alias"] = n["name"]
				if "desc" in n:
					system["planets"][n["index"]]["desc"] = n["desc"]
				system.pop("notable")
			for planet in system["planets"]:
				flags = planet["flags"]
				#planet["flags"] = [f.name for f in PlanetFlags if f & flags == f]
				for moon in planet["moons"]:
					pass
			if "station" in system:
				pass
		for body in sector["bodies"]:
			pass
		for station in sector["stations"]:
			pass
	
	return astro
