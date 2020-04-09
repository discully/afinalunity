import AFU.File as File
from enum import IntEnum

db = False

########################################################################################################################
# Blocks Core
########################################################################################################################


class Block:
	def __init__(self, type_id):
		self.type = BlockType(type_id)
		self.name = self.type.name
		self.id = int(self.type)
		self.length = 0xffff


class BlockType (IntEnum):
	OBJECT = 0x0
	DESCRIPTION = 0x1
	USE_ENTRIES = 0x2
	GET_ENTRIES = 0x3
	LOOK_ENTRIES = 0x4
	TIMER_ENTRIES = 0x5
	CONDITION = 0x6
	ALTER = 0x7
	REACTION = 0x8
	COMMAND = 0x9
	SCREEN = 0x10
	PATH = 0x11
	# 0x12 unused?
	GENERAL = 0x13
	CONVERSATION_RESPONSE = 0x14
	BEAMDOWN = 0x15
	TRIGGER = 0x16
	COMMUNICATE = 0x17
	CHOICE = 0x18
	# 0x19, 0x20, 0x21, 0x22 unused?
	# (planet, computer, game, encounter?)
	LIST_END_ENTRY = 0x23
	LIST_BEGIN_ENTRY = 0x24
	BLOCK_END = 0x25
	CHOICE1 = 0x26
	CHOICE2 = 0x27
	CONVERSATION_HEADER = 0x28
	CONVERSATION_WHOCANSAY = 0x29
	CONV_CHANGEACT_DISABLE = 0x30
	CONV_CHANGEACT_SET = 0x31
	CONV_CHANGEACT_ENABLE = 0x32
	CONV_CHANGEACT_UNKNOWN2 = 0x33
	CONVERSATION_TEXT = 0x34
	CONVERSATION_RESULT = 0x35
	PHASER_STUN = 0x36
	PHASER_GTP = 0x37
	PHASER_KILL = 0x38
	PHASER_HEADER = 0x39
	VOICE = 0x40


def _readBlockHeader(f):
	block_offset = f.pos()
	block_type = BlockType(f.readUInt8())
	assert (f.readUInt8() == 0x11)
	
	return {
		"offset": block_offset,
		"type": {
			"id": block_type,
			"name": block_type.name,
		}
	}


def _readBlock(f):
	blocks = []
	
	more = True
	return_list = False
	while more:
		block = _readBlockHeader(f)
		
		if db: print("{:>6x} {}".format(f.pos(), block["type"]["name"]))
		
		handlers = {
			BlockType.OBJECT: _readObject,
			BlockType.CONVERSATION_HEADER: _readConversationHeader,
			BlockType.DESCRIPTION: _readDescription,
			BlockType.VOICE: _readSpeechInfo,
			BlockType.CONVERSATION_WHOCANSAY: _readConversationWhocansay,
			BlockType.CONVERSATION_TEXT: _readConversationText,
			BlockType.USE_ENTRIES: _readList,
			BlockType.GET_ENTRIES: _readList,
			BlockType.LOOK_ENTRIES: _readList,
			BlockType.TIMER_ENTRIES: _readList,
			BlockType.LIST_BEGIN_ENTRY: _readListEntryBegin,
			BlockType.LIST_END_ENTRY: _readEmptyBlock,
			BlockType.CONVERSATION_RESULT: _readList,
			BlockType.BLOCK_END: _readEmptyBlock,
			BlockType.CHOICE1: _readEmptyBlock,
			BlockType.CHOICE2: _readEmptyBlock,
			BlockType.CONDITION: _readCondition,
			BlockType.COMMAND: _readCommand,
		}
		
		if block["type"]["id"] in handlers:
			more = handlers[block["type"]["id"]](f, block)
		else:
			if db: print("Cannot read block type:", block["type"])
			block["length"] = f.readUInt16()
			f.setPosition(f.pos() + block["length"])
			more = False
		
		if more:
			return_list = True
		blocks.append(block)
	
	if return_list:
		if blocks[-1]["type"]["id"] == BlockType.BLOCK_END:
			blocks.pop()
		return {
			"type": blocks[0]["type"],
			"blocks": blocks,
		}
	
	return blocks[0]


def _readEmptyBlock(f, block):
	return False
	

########################################################################################################################
# Standard Blocks
########################################################################################################################


