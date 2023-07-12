from argparse import ArgumentParser
from pathlib import Path
from AFU import Astro
from AFU.Utils import Encoder as AFUEncoder
from json import dump


def _m_add(nm, name, item):
	nm[ name.replace(" ", "").lower() ] = item

def selectByName(astro, name):
	name = name.replace(" ", "").lower()

	m = {}
	for sector in astro:
		_m_add(m, sector["name"], sector)
		for system in sector["systems"]:
			_m_add(m, system["name"], system)
			if "alias" in system:
				_m_add(m, system["alias"], system)
			if "station" in system:
				_m_add(m, system["station"]["name"], system["station"])
			for planet in system["planets"]:
				_m_add(m, planet["name"], planet)
				if "alias" in planet:
					_m_add(m, planet["alias"], planet)
				for moon in planet["moons"]:
					_m_add(m, moon["name"], moon)
		for body in sector["bodies"]:
			_m_add(m, body["name"], body)
		for station in sector["stations"]:
			_m_add(m, station["name"], station)
	
	return m.get(name, None)


def main():
	parser = ArgumentParser(description="Combines data from the three astro files into one json file")
	parser.add_argument("astrodb", type=Path, help="Path to astro.db")
	parser.add_argument("aststat", type=Path, help="Path to ast_stat.dat or a SAVEGAME file")
	parser.add_argument("-m", "--more", type=bool, help="Include all fields, not just processed ones.", default=False)
	parser.add_argument("-n", "--name", type=str, help="Output only the object with the specified name", default="")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place json in", default=".")
	args = parser.parse_args()

	ast = Astro.astrogation(args.astrodb, args.aststat)
	
	if not args.more:
		for sector in ast:
			sector.pop("n_systems")
			sector.pop("n_bodies")
			sector.pop("n_stations")
			for system in sector["systems"]:
				system.pop("random_seed")
				system.pop("station_planet_index")
				system.pop("station_type")
				system.pop("_star_class_int")
				system.pop("random_seed_2")
				if system["binary"]:
					system["binary"].pop("_class_int")
				for planet in system["planets"]:
					planet.pop("unknown4")
					planet.pop("random_seed")
					planet.pop("nth_created")
					planet.pop("_class_int")
					planet.pop("n_moons")
					for moon in planet["moons"]:
						moon.pop("random_seed")
						moon.pop("_class_int")
				if "station" in system:
					system["station"].pop("random_seed")
	
	if args.name:
		data = selectByName(ast, args.name)
		if not data:
			raise ValueError("Could not find '{}'".format(args.name))
	else:
		data = ast

	output_path = args.output_dir.joinpath("astro.json")
	dump(data, open(output_path, "w"), indent="\t", cls=AFUEncoder)


if __name__ == "__main__":
	main()
