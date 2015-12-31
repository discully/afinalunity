import os
import sys
import pathlib
import subprocess

# This works for .mac and .vac files.
# The .rac files are stereo, and sox (currently) refuses to deal with 2 channels.
# Instead, you must first pass it through afu_stereo_to_mono.py



def _toWav(input_file_path, output_file_name = None):
	if( output_file_name == None ):
		output_file_name = input_file_path.with_suffix(".wav").name
	subprocess.call(["sox", "-N", "-t", "ima", "-r", "22050", str(input_file_path), str(output_file_name)])
	return output_file_name



def _toStereo(left_file_path, right_file_path, stereo_file_path):
	subprocess.call(["sox", "-M", str(left_file_path), str(right_file_path), str(stereo_file_path)])



def _splitStereo(input_file_path):
	input_file = open(str(input_file_path), "rb")
	output_file_names = (
		input_file_path.with_suffix(".L.rac"),
		input_file_path.with_suffix(".R.rac")
		)
	output_files = (
		open(str(output_file_names[0]), "wb"),
		open(str(output_file_names[1]), "wb")
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

	return output_file_names



def main():

	supported_extensions = [".mac", ".rac", ".vac"]

	if( len(sys.argv) != 2 ):
		print("[USAGE]", __file__, "<audio file path>")
		print("")
		print("Converts", supported_extensions, "audio files to .wav format.")
		print("Expects sox to be installed and in PATH.")
		return

	input_file_path = pathlib.PurePath(sys.argv[1])
	output_file_name = input_file_path.with_suffix(".wav").name

	if( input_file_path.suffix not in supported_extensions ):
		print("Input file", input_file_path.name, "is not one of the supported types:", supported_extensions)
		return

	if( input_file_path.suffix == ".rac" ):
		rac_l,rac_r = _splitStereo(input_file_path)
		wav_l = _toWav(rac_l)
		wav_r = _toWav(rac_r)
		_toStereo(wav_l, wav_r, output_file_name)
		os.remove(str(rac_l))
		os.remove(str(rac_r))
		os.remove(str(wav_l))
		os.remove(str(wav_r))
	else:
		_toWav(input_file_path, output_file_name)

	print("Converted from:", input_file_path)
	print("Converted to:", output_file_name)



if __name__ == "__main__":
	main()
