from argparse import ArgumentParser
from pathlib import Path
import audioop
import AFU
from wave import open as wave_open


_FILE_SPECS = {
	".mac": {
		"type": "mac",
		"channels": 1,
		"width": 2,
	},
	".vac": {
		"type": "vac",
		"channels": 1,
		"width": 2,
	},
	".rac": {
		"type": "rac",
		"channels": 2,
		"width": 2,
	},
}


def _swapNibbles(b):
	return (0xf0 & (b << 4)) | (0x0f & (b >> 4))


def _audioToWav(input_file_path, output_dir):
	spec = _FILE_SPECS[input_file_path.suffix]
	output_file_path = output_dir.joinpath(input_file_path.name + ".wav")

	adpcm = open(input_file_path, "rb").read()
	adpcm = bytes([ _swapNibbles(b) for b in adpcm ])

	if spec["channels"] == 2:
		adpcm_l = bytes([b for b in adpcm[::2]])
		adpcm_r = bytes([b for b in adpcm[1::2]])
		lin_l = audioop.adpcm2lin(adpcm_l, spec["width"], None)[0]
		lin_r = audioop.adpcm2lin(adpcm_r, spec["width"], None)[0]
		lin_l = audioop.tostereo(lin_l, spec["width"], 1, 0)
		lin_r = audioop.tostereo(lin_r, spec["width"], 0, 1)
		lin = audioop.add(lin_l, lin_r, spec["width"])
	else:
		lin = audioop.adpcm2lin(adpcm, spec["width"], None)[0]

	wav = wave_open(str(output_file_path), "wb")
	wav.setnchannels(spec["channels"])
	wav.setsampwidth(spec["width"])
	wav.setframerate(22050)
	wav.writeframes(lin)
	
	return output_file_path


def _videoToWav(input_file_path, output_dir):
	output_file_path = output_dir.joinpath(input_file_path.name + ".wav")
	video = AFU.Video.fvf(input_file_path)
	audio = []
	for block in video["blocks"]:
		for frame in block["frames"]:
			if "audio" in frame:
				audio += frame["audio"]
	wav = wave_open(str(output_file_path), "wb")
	wav.setnchannels(video["audio_header"]["n_channels"])
	wav.setsampwidth(video["audio_header"]["bits_per_sample"] // 8)
	wav.setframerate(video["audio_header"]["sample_rate"])
	wav.writeframes(bytes(audio))

	return output_file_path


def _sprToWav(input_file_path, output_dir):
	sprite = AFU.Sprite.sprite(input_file_path, input_file_path.with_name("standard.pal"), input_file_path.with_name("standard.pal"))
	spec = _FILE_SPECS[".mac"]
	for block in sprite["blocks"]:
		if block["name"] == "DIGI":
			output_file_path = output_dir.joinpath(f"{input_file_path.name}.{block['offset']}.wav")
			wav = wave_open(str(output_file_path), "wb")
			wav.setnchannels(spec["channels"])
			wav.setsampwidth(spec["width"])
			wav.setframerate(22050)
			adpcm = block["audio"]
			adpcm = bytes([ _swapNibbles(b) for b in adpcm ])
			lin = audioop.adpcm2lin(adpcm, spec["width"], None)[0]
			wav.writeframes(lin)
			print("    -> {}".format(output_file_path.name))



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
			output_file_path = _audioToWav(input_file_path, args.output_dir)
			print("    -> {}".format(output_file_path.name))
		elif input_file_path.suffix == ".fvf":
			output_file_path = _videoToWav(input_file_path, args.output_dir)
			print("    -> {}".format(output_file_path.name))
		elif input_file_path.suffix == ".spr":
			_sprToWav(input_file_path, args.output_dir)
		else:
			print("{} is not a supported file type ('.mac', '.rac', '.vac', '.fvf', '.spr')".format(input_file_path.name))
			continue

		#print("{} -> {}".format(input_file_path.name, output_file_path.name))



if __name__ == "__main__":
	main()