def _readList(f, block):
	block["n_entries"] = f.readUInt8()
	block["entries"] = []
	for i in range(block["n_entries"]):
		_readListEntry(f, block)
	return False


def _readListEntry(f, entries_block):
	entry_block = {
		"list": [],
	}
	
	begin_block = _readBlock(f)
	assert (begin_block["type"]["id"] == BlockType.LIST_BEGIN_ENTRY)
	#entry_block["begin"] = begin_block
	
	while True:
		block = _readBlock(f)
		if block["type"]["id"] == BlockType.LIST_END_ENTRY:
			#entry_block["end"] = block
			break
		else:
			entry_block["list"].append(block)
	
	entries_block["entries"].append(entry_block)


def _readListEntryBegin(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0xae)
	
	assert(f.readUInt16() == 9)
	[f.readUInt32() for i in range(43)] # 172 bytes of unknown data. Offsets?
	return False


########################################################################################################################
# Utilities
########################################################################################################################


def _readObjectId(f):
	obj_id = f.readUInt8()
	obj_screen = f.readUInt8()
	obj_world = f.readUInt8()
	obj_unused = f.readUInt8()
	assert( obj_unused in (0, 0xff) )
	return {
		"id": obj_id,
		"screen": obj_screen,
		"world": obj_world,
		"unused": obj_unused,
	}


def _readEntryHeader(f, block, expected_header_type):
	header = {}
	
	internal = {}
	internal["id"] = f.readUInt8()
	internal["screen"] = f.readUInt8()
	internal["world"] = f.readUInt8()
	header["internal_object"] = internal

	header["counter1"] = f.readUInt8()
	header["counter2"] = f.readUInt8()
	header["counter3"] = f.readUInt8()
	header["counter4"] = f.readUInt8()

	header["type"] = f.readUInt8()
	assert(header["type"] == expected_header_type)

	header["stop_here"] = f.readUInt8()
	assert(header["stop_here"] in (0, 1, 0xff))

	# the state/response of this conversation block?, or 0xffff in an object
	header["response_counter"] = f.readUInt16()
	header["state_counter"] = f.readUInt16()
	
	block["header"] = header


def _getVoiceFile(speaker, voice):
	return "{1[group]:02x}{0:02x}{1[subgroup]:02x}{1[id]:02x}.vac".format(speaker, voice)


########################################################################################################################
# Conversation Blocks
########################################################################################################################


class ConversationResponseState (IntEnum):
	ENABLED = 0x2,
	DISABLED = 0x3,
	UNKNOWN_1 = 0x4


def _readConversationHeader(f, block):
	block["id"] = f.readUInt16()
	block["state"] = f.readUInt16()
	block["text"] = f.readStringBuffer(255)
	
	block["response_state"] = ConversationResponseState(f.readUInt8())
	
	f.readUInt16()  # unknown1
	f.readUInt16()  # unknown2
	f.readUInt16()  # unknown1
	
	block["next_situation"] = f.readUInt16()
	
	for i in range(5):
		f.readUInt16()  # unknown01
		f.readUInt16()  # unknown02
	
	block["target"] = _readObjectId(f)
	
	f.readUInt16()  # unknown3
	f.readUInt16()  # unknown4
	f.readUInt16()  # unknown5
	f.readUInt16()  # unknown6
	f.readUInt16()  # unknown7
	
	voice_id = f.readUInt32()
	voice_group = f.readUInt32()
	voice_subgroup = f.readUInt16()
	block["voice"] = {
		"id": voice_id,
		"group": voice_group,
		"subgroup": voice_subgroup,
	}
	
	conv_actions = (BlockType.CONV_CHANGEACT_DISABLE, BlockType.CONV_CHANGEACT_ENABLE, BlockType, BlockType.CONV_CHANGEACT_SET, BlockType.CONV_CHANGEACT_UNKNOWN2)
	
	block["whocansay"] = []
	block["text"] = []
	block["actions"] = []
	
	while True:
		sub_block = _readBlock(f)
		
		if sub_block["type"]["id"] == BlockType.BLOCK_END:
			break
		
		if sub_block["type"]["id"] == BlockType.CONVERSATION_WHOCANSAY:
			for whocansay in sub_block["blocks"]:
				block["whocansay"].append(whocansay["who"])
		elif sub_block["type"]["id"] == BlockType.CONVERSATION_TEXT:
			block["text"] += sub_block["blocks"]
		elif sub_block["type"]["id"] in conv_actions:
			block["actions"].append(sub_block)
		else:
			raise ValueError("Unexpected block type: {}".format(sub_block["type"]))
	return False
		


