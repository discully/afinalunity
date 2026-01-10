from pathlib import Path
from AFU.File import File, fpos
from AFU import Astro, Computer, Block, World
from enum import Enum


def _readBlockTravelHistory(f, block):
	data = []
	f.setPosition(block["data_offset"])
	assert(f.readUInt8() == 0) # padding
	
	while f.pos() != block["end_offset"]:
		
		entry = {}
		data_size = f.readUInt32()
		data_start = f.pos()

		f.readUInt32() # ptr name
		f.readUInt32() # ptr text
		assert(f.readUInt16() == 0)
		has_extra = {0: False, 0x10: True}[f.readUInt16()]
		f.readUInt32() # ptr name
		f.readUInt32() # ptr text
		assert(f.readUInt32() == 0)
		f.readUInt32() # ptr dest 2

		dest_sector_id = f.readUInt16()
		dest_system_index = f.readUInt16()
		dest_planet_index = f.readUInt16()
		dest_object_type = f.readUInt16() & 0xff # Stored in a short but only the little byte gets set
		dest_body_station_index = f.readUInt16()
		assert(f.readUInt16() == 0x0)

		if dest_system_index == 0xffff: dest_system_index = None
		if dest_planet_index == 0xffff: dest_planet_index = None
		if dest_body_station_index == 0xffff: dest_body_station_index = None
		if dest_object_type == 0xff:
			dest_object_type = None
		else:
			dest_object_type = Astro.ObjectType(dest_object_type)

		entry["destination"] = {
			"sector_id": dest_sector_id,
			"system_index": dest_system_index,
			"planet_index": dest_planet_index,
			"object_type": dest_object_type,
			"body_station_index": dest_body_station_index,
		}
		
		# Extra structure

		if has_extra:
			f.readUInt32() # ptr name
			extra_global_coords = [f.readUInt32() for i in range(3)]
			extra_system_coords = [f.readUInt32() for i in range(3)]
			assert(f.readUInt32() == 0xffffffff)

			extra_sector_id = f.readUInt16()
			extra_oject_type = f.readUInt8()
			extra_status = f.readUInt8() # TODO: Either 1 or 0. Think this is something to do with having been scanned/charterd.
			assert(f.readUInt16() == 0)
			extra_system_index = f.readUInt16()
			extra_planet_index = f.readUInt16()
			assert(f.readUInt16() == 0)
			extra_body_unknown26 = f.readUInt32()

			if extra_system_index == 0xffff: extra_system_index = None
			if extra_planet_index == 0xffff: extra_planet_index = None
			if extra_oject_type == 0xff:
				extra_oject_type = None
			else:
				extra_oject_type = Astro.ObjectType(extra_oject_type)

			entry["extra"] = {
				"global_coords": extra_global_coords,
				"system_coords": extra_system_coords,
				"sector_id": extra_sector_id,
				"object_type": extra_oject_type,
				"status": extra_status,
				"system_index": extra_system_index,
				"planet_index": extra_planet_index,
				"body_unknown26": extra_body_unknown26,
			}

		entry["name"] = f.readString()
		entry["desc"] = f.readString()
		
		data_end = f.pos()
		assert(data_end - data_start == data_size)

		data.append(entry)

	assert(f.pos() == block["end_offset"])
	return {
		"travel_history": data,
	}


