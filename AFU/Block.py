import AFU.File as File
from enum import IntEnum, Enum

db = False
db_data = False

########################################################################################################################
# Blocks Core
########################################################################################################################


class BlockType (Enum):
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
	CONVERSATION = 0x14
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
	CONV_RESPONSE = 0x28
	CONV_WHOCANSAY = 0x29
	CONV_CHANGEACT_DISABLE = 0x30
	CONV_CHANGEACT_SET = 0x31
	CONV_CHANGEACT_ENABLE = 0x32
	CONV_CHANGEACT_UNKNOWN2 = 0x33
	CONV_TEXT = 0x34
	CONV_RESULT = 0x35
	PHASER_STUN = 0x36
	PHASER_GTP = 0x37
	PHASER_KILL = 0x38
	PHASER_HEADER = 0x39
	VOICE = 0x40


# Expected Header Types
# ==
# TypeName		TypeVal		HeaderTypeVal
# Condition		0x06		0xff
# Alter			0x07		0x43
# Reaction		0x08		0x44
# Command		0x09		0x45
# Screen		0x10		0x46
# Path			0x11		0x47
#
# General		0x13		0x48
# Conversation	0x14		0x49
# Beamdown		0x15		0x4a
# Trigger		0x16		0x4b
# Communicate	0x17		0x4c
# Choice		0x18		0x4d


def _readBlockHeader(f):
	block_offset = f.pos()
	block_type = BlockType(f.readUInt8())
	assert(f.readUInt8() == 0x11)

	return {
		"_offset": block_offset,
		"type": block_type,
	}


def _readBlock(f):
	blocks = []

	more = True
	return_list = False
	while more:
		block = _readBlockHeader(f)

		if db: print("{:>6x} {}".format(f.pos(), block["type"]))

		handlers = {
			BlockType.OBJECT: _readObject,
			BlockType.DESCRIPTION: _readDescription,
			BlockType.USE_ENTRIES: _readList,
			BlockType.GET_ENTRIES: _readList,
			BlockType.LOOK_ENTRIES: _readList,
			BlockType.TIMER_ENTRIES: _readList,
			BlockType.CONDITION: _readCondition,
			BlockType.ALTER: _readAlter,
			BlockType.REACTION: _readReaction,
			BlockType.COMMAND: _readCommand,
			BlockType.SCREEN: _readScreen,
			BlockType.PATH: _readPath,
			BlockType.GENERAL: _readGeneral,
			BlockType.CONVERSATION: _readConversation,
			BlockType.BEAMDOWN: _readBeamdown,
			BlockType.TRIGGER: _readTrigger,
			BlockType.COMMUNICATE: _readCommunicate,
			BlockType.CHOICE: _readChoice,
			BlockType.LIST_END_ENTRY: _readEmptyBlock,
			BlockType.LIST_BEGIN_ENTRY: _readListEntryBegin,
			BlockType.BLOCK_END: _readEmptyBlock,
			BlockType.CHOICE1: _readEmptyBlock,
			BlockType.CHOICE2: _readEmptyBlock,
			BlockType.CONV_RESPONSE: _readConvResponse,
			BlockType.CONV_WHOCANSAY: _readConvWhocansay,
			BlockType.CONV_CHANGEACT_DISABLE: _readChangeAction,
			BlockType.CONV_CHANGEACT_SET: _readChangeAction,
			BlockType.CONV_CHANGEACT_ENABLE: _readChangeAction,
			BlockType.CONV_CHANGEACT_UNKNOWN2: _readChangeAction,
			BlockType.CONV_TEXT: _readConvText,
			BlockType.CONV_RESULT: _readList,
			BlockType.PHASER_STUN: _readList,
			BlockType.PHASER_GTP: _readList,
			BlockType.PHASER_KILL: _readList,
			BlockType.PHASER_HEADER: _readPhaserHeader,
			BlockType.VOICE: _readSpeechInfo,
		}

		more = handlers[block["type"]](f, block)
		
		if more:
			return_list = True
		blocks.append(block)

	if return_list:
		if blocks[-1]["type"] == BlockType.BLOCK_END:
			blocks.pop()
		return blocks

	return blocks[0]


def _readEmptyBlock(f, block):
	block["_length"] = 0
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


