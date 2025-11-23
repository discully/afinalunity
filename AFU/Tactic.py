from AFU.File import File, fpos
from enum import Enum, IntEnum


class TacticType (Enum):
	TEST = 0x0              # Wait until the test is passed
	ACTION = 0x1            # Action a change
	BRANCH = 0x2            # Go to a different page/entry, then return here. Page == -2 means idle.
	PAGE = 0x3              # Page of entries


class TacticSubtype (Enum):
	BUTTON = 0x1
	PUSH = 0x2
	POP = 0x3
	GOTO = 0x4
	GOTO_ONCE = 0x5
	SWITCH_ONE = 0x6      # implemented, but unused in .bin files
	PRINT = 0x7
	FIRE = 0x8
	FOLLOW = 0x9		  # unimplemented and unused in .bin files
	FLUSH = 0xa
	ORIENT_HEADING = 0xb
	ORIENT_CLIMB = 0xc
	ORIENT_BANK = 0xd
	SPEED = 0xe
	POS = 0xf             # implemented, but unused in .bin files
	PHASER = 0x10         # unimplemented and unused in .bin files
	PHOTON = 0x11         # unimplemented and unused in .bin files
	SYSTEM = 0x12
	STORY = 0x13          # implemented, but unused in .bin files
	THIS = 0x14           # unimplemented and unused in .bin files
	ALL = 0x15
	RAND = 0x16
	PROXIMITY = 0x17
	FOE = 0x18            # unimplemented and unused in .bin files
	FRIEND = 0x19         # unimplemented and unused in .bin files
	TARGET = 0x1a         # used as 'subject'
	BEARING = 0x1b        # implemented, but unused in .bin files
	FIRED = 0x1c          # test, if fired upon
	DELTA = 0x1d          # test, time delta
	SWITCH_SKILL = 0x1e   # implemented, but unused in .bin files
	PAGE = 0x1f
	DEBUG = 0x20
	GOSUB = 0x21
	GOSUB_ONCE = 0x22
	WAY = 0x23            # waypoint
	WAY_CLEAR = 0x24      # clear waypoint
	MESSAGE = 0x25
	ACQUIRE = 0x26        # implemented, but unused in .bin files
	CLOAK = 0x27
	MENU = 0x28
	ENGAGE = 0x29
	RETURN = 0x2a         # return to idle
	SET_IDLE = 0x2b
	WARP = 0x2c
	OPPOSE = 0x2d


_COMPARISON_OPS = {1:'>', 2:'>=', 3:'==', 4:'<', 5:'<=', 6:"!="}
_VALUE_OPS = {1:"+", 2:"-", 3:"/", 4:"*", 10:"=", 11:"+=", 12:"-=", 13:"*=", 14:"/=", 15:">>=", 16: "<<="}
_MEASURES = {1:'x', 2:'y', 3:'z', 4:"any", 5:"all", 6:"dist"}
_PROPS = {0:"damage", 1:"power"}


