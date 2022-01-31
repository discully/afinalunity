from pathlib import Path
from AFU.File import File
from AFU import Astro, Computer

# [offset      ][block][size][contents             ]
#  0x0    0      Header 14
#  0xf    15     GNT    544
#                             0x13   compstat
#                             0x1a0  ?
#  0x233  563    GNT    9600         ast_stat
#  0x27b7 10167  GNT    31
#  0x27da 10202  GNT    8
#  0x27e6 10214  GNT    2177
#  0x306b 12395  GNT    5
#  0x3074 12404  GNT    5799
#  0x471f 18207  ONT    2767
#  0x51f2 20978  ONT    81


def fpos(f, s=""):
	print(f.pos(), hex(f.pos()), s)


def readBlockAststat(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	data["astro_state"] = Astro.readAstroState(f)
	assert(f.pos() == block["end_offset"])
	return data


def readBlockCompstat(f, block):
	data = {}
	f.setPosition(block["data_offset"])
	data["computer_state"] = Computer.readCompstat(f)
	assert(f.readString() == "COMPSTAT")
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(3)])
	#print([f.readUInt8() for i in range(4)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(20)])
	#print([f.readUInt8() for i in range(8)])
	#print([f.readUInt8() for i in range(8)])
	#fpos(f)
	#assert(f.pos() == block["end_offset"])
	return data


def readBlockHeader(f):
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
		blocks.append(readBlockHeader(f))
		f.setPosition(blocks[-1]["end_offset"])
	return blocks


def savegame(input_path):
	f = File(input_path)
	data = {}

	# Header
	assert(f.readString() == "STTNG_GAME")

	blocks = readBlockHeaders(f)
	assert(len(blocks) == 9)

	#print(blocks[0])
	data |= readBlockCompstat(f, blocks[0])
	#print(blocks[1])
	data |= readBlockAststat(f, blocks[1])
	#print(blocks[2])
	#print(blocks[3])
	#print(blocks[4])
	#print(blocks[5])
	#print(blocks[6])
	#print(blocks[7])
	#print(blocks[8])

	return data
