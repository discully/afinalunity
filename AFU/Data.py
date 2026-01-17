from AFU.File import File
from AFU.Block import _readObjectId, identifyObject
from AFU.Utils import SystemEnt
from enum import Enum


class TriggerType (Enum):
	NORMAL = 0x0
	TIMER = 0x1
	PROXIMITY = 0x2
	UNUSED = 0x3


def triggers(file_path):
	f = File(file_path)
	data = []
	while not f.eof():
		trigger = {}
		
		trigger["id"] = f.readUInt32()
		assert(f.readUInt8() == 0xff) # data size
		assert(f.readUInt8() == 0xff) # to_save
		trigger["on_mission"] = (False, True)[f.readUInt8()]
		assert (f.readUInt8() == 0xff) # unused
		trigger["type"] = TriggerType(f.readUInt32())
		trigger["target_id"] = _readObjectId(f)
		obj_name = identifyObject(file_path.parent, trigger["target_id"])
		if obj_name:
			trigger["target_name"] = obj_name
		trigger["is_enabled"] = (False, True)[f.readUInt8()]
		trigger["unknown_11"] = f.readUInt8() # A counter of some kind? Either 0cff or 0x5
		
		if trigger["type"] == TriggerType.NORMAL:
			assert (f.readUInt16() == 0xffff)
			trigger["timer_start"] = f.readUInt32()
		if trigger["type"] == TriggerType.TIMER:
			assert (f.readUInt16() == 0xffff) # unused
			trigger["duration"] = f.readUInt32()
			trigger["time_started"] = f.readUInt32()
			trigger["time_to_fire"] = f.readUInt32()
		elif trigger["type"] == TriggerType.PROXIMITY:
			trigger["global_coords"] = [f.readUInt16() for i in range(3)]
			trigger["radius"] = f.readUInt16()
			assert(f.readUInt16() == 0xffff) # unused
			trigger["from_id"] = _readObjectId(f)
			obj_name = identifyObject(file_path.parent, trigger["from_id"])
			if obj_name:
				trigger["from_name"] = obj_name
			trigger["to_id"] = _readObjectId(f)
			obj_name = identifyObject(file_path.parent, trigger["to_id"])
			if obj_name:
				trigger["to_name"] = obj_name
			trigger["use_radius"] = (False, True)[f.readUInt8()]
			trigger["unknown_25"] = (False, True)[f.readUInt8()]
			assert(f.readUInt16() == 0xffff)
		elif trigger["type"] == TriggerType.UNUSED:	
			assert (f.readUInt16() == 0xffff) # unused
			trigger["time_next_update"] = f.readUInt32()
			assert(f.readUInt32() == 0)
		
		data.append(trigger)
	return data



def alert(file_path):
	f = File(file_path)
	data = []
	for s in range(35):
		sys = SystemEnt(s)
		data.append({
			"system": sys,
			"value": f.readUInt32(),
		})
	assert(f.eof())
	return data



def txt(file_path):
	f = File(file_path)
	lines = []
	while not f.eof():
		lines.append(f.readLine())
	return lines



def credits(file_path):
	f = File(file_path)
	pages = [[], ]
	while not f.eof() and f.peek() != 0x1a:
		line = f.readLine()
		if line == "NEWPAGE":
			pages.append([])
		else:
			line = line.replace("NL1.5", "")
			line = line.replace("NL", "")
			line = line.replace(">", "\t")
			line = line.replace("@", chr(0xf6))
			pages[-1].append(line)
	return pages
		
		
	