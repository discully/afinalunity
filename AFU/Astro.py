from AFU.File import File, DatabaseFile
from AFU.AstroCore import *
from AFU.AstroUtils import *
from AFU.AstroState import *
from AFU.AstroGen import BODY_UNKNOWN0


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
				system["station_orbit"] = station["orbit"]
				system["flags"] |= SystemFlags.STATION
				if station["type"] == ObjectType.STARBASE:
					system["flags"] |= SystemFlags.STARBASE
				station["coords"] = system["coords"]
			else:
				system["station_type"] = None
				system["station_orbit"] = None

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
				system["station_orbit"] = None
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
	for sector in astro_db:
		for system in sector["systems"]:
			if system["name"] == "Darien Beta":
				system["coords"] = (55,82,52)



def astrogationSystem(system, stat):
	system["state"] = stat["systems_bodies"][system["id"]]["state"]
	binary_class,binary_mag = systemGetBinaryStar(system)
	if binary_class != None:
		system["binary_class"] = Astro.STAR_CLASSES[binary_class // 10] + str(binary_class % 10)
		system["binary_mag"] = binary_mag/10.0
	systemSetPlanets(system)
	for planet in system["planets"]:
		c = planet["class"]
		planet["class_int"] = c
		planet["class"] = Astro.PLANET_CLASSES[c]
		for moon in planet["moons"]:
			c = moon["class"]
			moon["class_int"] = c
			moon["class"] = Astro.PLANET_CLASSES[c]


def astrogation(astro, stat):

	# Set the current state
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
			binary_class,binary_mag = systemGetBinaryStar(system)
			if binary_class != None:
				system["binary_class"] = Astro.STAR_CLASSES[binary_class // 10] + str(binary_class % 10)
				system["binary_mag"] = binary_mag/10.0
			systemSetPlanets(system)
			for planet in system["planets"]:
				c = planet["class"]
				planet["class_int"] = c
				planet["class"] = Astro.PLANET_CLASSES[c]
				for moon in planet["moons"]:
					c = moon["class"]
					moon["class_int"] = c
					moon["class"] = Astro.PLANET_CLASSES[c]
	
	return astro


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
