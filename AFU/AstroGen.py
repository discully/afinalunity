from AFU.AstroCore import *
from enum import IntEnum, Enum




#
# Sector
#


SECTOR_ALIGN_DESCRIPTIONS = {
	Alignment.FEDERATION: "This sector is aligned with the Federation.",
	Alignment.ROMULAN: "This sector is aligned with the Romulans.",
	Alignment.NEUTRAL: "This sector is in the neutral zone.",
	Alignment.NEBULA: "This sector is in the Z'Tarnis Nebula.",
	Alignment.NONALIGNED: "This sector is nonaligned.",
}


def sectorDescription(sector):
	d = "Sector "
	d += sector["name"]
	d += SECTOR_ALIGN_DESCRIPTIONS[sector["alignment"]]
	if "desc" in sector and sector["desc"]:
		d += "  " + sector["desc"]
	return d


#
# SYSTEM
#


_GLOB_SYSTEM_PLANETS_CREATED = 0
_GLOB_SYSTEM_MOON_CAPACITY = 10
_GLOB_SYSTEM_N_PLANETS = 0


class SystemState (IntEnum):
	CHARTED = 0x1
	UNKNOWN_LETHE = 0x2
	UNKNOWN_SCANNED = 0x4
	SCANNED = 0x8
	UNKNOWN_STORY = 0x10


def systemGenerate(system):
	"""Adds the binary star data, moons, planets, asteroid belts, etc. to a system.
	The system's state must have been already set."""

	if not "state" in system:
		raise ValueError("The system has not had its state set.")
	
	b_class,b_mag = _systemGetBinaryStar(system)
	if b_class is None:
		system["binary"] = None
	else:
		system["binary"] = {
			"_class_int": b_class,
			"class": starClassFromInt(b_class),
			"mag": b_mag,
		}

	_systemSetPlanets(system)
	for planet in system["planets"]:
		planet["class"] = PLANET_CLASSES[planet["_class_int"]]
		#planet["name"] = planetName(planet)
		#planet["desc"] = planetDescription(planet)
		for moon in planet["moons"]:
			moon["class"] = PLANET_CLASSES[moon["_class_int"]]
			#moon["name"] = moonName(moon)
			moon["desc"] = moonDescription(moon)


def systemInhabited(system):
	"""Returns the number of planets in the system which are inhabited."""
	n = 0
	for planet in system["planets"]:
		if planet["flags"] & PlanetFlags.INHABITED != 0:
			n += 1
	if n == 0:
		# Frigis: 088,045,105
		if system["coords"][2] + system["coords"][0] * 1000000 + system["coords"][1] * 1000 == 0x53f7631:
			if system["state"] & SystemState.UNKNOWN_STORY != 0:
				n = 1
	return n


def _systemSetPlanets(system):
	global _GLOB_SYSTEM_PLANETS_CREATED
	global _GLOB_SYSTEM_MOON_CAPACITY
	global _GLOB_SYSTEM_N_PLANETS
	global _GLOB_PLANET_INIT_0015f5b5

	_randomInit(system["random_seed"])
	_GLOB_PLANET_INIT_0015f5b5 = 0x22
	_random(999)
	_random(1)
	_random(9)
	if not "planets" in system:
		system["planets"] = []
		_systemSetNPlanets(system)
		if system["n_planets"] != 0:

			_GLOB_SYSTEM_PLANETS_CREATED = 0
			_GLOB_SYSTEM_MOON_CAPACITY = 10
			_GLOB_SYSTEM_N_PLANETS = system["n_planets"]

			for i in range(system["n_planets"]):
				planet = {
					"index": i,
					"flags": 0,
					"unknown4": 0,
				}
				_planetInit(system, planet)
				system["planets"].append(planet)
			
			x = _random(99)
			if 0x45 < x:
				if system["n_planets"] == 1:
					l2c = 0
				else:
					l2c = _random(system["n_planets"] - 2) & 0xffff
				system["planets"][l2c]["flags"] |= PlanetFlags.ASTEROIDS
			
			if system["flags"] & SystemFlags.INHABITED:
				n_inhabited = 0
				if (not "notable" in system) or (not "name" in system["notable"]):
					for planet in system["planets"]:
						i4 = planetSetInhabited(planet, True)
						n_inhabited += i4
					if n_inhabited == 0:
						idx = _random(system["n_planets"] - 1)
						planetSetInhabited(system["planets"][idx], False)
				else:
					idx = system["notable"]["index"]
					planetSetInhabited(system["planets"][idx], False)
			
			for i,planet in enumerate(system["planets"]):
				# Not 100% sure on this. Looks like it will check for whether the
				# system contains a story planet, and if so sets the unknown4 flag
				# -- but this will only work on the first planet in the system??
				if system["state"] & 1 << (i + 5 & 0x1f):
					planet["unknown4"] |= 2
			
			if ("notable" in system and "name" in system["notable"]) and (system["state"] & SystemState.UNKNOWN_STORY):
				idx = system["notable"]["index"]
				system["planets"][idx]["name"] = system["notable"]["name"]
		
		# Not sure this is how it's intended to be implemented.
		# I think they forgot to incrememnt the planet pointer
		# so just repeatedly set the value for the first planet.
		for planet in system["planets"]:
			u5 = _randomNext()
			system["planets"][0]["random_seed"] = u5