def _readConversationWhocansay(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 8)
	
	block["who"] = _readObjectId(f)
	f.readUInt8() # unknown1
	f.readUInt8() # unknown2
	f.readUInt8() # unknown3
	f.readUInt8() # unknown4
	return True


def _readConversationText(f, block):
	block["length"] = f.readUInt16()
	assert (block["length"] == 0x10d)
	
	block["text1"] = f.readStringBuffer(255)
	block["text2"] = f.readStringBuffer(4)
	
	voice_id = f.readUInt32()
	voice_group = f.readUInt32()
	voice_subgroup = f.readUInt16()
	block["voice"] = {
		"id": voice_id,
		"group": voice_group,
		"subgroup": voice_subgroup,
	}
	return True


########################################################################################################################
# Object Blocks
########################################################################################################################


class ObjectWalkType (IntEnum):
	NORMAL = 0x0
	SCALED = 0x1 # scaled with walkable polygons (e.g.characters)
	TRANSITION_SQUARE = 0x2
	ACTION_SQUARE = 0x3


def _readObject(f, block):
	block["length"] = f.readUInt16()
	assert (block["length"] == 0x128)
	
	block["id"] = _readObjectId(f)
	block["curr_screen"] = f.readUInt8()
	
	f.readUInt8()  # unknown3
	
	block["width"] = f.readSInt16()
	block["height"] = f.readSInt16()
	block["x"] = f.readSInt16()
	block["y"] = f.readSInt16()
	block["z"] = f.readSInt16()
	block["universe_x"] = f.readSInt16()
	block["universe_y"] = f.readSInt16()
	block["universe_z"] = f.readSInt16()
	
	block["y_adjust"] = f.readSInt16()  # TODO: this doesn't work properly (see DrawOrderComparison)
	block["anim_index"] = f.readUInt16()
	block["sprite_id"] = f.readUInt16()
	block["region_id"] = f.readUInt32()
	block["flags"] = f.readUInt8()
	block["state"] = f.readUInt8()
	n_uses = f.readUInt8()
	n_gets = f.readUInt8()
	n_looks = f.readUInt8()
	
	assert (f.readUInt8() == 0)  # unknown11
	
	block["walk_type"] = ObjectWalkType(f.readUInt8()).name
	n_descriptions = f.readUInt8()
	block["name"] = f.readStringBuffer(20)
	
	for i, thing in enumerate(["DESCRIPTION", "USE", "LOOK", "WALK", "TIME"]):  # todo pointers to the relevant blocks?
		f.readUInt16()  # unknowna
		f.readUInt8()  # unknownb
		f.readUInt8()  # unknownc
		if i == 0:
			block["transition"] = _readObjectId(f)
	
	block["skills"] = f.readUInt16()
	block["timer"] = f.readUInt16()
	block["talk"] = f.readStringBuffer(100)
	
	assert (f.readUInt16() == 0)  # unknown19
	assert (f.readUInt16() == 0)  # unknown20
	assert (f.readUInt16() == 0)  # zero16
	f.readUInt16()  # unknown21, unused?
	
	voice_id = f.readUInt32()
	voice_group = f.readUInt32()
	voice_subgroup = f.readUInt16()
	block["voice"] = {
		"id": voice_id,
		"group": voice_group,
		"subgroup": voice_subgroup,
	}
	
	cursor_id = f.readUInt8()
	cursor_flag = f.readUInt8()
	block["cursor"] = {
		"id": cursor_id,
		"flag": cursor_flag,
	}
	
	f.readUInt8()  # unknown26
	f.readUInt8()  # unknown27
	
	assert (f.readUInt16() == 0x0)  # zero16
	
	for i in range(21):
		assert (f.readUInt32() == 0)  # padding
	
	block["descriptions"] = []
	if n_descriptions > 0:
		description_blocks = _readBlock(f)
		assert(description_blocks["type"]["id"] == BlockType.DESCRIPTION)
		for description_block in description_blocks["blocks"]:
			block["descriptions"].append({
				"speaker": description_block["speaker"],
				"text": description_block["text"],
				"voice": _getVoiceFile(description_block["speaker"], description_block["voice"]),
			})
	assert(len(block["descriptions"]) == n_descriptions)
	
	block["uses"] = []
	block["gets"] = []
	block["looks"] = []
	block["timers"] = []
	while not f.eof():
		list_block = _readBlock(f)
		if list_block["type"]["id"] == BlockType.BLOCK_END:
			break
		elif list_block["type"]["id"] == BlockType.USE_ENTRIES:
			block["uses"] += list_block["entries"]
		elif list_block["type"]["id"] == BlockType.GET_ENTRIES:
			block["gets"] += list_block["entries"]
		elif list_block["type"]["id"] == BlockType.LOOK_ENTRIES:
			block["looks"] += list_block["entries"]
		elif list_block["type"]["id"] == BlockType.TIMER_ENTRIES:
			block["timers"] += list_block["entries"]
	
	assert(len(block["uses"]) == n_uses)
	assert(len(block["gets"]) == n_gets)
	assert(len(block["looks"]) == n_looks)
	assert(len(block["timers"]) <= 1) # timers can only have one result
	
	return False


