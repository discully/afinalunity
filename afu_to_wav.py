from argparse import ArgumentParser
from pathlib import Path
import audioop
from audioop import adpcm2lin
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


def _toWav(input_file_path, output_dir):
	spec = _FILE_SPECS[input_file_path.suffix]
	output_file_path = output_dir.joinpath(input_file_path.name + ".wav")

	adpcm = open(input_file_path, "rb").read()
	adpcm = bytes([ _swapNibbles(b) for b in adpcm ])

	if spec["channels"] == 2:
		adpcm_l = bytes([b for b in adpcm[::2]])
		adpcm_r = bytes([b for b in adpcm[1::2]])
		lin_l = adpcm2lin(adpcm_l, spec["width"], None)[0]
		lin_r = adpcm2lin(adpcm_r, spec["width"], None)[0]
		lin_l = audioop.tostereo(lin_l, spec["width"], 1, 0)
		lin_r = audioop.tostereo(lin_r, spec["width"], 0, 1)
		lin = audioop.add(lin_l, lin_r, spec["width"])
	else:
		lin = adpcm2lin(adpcm, spec["width"], None)[0]

	wav = wave_open(str(output_file_path), "wb")
	wav.setnchannels(spec["channels"])
	wav.setsampwidth(spec["width"])
	wav.setframerate(22050)
	wav.writeframes(lin)
	
	return output_file_path


def main():

	parser = ArgumentParser(description="Converts '.mac', '.rac' and '.vac' audio files to '.wav'.")
	parser.add_argument("audio_file", type=Path, help="Path to the audio file(s)", nargs="+")
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place wav files in", default=".")
	args = parser.parse_args()

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

		output_file_path = _toWav(input_file_path, args.output_dir)

		print("{} -> {}".format(input_file_path.name, output_file_path.name))


if __name__ == "__main__":
	main()