def systemTitle(system):
	t = system["name"]
	if "alias" in system:
		t += " (" + system["alias"] + ")"
	if "description" in system:
		t += " " + system["description"]
	return t


def systemDescription(system):
	# Todo: this is not as-implemented
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


def _systemGetBinaryStar(system):
	global _GLOB_SEED_BINARY_0015f634
	if system["flags"] & SystemFlags.BINARY == 0:
		return None,None
	
	_randomInit(system["random_seed"])
	u1 = _random(99)
	if u1 < 0x23:
		u1 = _random(99)
		if u1 < 0x55:
			u1 = _random(99)
			if u1 < 0x5c:
				u1 = _random(99)
				if u1 < 0x62:
					s2 = _random(0x1d)
					binary_class = s2
				else:
					s2 = _random(9)
					binary_class = s2 + 0x1e
			else:
				s2 = _random(9)
				binary_class = s2 + 0x28
		else:
			s2 = _random(9)
			binary_class = s2 + 0x32
	else:
		s2 = _random(9)
		binary_class = s2 + 0x3c
	binary_mag = _GLOB_SEED_BINARY_0015f634[binary_class*2]

	return binary_class,binary_mag


def _systemSetNPlanets(system):
	_randomInit(system["random_seed"])
	if (system["flags"] & SystemFlags.WHITE_DWARF) == 0:
		u1 = _random(99)
		if u1 < 10:
			system["n_planets"] = 0
		else:
			if (system["flags"] & SystemFlags.BINARY) == 0:
				local14 = 9
			else:
				local14 = 5
			u1 = _random(local14)
			system["n_planets"] = u1 + 1
	else:
		# white dwarf
		u1 = _random(99)
		if u1 < 0x5a:
			system["n_planets"] = 0
		else:
			system["n_planets"] = 1
	
	if (system["n_planets"] == 0) and ( ((system["flags"] & SystemFlags.INHABITED) != 0) or ((system["flags"] & SystemFlags.STATION) != 0) ):
		system["n_planets"] = 1


def systemHasAsteroidBelt(system):
	for planet in system["planets"]:
		if planet["flags"] & PlanetFlags.ASTEROIDS:
			return True
	return False

		
#
# Planets
#


PLANET_POSTFIXES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


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


def _planetInit(system, planet):
	global _GLOB_SYSTEM_PLANETS_CREATED
	global _GLOB_SYSTEM_MOON_CAPACITY

	planet["random_seed"] = _random(0xffff) & 0xffff
	planet["nth_created"] = _GLOB_SYSTEM_PLANETS_CREATED
	_utilsSetOrbit(planet, system["scale"] & 0xffff, planet["nth_created"])
	planet["_class_int"] = planetGetClass(system, planet)
	
	if system["flags"] & SystemFlags.STARBASE == 0:
		l14 = 0x3b < _random(99)
	else:
		l14 = False
	
	if l14:
		planet["flags"] |= PlanetFlags.UNKNOWN

	_GLOB_SYSTEM_PLANETS_CREATED += 1
	if "alias" in system:
		planet["name"] = system["alias"]
	else:
		planet["name"] = system["name"]
	planet["name"] += " " + PLANET_POSTFIXES[planet["index"]]

	if _GLOB_SYSTEM_MOON_CAPACITY < 1 or 0x3b < _random(99):
		planet["n_moons"] = 0
		planet["moons"] = []
	else:
		planet["n_moons"] = 1
		if 0x3f < _random(99):
			planet["n_moons"] += 1
			if 0x4d < _random(99):
				planet["n_moons"] += 1
				if 0x56 < _random(99):
					planet["n_moons"] += 1
		if _GLOB_SYSTEM_MOON_CAPACITY < planet["n_moons"]:
			planet["n_moons"] = _GLOB_SYSTEM_MOON_CAPACITY
		_GLOB_SYSTEM_MOON_CAPACITY -= planet["n_moons"]
		planet["moons"] = []
		for i in range(planet["n_moons"]):
			moon = {
				"index": i,
			}
			moonSetCoords(planet, system["scale"] & 0xffff, moon)
			moon["random_seed"] = _randomNext()
			moon["name"] = planet["name"] + MOON_POSTFIXES[i]
			moon["_class_int"] = moonGetClass(system, planet, moon)
			planet["moons"].append(moon)
	planet["flags"] &= 0xfe