def _readListEntry(f, block_entries):
	entry = []

	begin_block = _readBlock(f)
	assert(begin_block["type"] == BlockType.LIST_BEGIN_ENTRY)
	block_entries["_begin"] = begin_block

	while True:
		block = _readBlock(f)
		entry.append(block)
		t = block[0]["type"] if type(block) == list else block["type"]
		if t == BlockType.LIST_END_ENTRY:
			block_entries["_end"] = entry.pop()
			break
	
	block_entries["entries"].append(entry)


def _readListEntryBegin(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0xae)

	assert(f.readUInt16() == 9)
	[f.readUInt32() for i in range(43)] # 172 bytes of unknown data. Offsets?
	return False


########################################################################################################################
# Utilities
########################################################################################################################


class ObjectId:

	def __init__(self, id, screen=None, world=None, unused=None):
		if screen is None and world is None and unused is None:
			self.value = 0xffffffff & int(id)
		else:
			assert(unused == 0 or unused == 0xff)
			self.value = (id & 0xff) + ((screen & 0xff) << 8) + ((world & 0xff) << 16) + ((unused & 0xff) << 24)
	

	def __getitem__(self, name):
		if name == "id":
			return self.value & 0xff
		elif name == "screen":
			return (self.value >> 8) & 0xff
		elif name == "world":
			return (self.value >> 16) & 0xff
		elif name == "unused":
			return (self.value >> 24) & 0xff
		else:
			raise KeyError("ObjectId does not have '{}'".format(name))
	

	def __setitem__(self, name, value):
		if name == "id":
			self.value = (self.value & 0xffffff00) + (value & 0xff)
		elif name == "screen":
			self.value = (self.value & 0xffff00ff) + ((value & 0xff) << 8)
		elif name == "world":
			self.value = (self.value & 0xff00ffff) + ((value & 0xff) << 16)
		elif name == "unused":
			assert(value == 0x0 or value == 0xff)
			self.value = (self.value & 0x00ffffff) + ((value & 0xff) << 24)
		else:
			raise KeyError("ObjectId does not have '{}'".format(name))
	

	def __str__(self):
		return "{:06x}".format(self.value)
	

	def __eq__(self, value):
		return self.value == value
	

	def __hash__(self):
		return self.value




def _readObjectId(f):
	obj_id = f.readUInt8()
	obj_screen = f.readUInt8()
	obj_world = f.readUInt8()
	obj_unused = f.readUInt8()
	return ObjectId(obj_id, obj_screen, obj_world, obj_unused)


def _readEntryHeader(f, expected_header_type):
	header = {}

	
	parent_id = f.readUInt8()
	parent_screen = f.readUInt8()
	parent_world = f.readUInt8()
	parent_unused = f.readUInt8()
	header["parent_id"] = ObjectId(parent_id, parent_screen, parent_world, parent_unused)

	header["counter2"] = f.readUInt8()
	header["counter3"] = f.readUInt8()
	header["counter4"] = f.readUInt8()

	assert(f.readUInt8() == expected_header_type)

	stop = f.readUInt8()
	header["stop_here"] = None if stop == 0xff else bool(stop)

	# the state/response of this conversation block?, or 0xffff in an object
	response = f.readUInt16()
	state = f.readUInt16()
	header["response_counter"] = None if response == 0xffff else response
	header["state_counter"] = None if state == 0xffff else state

	return header


def _getVoiceFile(speaker, voice, file_type=None):
	speaker_id = speaker["id"]
	# 0x20 - 0x28 indicate the speaker is on the Enterprise speaking over comms
	if speaker["world"] == 0 and speaker["screen"] == 0 and (speaker["id"] >= 0x20 and speaker["id"] <= 0x28):
		speaker_id -= 0x20
	elif speaker["world"] == 0 and speaker["screen"] == 0 and (speaker["id"] >= 0x30 and speaker["id"] <= 0x38):
		speaker_id -= 0x30
	elif speaker["world"] != 0 or speaker["screen"] != 0 or speaker["id"] > 9:
		speaker_id = 0xff

	if voice["group"] == 0xfe:
		file_name = "{1[group]:02x}{0:02x}{1[subgroup]:02x}{1[id]:02x}.vac".format(speaker_id, voice)
	elif voice["group"] == 0xfd:
		file_name = "{1[group]:02x}_{0:02x}_{1[subgroup]:02x}_{1[id]:02x}.vac".format(speaker_id, voice)
	elif not file_type is None:
		file_name = "{1[group]:02x}{2}{1[subgroup]:01x}{0:02x}{1[id]:02x}.vac".format(speaker_id, voice, file_type)
	else:
		file_name = "{1[group]:02x}{1[subgroup]:02x}{0:02x}{1[id]:02x}.vac".format(speaker_id, voice)

	return file_name


