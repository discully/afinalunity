from argparse import ArgumentParser
from pathlib import Path
import AFU


def _audioToWav(input_file_path, output_dir):
	data = AFU.audio(input_file_path)

	output_file_path = output_dir.joinpath(input_file_path.name + ".wav")
	with open(output_file_path, "wb") as f:
		f.write(data["file"].getbuffer())


def _videoToWav(input_file_path, output_dir):
	video = AFU.Video.fvf(input_file_path)

	audio = []
	for block in video["blocks"]:
		for frame in block["frames"]:
			if "audio" in frame:
				audio += frame["audio"]
	audio = bytes(audio)

	spec = {
		"src": str(input_file_path.name),
		"type": "lin",
		"channels": video["audio_header"]["n_channels"],
		"width": video["audio_header"]["bits_per_sample"] // 8,
		"framerate": video["audio_header"]["sample_rate"],
	}
	data = AFU.Audio.toWav(audio, spec)

	output_file_path = output_dir.joinpath(input_file_path.name + ".wav")
	with open(output_file_path, "wb") as f:
		f.write(data["file"].getbuffer())


def _sprToWav(input_file_path, output_dir):
	sprite = AFU.Sprite.sprite(input_file_path, input_file_path.with_name("standard.pal"), input_file_path.with_name("standard.pal"))
	
	for block in sprite["blocks"]:
		if block["name"] != "DIGI": continue

		spec = AFU.Audio._FILE_SPECS[".mac"].copy()
		spec["src"] = f"{input_file_path.name}.{block["offset"]}"
		data = AFU.Audio.toWav(block["audio"], spec)

		output_file_path = output_dir.joinpath(f"{input_file_path.name}.{block['offset']}.wav")
		with open(output_file_path, "wb") as f:
			f.write(data["file"].getbuffer())


def main():

	parser = ArgumentParser(description="Converts '.mac', '.rac' and '.vac' audio files to '.wav'. Or extracts audio from '.fvf' video files and '.spr' sprite files.")
	parser.add_argument("files", type=Path, help="Path(s) to the input file(s)", nargs="+")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place wav files in", default=".")
	args = parser.parse_args()

	if not args.output_dir.is_dir():
		print("Output directory path is not a valid directory:", args.output_dir)
		return

	for input_file_path in args.files:

		if not input_file_path.is_file():
			print("{} is not a file".format(input_file_path.name))
			continue

		print(input_file_path.name)

		if input_file_path.suffix in [".mac", ".rac", ".vac"]:
			_audioToWav(input_file_path, args.output_dir)
		elif input_file_path.suffix == ".fvf":
			_videoToWav(input_file_path, args.output_dir)
		elif input_file_path.suffix == ".spr":
			_sprToWav(input_file_path, args.output_dir)
		else:
			print("{} is not a supported file type ('.mac', '.rac', '.vac', '.fvf', '.spr')".format(input_file_path.name))
			continue



if __name__ == "__main__":
	main()
