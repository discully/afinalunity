from enum import IntEnum
from json import dump
from AFU import File, Block
import AFU







#### Utils

def _readOffsetString(f, ignore_zero=False, ignore_null=True):
	offset = f.readUInt32()
	if offset == 0xffffffff and ignore_null:
		return None
	if offset == 0 and ignore_zero:
		return None
	return f.readOffsetString(offset)

def _readObjectId(f):
	return Block._readObjectId(f)



# Bridge Items

def _readBridgeItem(f):
	name = _readOffsetString(f)
	id = _readObjectId(f)
	x = f.readUInt32()
	y = f.readUInt32()
	width = f.readUInt32()
	height = f.readUInt32()
	unknown = f.readUInt32()
	assert(f.readUInt32() == 0) # pointer to image struct
	y_adjust = f.readSInt32()
	return {
		"id": id,
		"name": name,
		"pos": (x,y),
		"size": (width,height),
		"y_adjust": y_adjust,
		"unknown": unknown,
	}

def readBridgeItems(f, print_items=False):
	bridge_items = [_readBridgeItem(f) for i in range(11)]

	if print_items:
		for item in bridge_items:
			print(item)

	return bridge_items



# Engineering

def _readEngineeringReadout(f):
	assert(f.readUInt32() == 0)  # current percentage
	assert(f.readUInt32() == 0) # target percentage
	assert(f.readUInt32() == 0xffffffff)
	assert(f.readUInt32() == 0xffffffff)
	readout_x = f.readUInt32()
	readout_y = f.readUInt32()
	# 17=repair, 33=power, 4096=torpedos, 2081=full height power (eps grid), 546,552=reactor power with extra bar at bottom
	# 
	# repair        =   17 = 0x  11 =           0001 0001
	# power default =   33 = 0x  21 =           0010 0001
	# power reactor =  546 = 0x 222 =      0010 0010 0010
	# power reactor =  552 = 0x 228 =      0010 0010 1000
	# power epsgrid = 2081 = 0x 821 =      1000 0010 0001
	# torpedoes     = 4096 = 0x1000 = 0001 0000 0000 0000
	#
	# (x & 0x40 != 0) ???                       0100 0000
	# (x & 0x20 != 0) power                     0010 0000
	# (x & 0x10 != 0) repair                    0001 0000
	# (x+1 & 0x04 != 0)               0000 0100
	# (x+1 & 0x10 != 0) torpedoes     0001 0000
	#
	#readout_type = {0x10: "Repair", 0x20: "Power", 0x1000: "Torpedoes"}[f.readUInt32()]
	readout_type = f.readUInt32()
	assert(f.readUInt32() == 1) # unknown
	assert(f.readUInt32() in (0,18)) # unknown
	assert(f.readUInt32() == 0) # unknown
	assert(f.readUInt32() == 0) # pointer to image
	assert(f.readUInt32()  == 0) # potinter to system struct
	return {
		"pos": (readout_x,readout_y),
		"type": readout_type,
	}

def readEngineeringReadouts(f, print_readouts=False):
	readouts = [_readEngineeringReadout(f) for i in range(70)]

	if print_readouts:
		for readout in readouts:
			print(readout)
	
	return readouts


def _readEngineeringScreenButton(f):
	sb_unknown0 = f.readUInt8()
	sb_is_down = f.readUInt8() != 0
	sb_unknown2 = f.readUInt8()
	sb_unknown3 = f.readUInt8()
	assert(sb_unknown0 == 0)
	assert(sb_is_down == 0)
	assert(sb_unknown2 == 0)
	assert(sb_unknown3 == 0)
	sb_next_update_time = f.readUInt32()
	assert(sb_next_update_time == 0)
	sb_posA_x1 = f.readUInt32()
	sb_posA_y1 = f.readUInt32()
	sb_posA_x2 = f.readUInt32()
	sb_posA_y2 = f.readUInt32()
	sb_posA_width = f.readUInt32()
	sb_posA_height = f.readUInt32()
	sb_posB_x1 = f.readUInt32()
	sb_posB_y1 = f.readUInt32()
	sb_posB_x2 = f.readUInt32()
	sb_posB_y2 = f.readUInt32()
	sb_posB_width = f.readUInt32()
	sb_posB_height = f.readUInt32()
	sb_img_up = f.readUInt32()
	sb_img_down = f.readUInt32()
	assert(sb_img_up == 0)
	assert(sb_img_down == 0)
	return {
		"A": {
			"x1": sb_posA_x1,
			"y1": sb_posA_y1,
			"x2": sb_posA_x2,
			"y2": sb_posA_y2,
			"width": sb_posA_width,
			"height": sb_posA_height,
		},
		"B": {
			"x1": sb_posB_x1,
			"y1": sb_posB_y1,
			"x2": sb_posB_x2,
			"y2": sb_posB_y2,
			"width": sb_posB_width,
			"height": sb_posB_height,
		},
	}