def _readVoiceId(f):
	voice_id = f.readUInt32()
	voice_group = f.readUInt32()
	voice_subgroup = f.readUInt16()
	return {
		"id": voice_id,
		"group": voice_group,
		"subgroup": voice_subgroup,
	}


def _getTextTargets(t):
	assert( len(t) % 4 == 0 )
	tt = { int(t[x]) : t[x+1:x+4] for x in range(0, len(t), 4) }
	return { k: "fe0{}0{}.vac".format(k,v) for k,v in tt.items() }


########################################################################################################################
# Conversation Blocks
########################################################################################################################


class ConversationResponseState (Enum):
	ENABLED = 0x2
	DISABLED = 0x3
	UNKNOWN_1 = 0x4


def _readConvResponse(f, block):
	block["unknown"] = []

	block["id"] = f.readUInt16()
	block["state"] = f.readUInt16()

	txts = f.readStringBuffer(255).split("@")
	assert(len(txts) in (1,3))
	block["text1"] = txts[0].strip()
	if len(txts) == 3:
		block["text1_vacs"] = _getTextTargets(txts[1])

	block["response_state"] = ConversationResponseState(f.readUInt8())
	block["unknown"].append([f.readUInt16() for i in range(3)])
	block["next_situation"] = f.readUInt16()
	block["unknown"].append([(f.readUInt16(),f.readUInt16()) for i in range(5)])
	block["target_id"] = _readObjectId(f)
	block["unknown"].append([f.readUInt16() for i in range(5)])
	block["voice"] = _readVoiceId(f)

	conv_actions = (BlockType.CONV_CHANGEACT_DISABLE, BlockType.CONV_CHANGEACT_ENABLE, BlockType.CONV_CHANGEACT_SET, BlockType.CONV_CHANGEACT_UNKNOWN2)

	block["whocansay"] = []
	block["text"] = []
	block["actions"] = []
	block["results"] = []

	while True:
		sub_block = _readBlock(f)
		t = sub_block[0]["type"] if type(sub_block) is list else sub_block["type"]
		if t == BlockType.BLOCK_END:
			break
		if t == BlockType.CONV_WHOCANSAY:
			for whocansay in sub_block:
				# TODO: this is a temporary bodge to allow the code below to set the "file" and "vac" on this object id,
				# which would fail if it's stored as an ObjectId
				#block["whocansay"].append(whocansay["who"])
				block["whocansay"].append({
					"id": whocansay["who"]["id"],
					"world": whocansay["who"]["world"],
					"screen": whocansay["who"]["screen"],
					"unused": whocansay["who"]["unused"],
				})
		elif t == BlockType.CONV_TEXT:
			block["text"] += sub_block
		elif t in conv_actions:
			block["actions"].append(sub_block)
		elif t == BlockType.CONV_RESULT:
			block["results"].append(sub_block)
		else:
			raise ValueError("Unexpected block type: {}".format(t))

	if len(block["text"]) == 2 and block["text"][0]["text"][-1] == '>':
		extra = block["text"].pop()
		block["text"][0]["text"] = block["text"][0]["text"][:-1] + extra["text"]

	#assert(len(block["text"]) == 1) # w006c035.bst, w05fc034.bst
	if block["voice"]["id"] != 0xffffffff and block["voice"]["group"] != 0xcc:
		if len(block["text1"]) > 0:
			for who in block["whocansay"]:
				if block["voice"]["group"] == 0xfd:
					who["file"] = block["text1_vacs"][who["id"]]
					who["vac"] = {
						"file": block["text1_vacs"][who["id"]],
						"speaker": {"id": who["id"], "world": who["world"], "screen": who["screen"], "unused": who["unused"]},
						"voice": block["voice"],
						"text": block["text1"]
					}
				else:
					who["file"] = _getVoiceFile(who, block["voice"])
					who["vac"] = {
						"file": _getVoiceFile(who, block["voice"]),
						"speaker": {"id": who["id"], "world": who["world"], "screen": who["screen"], "unused": who["unused"]},
						"voice": block["voice"],
						"text": block["text1"]
					}
	for text in block["text"]:
		if len(text["text"]) > 0 and text["voice"]["group"] != 0xcc:
			text["file"] = _getVoiceFile(block["target_id"], text["voice"])
			text["speaker"] = block["target_id"]
	if not db_data:
		block.pop("unknown")

	return False



