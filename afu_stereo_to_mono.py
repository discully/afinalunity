"""
The .rac audio files are IMA ADPCM, like the .mac and .vac audio files.
However, unlike .vac and .mac which are mono, the .rac files are stereo.
Currently, sox will not deal with stero IMA files.
This application strips the two channels into separate files.
"""

import sys
import os.path



def usage():
	print("[USAGE]",__file__,"<file.rac>")
	return 1



def main():
	if( len(sys.argv) != 2 ):
		return usage()
	
	input_file_path = sys.argv[1]
	if( os.path.splitext(input_file_path)[1] != ".rac" ):
		raise ValueError("Invalid input file path. Only .rac files are supported")
	
	input_file = open(input_file_path, "rb")
	
	file_name = os.path.splitext(os.path.basename(input_file_path))[0]
	
	output_files = (
		open("{0}.L.rac".format(file_name), "wb"),
		open("{0}.R.rac".format(file_name), "wb")
		)
	
	while True:
		b = input_file.read(1)
		if( b == b"" ):
			break
		output_files[0].write(b)
		output_files = (output_files[1], output_files[0])
	
	input_file.close()
	output_files[0].close()
	output_files[1].close()
	


if __name__ == "__main__":
	main()