def readEngineeringScreenButtons(f, print_buttons=False):
	screen_buttons = [_readEngineeringScreenButton(f) for i in range(3)]

	if print_buttons:
		for sb in screen_buttons:
			print(sb)

	return screen_buttons


def readEngineeringDelegateButton(f, print_delegate=False):
	delegate = {}
	assert(f.readUInt32() == 0) # is button down?
	assert(f.readUInt32() == 0) # next update time
	delegate["button_x1"] = f.readUInt32()
	delegate["button_y1"] = f.readUInt32()
	delegate["button_x2"] = f.readUInt32()
	delegate["button_y2"] = f.readUInt32()
	delegate["status_x"] = f.readUInt32()
	delegate["status_y"] = f.readUInt32()
	delegate["unknown0_x"] = f.readUInt32()
	delegate["unknown0_y"] = f.readUInt32()
	delegate["unknown1_x"] = f.readUInt32()
	delegate["unknown1_y"] = f.readUInt32()
	delegate["graphic_x1"] = f.readUInt32()
	delegate["graphic_y1"] = f.readUInt32()
	delegate["graphic_x2"] = f.readUInt32()
	delegate["graphic_y2"] = f.readUInt32()
	delegate["unknown2_x"] = f.readUInt32()
	delegate["unknown2_y"] = f.readUInt32()
	assert(f.readUInt32() == 0) # pointer to button image up
	assert(f.readUInt32() == 0) # pointer to button image down
	delegate["unknown3_x"] = f.readUInt32()
	delegate["unknown3_y"] = f.readUInt32()
	delegate["unknown4_x"] = f.readUInt32()
	delegate["unknown4_y"] = f.readUInt32()
	assert(f.readUInt32() == 0) # pointer to status image current
	assert(f.readUInt32() == 0) # pointer to status image other

	if print_delegate:
		print(delegate)

	return delegate


def _readEngineeringLabel(f):
	label = {}
	label["x1"] = f.readUInt32()
	label["y1"] = f.readUInt32()
	label["x2"] = f.readUInt32()
	label["y2"] = f.readUInt32()
	label["text"] = s = _readOffsetString(f)
	return label

def readEngineeringLabels(f, print_labels=False):
	labels = [_readEngineeringLabel(f) for i in range(59)]

	if print_labels:
		for label in labels:
			print(label)

	return labels


def _readEngineeringMRGGraphic(f):
	pos = {}
	pos["x1"] = f.readUInt32()
	pos["y1"] = f.readUInt32()
	pos["x2"] = f.readUInt32()
	pos["y2"] = f.readUInt32()
	pos["width"] = f.readUInt32()
	pos["height"] = f.readUInt32()
	assert(f.readUInt32() == 0) # image pointer
	return pos

def readEngineeringMRGGraphics(f, print_graphics=False):
	# enterprise schematics (x10), warp engine, fusion reactors, table
	graphics = [_readEngineeringMRGGraphic(f) for i in range(13)]

	if print_graphics:
		for pos in graphics:
			print(pos)

	return graphics


