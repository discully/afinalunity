from AFU.AstroCore import *
from enum import IntEnum, Enum


# RANDOM

GLOB_UNKNOWN_0 = 0x1
#GLOB_DAT_0015f5fa = [
#	0x04,0x00,0x07,0x00,0x0a,0x00,0x10,0x00,0x1c,0x00,0x34,0x00,0x64,0x00,0xc4,0x00,
#	0x84,0x01,0x04,0x03, 0x04,0x06, 0x04,0x0c, 0x04,0x18, 0x04,0x30,0xe4,0x5f,0x00,0x00,
#	0x00,0x00,0xd4,0xd3,0x05,0x00,0xf5,0xd3,0x05,0x00,0x00,0x00,0x00,0x00,0x16,0xd4,
#	0x05,0x00,0x63,0xd4,0x05,0x00,0x00,0x00,0x00,0x00]
GLOB_DAT_0015f5fa = [ 0x04, 0x07, 0x0a, 0x10, 0x1c, 0x34, 0x64, 0xc4, 0x184, 0x304, 0x604]
GLOB_DAT_0015f634 = [
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
GLOB_DAT_ForAstroUse = 0

DAT_InitBodyUnknown26 = [
	0x3C750A03, 0x3C6EBF66, 0x3C6878FB, 0x3C622E5E, 0x3C5BE7F3, 0x3C559D56, 0x3C4F56EB, 0x3C491080,
	0x3C42C5E3, 0x3C3C7F78, 0x3C3634DB, 0x3C2FEE70, 0x3C29A3D3, 0x3C235D68, 0x3C1D12CB, 0x3C16CC60,
	0x3C1081C3, 0x3C0A3B58, 0x3C03F0BB, 0x3BFB54A0, 0x3BEEBF66, 0x3BE23290, 0x3BD59D56, 0x3BC91080,
	0x3BBC7B46, 0x3BAFEE70, 0x3BA35936, 0x3B96CC60, 0x3B8A3726, 0x3B7B54A0, 0x3B622A2C, 0x3B491080,
	0x3B2FE60C, 0x3B16CC60, 0x3AFB43D9, 0x3AC91080, 0x3A96BB99, 0x3A491080, 0x39C8CD64,
]





def RandomInit(u0):
	global GLOB_UNKNOWN_0
	u0 &= 0xffffffff
	GLOB_UNKNOWN_0 = u0

def RandomNext():
	global GLOB_UNKNOWN_0
	u2 = GLOB_UNKNOWN_0 * 0x41c64e6d + 0x3039
	u2 &= 0xffffffff
	GLOB_UNKNOWN_0 = u2
	return u2 >> 0x10 & 0x7fff

def Random(param_1):
	u1 = RandomNext()
	return (u1 & 0xff) * param_1 + 0x80 >> 8


#
# Sector
#


SECTOR_DESCRIPTIONS = {
	Alignment.FEDERATION: "This sector is aligned with the Federation.",
	Alignment.ROMULAN: "This sector is aligned with the Romulans.",
	Alignment.NEUTRAL: "This sector is in the neutral zone.",
	Alignment.NEBULA: "This sector is in the Z'Tarnis Nebula.",
	Alignment.NONALIGNED: "This sector is nonaligned.",
}


def sectorDescription(sector):
	d = "Sector "
	d += sector["name"]
	d += SECTOR_DESCRIPTIONS[sector["alignment"]]
	if "desc" in sector and sector["desc"]:
		d += "  " + sector["desc"]
	return d


#
# SYSTEM
#


GLOB_SYSTEM_PLANETS_CREATED = 0
GLOB_SYSTEM_MOON_CAPACITY = 10
GLOB_SYSTEM_N_PLANETS = 0

PLANET_POSTFIXES = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
MOON_POSTFIXES = ["a", "b", "c", "d"]



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



def systemGetBinaryStar(system):
	global GLOB_DAT_0015f634
	if system["flags"] & 2 == 0:
		return None,None
	
	RandomInit(system["random_seed"])
	u1 = Random(99)
	if u1 < 0x23:
		u1 = Random(99)
		if u1 < 0x55:
			u1 = Random(99)
			if u1 < 0x5c:
				u1 = Random(99)
				if u1 < 0x62:
					s2 = Random(0x1d)
					binary_class = s2
				else:
					s2 = Random(9)
					binary_class = s2 + 0x1e
			else:
				s2 = Random(9)
				binary_class = s2 + 0x28
		else:
			s2 = Random(9)
			binary_class = s2 + 0x32
	else:
		s2 = Random(9)
		binary_class = s2 + 0x3c
	binary_mag = GLOB_DAT_0015f634[binary_class*2]

	return binary_class,binary_mag



def SystemSetNPlanets(system):
	RandomInit(system["random_seed"])
	if (system["flags"] & 1) == 0:
		# not wite dwarf
		u1 = Random(99)
		if u1 < 10:
			system["n_planets"] = 0
		else:
			if (system["flags"] & 2) == 0:
				# not binary
				local14 = 9
			else:
				# binary
				local14 = 5
			u1 = Random(local14)
			system["n_planets"] = u1 + 1
	else:
		# white dwarf
		u1 = Random(99)
		if u1 < 0x5a:
			system["n_planets"] = 0
		else:
			system["n_planets"] = 1
	
	if (system["n_planets"] == 0) and ( ((system["flags"] & 0x10) != 0) or ((system["flags"] & 0x4) != 0) ):
		# 0 planets and inhabited or station
		system["n_planets"] = 1


def Astro_System_HasAsteroidBelt(system):
	for planet in system["planets"]:
		if planet["flags"] & PlanetFlags.ASTEROIDS:
			return True
	return False


def Astro_System_Status(system):
	return system["state"]


def _UtilsSetCoords(object, system_u2, planet_nth):
	i1 = (GLOB_DAT_0015f5fa[planet_nth] * system_u2) // 10
	z = i1 // 3600
	i1 = i1 + z * -3600
	y = i1 // 60
	x = i1 + y * -60
	object["coords"] = [x,y,z]


def _UtilsCombineCoords(x,y,z):
	return ((z*3600 + y*60 + x) * 1024) // 498


def _UtilsGetValueFromStar(star_class, p2):
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


def _UtilsGetValue(p):
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
	

def _UtilsGetValueFromParams(system, planet, p3, p4):
	global GLOB_DAT_ForAstroUse

	# possible outputs: p3, 8, p4
	
	i2 = _UtilsGetValue(p3)
	i3 = _UtilsGetValue(p4)
	n = system["n_planets"] - planet["index"]
	l28 = i2
	if planet["index"] == 0:
		GLOB_DAT_ForAstroUse -= l28
		l2c = p3
	else:
		l14 = GLOB_DAT_ForAstroUse
		if n != 1:
			if n == 2:
				l14 = GLOB_DAT_ForAstroUse >> 0x1
			else:
				l14 = (l14 - 6) // (n -1)
		# if l14 < 2 is an error
		if l14 < i2:
			if l14 < i3:
				GLOB_DAT_ForAstroUse -= 2
				l2c = 8
			else:
				l24 = i3
				GLOB_DAT_ForAstroUse -= l24
				l2c = p4
		else:
			GLOB_DAT_ForAstroUse -= l28
			l2c = p3
	return l2c

		
#
# Planets
#


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





def _planetInit(system, planet):
	global GLOB_SYSTEM_PLANETS_CREATED
	global GLOB_SYSTEM_MOON_CAPACITY

	planet["random_seed"] = Random(0xffff) & 0xffff
	planet["nth_created"] = GLOB_SYSTEM_PLANETS_CREATED
	_UtilsSetCoords(planet, system["unknown2"] & 0xffff, planet["nth_created"])
	planet["class"] = planetGetClass(system, planet)
	
	if system["flags"] & SystemFlags.STARBASE == 0:
		l14 = 0x3b < Random(99)
	else:
		l14 = False
	
	if l14:
		planet["flags"] |= PlanetFlags.UNKNOWN

	GLOB_SYSTEM_PLANETS_CREATED += 1
	if "alias" in system:
		planet["name"] = system["alias"]
	else:
		planet["name"] = system["name"]
	planet["name"] += " " + PLANET_POSTFIXES[planet["index"]]

	if GLOB_SYSTEM_MOON_CAPACITY < 1 or 0x3b < Random(99):
		planet["n_moons"] = 0
		planet["moons"] = []
	else:
		planet["n_moons"] = 1
		if 0x3f < Random(99):
			planet["n_moons"] += 1
			if 0x4d < Random(99):
				planet["n_moons"] += 1
				if 0x56 < Random(99):
					planet["n_moons"] += 1
		if GLOB_SYSTEM_MOON_CAPACITY < planet["n_moons"]:
			planet["n_moons"] = GLOB_SYSTEM_MOON_CAPACITY
		GLOB_SYSTEM_MOON_CAPACITY -= planet["n_moons"]
		planet["moons"] = []
		for i in range(planet["n_moons"]):
			moon = {
				"index": i,
			}
			moonSetCoords(planet, system["unknown2"] & 0xffff, moon)
			moon["random_seed"] = RandomNext()
			moon["name"] = planet["name"] + MOON_POSTFIXES[i]
			moon["class"] = moonGetClass(system, planet, moon)
			planet["moons"].append(moon)
	planet["flags"] &= 0xfe


def planetSetInhabited(planet, optional):
	u2 = Random(0xffff)
	c = planet["class"]
	if not optional:
		planet["flags"] |= PlanetFlags.INHABITED
		inhabited = True
	else:
		if c in (12,13):
			inhabited = True
		else:
			if c in (0,7):
				inhabited = 0x4f < Random(99)
			else:
				if c in (2,4,5,6,10):
					inhabited = 0x59 < Random(99)
				else:
					inhabited = 0x5e < Random(99)
		if inhabited:
			planet["flags"] |= 0x10
			if planet["n_moons"] != 0:
				inhabited = 0x5e < Random(99)
				if inhabited:
					planet["moons"][0]["unknown32"] |= 0x10
	RandomInit(u2)
	return inhabited


def planetGetClass(system, planet):
	u3 = _UtilsCombineCoords(planet["coords"][0], planet["coords"][1], planet["coords"][2])
	s1 = _UtilsGetValueFromStar(system["star_class_int"], u3)
	if s1 < 1 or 3 < s1:
		if s1 < 1:
			u2 = Random(99)
			if u2 < 0x2f:
				u2 = Random(99)
				if u2 < 0x41:
					l34 = _UtilsGetValueFromParams(system, planet, 8, 8)
				else:
					l34 = _UtilsGetValueFromParams(system, planet, 6, 9)
			else:
				l34 = _UtilsGetValueFromParams(system, planet, 9, 8)
		else:
			u2 = Random(99)
			if u2 < 0x32:
				u2 = Random(99)
				if u2 < 0x50:
					u2 = Random(99)
					if u2 < 0x5a:
						u2 = Random(99)
						if u2 < 0x5f:
							u2 = Random(99)
							if u2 < 0x61:
								s1 = Random(2)
								if s1 == 0:
									l34 = _UtilsGetValueFromParams(system, planet, 7, 0xb)
								else:
									if s1 == 2:
										l34 = _UtilsGetValueFromParams(system, planet, 8, 8)
									else:
										l34 = _UtilsGetValueFromParams(system, planet, 14, 0)
							else:
								l34 = _UtilsGetValueFromParams(system, planet, 0xf, 1)
						else:
							l34 = _UtilsGetValueFromParams(system, planet, 0xb, 8)
					else:
						l34 = _UtilsGetValueFromParams(system, planet, 8, 8)
				else:
					l34 = _UtilsGetValueFromParams(system, planet, 0, 0xb)
			else:
				l34 = _UtilsGetValueFromParams(system, planet, 1, 0xb)
	else:
		u2 = Random(99)
		if u2 < 0x2d:
			Random(99)
			if u2 < 0x5a:
				u2 = Random(99)
				if u2 < 0x5d:
					s1 = Random(2)
					if s1 == 0:
						l34 = _UtilsGetValueFromParams(system, planet, 3, 10)
					else:
						if s1 == 1:
							l34 = _UtilsGetValueFromParams(system, planet, 4, 10)
						else:
							l34 = _UtilsGetValueFromParams(system, planet, 5, 10)
				else:
					if system["star_class_int"] < 0x1a or system["flags"] & PlanetFlags.INHABITED == 0:
						l34 = _UtilsGetValueFromParams(system, planet, 2, 10)
					else:
						l34 = _UtilsGetValueFromParams(system, planet, 0xd, 10)
			else:
				s1 = Random(2)
				if s1 == 0:
					l34 = _UtilsGetValueFromParams(system, planet, 2, 10)
				else:
					if s1 == 1:
						l34 = _UtilsGetValueFromParams(system, planet, 10, 8)
					else:
						l34 = _UtilsGetValueFromParams(system, planet, 8, 8)
		else:
			if system["star_class_int"] < 0x1a or system["flags"] & PlanetFlags.INHABITED == 0:
				l34 = _UtilsGetValueFromParams(system, planet, 2, 10)
			else:
				l34 = _UtilsGetValueFromParams(system, planet, 0xc, 10)
	return l34


#
# Moons
#


def moonSetCoords(planet, system_u2, moon):
	next_planet = {}
	if planet["index"] == 14:
		scale = 63
	else:
		_UtilsSetCoords(next_planet, system_u2, planet["index"] + 1)
		u0 = planet["coords"][0] + planet["coords"][1] * 60 + planet["coords"][2] * 3600
		u1 = next_planet["coords"][0] + next_planet["coords"][1]*60 + next_planet["coords"][2]*3600
		delta = u1 - u0
		scale = delta - delta//10 >> 2
	
	if 63 < scale or scale == 0:
		scale = 63
	
	moon["coords"] = [0,0,0]
	delta = scale >> 1
	l30 = Random(delta & 0xffff) + delta
	delta = planet["coords"][0] + l30 + moon["index"]*scale + planet["coords"][1]*60 + planet["coords"][2]*3600
	moon["coords"][2] = delta // 3600
	delta = delta - moon["coords"][2]*3600
	moon["coords"][1] = delta // 60
	l34 = delta - moon["coords"][1]*60
	moon["coords"][0] = l34


def moonGetClass(system, planet, moon):
	u3 = _UtilsCombineCoords(moon["coords"][0], moon["coords"][1], moon["coords"][2])
	s1 = _UtilsGetValueFromStar(system["_star_class_int"], u3)
	if s1 < 1 or 3 < s1:
		if s1 < 1:
			if planet["class"] == 6 and 0x2e < Random(99):
				moon_class = 9
			else:
				moon_class = 8
		else:
			if (planet["class"] == 0xe or planet["class"] == 0xf or planet["class"] == 0) and 0x31 < Random(99):
				moon_class = 1
			else:
				if planet["class"] == 1:
					if Random(99) < 0x5a:
						if Random(1) == 0:
							moon_class = 11
						else:
							moon_class = 7
					else:
						moon_class = 8
				else:
					moon_class = 8
	else:
		if planet["class"] in (12, 13, 5, 4, 3, 2):
			s1 = Random(1)
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
# System
#


class SystemState (IntEnum):
	CHARTED = 0x1
	UNKNOWN_LETHE = 0x2
	UNKNOWN_SCANNED = 0x4
	SCANNED = 0x8
	UNKNOWN_STORY = 0x10


def systemSetPlanets(system):
	global GLOB_SYSTEM_PLANETS_CREATED
	global GLOB_SYSTEM_MOON_CAPACITY
	global GLOB_SYSTEM_N_PLANETS
	global GLOB_DAT_ForAstroUse

	RandomInit(system["random_seed"])
	GLOB_DAT_ForAstroUse = 0x22
	Random(999)
	Random(1)
	Random(9)
	if not "planets" in system:
		system["planets"] = []
		SystemSetNPlanets(system)
		if system["n_planets"] != 0:

			GLOB_SYSTEM_PLANETS_CREATED = 0
			GLOB_SYSTEM_MOON_CAPACITY = 10
			GLOB_SYSTEM_N_PLANETS = system["n_planets"]

			for i in range(system["n_planets"]):
				planet = {
					"index": i,
					"flags": 0,
					"unknown4": 0,
				}
				_planetInit(system, planet)
				system["planets"].append(planet)
			
			x = Random(99)
			if 0x45 < x:
				if system["n_planets"] == 1:
					l2c = 0
				else:
					l2c = Random(system["n_planets"] - 2) & 0xffff
				system["planets"][l2c]["flags"] |= PlanetFlags.ASTEROIDS
			
			if system["flags"] & SystemFlags.INHABITED:
				n_inhabited = 0
				if (not "notable" in system) or (not "name" in system["notable"]):
					for planet in system["planets"]:
						i4 = planetSetInhabited(planet, True)
						n_inhabited += i4
					if n_inhabited == 0:
						idx = Random(system["n_planets"] - 1)
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
			u5 = RandomNext()
			system["planets"][0]["random_seed"] = u5


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