def _readConvWhocansay(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 8)

	# An id of 0x10 means anyone in the away team
	block["who"] = _readObjectId(f)

	block["unknown"] = [f.readUInt8() for i in range(4)] # looks like an offset?

	return True


def _readConvText(f, block):
	block["_length"] = f.readUInt16()
	assert (block["_length"] == 0x10d)

	block["text"] = f.readStringBuffer(255)
	# two files have text2: w006c035.bst, w05fc034.bst
	block["text2"] = f.readUInt32()
	block["voice"] = _readVoiceId(f)

	return True


def _readChangeAction(f, block):
	assert(f.readUInt16() == 8)

	block["response_id"] = f.readUInt16()
	block["state_id"] = f.readUInt16()
	block["unknown"] = []
	block["unknown"].append(f.readUInt8()) # unknown4
	block["unknown"].append(f.readUInt8()) # unknown5
	block["unknown"].append(f.readUInt16()) # unknown6

	return True


########################################################################################################################
# Object Blocks
########################################################################################################################


class ObjectWalkType (Enum):
	NORMAL = 0x0
	SCALED = 0x1 # scaled with walkable polygons (e.g.characters)
	TRANSITION_SQUARE = 0x2
	ACTION_SQUARE = 0x3


def _readObject(f, block):
	block["_length"] = f.readUInt16()
	assert (block["_length"] == 0x128)

	block["object_id"] = _readObjectId(f)
	block["curr_screen"] = f.readUInt8()

	block["unknown_3"] = f.readUInt8()

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

	assert(f.readUInt8() == 0)

	block["walk_type"] = ObjectWalkType(f.readUInt8())
	n_descriptions = f.readUInt8()
	block["name"] = f.readStringBuffer(20)

	for i, thing in enumerate(["DESCRIPTION", "USE", "LOOK", "WALK", "TIME"]):  # TODO: pointers to the relevant blocks?
		unknown_a1 = f.readUInt16()
		unknown_a2 = f.readUInt8()
		unknown_a3 = f.readUInt8()
		block["unknown_{}".format(thing)] = (unknown_a1, unknown_a2, unknown_a3)
		if i == 0:
			block["transition"] = _readObjectId(f)

	block["skills"] = f.readUInt16()
	block["timer"] = f.readUInt16()
	block["talk"] = f.readStringBuffer(100)

	assert(f.readUInt16() == 0)
	assert(f.readUInt16() == 0)
	assert(f.readUInt16() == 0)
	block["unknown_21"] = f.readUInt16()

	block["voice"] = _readVoiceId(f)

	cursor_id = f.readUInt8()
	cursor_flag = f.readUInt8()
	block["cursor"] = {
		"id": cursor_id,
		"flag": cursor_flag,
	}

	block["unknown_26"] = f.readUInt8()
	block["unknown_27"] = f.readUInt8()

	assert(f.readUInt16() == 0)

	for i in range(21):
		assert(f.readUInt32() == 0)

	block["descriptions"] = []
	if n_descriptions > 0:
		descriptions = _readBlock(f)
		assert(descriptions[0]["type"] == BlockType.DESCRIPTION)
		for desc in descriptions:

			if desc["speaker"]["id"] == 0xff:
				# Looks like 0xff means use a default speaker, though I'm not sure where that's set
				# So replace with the voice id we'd expect at this point
				assert(desc["speaker"]["world"] == 0)
				assert(desc["speaker"]["screen"] == 0)
				desc["speaker"]["id"] = len(block["descriptions"])

			if desc["voice"]["id"] != 0xffffffff and desc["voice"]["group"] != 0xcc:
				desc["file"] = _getVoiceFile(desc["speaker"], desc["voice"], 'l')
			
		block["descriptions"] = descriptions
	assert(len(block["descriptions"]) == n_descriptions)

	block["uses"] = []
	block["gets"] = []
	block["looks"] = []
	block["timers"] = []
	while not f.eof():
		list_block = _readBlock(f)
		if list_block["type"] == BlockType.BLOCK_END:
			break
		elif list_block["type"] == BlockType.USE_ENTRIES:
			block["uses"] += list_block["entries"]
		elif list_block["type"] == BlockType.GET_ENTRIES:
			block["gets"] += list_block["entries"]
		elif list_block["type"] == BlockType.LOOK_ENTRIES:
			block["looks"] += list_block["entries"]
		elif list_block["type"] == BlockType.TIMER_ENTRIES:
			block["timers"] += list_block["entries"]

	assert(len(block["uses"]) == n_uses)
	assert(len(block["gets"]) == n_gets)
	assert(len(block["looks"]) == n_looks)
	assert(len(block["timers"]) <= 1) # timers can only have one result

	return False


