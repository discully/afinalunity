

#
# Co-ordinates
#

# The game space consists of an 8x8x8 grid (512 major co-ordinates), each cube in the grid is a "sector".
# Each sector has a 20*20*20 grid (8000 minor co-ordinates), some of which will contain a star system.

N_SECTORS = 512 # 8x8x8

def globalCoords(major_coords, minor_coords):
	return tuple(major*20 + minor for major,minor in zip(major_coords,minor_coords))


def minorCoords(global_coords):
	return (global_coords[0] % 20, global_coords[1] % 20, global_coords[2] % 20)


def majorCoords(global_coords):
	return (global_coords[0] // 20, global_coords[1] // 20, global_coords[2] // 20)


#
# Standard Structs
#

def readLocation(f):
	loc = {}
	loc["sector_id"] = f.readUInt16()
	loc["system_index"] = f.readUInt16()
	loc["planet_index"] = f.readUInt16()
	loc["obj_type"] = f.readUInt16()
	loc["body_station_index"] = f.readUInt16()
	loc["body_index"] = f.readUInt16()
	return loc


def locationIndex(x, y, z):
	return x*1000000 + y*1000 + z


def locationIndexToCoords(index):
	x = index // 1000000
	y = index % 1000000 // 1000
	z = index % 1000
	return [x,y,z]