def planetSetInhabited(planet, optional):
	u2 = _random(0xffff)
	c = planet["_class_int"]
	if not optional:
		planet["flags"] |= PlanetFlags.INHABITED
		inhabited = True
	else:
		if c in (12,13):
			inhabited = True
		else:
			if c in (0,7):
				inhabited = 0x4f < _random(99)
			else:
				if c in (2,4,5,6,10):
					inhabited = 0x59 < _random(99)
				else:
					inhabited = 0x5e < _random(99)
		if inhabited:
			planet["flags"] |= PlanetFlags.INHABITED
			if planet["n_moons"] != 0:
				inhabited = 0x5e < _random(99)
				if inhabited:
					# not sure this ever happens, or gets used?
					planet["moons"][0]["flags"] |= PlanetFlags.INHABITED
	_randomInit(u2)
	return inhabited


def planetGetClass(system, planet):
	u3 = _utilsCombineCoords(planet["orbit"][0], planet["orbit"][1], planet["orbit"][2])
	s1 = _utilsGetValueFromStar(system["_star_class_int"], u3)
	if s1 < 1 or 3 < s1:
		if s1 < 1:
			u2 = _random(99)
			if u2 < 0x2f:
				u2 = _random(99)
				if u2 < 0x41:
					l34 = _utilsGetValueFromPlanetParams(system, planet, 8, 8)
				else:
					l34 = _utilsGetValueFromPlanetParams(system, planet, 6, 9)
			else:
				l34 = _utilsGetValueFromPlanetParams(system, planet, 9, 8)
		else:
			u2 = _random(99)
			if u2 < 0x32:
				u2 = _random(99)
				if u2 < 0x50:
					u2 = _random(99)
					if u2 < 0x5a:
						u2 = _random(99)
						if u2 < 0x5f:
							u2 = _random(99)
							if u2 < 0x61:
								s1 = _random(2)
								if s1 == 0:
									l34 = _utilsGetValueFromPlanetParams(system, planet, 7, 0xb)
								else:
									if s1 == 2:
										l34 = _utilsGetValueFromPlanetParams(system, planet, 8, 8)
									else:
										l34 = _utilsGetValueFromPlanetParams(system, planet, 14, 0)
							else:
								l34 = _utilsGetValueFromPlanetParams(system, planet, 0xf, 1)
						else:
							l34 = _utilsGetValueFromPlanetParams(system, planet, 0xb, 8)
					else:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 8, 8)
				else:
					l34 = _utilsGetValueFromPlanetParams(system, planet, 0, 0xb)
			else:
				l34 = _utilsGetValueFromPlanetParams(system, planet, 1, 0xb)
	else:
		u2 = _random(99)
		if u2 < 0x2d:
			_random(99)
			if u2 < 0x5a:
				u2 = _random(99)
				if u2 < 0x5d:
					s1 = _random(2)
					if s1 == 0:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 3, 10)
					else:
						if s1 == 1:
							l34 = _utilsGetValueFromPlanetParams(system, planet, 4, 10)
						else:
							l34 = _utilsGetValueFromPlanetParams(system, planet, 5, 10)
				else:
					if system["_star_class_int"] < 0x1a or system["flags"] & PlanetFlags.INHABITED == 0:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 2, 10)
					else:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 0xd, 10)
			else:
				s1 = _random(2)
				if s1 == 0:
					l34 = _utilsGetValueFromPlanetParams(system, planet, 2, 10)
				else:
					if s1 == 1:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 10, 8)
					else:
						l34 = _utilsGetValueFromPlanetParams(system, planet, 8, 8)
		else:
			if system["_star_class_int"] < 0x1a or system["flags"] & PlanetFlags.INHABITED == 0:
				l34 = _utilsGetValueFromPlanetParams(system, planet, 2, 10)
			else:
				l34 = _utilsGetValueFromPlanetParams(system, planet, 0xc, 10)
	return l34