def bin(file_path):
	f = File(file_path)
	assert(f.readStringBuffer(7) == "TACTICS")

	tactics = []
	page = None

	while not f.eof():
		entry = _readEntryHeader(f)
		
		if entry["subtype"] == TacticSubtype.BUTTON:
			_readButton(f, entry)
		elif entry["subtype"] in (TacticSubtype.GOTO, TacticSubtype.GOTO_ONCE):
			_readBranch(f, entry)
		elif entry["subtype"] in (TacticSubtype.SWITCH_ONE, TacticSubtype.SWITCH_SKILL, TacticSubtype.RAND):
			_readSwitch(f, entry)
		elif entry["subtype"] == TacticSubtype.PRINT:
			_readLog(f, entry)
		elif entry["subtype"] == TacticSubtype.FIRE:
			_readFire(f, entry)
		elif entry["subtype"] == TacticSubtype.FLUSH:
			_readFlush(f, entry)
		elif entry["subtype"] in (TacticSubtype.ORIENT_HEADING, TacticSubtype.ORIENT_CLIMB, TacticSubtype.ORIENT_BANK):
			_readOrientation(f, entry)
		elif entry["subtype"] == TacticSubtype.SPEED:
			_readSpeed(f, entry)
		elif entry["subtype"] == TacticSubtype.POS:
			_readPosition(f, entry)
		elif entry["subtype"] == TacticSubtype.SYSTEM:
			_readSystem(f, entry)
		elif entry["subtype"] == TacticSubtype.STORY:
			_readStory(f, entry)
		elif entry["subtype"] == TacticSubtype.PROXIMITY:
			_readProximity(f, entry)
		elif entry["subtype"] == TacticSubtype.BEARING:
			_readBearing(f, entry)
		elif entry["subtype"] == TacticSubtype.DELTA:
			_readTimeDelta(f, entry)
		elif entry["subtype"] == TacticSubtype.PAGE:
			_readPage(f, entry)
		elif entry["subtype"] == TacticSubtype.DEBUG:
			_readDebug(f, entry)
		elif entry["subtype"] in (TacticSubtype.GOSUB, TacticSubtype.GOSUB_ONCE):
			_readSubroutine(f, entry)
		elif entry["subtype"] == TacticSubtype.WAY:
			_readWayPoint(f, entry)
		elif entry["subtype"] == TacticSubtype.MESSAGE:
			_readMessage(f, entry)
		elif entry["subtype"] == TacticSubtype.ACQUIRE:
			_readAcquire(f, entry)
		elif entry["subtype"] == TacticSubtype.CLOAK:
			_readCloak(f, entry)
		elif entry["subtype"] == TacticSubtype.MENU:
			_readMenu(f, entry)
		elif entry["subtype"] == TacticSubtype.ENGAGE:
			_readEngage(f, entry)
		elif entry["subtype"] == TacticSubtype.SET_IDLE:
			_readSetIdle(f, entry)
		elif entry["subtype"] == TacticSubtype.WARP:
			_readWarpAway(f, entry)
		elif entry["subtype"] == TacticSubtype.OPPOSE:
			_readOppose(f, entry)
		elif entry["subtype"] in (
			TacticSubtype.PUSH,
			TacticSubtype.POP,
			TacticSubtype.RETURN,
			TacticSubtype.WAY_CLEAR,
			TacticSubtype.FIRED ):
			assert(entry["_length"] == 0)
		else:
			raise ValueError(f"Unknown or unsupported entry type: {entry["type"]},{entry["subtype"]}")
		
		if entry["type"] == TacticType.PAGE:
			page = entry
			tactics.append(entry)
		else:
			page["entries"].append(entry)
		
		assert(f.pos() == entry["_offset"] + 0xc + entry["_length"])

	# Replace offsets with page ids and entry indices
	targets = {}
	for page in tactics:
		for i,entry in enumerate(page["entries"]):
			targets[ entry["_offset"] ] = (page["id"],i)
	for page in tactics:
		for entry in page["entries"]:
			if "_entry_offset" in entry:
				if entry["subtype"] == TacticSubtype.GOTO and entry["page"] == -2:
					assert(entry["_entry_offset"] == 0)
					entry["page"] = "idle"
					entry["entry"] = 0
				else:
					target = targets[entry["_entry_offset"]]
					assert(entry["page"] == target[0])
					entry["entry"] = target[1]
			
			if entry["subtype"] in (TacticSubtype.RAND, TacticSubtype.SWITCH_ONE, TacticSubtype.SWITCH_SKILL):
				for t in entry["targets"]:
					target = targets[ t["_entry_offset"] ]
					assert(t["page"] == target[0])
					t["entry"] = target[1]

	return tactics


def _readEntryHeader(f):
	p = f.pos()
	entry_type = TacticType(f.readUInt32())
	entry_subtype = TacticSubtype(f.readUInt32())
	entry_length = f.readUInt32()
	return {
		"type": entry_type,
		"subtype": entry_subtype,
		"_length": entry_length,
		"_offset": p,
	}


def _readButton(f, entry):
	assert(entry["subtype"] == TacticSubtype.BUTTON)
	assert(entry["_length"] == 0x60)
	entry["id"] = f.readUInt32()       # indicates which tactical menu
	entry["page"] = f.readUInt32()
	entry["_entry_offset"] = f.readUInt32()
	text_len = f.readUInt32()
	entry["text"] = f.readStringBuffer(text_len + 1)
	data_len = 0x60 - 16 - (text_len + 1)
	# TODO: understand this data
	entry["data"] = [f.readUInt8() for i in range(data_len)]


def _readBranch(f, entry):
	assert(entry["subtype"] in (TacticSubtype.GOTO,TacticSubtype.GOTO_ONCE))
	assert(entry["_length"] == 0xc)
	assert( TacticSubtype(f.readUInt32()) == entry["subtype"] )
	entry["_entry_offset"] = f.readUInt32()
	entry["page"] = f.readSInt32() # if -2, go to idle page