def _readEngineeringTab(f):
	tab = {}
	assert(f.readUInt32() == 0) # is active?
	assert(f.readUInt32() == 0) # image active
	assert(f.readUInt32() == 0) # image inactive
	tab["index"] = f.readUInt32()
	tab["outer_x1"] = f.readUInt32()
	tab["outer_y1"] = f.readUInt32()
	tab["outer_x2"] = f.readUInt32()
	tab["outer_y2"] = f.readUInt32()
	tab["outer_width"] = f.readUInt32()
	tab["outer_height"] = f.readUInt32()
	tab["grapic_x1"] = f.readUInt32()
	tab["grapic_y1"] = f.readUInt32()
	tab["grapic_x2"] = f.readUInt32()
	tab["grapic_y2"] = f.readUInt32()
	tab["graphic_width"] = f.readUInt32()
	tab["graphic_height"] = f.readUInt32()
	return tab

def readEngineeringTabs(f, print_tabs=False):
	tabs = [_readEngineeringTab(f) for i in range(5)]

	if print_tabs:
		for tab in tabs:
			print(tab)

	return tabs


def _readEngineeringRectangle(f):
	rect = {}
	rect["x1"] = f.readUInt16()
	rect["y1"] = f.readUInt16()
	rect["x2"] = f.readUInt16()
	rect["y2"] = f.readUInt16()
	return rect

def readEngineeringRectangles(f, print_rects=False):
	rects = [_readEngineeringRectangle(f) for i in range(38)]

	if print_rects:
		for rect in rects:
			print(rect)

	return rects



# Ship Systems

class ShipSystemType (IntEnum):
	SHIP_SYS_PHASER = 1
	SHIP_SYS_TORPEDO = 2
	SHIP_SYS_IMPULSE = 3
	SHIP_SYS_WARP = 4
	SHIP_SYS_FUSION_REACTOR = 5
	SHIP_SYS_ANTIMATTER_REACTOR = 6
	SHIP_SYS_SHIELD = 7
	SHIP_SYS_SENSOR = 8
	SHIP_SYS_TRACTOR = 9
	SHIP_SYS_LIFE_SUPPORT = 10
	SHIP_SYS_COMPUTER = 11
	SHIP_SYS_POWER = 13

def _readShipSystem(f):
	system = {}
	system["name"] = f.readStringBuffer(32)
	system["type"] = ShipSystemType(f.readUInt32())
	assert(f.readUInt32() == 0xffffffff)
	system["damage_group"] = f.readUInt32()
	system["palette_index"] = f.readUInt32()
	system["charge_current"] = f.readUInt32()
	system["charge_target"] = f.readUInt32()
	system["charge_max"] = f.readUInt32()
	system["unknown_3c"] = f.readUInt32()
	system["rate_charge"] = f.readUInt32()
	system["rate_discharge"] = f.readUInt32()
	system["time_update_usage"] = f.readUInt32()
	system["rate_usage"] = f.readUInt32()
	system["unknown_50"] = f.readUInt32()
	system["unknown_54"] = f.readUInt32()
	assert(f.readUInt32() == 0) # time_udpate_charge
	assert(f.readUInt32() == 0) # time_update_5c
	assert(f.readUInt32() == 0) # health_damage
	assert(f.readUInt32() == 0) # unknown damage?
	system["unknown_68"] = f.readUInt32()
	system["damage_min"] = f.readUInt32()
	system["health_max"] = f.readUInt32()
	assert(f.readUInt32() == 0xffffffff)
	system["health_normal"] = f.readUInt32() # 0-95. The green bars under a power reactor
	system["unknown_7c"] = f.readUInt32()
	system["unknown_80"] = f.readUInt32()
	system["damage_chance"] = f.readUInt32() # chance of being damaged in a hit
	assert(f.readUInt32() == 0) # pointer to power readout struct
	assert(f.readUInt32() == 0) # pointer to repair readout struct
	assert(f.readUInt32() == 0) # charge requested?
	assert(f.readUInt32() == 0)
	assert(f.readUInt32() == 0) # charge requested?
	return system

def readShipSystemsEnterprise(f, print_systems=False):
	ship_systems = [_readShipSystem(f) for i in range(35)]

	if print_systems:
		for system in ship_systems:
			print(system)

	return ship_systems

def readShipSystemsOther(f, print_systems=False):
	ship_systems = [_readShipSystem(f) for i in range(20)]

	if print_systems:
		for system in ship_systems:
			print(system)

	return ship_systems