#
# Moons
#


MOON_POSTFIXES = ["a", "b", "c", "d"]


def moonSetCoords(planet, system_u2, moon):
	next_planet = {}
	if planet["index"] == 14:
		scale = 63
	else:
		_utilsSetOrbit(next_planet, system_u2, planet["index"] + 1)
		u0 = planet["orbit"][0] + planet["orbit"][1] * 60 + planet["orbit"][2] * 3600
		u1 = next_planet["orbit"][0] + next_planet["orbit"][1]*60 + next_planet["orbit"][2]*3600
		delta = u1 - u0
		scale = delta - delta//10 >> 2
	
	if 63 < scale or scale == 0:
		scale = 63
	
	moon["orbit"] = [0,0,0]
	delta = scale >> 1
	l30 = _random(delta & 0xffff) + delta
	delta = planet["orbit"][0] + l30 + moon["index"]*scale + planet["orbit"][1]*60 + planet["orbit"][2]*3600
	moon["orbit"][2] = delta // 3600
	delta = delta - moon["orbit"][2]*3600
	moon["orbit"][1] = delta // 60
	l34 = delta - moon["orbit"][1]*60
	moon["orbit"][0] = l34


def moonGetClass(system, planet, moon):
	u3 = _utilsCombineCoords(moon["orbit"][0], moon["orbit"][1], moon["orbit"][2])
	s1 = _utilsGetValueFromStar(system["_star_class_int"], u3)
	if s1 < 1 or 3 < s1:
		if s1 < 1:
			if planet["_class_int"] == 6 and 0x2e < _random(99):
				moon_class = 9
			else:
				moon_class = 8
		else:
			if (planet["_class_int"] == 0xe or planet["_class_int"] == 0xf or planet["_class_int"] == 0) and 0x31 < _random(99):
				moon_class = 1
			else:
				if planet["_class_int"] == 1:
					if _random(99) < 0x5a:
						if _random(1) == 0:
							moon_class = 11
						else:
							moon_class = 7
					else:
						moon_class = 8
				else:
					moon_class = 8
	else:
		if planet["_class_int"] in (12, 13, 5, 4, 3, 2):
			s1 = _random(1)
			if s1 == 0:
				moon_class = 10
			else:
				moon_class = 8
		else:
			moon_class = 8
	return moon_class


def moonDescription(moon):
	if "class" in moon:
		letter = moon["class"]
	else:
		letter = PLANET_CLASSES[moon["_class_int"]]
	return "This is a class {} moon.".format(letter)


#
# Body
#


BODY_UNKNOWN0 = {
	ObjectType.ION_STORM: 8591061,
	ObjectType.QUASAROID: 8591388,
	ObjectType.BLACK_HOLE: 8592151,
	ObjectType.SUBSPACE_VORTEX: 8592697,
	ObjectType.UNITY_DEVICE: 0,
	ObjectType.SPECIAL_ITEM: 0,
}


def bodyDescription(body):
	# Todo: this is a guess, and needs to be replaced with the actual function
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


#
# Station
#


def stationDescription(station):
	# Todo: this is a guess, and needs to be replaced with the actual function
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
# Utils
#


