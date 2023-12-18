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


def _readBlockHeader(f):
	block_offset = f.pos()
	block_type = BlockType(f.readUInt8())
	assert (f.readUInt8() == 0x11)

	return {
		"offset": block_offset,
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
			BlockType.ALTER: _readAlter,
			BlockType.OBJECT: _readObject,
			BlockType.CONV_RESPONSE: _readConvResponse,
			BlockType.DESCRIPTION: _readDescription,
			BlockType.VOICE: _readSpeechInfo,
			BlockType.CONVERSATION: _readConversation,
			BlockType.CONV_WHOCANSAY: _readConvWhocansay,
			BlockType.CONV_CHANGEACT_DISABLE: _readChangeAction,
			BlockType.CONV_CHANGEACT_ENABLE: _readChangeAction,
			BlockType.CONV_CHANGEACT_SET: _readChangeAction,
			BlockType.CONV_TEXT: _readConvText,
			BlockType.USE_ENTRIES: _readList,
			BlockType.GET_ENTRIES: _readList,
			BlockType.LOOK_ENTRIES: _readList,
			BlockType.TIMER_ENTRIES: _readList,
			BlockType.LIST_BEGIN_ENTRY: _readListEntryBegin,
			BlockType.LIST_END_ENTRY: _readEmptyBlock,
			BlockType.CONV_RESULT: _readList,
			BlockType.BLOCK_END: _readEmptyBlock,
			BlockType.CHOICE1: _readEmptyBlock,
			BlockType.CHOICE2: _readEmptyBlock,
			BlockType.CONDITION: _readCondition,
			BlockType.COMMAND: _readCommand,
			BlockType.GENERAL: _readGeneral,
		}
		need_more = [
			BlockType.ALTER,
			BlockType.TRIGGER,
			BlockType.CONV_CHANGEACT_UNKNOWN2,
		]

		if block["type"] in handlers:
			more = handlers[block["type"]](f, block)
		else:
			if db: print("Cannot read block type:", block["type"])
			block["length"] = f.readUInt16()
			f.setPosition(f.pos() + block["length"])
			more = block["type"] in need_more #False

		if more:
			return_list = True
		blocks.append(block)

	if return_list:
		if blocks[-1]["type"] == BlockType.BLOCK_END:
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
	assert (begin_block["type"] == BlockType.LIST_BEGIN_ENTRY)
	entry_block["begin"] = begin_block

	while True:
		block = _readBlock(f)
		if block["type"] == BlockType.LIST_END_ENTRY:
			entry_block["end"] = block
			break
		else:
			entry_block["list"].append(block)

	if db_data:
		entries_block["entries"].append(entry_block)
	else:
		entries_block["entries"].append(entry_block["list"])


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


def _readEntryHeader(f, expected_header_type):
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

	header["type"] = f.readUInt8() #BlockType(f.readUInt8())
	assert(header["type"] == expected_header_type)

	header["stop_here"] = f.readUInt8()
	assert(header["stop_here"] in (0, 1, 0xff))

	# the state/response of this conversation block?, or 0xffff in an object
	header["response_counter"] = f.readUInt16()
	header["state_counter"] = f.readUInt16()

	return header


# TextBlock::execute
# _vm->voiceFileFor(voice_group, voice_subgroup, speaker->id, voice_id);
# Response::execute
# _vm->voiceFileFor(voice_group, voice_subgroup, speaker->id, voice_id);
# UnityEngine::playDescriptionFor
# voiceFileFor(desc.voice_group, desc.voice_subgroup, objectID(desc.entry_id, 0, 0), desc.voice_id, 'l');

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

	if voice["group"] == 0xfd:
		print(speaker, voice, file_name, file_type)

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
	block["target"] = _readObjectId(f)
	block["unknown"].append([f.readUInt16() for i in range(5)])
	block["voice"] = _readVoiceId(f)

	conv_actions = (BlockType.CONV_CHANGEACT_DISABLE, BlockType.CONV_CHANGEACT_ENABLE, BlockType.CONV_CHANGEACT_SET, BlockType.CONV_CHANGEACT_UNKNOWN2)

	block["whocansay"] = []
	block["text"] = []
	block["actions"] = []
	block["results"] = []

	while True:
		sub_block = _readBlock(f)

		if sub_block["type"] == BlockType.BLOCK_END:
			break
		if sub_block["type"] == BlockType.CONV_WHOCANSAY:
			for whocansay in sub_block["blocks"]:
				block["whocansay"].append(whocansay["who"])
		elif sub_block["type"] == BlockType.CONV_TEXT:
			block["text"] += sub_block["blocks"]
		elif sub_block["type"] in conv_actions:
			block["actions"].append(sub_block["blocks"])
		elif sub_block["type"] == BlockType.CONV_RESULT:
			block["results"].append(sub_block)
		else:
			raise ValueError("Unexpected block type: {}".format(sub_block["type"]))

	if len(block["text"]) == 2 and block["text"][0]["text1"][-1] == '>':
		extra = block["text"].pop()
		block["text"][0]["text1"] = block["text"][0]["text1"][:-1] + extra["text1"]

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
		if len(text["text1"]) > 0 and text["voice"]["group"] != 0xcc:
			text["file"] = _getVoiceFile(block["target"], text["voice"])
			text["vac"] = {
				"file": _getVoiceFile(block["target"], text["voice"]),
				"speaker": block["target"],
				"voice": text["voice"],
				"text": text["text1"]
			}
	if not db_data:
		block.pop("unknown")

	return False