def _readDescription(f, block):
	block["_length"] = f.readUInt16()
	assert (block["_length"] == 0xa5)

	block["speaker"] = ObjectId(f.readUInt8(), 0, 0, 0)

	for i in range(7):
		assert(f.readUInt16() == 0xffff)

	block["text"] = f.readStringBuffer(149)
	block["unknown_2"] = f.readUInt8()  # Is this just corrupt entries and there should be a null byte here?

	voice = _readBlock(f)
	assert(voice["type"] == BlockType.VOICE)
	block["voice"] = voice["voice"]

	return True



def _readConversation(f, block):
	block["_length"] = f.readUInt16()
	assert (block["_length"] == 0x7c)
	assert(f.readUInt16() == 9)

	_readEntryHeader(f, 0x49)
	block["world_id"] = f.readUInt16()
	block["conv_id"] = f.readUInt16()
	block["conv_response"] = f.readUInt16()
	block["conv_state"] = f.readUInt16()
	block["action_type"] = ConversationResponseState(f.readUInt16())
	for i in range(99):
		assert(f.readUInt8() == 0)

	# TODO: This is generating invalid file names when world_id == 0xffff. Perhaps this is world 05f?
	block["file"] = "w{0:03x}c{1:03d}.bst".format(block["world_id"], block["conv_id"])

	return True


def _readSpeechInfo(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x0c)

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
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0xda)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0xff)

	block["target_id"] = _readObjectId(f)
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
	# TODO: These are often all null, and make a lot of noise in the file. So commented out to remove the noise. Think about chekcing value then storing?
	#block["list"] = entries 

	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)

	block["how_close_x"] = f.readUInt16()
	block["how_close_y"] = f.readUInt16()

	assert(f.readUInt16() == 0xffff)

	block["how_close_dist"] = f.readUInt16()
	block["skill_check"] = f.readUInt16()

	block["counter_value"] = f.readUInt16()
	block["counter_when"] = f.readUInt8()

	for i in range(25):
		assert(f.readUInt32() == 0)

	return False


def _readAlter(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x105)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x43)
	block["target_id"] = _readObjectId(f)
	block["alter_flags"] = f.readUInt8()
	block["alter_reset"] = f.readUInt8()
	block["alter_time"] = f.readUInt16()
	assert(f.readUInt16() == 0xffff)
	block["alter_anim"] = f.readUInt16()
	block["alter_state"] = f.readUInt8()
	block["play_description"] = f.readUInt8()
	block["x_pos"] = f.readUInt16()
	block["y_pos"] = f.readUInt16()
	block["unknown_8"] = f.readUInt16() # z_pos?

	# these are always 0xffff inside objects..
	block["universe_x"] = f.readUInt16()
	block["universe_y"] = f.readUInt16()
	block["universe_z"] = f.readUInt16()

	block["alter_name"] = f.readStringBuffer(20)
	block["alter_hail"] = f.readStringBuffer(100)

	assert(f.readUInt32() == 0xffffffff)

	block["voice"] = _readVoiceId(f)
	assert(block["voice"]["group"] != 0xffffffff or block["voice"]["subgroup"] == 0xffff)
	assert(block["voice"]["group"] != 0xffffffff or block["voice"]["id"] == 0xffffffff)

	# talk begin/end stuff??
	block["unknown_talk1"] = f.readUInt8()
	block["unknown_talk2"] = f.readUInt8()
	assert(block["unknown_talk1"] in (0xff, 0, 1, 2, 3))
	assert(block["unknown_talk2"] in (0xff, 0, 1))

	for i in range(21):
		assert(f.readUInt32() == 0)

	if len(block["alter_hail"]) > 0 and block["voice"]["id"] != 0xffffffff:
		block["alter_hail_immediate"] = block["alter_hail"][0] == '1'
		if block["alter_hail_immediate"]:
			block["alter_hail"] = block["alter_hail"][1:]
		assert(block["play_description"] == 0)
		assert(block["unknown_talk1"] == 0xff)
		assert(block["unknown_talk2"] == 0xff)
		if not block["alter_hail"].startswith("@") and block["voice"]["group"] != 0xcc:
			block["voice_file"] = _getVoiceFile(block["target_id"], block["voice"], 't')
			block["vac"] = {
				"file": _getVoiceFile(block["target_id"], block["voice"], 't'),
				"speaker": block["target_id"],
				"voice": block["voice"],
				"text": block["alter_hail"]
			}
	return True