_GLOB_PLANET_INIT_0015f5b5 = 0
_GLOB_PLANET_ORBITS_dAU = [ 0x04, 0x07, 0x0a, 0x10, 0x1c, 0x34, 0x64, 0xc4, 0x184, 0x304, 0x604]
_GLOB_SEED_BINARY_0015f634 = [
	0xba,0xff,0xbd,0xff,0xc0,0xff,0xc3,0xff,0xc6,0xff,0xc9,0xff,0xcb,0xff,0xce,0xff,
	0xd1,0xff,0xd4,0xff,0xd8,0xff,0xdf,0xff,0xe5,0xff,0xec,0xff,0xf3,0xff,0xf6,0xff,
	0x00,0x00,0x03,0x00,0x07,0x00,0x0a,0x00,0x0b,0x00,0x0e,0x00,0x11,0x00,0x14,0x00,
	0x15,0x00,0x16,0x00,0x17,0x00,0x19,0x00,0x1b,0x00,0x1d,0x00,0x1e,0x00,0x1f,0x00,
	0x20,0x00,0x21,0x00,0x23,0x00,0x25,0x00,0x27,0x00,0x28,0x00,0x29,0x00,0x2b,0x00,
	0x2c,0x00,0x2e,0x00,0x30,0x00,0x32,0x00,0x34,0x00,0x35,0x00,0x36,0x00,0x37,0x00,
	0x39,0x00,0x3b,0x00,0x3c,0x00,0x3e,0x00,0x41,0x00,0x43,0x00,0x46,0x00,0x4a,0x00,
	0x4d,0x00,0x50,0x00,0x54,0x00,0x57,0x00,0x5a,0x00,0x60,0x00,0x64,0x00,0x6a,0x00,
	0x6e,0x00,0x75,0x00,0x78,0x00,0x8c,0x00,0xa0,0x00,0xb4,0x00,0x00,0x00,0x00,0x00
	]


def _utilsSetOrbit(object, system_scale, planet_nth):
	orbit = (_GLOB_PLANET_ORBITS_dAU[planet_nth] * system_scale) // 10
	orbit_Ls = orbit // 3600
	orbit = orbit - (orbit_Ls * 3600)
	orbit_Lmin = orbit // 60
	orbit_LH = orbit - (orbit_Lmin * 60)
	object["orbit"] = [orbit_LH,orbit_Lmin,orbit_Ls]


def _utilsCombineCoords(x,y,z):
	return ((z*3600 + y*60 + x) * 1024) // 498


def _utilsGetValueFromStar(star_class, p2):
	if star_class < 6:
		l18 = p2 >> 0xc
	else:
		if star_class < 16:
			l18 = p2 // 0xa00
		else:
			if star_class < 26:
				l18 = p2 // 0x600
			else:
				if star_class < 36:
					l18 = p2 // 0x300
				else:
					if star_class < 46:
						l18 = p2 >> 9
					else:
						if star_class < 56:
							l18 = p2 // 0x180
						else:
							l18 = p2 >> 7
	return l18


def _utilsGetValueFromParam(p):
	if p == 14 or p == 15:
		return 6
	else:
		if p == 0 or p == 1:
			return 4
		else:
			if p == 8 or p == 9 or p == 10 or p == 11:
				return 2
			else:
				# 2 3 4 5 6 7 12 13
				return 4
	

def _utilsGetValueFromPlanetParams(system, planet, p3, p4):
	global _GLOB_PLANET_INIT_0015f5b5

	i2 = _utilsGetValueFromParam(p3)
	i3 = _utilsGetValueFromParam(p4)
	n = system["n_planets"] - planet["index"]
	l28 = i2
	if planet["index"] == 0:
		_GLOB_PLANET_INIT_0015f5b5 -= l28
		l2c = p3
	else:
		l14 = _GLOB_PLANET_INIT_0015f5b5
		if n != 1:
			if n == 2:
				l14 = _GLOB_PLANET_INIT_0015f5b5 >> 0x1
			else:
				l14 = (l14 - 6) // (n -1)
		
		if l14 < i2:
			if l14 < i3:
				_GLOB_PLANET_INIT_0015f5b5 -= 2
				l2c = 8
			else:
				l24 = i3
				_GLOB_PLANET_INIT_0015f5b5 -= l24
				l2c = p4
		else:
			_GLOB_PLANET_INIT_0015f5b5 -= l28
			l2c = p3
	return l2c


_GLOB_RANDOM_VALUE = 0x1


def _randomInit(seed):
	global _GLOB_RANDOM_VALUE
	seed &= 0xffffffff
	_GLOB_RANDOM_VALUE = seed


def _randomNext():
	global _GLOB_RANDOM_VALUE
	u2 = _GLOB_RANDOM_VALUE * 0x41c64e6d + 0x3039
	u2 &= 0xffffffff
	_GLOB_RANDOM_VALUE = u2
	return u2 >> 0x10 & 0x7fff


def _random(param_1):
	next = _randomNext()
	return (next & 0xff) * param_1 + 0x80 >> 8
