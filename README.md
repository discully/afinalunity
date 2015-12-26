# afinalunity

Tools for extracting files from A Final Unity, the classic Start Trek: The Next Generation game by Spectrum Holobyte.

## Image Files

The `afu_to_png.py` application converts sprite, background and font files to png.
However, not all of those files in A Final Unity are currently supported.

The application requires the [PIL module](https://pypi.python.org/pypi/PIL).

Before converting any images the `afinalunity` library needs to know where the standard
colour palette `standard.pal` is.
This is achieved by setting its location in an environment variable:
```sh
export STTNG_PAL=/path/to/standard.pal
```

To convert a `.spr` or `.spt` sprite file you must provide both the sprite file
and a `.rm` or `.scr` background image upon which the sprite would be drawn.
For example:
```sh
python afu_to_png.py brdgpica.spr bridge.rm
```
will output 31 pngs representing the frames making up the Picard bridge sprite.

To convert a `.rm` or `.scr` background image requires just the image path itself.
For example:
```sh
python afu_to_png.ps transp.rm
```
will output `transp.rm.png`.

To convert a `.fon` font file also requires an additional `.rm` or `.scr` background file.
For example:
```sh
python afu_to_png.py brdgpica.spr bridge.rm
```
will output a png for each character in the font.

## Audio Files

The `.rac` `.vac` and `.mac` files contain audio.
To convert these into .wav files you will first require sox to be installed.
Then run `afu_to_wav.sh` with the path to the audio file as the first and only argument.
For example:
```sh
./afu_to_wav.sh redalert.mac
```
will output `readalert.mac.wav`.

Before converting `.rac` files which, unlike `.vac` and `.mac` files, are stereo audio
you must first separate out the two channels and convert just one of them.
The `afu_stereo_to_mono.py` application will do this.
For example:
```sh
python afu_stereo_to_mono.py beamout.rac
```
will output `beamout.L.rac` and `beamout.R.rac`.
Either one of the output files can then be converted to wav using `afu_to_wav.sh`.

## Thanks

A lot of information required for writing this came from
the work of [fuzzie](https://github.com/fuzzie/unity).