def _readSwitch(f, entry):
	assert(entry["subtype"] in (TacticSubtype.SWITCH_ONE,TacticSubtype.SWITCH_SKILL,TacticSubtype.RAND))
	assert(entry["_length"] == 0x60)
	assert(TacticSubtype(f.readUInt32()) == entry["subtype"])
	entry["index"] = f.readUInt32() # unused?
	entry["_return"] = f.readUInt32() # unused unless 0x21?
	entry["return_here"] = entry["_return"] == 0x21 # If true, return here after execution
	n = f.readUInt32()
	offsets = [ f.readUInt32() for i in range(10) ]
	pages =   [ f.readUInt32() for i in range(10) ]
	entry["targets"] = []
	for i in range(n):
		entry["targets"].append( {"page": pages[i], "_entry_offset": offsets[i]} )
	# If SWITCH_ONE: n should be 1, and you go to that page/entry
	# If SWITCH_SKILL: n should be 3, and you go to the page/entry for the selected difficulty level
	# If RANDOM: n should be <= 10, and you generate a random value 0 <= x < n to select which page/entry to go to
	# Note, SWITCH_ONE and SWITCH_SKILL are unused in the .bin files, so their implementation here is untested


def _readLog(f, entry):
	assert(entry["subtype"] == TacticSubtype.PRINT)
	assert(entry["_length"] == 0x54)
	text_len = f.readUInt32()
	entry["text"] = f.readStringBuffer(text_len+1)
	data_len = 0x54 - 4 - (text_len+1)
	entry["data"] = [f.readUInt8() for i in range(data_len)] # junk, ignored


def _readFire(f, entry):
	assert(entry["subtype"] == TacticSubtype.FIRE)
	assert(entry["_length"] == 0x4)
	entry["weapon"] = TacticSubtype(f.readUInt32())
	assert(entry["weapon"] in (TacticSubtype.PHASER, TacticSubtype.PHOTON))


def _readFlush(f, entry):
	assert(entry["subtype"] == TacticSubtype.FLUSH)
	assert(entry["_length"] == 0x4)
	# Remove all entries of this type from the current event queue.
	# If remove_type == ALL (0x15) then just empty the entire queue of everything.
	# In practice, have only seen remove_type BUTTON and ALL.
	entry["remove"] = TacticSubtype(f.readUInt32())


def _readOrientation(f, entry):
	assert(entry["subtype"] in (TacticSubtype.ORIENT_HEADING,TacticSubtype.ORIENT_CLIMB,TacticSubtype.ORIENT_BANK))
	assert(entry["_length"] == 0x10)
	entry["operation"] = _VALUE_OPS[f.readUInt32()]
	assert(TacticSubtype(f.readUInt32()) == entry["subtype"])
	subj = f.readUInt32()
	entry["subject"] = None if subj == 0 else TacticSubtype(subj)
	entry["value"] = f.readSInt32()


def _readSpeed(f, entry):
	assert(entry["subtype"] == TacticSubtype.SPEED)
	assert(entry["_length"] == 12)
	entry["speed"] = f.readUInt32()
	subj = f.readUInt32()
	entry["subject"] = None if subj == 0 else TacticSubtype(subj)
	entry["operation"] = _VALUE_OPS[f.readUInt32()]


def _readPosition(f, entry):
	assert(entry["subtype"] == TacticSubtype.POS)
	raise ValueError("Tactic subtype POS is unused, so implementation is untested")
	assert(entry["_length"] == 0x10)
	entry["axis"] = _MEASURES[f.readUInt32()]
	subj = f.readUInt32()
	entry["subject"] = None if subj == 0 else TacticSubtype(subj)
	entry["value"] = f.readUInt32()
	entry["operation"] = _VALUE_OPS[f.readUInt32()]


def _readSystem(f, entry):
	assert(entry["subtype"] == TacticSubtype.SYSTEM)
	assert(entry["_length"] == 0x10)
	entry["system"] = f.readUInt32()
	sys_set = f.readUInt32()
	entry["set"] = _PROPS[sys_set]
	entry["value"] = f.readUInt32()
	entry["operation"] = _VALUE_OPS[f.readUInt32()]


def _readStory(f, entry):
	assert(entry["subtype"] == TacticSubtype.STORY)
	raise ValueError("Tactic subtype STORY is unused, so unimplemented")


def _readProximity(f, entry):
	assert(entry["subtype"] == TacticSubtype.PROXIMITY)
	assert(entry["_length"] == 0x8)
	entry["operation"] = _COMPARISON_OPS[f.readUInt32()]
	entry["distance"] = f.readFloat()


def _readBearing(f, entry):
	assert(entry["subtype"] == TacticSubtype.BEARING)
	raise ValueError("Tactic subtype BEARING is unused, so unimplemented")


