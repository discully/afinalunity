from argparse import ArgumentParser
from pathlib import Path
from shutil import which as shutil_which
from subprocess import call as subproc_call


# This works for .mac and .rac and .vac files.
# The .rac files are stereo, and sox (currently) refuses to deal with 2 channels.
# Instead, we split the .rac into left/right files, convert them both to wavs,
# then merge the two wavs into a final stereo file.


def _toWav(input_file_path, output_dir):
	ext = "{}.wav".format(input_file_path.suffix)
	output_file_path = output_dir.joinpath(input_file_path).with_suffix(ext)
	subproc_call(["sox", "-N", "-t", "ima", "-r", "22050", str(input_file_path), str(output_file_path)])
	return output_file_path


def _toStereoWav(input_file_path, output_dir):
	ext = "{}.wav".format(input_file_path.suffix)
	output_file_path = output_dir.joinpath(input_file_path).with_suffix(ext)
	rac_l,rac_r = _splitStereo(input_file_path, output_dir)
	wav_l = _toWav(rac_l, output_dir)
	wav_r = _toWav(rac_r, output_dir)
	_toStereo(wav_l, wav_r, output_file_path)
	rac_l.unlink()
	rac_r.unlink()
	wav_l.unlink()
	wav_r.unlink()
	return output_file_path


def _toStereo(left_file_path, right_file_path, stereo_file_path):
	subproc_call(["sox", "-M", str(left_file_path), str(right_file_path), str(stereo_file_path)])


def _splitStereo(input_file_path, output_dir):
	input_file = open(str(input_file_path), "rb")
	output_file_paths = (
		output_dir.joinpath(input_file_path.with_suffix(".L.rac").name),
		output_dir.joinpath(input_file_path.with_suffix(".R.rac").name)
		)
	output_files = (
		open(str(output_file_paths[0]), "wb"),
		open(str(output_file_paths[1]), "wb")
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

	return output_file_paths



def main():

	parser = ArgumentParser(
		description="Converts '.mac', '.rac' and '.vac' audio files to '.wav'.",
		epilog="Application expects sox to be installed and in PATH."
		)
	parser.add_argument("audio_file", type=Path, help="Path to the audio file(s)", nargs="+")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place wav files in", default=".")
	args = parser.parse_args()

	if shutil_which("sox") is None:
		print("Sox is not installed and in PATH.")
		return

	if not args.output_dir.is_dir():
		print("Output directory path is not a valid directory:", args.output_dir)
		return

	for input_file_path in args.audio_file:

		if not input_file_path.is_file():
			print("{} is not a file".format(input_file_path.name))
			continue

		if not input_file_path.suffix in [".mac", ".rac", ".vac"]:
			print("{} is not a supported file type ('.mac', '.rac', '.vac')".format(input_file_path.name))
			continue

		if( input_file_path.suffix == ".rac" ):
			output_file_path = _toStereoWav(input_file_path, args.output_dir)
		else:
			output_file_path = _toWav(input_file_path, args.output_dir)

		print("{} -> {}".format(input_file_path.name, output_file_path.name))



if __name__ == "__main__":
	main()