def _readCommand(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x84)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x45)

	block["targets"] = [_readObjectId(f) for i in range(3)]

	# both usually 0xffff
	block["target_x"] = f.readUInt16()
	block["target_y"] = f.readUInt16()
	block["command_id"] = f.readUInt32() # command_id >= 2 && command_id <= 6

	for i in range(97):
		assert(f.readUInt8() == 0)

	return True


def _readGeneral(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x7b)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x48)

	block["movie_id"] = f.readUInt16()
	block["unknown"] = [f.readUInt16() for i in range(3)]
	for i in range(0x64):
		assert(f.readUInt8() == 0)
	
	return False


def _readScreen(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x90)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x46)

	block["screen_id"] = f.readUInt8()
	block["entrance_id"] = f.readUInt8()
	block["advice_screen"] = f.readUInt8()
	block["advice_id"] = f.readUInt16()
	block["world_id"] = f.readUInt16()

	unknown = []
	unknown.append(f.readUInt16())
	unknown.append(f.readUInt32())
	unknown.append(f.readUInt8())
	unknown.append(f.readUInt32())
	unknown.append(f.readUInt32())
	unknown.append(f.readUInt16())
	unknown.append(f.readUInt16())
	unknown.append(f.readUInt16())
	unknown.append(f.readUInt8())
	unknown.append(f.readUInt8())
	unknown.append(f.readUInt8())
	block["unknown"] = unknown

	block["advice_time"] = f.readUInt16() # should be 1 byte???

	for i in range(24):
		assert(f.readUInt32() == 0)
	
	return False


def _readTrigger(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x78)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x4b)
	block["trigger_id"] = f.readUInt32()
	flag = f.readUInt8()
	assert(flag in (0,1))
	block["enabled"] = flag == 1

	for i in range(25):
		assert(f.readUInt32() == 0)

	return True


def _readCommunicate(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x7c)
	assert(f.readUInt16() == 9)
	block["header"] = _readEntryHeader(f, 0x4c)

	block["target_id"] = _readObjectId(f)
	block["conversation_id"] = f.readUInt16()
	block["sitaution_id"] = f.readUInt16()
	block["hail_type"] = f.readUInt8()
	assert(block["hail_type"] <= 0x10)

	for i in range(25):
		assert(f.readUInt32() == 0)
	
	return False


def _readBeamdown(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x9f)
	assert(f.readUInt16() == 9)
	block["header"] = _readEntryHeader(f, 0x4a)

	block["world_id"] = f.readUInt16()
	block["unknown1"] = f.readUInt16()
	assert(block["unknown1"] in (0xffff, 1, 4))
	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)

	block["unknown3"] = f.readUInt16()
	assert(block["unknown3"] in (0, 0xffff))

	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)
	assert(f.readUInt16() == 0xffff)

	block["screen_id"] = f.readUInt16()
	assert(block["screen_id"] in (0,1,2,3,4,0xffff))

	assert(f.readUInt16() in (0xffff, 0, 0x60))
	assert(f.readUInt16() in (0xffff, 0x20, 0x1b))
	for i in range(3):
		assert(f.readUInt16() == 0)
		assert(f.readUInt32() == 0xffffffff)
	for i in range(51):
		assert(f.readUInt16() == 0)
	
	return False