def _readBlockAststat(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	data["astro_state"] = Astro.readAstroState(f)
	assert(f.pos() == block["end_offset"])
	return data


def _readBlockCompstat(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	data["computer_state"] = Computer.readCompstat(f)

	# Pretty sure what follows is just junk grabbed from reading too
	# many bytes from memory. The COMPSTAT file is 388 bytes. But
	# the game copies 540 bytes in/out of memory. That means the last
	# 152 bytes of this section are just junk.
	f.setPosition(f.pos() + 152)

	assert(f.pos() == block["end_offset"])
	return data


def _readBlockVideos(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	i = 0
	videos = []
	while f.pos() < block["end_offset"]:
		visible = (False, True)[f.readUInt8()]
		videos.append({"index": i, "visible": visible})
		i += 1
	data["videos"] = videos

	assert(f.pos() == block["end_offset"])
	return data


def _readBlockScreenRegions(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	screen_regions = []
	while True:
		n = f.readUInt32()
		if n == 0xffffffff: break

		world_id = World.WorldId(f.readUInt32())
		screen_id = f.readUInt32()
		n_regions = f.readUInt32()
		region_types = [World.ScreenRegionType(f.readUInt8()) for i in range(n_regions)]

		[f.readUInt8() for i in range(3)] # either padding or an error in the game's arithmetic

		screen_regions.append({
			"world_id": world_id,
			"screen_id": screen_id,
			"n_regions": n_regions,
			"region_types": region_types
		})
	
	assert(f.pos() == block["end_offset"])
	return {
		"screen_regions": screen_regions,
	}


def _readBlockConverations(f, block):
	f.setPosition(block["data_offset"])

	assert(f.readUInt8() == 0)

	conversation_buffer_n = f.readUInt32() # entries in the buffer
	conversation_buffer_size = f.readUInt32() # allocated size of the buffer
	situation_buffer_n = f.readUInt32()
	situation_buffer_size = f.readUInt32()
	action_buffer_n = f.readUInt32()
	action_buffer_size = f.readUInt32()
	
	conversation_buffer = []
	for i in range(conversation_buffer_n):
		conversation_buffer.append([f.readUInt32() for j in range(3)])
	
	situation_buffer = []
	for i in range(situation_buffer_n):
		situation_buffer.append([f.readUInt32() for j in range(3)])
	
	action_buffer = [f.readUInt8() for j in range(action_buffer_n)]

	conversation_history_n = f.readUInt32()
	conversation_history = []
	for i in range(conversation_history_n):
		conversation = []
		c_size = f.readUInt32()
		c_start = f.pos()
		assert(f.readUInt32() == c_size)
		while True:
			c_world = f.readUInt8()
			c_index = f.readUInt8()
			if c_world == 0xff:
				assert(c_index == 0xff)
				break
			elif c_world == 0:
				assert(c_index == 0xff)
				c_line = f.readString()
			else:
				c_id = f.readUInt8()
				c_state = f.readUInt8()
				c_unknown1 = f.readUInt8()
				c_unknown2 = f.readUInt8()
				c_line = {
					"world": c_world, "index": c_index,
					"id": c_id, "state": c_state, "unknown1": c_unknown1, "unknown2": c_unknown2
					}
			conversation.append(c_line)
		assert(f.pos() == c_start + c_size)
		conversation_history.append(conversation)

	recent_vacs = [f.readStringBuffer(14) for j in range(3)]

	return {
		"conversations": {
			"conversation_buffer": conversation_buffer,
			"situation_buffer": situation_buffer,
			"action_buffer": action_buffer,
			"conversation_history": conversation_history,
			"recent_vacs": recent_vacs,
		}
	}


class BlockDiffType (Enum):
	CORE = 0x1
	OBJ = 0x2
	PHASER = 0x4
	SCREEN = 0x8
	UNKNOWN_9 = 0x9
	START = 0x10
	UNKNOWN_11 = 0x11
	RESULT_COUNTER = 0x20


def _readDiffHeader(f):
	diff = {}
	diff["target"] = f.readUInt32()
	diff["type"] = f.readUInt32()
	diff["unknown_8"] = f.readUInt32()
	diff["ptr_next"] = f.readUInt32()
	if diff["target"] != 0xffffffff:
		diff["type"] = BlockDiffType(diff["type"])
	return diff


def _readDiff(f):
	diff_type = f.readUInt32()
	if diff_type == 0xffffffff: return None
	diff_type = BlockDiffType(diff_type)

	diff = _readDiffHeader(f)

	assert(diff_type == diff["type"])

	if diff_type == BlockDiffType.CORE:
		data = [f.readUInt8() for i in range(0x24)]
	elif diff_type == BlockDiffType.OBJ:
		data = [f.readUInt8() for i in range(0xd4)]
	elif diff_type == BlockDiffType.PHASER:
		data = [f.readUInt8() for i in range(0x14)]
	elif diff_type == BlockDiffType.SCREEN:
		data = [f.readUInt8() for i in range(0x0c)]
	elif diff_type == BlockDiffType.START:
		data = [f.readUInt8() for i in range(0x28)]
	else:
		raise ValueError(f"Unexpected diff type: {diff_type}")
	diff["data"] = data

	return diff


def _readDiffObj(f):
	diff = _readDiffHeader(f)
	diff["flags"] = f.readUInt32()
	diff["state"] = f.readUInt16()
	diff["y_adjust"] = f.readUInt16()
	diff["anim_index"] = f.readUInt16()
	diff["sprite_id"] = f.readUInt16()
	diff["world_coords"] = [f.readUInt32() for i in range(3)]
	diff["universe_coords"] = [f.readUInt32() for i in range(3)]
	diff["unknown_34"] = f.readUInt32()
	diff["unknown_38"] = f.readUInt32()
	diff["curr_screen"] = f.readUInt8()
	diff["cursor_id"] = f.readUInt8()
	diff["cursor_flag"] = f.readUInt8()
	diff["unkonwn_3f"] = f.readUInt8()
	diff["voice"] = {}
	diff["voice"]["id"] = f.readUInt32()
	diff["voice"]["group"] = f.readUInt32()
	diff["voice"]["subgroup"] = f.readUInt16()
	diff["width"] = f.readUInt16()
	diff["height"] = f.readUInt16()
	diff["name"] = f.readStringBuffer(20)
	diff["talk"] = f.readStringBuffer(100)
	diff["unknown_c6"] = f.readUInt8()
	diff["unknown_c7"] = f.readUInt8()
	diff["region_id"] = f.readUInt32()
	diff["unknown_c8"] = f.readUInt8()
	diff["walk_type"] = f.readUInt8()
	diff["unknown_ce"] = f.readUInt16()
	diff["transition_object_id"] = f.readUInt32()
	diff["skills"] = f.readUInt16()
	diff["timer"] = f.readUInt16()
	diff["unknown_d8"] = f.readUInt16()
	diff["unknown_da"] = f.readUInt16()
	diff["unknown_dc"] = f.readUInt16()
	diff["unknown_de"] = f.readUInt16()
	diff["time_next_update"] = f.readUInt32()
	return diff
	

def _readChunksDiff(f):
	diffs = []
	while True:
		diff = _readDiff(f)
		if diff is None: break
		diffs.append(diff)
	return diffs


def _readChunksWorld(f):
	world = {}
	world["unknown_0"] = f.readUInt8()
	world["phaser_level"] = f.readUInt32()
	world["team_lead_id"] = f.readUInt32()
	world["exit_id"] = f.readUInt32()
	world["screen_id"] = f.readUInt32()
	world["world_id"] = f.readUInt32()
	world["entrance_id"] = f.readUInt32()
	world["unknown_2c"] = f.readUInt32()
	world["mission_screen_id"] = f.readUInt32()
	world["mission_world_id"] = f.readUInt32()
	world["mission_entrance_id"] = f.readUInt32()

	if world["world_id"] == 0xffffff00: world["world_id"] = None
	if world["mission_world_id"] == 0xffffff00: world["mission_world_id"] = None

	return world


def _readChunksWalkQueues(f):
	queue = []
	n = f.readUInt32()
	for i in range(n):
		entry = {}
		entry["object_id"] = f.readUInt32()
		entry["event_type"] = f.readUInt32()
		entry["ptr_object"] = f.readUInt32()
		entry["other"] = f.readUInt32()
		entry["who"] = f.readUInt32()
		entry["x"] = f.readUInt32()
		entry["y"] = f.readUInt32()
		queue.append(entry)
	
	return queue


def _readChunksObjDiffs(f):
	obj_diffs = []
	while True:
		diff = _readDiffObj(f)
		if diff["target"] == 0xffffffff: break
		obj_diffs.append(diff)
	return obj_diffs


def _readChunksObjectLists(f):
	list_keys = [
		"crew_ship",
		None,
		None,
		"inventory_away",
		"inventory_ship",
		"unknown_88",
		"unknown_8c",
		"unknown_90",
		"unknown_94",
		"unknown_98",
		"unknown_9c",
		"unknown_a0",
		"unknown_a8",
		"unknown_ac",
		"unknown_b0",
		"crew_away_original"
	]
	object_lists = { key:[] for key in list_keys}
	while True:
		list_id = f.readUInt32()
		object_id = f.readUInt32()
		if list_id == 0x11: break
		assert(object_id != 0xffffffff)
		object_lists[ list_keys[list_id] ].append(object_id)
	return object_lists
		

def _readChunksWorld2(f):
	world = {}
	world["unknown_60"] = f.readUInt8()
	world["unknown_64"] = f.readUInt32()
	world["unknown_68"] = [f.readUInt32() for i in range(3)]
	world["unknown_b8"] = f.readUInt8()
	world["unknown_bc_object_id"] = f.readUInt32()
	world["unknown_c4"] = f.readUInt32()
	world["unknown_c0"] = f.readUInt32()
	world["unknown_c8"] = [f.readUInt32() for i in range(2)]
	world["difficulty"] = f.readUInt32()
	return world


def _readChunksTriggers(f):
	total_size = f.readUInt32()
	triggers_enabled = []
	for i in range(total_size):
		trigger = {}
		trigger["id"] = f.readUInt32()
		trigger["enabled"] = (False, True)[f.readUInt32()]
		triggers_enabled.append(trigger)
	
	assert(f.readUInt32() == 0x06060606)
	assert(f.readUInt32() == 0x03030303)
	total_size = f.readUInt32()
	# TODO: None of my files had this in them, so it's untested.
	triggers = []
	if total_size != 0:
		end = f.pos() + total_size
		while f.pos() < end:
			trigger = {}
			trigger["id"] = f.readUInt32()
			trigger["header_size"] = f.readUInt8()
			trigger["unknown_6"] = [f.readUInt8() for i in range(3)]
			trigger_type = f.readUInt32()
			if trigger_type == 0:
				data_size = trigger["header_size"] + 0x18 - 12
			elif trigger_type == 1:
				data_size = trigger["header_size"] + 0x20 - 12
			elif trigger_type == 2:
				data_size = trigger["header_size"] + 0x28 - 12
			elif trigger_type == 3:
				data_size = trigger["header_size"] + 0x1c - 12
			trigger["data"] = [f.readUInt8() for i in range(data_size)]
			triggers.append(trigger)
	
	assert(f.readUInt32() == 0x06060606)
	return {
		"enabled": triggers_enabled,
		"triggers": triggers,
	}


def _readChunksCommands(f):
	# TODO: Also untested
	cmds = []
	while True:
		n = f.readUInt32()
		if n == 0xffffffff: break
		cmd = f.readStringBuffer(n)
		cmds.append(cmd)
	return cmds


def _readBlockChunks(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	assert(f.readUInt32() == 0x01010101)
	data["current_time"] = f.readUInt32()
	data["diffs"] = _readChunksDiff(f)
	assert(f.readUInt32() == 0x10101010)
	data["world"] = _readChunksWorld(f)
	assert(f.readUInt32() == 0x40404040)
	data["walk_queue_1"] = _readChunksWalkQueues(f)
	assert(f.readUInt32() == 0x04040404)
	data["walk_queue_2"] = _readChunksWalkQueues(f)
	assert(f.readUInt32() == 0x02020202)
	data["crew_away_diffs"] = _readChunksObjDiffs(f)
	data["crew_stunned_diffs"] = _readChunksObjDiffs(f)
	data["unknown_a4_diffs"] = _readChunksObjDiffs(f)
	assert(f.readUInt32() == 0x20202020)
	data["object_lists"] = _readChunksObjectLists(f)
	data["world2"] = _readChunksWorld2(f)
	assert(f.readUInt32() == 0x30303030)
	data["triggers"] = _readChunksTriggers(f)
	data["commands"] = _readChunksCommands(f)

	assert(f.pos() == block["end_offset"])
	return {"objects": data}


def _readBlockEnterprise(f, block):
	data = {}
	f.setPosition(block["data_offset"])

	assert(f.readUInt32() == 0x08080808)
	combat = {}
	combat["unknown_1"] = f.readUInt32()
	combat["screen"] = f.readUInt32()
	if combat["screen"] == 0xffffffff: combat["screen"] = None
	
	assert(f.readUInt32() == 0x0a0a0a0a)
	enterprise = {}
	enterprise["name"] = f.readStringBuffer(30)
	enterprise["n_systems"] = f.readUInt32()
	enterprise["type"] = f.readUInt32()
	# Power
	power = {"generators":[]}
	for i in range(2):
		generator = {}
		generator["unknown_g1"] = f.readUInt32()
		generator["power_free"] = f.readUInt32()
		generator["unknown_g2"] = f.readUInt32()
		generator["time_last_power_update"] = f.readUInt32()
		generator["time_normal_operation_update"] = f.readUInt32()
		generator["unknown_g3"] = f.readUInt32()
		generator["ptr_system"] = f.readUInt32()
		power["generators"].append(generator)
	power["total_power_free"] = f.readUInt32()
	power["unknown_1"] = f.readUInt32()
	power["time_repair_update"] = f.readUInt32()
	power["ptr_battery_system"] = f.readUInt32()
	power["unknown_2"] = [f.readUInt32() for i in range(6)]
	power["total_power_requested"] = f.readUInt32()
	power["total_power_applied"] = f.readUInt32()
	enterprise["power"] = power
	
	enterprise["h"] = [f.readUInt32() for i in range(14)]

	enterprise["systems"] = []
	for i in range(enterprise["n_systems"]):
		system = {}
		system["charge_current"] = f.readUInt32()
		system["charge_target"] = f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		system["rate_usage"] = f.readUInt32() # not sure this is the right label
		system["health_damage"] = f.readUInt32()
		system["unknown_64"] = f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		f.readUInt32()
		system["charge_requested_min"] = f.readUInt32() # not sure this is the right label
		system["charge_requested"] = f.readUInt32()
		system["unknown_94"] = f.readUInt32()
		system["readout_power_target"] = f.readUInt32()
		system["readout_power_current"] = f.readUInt32()
		system["readout_repair_target"] = f.readUInt32()
		system["readout_repair_current"] = f.readUInt32()
		enterprise["systems"].append(system)
	assert(f.readUInt32() == 0xa0a0a0a0)

	assert(f.readUInt32() == 0x0b0b0b0b)
	tactical = {}
	tactical["weapons_lock"] = (False, True)[f.readUInt8()]
	tactical["torpedo_spread"] = f.readUInt32() / 46
	tactical["shields_raised"] = (False, True)[f.readUInt8()]
	tactical["deletgate_on"] = (False, True)[f.readUInt8()]
	f.readUInt8()
	tactical["unknown_74"] = f.readUInt8()
	tactical["alert_level"] = f.readUInt32()
	assert(f.readUInt32() == 0xb0b0b0b0)

	assert(f.readUInt32() == 0x80808080)

	assert(f.pos() == block["end_offset"])
	return { "ncc1701d": {
		"combat": combat,
		"enterprise": enterprise,
		"tactical": tactical,
	}}


def _readBlockGlobals(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	
	while True:
		x = f.readUInt32()
		if x == 0:
			data["dialogue_scrollable_pos"] = (f.readUInt16(), f.readUInt16())
		elif x == 1:
			data["dialogue_talking_pos"] = (f.readUInt16(), f.readUInt16())
		elif x == 2:
			data["unknown"] = [f.readUInt8() for i in range(0x20)]
		elif x == 3:
			data["astrogation_location_updated"] = (False, True)[f.readUInt8()]
		elif x == 4:
			data["warpout_video_state"] = f.readUint8()
		elif x == 5:
			data["phaser_setting"] = f.readUInt32()
		elif x == 0xffffffff:
			break

	assert(f.pos() == block["end_offset"])
	return {"globals": data}


def _readBlockHeader(f):
	block_offset = f.pos()
	block_type = f.readStringBuffer(4)
	assert(block_type in ["GNT", "ONT"])
	block_data_size = f.readUInt32() - 4
	block_data_offset = f.pos()
	block_end_offset = block_data_offset + block_data_size
	return {
		"type": block_type,
		"offset": block_offset,
		"data_offset": block_data_offset,
		"data_size": block_data_size,
		"end_offset": block_end_offset,
	}


def readBlockHeaders(f):
	blocks = []
	while not f.eof():
		blocks.append(_readBlockHeader(f))
		f.setPosition(blocks[-1]["end_offset"])
	
	assert(len(blocks) == 9)
	names = ["compstat", "aststat", "videos", "screen_regions", "converations", "travel_history", "objects", "enterprise", "globals"]
	for i,name in enumerate(names):
		blocks[i]["name"] = name

	return blocks


def savegame(input_path):
	f = File(input_path)
	data = {}

	# Header
	assert(f.readString() == "STTNG_GAME")

	blocks = readBlockHeaders(f)
	assert(len(blocks) == 9)

	data |= _readBlockCompstat(f, blocks[0])
	data |= _readBlockAststat(f, blocks[1])
	data |= _readBlockVideos(f, blocks[2])
	data |= _readBlockScreenRegions(f, blocks[3])
	data |= _readBlockConverations(f, blocks[4])
	data |= _readBlockTravelHistory(f, blocks[5])
	data |= _readBlockChunks(f, blocks[6])
	data |= _readBlockEnterprise(f, blocks[7])
	data |= _readBlockGlobals(f, blocks[8])

	return data
