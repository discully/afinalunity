# afinalunity

Tools for extracting files from A Final Unity, the classic Star Trek: The Next Generation game by Spectrum Holobyte.

## Image Files

The `afu_to_png.py` application converts `.spr` and `.spt` sprites, `.rm` and `.scr` backgrounds, and `.fon` fonts to PNG.
However, not all of those files are currently supported.

The application requires the [PyPNG](https://pythonhosted.org/pypng/) module to be installed.

If the standard palette file `standard.pal` is not in the same directory as the image
file being converted, its location must be provided using the `--palette` argument.
For example:
```sh
python afu_to_png.py transp.rm --palette other/directory/standard.pal
```
which will output the transporter room scene as `transp.rm.png`.

To convert a sprite or font file you must also provide a `.rm` or `.scr`
background image upon which they would be drawn, using the `--background` argument.
For example:
```sh
python afu_to_png.py brdgpica.spr --background bridge.rm
```
will output 31 pngs representing the frames making up the Picard bridge sprite.
Another example:
```sh
python afu_to_png.py font2.fon --background bridge.rm
```
will output a png for each character in font number 2.


## Audio Files

The `.rac` `.vac` and `.mac` files contain audio.
To convert these into .wav files you will first require [sox](http://sox.sourceforge.net) to be installed
and in PATH.
Then run `afu_to_wav.py` with the path to the audio file as the first and only argument.
For example:
```sh
python afu_to_wav.py redalert.mac
```
will output `readalert.wav`.

## Thanks

A lot of information required for writing this came from
the work of [fuzzie](https://github.com/fuzzie/unity).

