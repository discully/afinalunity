from collections import deque
from struct import pack
from pathlib import Path
from argparse import ArgumentParser
from AFU import Astro,File,SaveGame



class EditFile (File.File):
	def __init__(self, file_name):
		self.file_name = str(file_name)
		self.f = open(self.file_name, "r+b")
		self.start = self.pos()
		self.bits = deque()
		self._size = None
	
	def replaceLastUInt16(self, x):
		self.setPosition(self.pos() - 2)
		b = pack('H', x)
		self.f.write(b)



def main():
	
	parser = ArgumentParser(
		description="Edits a SAVEGAME file so that all the star systems are visible and have been scanned, so you can explore them in the Astrogation menu."
		)
	parser.add_argument("savegame", type=Path, help="Path to savegame file")
	args = parser.parse_args()

	f = EditFile(args.savegame)

	header = f.readString()
	if not header == "STTNG_GAME":
		raise ValueError("File is not a valid save game")

	blocks = SaveGame.readBlockHeaders(f)
	block_aststat = blocks[1]

	# The information on which systems are visible/scanned is stored
	# at 0x2e2 bytes into the ast_stat block.
	f.setPosition(block_aststat["data_offset"] + 0x2e2)

	sector_end = []
	for i in range(Astro.N_SECTORS):
		sector_end.append(f.readUInt16())

	object_id = 0
	for end in sector_end:
		while object_id < end:
			state = f.readUInt16()
			state_visible = (state & 0b00000001) != 0
			state_scanned = (state & 0b00001000) != 0
			if not (state_visible and state_scanned):
				state |= 0b00001001
				f.replaceLastUInt16(state)
			object_id += 1



if __name__ == "__main__":
    main()