def _readChoice(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x10b)
	assert(f.readUInt16() == 9)
	block["header"] = _readEntryHeader(f, 0x4d)

	block["unknown1"] = f.readUInt16()
	block["unknown2"] = f.readUInt16()

	block["question"] = f.readStringBuffer(100)
	block["choice1"] = f.readStringBuffer(16)
	block["choice2"] = f.readStringBuffer(16)

	block["object_id"] = _readObjectId(f)

	block["choice1_offset"] = f.readUInt32()
	block["choice2_offset"] = f.readUInt32()
	block["choice1_count"] = f.readUInt16()
	block["choice2_count"] = f.readUInt16()

	for i in range(25):
		assert(f.readUInt32() == 0)


def _readPath(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x17b)
	assert(f.readUInt16() == 9)
	block["header"] = _readEntryHeader(f, 0x47)

	block["regions_activate"] = [f.readUInt8() for i in range(4)]
	block["regions_deactivate"] = [f.readUInt8() for i in range(4)]

	block["stops"] = []
	for i in range(0x10):
		stop = {}
		stop["x"] = f.readUInt32()
		stop["y"] = f.readUInt32()
		stop["unknown0"] = f.readUInt16()
		stop["unknown1"] = f.readUInt16()
		stop["region_id"] = f.readUInt16()
		stop["scale"] = f.readUInt16()
	
	for i in range(25):
		assert(f.readUInt32() == 0)


def _readReaction(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x87)
	assert(f.readUInt16() == 9)
	block["header"] = _readEntryHeader(f, 0x44)

	block["target_id"] = _readObjectId(f)
	block["dest_world"]= f.readUInt16()
	block["dest_screen"]= f.readUInt16()
	block["dest_entrance"]= f.readUInt16()
	block["target_type"]= f.readUInt8()
	block["action_type"]= f.readUInt8()
	block["damage_amount"]= f.readUInt8()
	block["beam_type"]= f.readUInt8()
	block["dest_x"]= f.readUInt16()
	block["dest_y"]= f.readUInt16()
	block["dest_unknown"]= f.readUInt16()

	assert(block["target_type"] in range(1, 8) or block["target_type"] == 0xff)
	if block["target_type"] != 6:
		assert(block["target_id"]["id"] == 0xff)
	else:
		assert(block["target_id"]["id"] != 0xff)
	if block["damage_amount"] == 0:
		assert(block["action_type"] <= 3 or block["action_type"] == 0xff)

	for i in range(25):
		assert(f.readUInt32() == 0)






########################################################################################################################
# Phaser Blocks
########################################################################################################################



def _readPhaserHeader(f, block):
	block["_length"] = f.readUInt16()
	assert(block["_length"] == 0x7e)
	start = f.pos()

	block["object_id"] = _readObjectId(f)
	block["field_0x4"] = f.readUInt16()
	block["health_max"] = f.readUInt8()
	assert(f.readUInt8() == 0)
	block["health_current"] = block["health_max"]
	block["health_unknown"] = f.readUInt8()
	assert(f.readUInt8() == 0)
	block["health_stunned"] = block["health_unknown"]
	block["field_0xd"] = f.readUInt8()
	block["field_0xe"] = f.readUInt8()
	block["field_0xb"] = f.readUInt8()
	block["field_0xc"] = f.readUInt8()

	assert(f.readUInt32() == 0)
	assert(f.readUInt32() == 0) # The game sets these to zero
	assert(f.readUInt32() == 0)

	# As far as I can tell, the game ignores the rest of this block

	assert(f.readUInt16() == 0)
	for i in range(86):
		assert(f.readUInt8() == 0)
	
	# Not sure what these are, but they're only non-zero when there are entries in the respective lists
	block["unknown_stun"] = [f.readUInt8() for i in range(4)]
	block["unknown_gtp"] = [f.readUInt8() for i in range(4)]
	block["unknown_kill"] = [f.readUInt8() for i in range(4)]

	# todo: not reading to the end?

	f.setPosition(start + block["_length"])
	return False



########################################################################################################################
# Public Functions
########################################################################################################################


def identifyObject(dir, id):
	o = getObject(dir, id)
	if o:
		id["name"] = o[0]["name"]
	return id


def getObject(dir, id):
	name = "o_{:02x}{:02x}{:02x}.bst".format(id["world"], id["screen"], id["id"])
	path = dir.joinpath(name)
	try:
		obj = bst(path)
	except:
		return None
	return obj


def bst(file_path):
	f = File.File(file_path)

	blocks = []
	while not f.eof():
		blocks.append(_readBlock(f))

	return blocks