# Combat Audio

def _readCombatAudio(f):
	audio = {}
	audio["unknown_0"] = f.readUInt32()
	audio["fname_2"] = _readOffsetString(f, ignore_zero=True)
	audio["fname_1"] = _readOffsetString(f, ignore_zero=True)
	assert(f.readUInt32() == 0)
	audio["unknown_10"] = f.readUInt32()
	return audio

def readCombatAudio(f, print_audio=False):
	combat_audio = [_readCombatAudio(f) for i in range(131)]

	if print_audio:
		for audio in combat_audio:
			print(audio)

	for i,audio in enumerate(combat_audio):
		audio["index"] = i

	return combat_audio



OVERLAY_OFFSET = 0x5fea4
DATA_SEGMENT_OFFSET = OVERLAY_OFFSET + 0xf0000 # 0x14fea4

BRIDGE_ITEMS_OFFSET = 0x6fb54
ENGINEERING_READOUTS_OFFSET = 0x70424
ENGINEERING_SCREEN_BUTTONS_OFFSET = 0x71144
ENGINEERING_DELEGATE_BUTTONS_OFFSET = 0x71204
ENGINEERING_LABELS_OFFSET = 0x7126c
ENGINEERING_MRG_GRAPHICS_OFFSET = 0x71708
ENGINEERING_TABS_OFFSET = 0x71874
ENGINEERING_RECTANGLES_OFFSET = 0x719b4
SHIP_SYSTEMS_ENTERPRISE_OFFSET = 0x71ae8
SHIP_SYSTEMS_OTHER_OFFSET = 0x7303c
COMBAT_AUDIO_OFFSET = 0x73d0c


SECTIONS = {
	"Bridge Items": (BRIDGE_ITEMS_OFFSET, readBridgeItems),
	"Engineering Readouts": (ENGINEERING_READOUTS_OFFSET, readEngineeringReadouts),
	"Engineering Screen Buttons": (ENGINEERING_SCREEN_BUTTONS_OFFSET, readEngineeringScreenButtons),
	"Engineering Delegate Buttons": (ENGINEERING_DELEGATE_BUTTONS_OFFSET, readEngineeringDelegateButton),
	"Engineering Labels": (ENGINEERING_LABELS_OFFSET, readEngineeringLabels),
	"Engineering MRG Graphics": (ENGINEERING_MRG_GRAPHICS_OFFSET, readEngineeringMRGGraphics),
	"Engineering Tabs": (ENGINEERING_TABS_OFFSET, readEngineeringTabs),
	"Engineering Rectangles": (ENGINEERING_RECTANGLES_OFFSET, readEngineeringRectangles),
	"Ship Systems (Enterprise)": (SHIP_SYSTEMS_ENTERPRISE_OFFSET, readShipSystemsEnterprise),
	"Ship Systems (Other)": (SHIP_SYSTEMS_OTHER_OFFSET, readShipSystemsOther),
	"Combat Audio": (COMBAT_AUDIO_OFFSET, readCombatAudio),
}


def ovl(ovl_path):
	f = File.DatabaseFile(ovl_path)
	f.setOffsetBase(DATA_SEGMENT_OFFSET)

	sections = [
		"Bridge Items",
		"Engineering Readouts",
		"Engineering Screen Buttons",
		"Engineering Delegate Buttons",
		"Engineering Labels",
		"Engineering MRG Graphics",
		"Engineering Tabs",
		"Engineering Rectangles",
		"Ship Systems (Enterprise)",
		"Ship Systems (Other)",
		"Combat Audio",
	]

	data = {}
	for section_name in sections:
		f.setOffset(SECTIONS[section_name][0])
		print(f"#     {f.pos():#x}    {f.offset():#x}    {section_name}")
		data[section_name] = SECTIONS[section_name][1](f)
		print(f"#     {f.pos():#x}    {f.offset():#x}")

	#print(f"#     {f.pos():#x}    {f.offset():#x}")

	#dump(data, open("sttng.ovl.json", "w"), indent="\t", cls=AFU.Utils.Encoder)
	
	return data
