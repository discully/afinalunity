import audioop
from wave import open as wave_open
from io import BytesIO


_FILE_SPECS = {
	".mac": {
		"type": "adpcm",
		"channels": 1,
		"width": 2,
		"framerate": 22050,
	},
	".vac": {
		"type": "adpcm",
		"channels": 1,
		"width": 2,
		"framerate": 22050,
	},
	".rac": {
		"type": "adpcm",
		"channels": 2,
		"width": 2,
		"framerate": 22050,
	},
}


def _swapNibbles(b):
	return (0xf0 & (b << 4)) | (0x0f & (b >> 4))


def toWav(audio_data, spec):
	if spec["type"] == "adpcm":
		adpcm = bytes([ _swapNibbles(b) for b in audio_data ])

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
	else:
		lin = audio_data
	
	f = BytesIO()
	wav = wave_open(f, "wb")
	wav.setnchannels(spec["channels"])
	wav.setsampwidth(spec["width"])
	wav.setframerate(spec["framerate"])
	wav.writeframes(lin)
	f.seek(0)
	spec["file"] = f

	return spec


def audio(file_path):
	spec = _FILE_SPECS[file_path.suffix].copy()
	spec["src"] = str(file_path.name)
	adpcm = open(file_path, "rb").read()
	return toWav(adpcm, spec)
