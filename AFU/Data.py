from AFU.File import File
from AFU.Block import _readObjectId
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
		trigger = {
			"id": f.readUInt32()
		}
		
		assert(f.readUInt16() == 0xffff)
		trigger["unknown_a"] = f.readUInt8()
		assert (f.readUInt8() == 0xff);
		trigger["type"] = TriggerType(f.readUInt32())
		trigger["target"] = _readObjectId(f)
		trigger["enabled"] = bool( f.readUInt8() )
		trigger["unknown_b"] = f.readUInt8()
		assert (f.readUInt16() == 0xffff);
		trigger["timer_start"] = f.readUInt32()
	
		if trigger["type"] == TriggerType.TIMER:
			assert( f.readUInt32() == 0)
			assert( f.readUInt32() == 0)
		elif trigger["type"] == TriggerType.PROXIMITY:
			trigger["distance"] = f.readUInt16()
			assert(f.readUInt16() == 0xffff)
			trigger["from"] = _readObjectId(f)
			trigger["to"] = _readObjectId(f)
			trigger["reversed"] = bool(f.readUInt8())
			trigger["instant"] = bool(f.readUInt8())
			assert(f.readUInt16() == 0xffff)
		elif trigger["type"] == TriggerType.UNUSED:
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
		print(sys)
	assert(f.eof())
	return data