def _readConvWhocansay(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 8)

	# An id of 0x10 means anyone in the away team
	block["who"] = _readObjectId(f)

	unknown = [f.readUInt8() for i in range(4)] # looks like an offset?
	if db: block["unknown"] = unknown

	return True


def _readConvText(f, block):
	block["length"] = f.readUInt16()
	assert (block["length"] == 0x10d)

	block["text1"] = f.readStringBuffer(255)
	#block["text2"] = f.readStringBuffer(4) # two files have text here: w006c035.bst, w05fc034.bst
	block["text2"] = [f.readUInt8() for i in range(4)]
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

	block["voice"] = _readVoiceId(f)

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
		assert(description_blocks["type"] == BlockType.DESCRIPTION)
		for description_block in description_blocks["blocks"]:

			speaker = description_block["speaker"]
			if speaker["id"] == 0xff:
				# Looks like 0xff means use a default speaker, though I'm not sure where that's set
				# So replace with the voice id we'd expect at this point
				assert(speaker["world"] == 0)
				assert(speaker["screen"] == 0)
				speaker["id"] = len(block["descriptions"])

			block["descriptions"].append({
				"speaker": description_block["speaker"],
				"text": description_block["text"],
				"voice": description_block["voice"],
			})
			if description_block["voice"]["id"] != 0xffffffff and description_block["voice"]["group"] != 0xcc:
				block["descriptions"][-1]["file"] = _getVoiceFile(speaker, description_block["voice"], 'l')
				block["descriptions"][-1]["vac"] = {
					"file": _getVoiceFile(speaker, description_block["voice"], 'l'),
					"speaker": speaker,
					"text": description_block["text"],
					"voice": description_block["voice"]
				}
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
	block["length"] = f.readUInt16()
	assert (block["length"] == 0xa5)

	block["speaker"] = {"id": f.readUInt8(), "world": 0, "screen":0, "unused": 0}

	for i in range(7):
		assert (f.readUInt16() == 0xffff)  # unknowna

	block["text"] = f.readStringBuffer(149)
	f.readUInt8()  # unknown2. is this just corrupt entries and there should be a null byte here?

	voice = _readBlock(f)
	assert(voice["type"] == BlockType.VOICE)
	block["voice"] = voice["voice"]

	return True



def _readConversation(f, block):
	block["length"] = f.readUInt16()
	assert (block["length"] == 0x7c)
	assert(f.readUInt16() == 9)

	_readEntryHeader(f, 0x49)
	block["world_id"] = f.readUInt16()
	block["conversation_id"] = f.readUInt16()
	block["response_id"] = f.readUInt16()
	block["state_id"] = f.readUInt16()
	block["action_id"] = ConversationResponseState(f.readUInt16())
	for i in range(99):
		assert(f.readUInt8() == 0)

	block["file"] = "w{0:03x}c{1:03d}.bst".format(block["world_id"], block["conversation_id"])

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

	block["header"] = _readEntryHeader(f, 0xff)

	block["target"] = _readObjectId(f)
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


def _readAlter(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0x105)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x43)
	block["target"] = _readObjectId(f)
	block["alter_flags"] = f.readUInt8()
	block["alter_reset"] = f.readUInt8()
	block["alter_time"] = f.readUInt16()
	assert(f.readUInt16() == 0xffff) # unknown16
	block["alter_anim"] = f.readUInt16()
	block["alter_state"] = f.readUInt8()
	block["play_description"] = f.readUInt8()
	block["x_pos"] = f.readUInt16()
	block["y_pos"] = f.readUInt16()
	unknown8 = f.readUInt16() # z_pos?

	# these are always 0xffff inside objects..
	block["universe_x"] = f.readUInt16()
	block["universe_y"] = f.readUInt16()
	block["universe_z"] = f.readUInt16()

	block["alter_name"] = f.readStringBuffer(20)
	block["alter_hail"] = f.readStringBuffer(100)

	assert(f.readUInt32() == 0xffffffff) #unknown32

	block["voice"] = _readVoiceId(f)
	assert(block["voice"]["group"] != 0xffffffff or block["voice"]["subgroup"] == 0xffff)
	assert(block["voice"]["group"] != 0xffffffff or block["voice"]["id"] == 0xffffffff)

	# talk begin/end stuff??
	block["unknown_talk1"] = f.readUInt8()
	block["unknown_talk2"] = f.readUInt8()
	assert(block["unknown_talk1"] in (0xff, 0, 1, 2, 3)) #unknown11
	assert(block["unknown_talk2"] in (0xff, 0, 1)) #unknown12

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
			block["voice_file"] = _getVoiceFile(block["target"], block["voice"], 't')
			block["vac"] = {
				"file": _getVoiceFile(block["target"], block["voice"], 't'),
				"speaker": block["target"],
				"voice": block["voice"],
				"text": block["alter_hail"]
			}
	return True


def _readCommand(f, block):
	block["length"] = f.readUInt16()
	assert(block["length"] == 0x84)
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
	block["length"] = f.readUInt16()
	assert(block["length"] == 0x7b)
	assert(f.readUInt16() == 9)

	block["header"] = _readEntryHeader(f, 0x48)

	block["movie_id"] = f.readUInt16()
	block["unknown"] = [f.readUInt16() for i in range(3)]
	for i in range(0x64):
		assert(f.readUInt8() == 0)


########################################################################################################################
# Phaser Blocks
########################################################################################################################



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