def _readDescription(f, block):
	block["length"] = f.readUInt16()
	assert (block["length"] == 0xa5)
	
	block["speaker"] = f.readUInt8()
	
	for i in range(7):
		assert (f.readUInt16() == 0xffff)  # unknowna
	
	block["text"] = f.readStringBuffer(149)
	f.readUInt8()  # unknown2. is this just corrupt entries and there should be a null byte here?
	
	voice = _readBlock(f)
	assert(voice["type"]["id"] == BlockType.VOICE)
	block["voice"] = voice["voice"]
	
	return True


def _readSpeechInfo(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0x0c)
	
	voice_id = f.readUInt32()
	voice_group = f.readUInt32()
	voice_subgroup = f.readUInt32()
	block["voice"] = {
		"id": voice_id,
		"group": voice_group,
		"subgroup": voice_subgroup,
	}
	
	return False


def _readCondition(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0xda)
	assert(f.readUInt16() == 9)
	
	_readEntryHeader(f, block, 0xff)
	
	block["target"] = _readObjectId(f);
	block["whocan"] = _readObjectId(f)
	
	entries = []
	for i in range(4):
		entry = {}
		entry["condition"] = _readObjectId(f)
		entry["check_x"] = f.readUInt16()
		entry["check_y"] = f.readUInt16()
		entry["check_z"] = f.readUInt16() # unused?
		entry["check_univ_x"] = f.readUInt16()
		entry["check_univ_y"] = f.readUInt16()
		entry["check_univ_z"] = f.readUInt16()
		entry["check_screen"] = f.readUInt8()
		entry["check_status"] = f.readUInt8()
		entry["check_state"] = f.readUInt8()
		entries.append(entry)
	#block["list"] = entries
	
	assert(f.readUInt16() == 0xffff) # unknown1
	assert(f.readUInt16() == 0xffff) # unknown2
	assert(f.readUInt16() == 0xffff) # unknown3
	
	block["how_close_x"] = f.readUInt16()
	block["how_close_y"] = f.readUInt16()

	assert(f.readUInt16() == 0xffff) # unknown4

	block["how_close_dist"] = f.readUInt16()
	block["skill_check"] = f.readUInt16()

	block["counter_value"] = f.readUInt16()
	block["counter_when"] = f.readUInt8()

	for i in range(25):
		assert(f.readUInt32() == 0)
	
	return False


def _readCommand(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0x84)
	assert(f.readUInt16() == 9)
	
	_readEntryHeader(f, block, 0x45)
	
	block["targets"] = [_readObjectId(f) for i in range(3)]
	
	# both usually 0xffff
	block["target_x"] = f.readUInt16()
	block["target_y"] = f.readUInt16()
	block["command_id"] = f.readUInt32() # command_id >= 2 && command_id <= 6
	
	for i in range(97):
		assert(f.readUInt8() == 0)
	
	return True


########################################################################################################################
# Phaser Blocks
########################################################################################################################



########################################################################################################################
# Public Functions
########################################################################################################################


def bst(file_path):
	f = File.File(file_path)
	
	blocks = []
	while not f.eof():
		blocks.append(_readBlock(f))
	
	return blocks