def _readTimeDelta(f, entry):
	assert(entry["subtype"] == TacticSubtype.DELTA)
	assert(entry["_length"] == 0x8)
	entry["time_delta"] = f.readUInt32()
	assert(f.readUInt32() == 0) # Used to store target time (current_time + delta) at point of use, so always zero to start


def _readPage(f, entry):
	assert(entry["type"] == TacticType.PAGE)
	assert(entry["subtype"] == TacticSubtype.PAGE)
	assert(entry["_length"] == 0x58)
	entry["_offset_entry0"] = f.readUInt32()
	entry["id"] = f.readUInt32()
	entry["name"] = f.readString()
	data_len = 0x58 - 8 - (len(entry["name"]) + 1)
	entry["data"] = [f.readUInt8() for i in range(data_len)]
	entry["entries"] = []


def _readDebug(f, entry):
	assert(entry["subtype"] == TacticSubtype.DEBUG)
	assert(entry["_length"] == 0x4)
	entry["debug"] = f.readUInt32() != 0x0


def _readSubroutine(f, entry):
	assert(entry["subtype"] in (TacticSubtype.GOSUB,TacticSubtype.GOSUB_ONCE))
	assert(entry["_length"] == 0x10)
	subroutine_type = f.readUInt32() # Either the same as entry["subtype"], or occasionally GOTO_ONCE. But ignored.
	entry["_entry_offset"] = f.readUInt32()
	entry["page"] = f.readUInt32()
	entry["retval"] = f.readUInt32()


def _readWayPoint(f, entry):
	assert(entry["subtype"] == TacticSubtype.WAY)
	assert(entry["_length"] ==  0x10)
	entry["measure"] = _MEASURES[f.readUInt32()]
	subj = f.readUInt32()
	entry["subject"] = None if subj == 0 else TacticSubtype(subj)
	entry["value"] = f.readFloat()
	if "test" in entry:
		# Example:
		#     measure=6 ("dist"); op=4 ("<")
		#     return = ship_distance_from_waypoint < wapoint_value
		entry["operation"] = _COMPARISON_OPS[f.readUInt32()]
	else:
		entry["operation"] = _VALUE_OPS[f.readUInt32()]


def _readMessage(f, entry):
	assert(entry["subtype"] == TacticSubtype.MESSAGE)
	assert(entry["_length"] == 0x54)
	text_len = f.readUInt32()
	entry["text"] = f.readStringBuffer(text_len+1)
	data_len = 0x54 - 4 - (text_len+1)
	entry["data"] = [f.readUInt8() for i in range(data_len)]


def _readAcquire(f, entry):
	assert(entry["subtype"] == TacticSubtype.ACQUIRE)
	raise ValueError("Tactic subtype ACQUIRE is unused, so implementation is untested")
	assert(entry["_length"] == 0x4)
	entry["ship_type"] = f.readUInt32() # spaceobj type


def _readCloak(f, entry):
	assert(entry["subtype"] == TacticSubtype.CLOAK)
	assert(entry["_length"] == 0x4)
	# True = cloak, False = decloak
	entry["cloak"] = f.readUInt32() != 0


def _readMenu(f, entry):
	assert(entry["subtype"] == TacticSubtype.MENU)
	assert(entry["_length"] == 0x60)
	entry["id_add"] = f.readSInt32()
	entry["id_remove"] = f.readSInt32()
	entry["unknown"] = f.readUInt32() # TODO: What is this field in the menu tactic?
	text_len = f.readUInt32()
	entry["text"] = f.readStringBuffer(text_len+1)
	data_len = 0x60 - 16 - (text_len+1)
	entry["data"] = [f.readUInt8() for i in range(data_len)]


def _readEngage(f, entry):
	assert(entry["subtype"] == TacticSubtype.ENGAGE)
	assert(entry["_length"] == 0x4)
	action = f.readUInt32()
	entry["action"] = {0: "OFF", 1: "ON", 2: "LOCK", 3: "UNLOCK"}[action]


def _readSetIdle(f, entry):
	assert(entry["subtype"] == TacticSubtype.SET_IDLE)
	assert(entry["_length"] == 0x8)
	entry["page"] = f.readUInt32()
	entry["_entry_offset"] = f.readUInt32()


def _readWarpAway(f, entry):
	assert(entry["subtype"] == TacticSubtype.WARP)
	assert(entry["_length"] == 0x4)
	op = f.readUInt32()
	entry["mode"] = {0: "emergency0", 1: "emergency1", 2: "standard"}[op]


def _readOppose(f, entry):
	assert(entry["subtype"] == TacticSubtype.OPPOSE)
	assert(entry["_length"] == 0xa8)
	entry["data"] = [f.readUInt32() for i in range(42)]

