# afinalunity

Tools for extracting files from A Final Unity, the classic Star Trek: The Next Generation game by Spectrum Holobyte.

Information on the different files in A Final Unity is documented in [FILES.md](FILES.md),
and [ASTRO.md](ASTRO.md) contains information specifically on the astrogation files.

## Image Files

The `afu_to_png.py` application converts `.spr` and `.spt` sprites, `.rm` and `.scr` backgrounds, `.fon` fonts, and `.mrg` menus to PNG.
However, not all of those files are currently supported. It will also export images from `computer.db`.

The application requires the [Pillow](http://python-pillow.github.io) module to be installed.

If the standard palette file `standard.pal` is not in the same directory as the image
file being converted, its location must be provided using the `--palette` argument.
For example:
```sh
python3 afu_to_png.py transp.rm --palette other/directory/standard.pal
```
which will output the transporter room scene as `transp.rm.png`.

To convert a sprite or font file you must also provide a `.rm` or `.scr`
background image upon which they would be drawn, using the `--background` argument.
For example:
```sh
python3 afu_to_png.py brdgpica.spr --background bridge.rm
```
will output 31 pngs representing the frames making up the Picard bridge sprite.
Another example:
```sh
python3 afu_to_png.py font2.fon --background bridge.rm
```
will output a png for each character in font number 2.

Finally, you can export all the images within `computer.db`, provided that `compupnl.ast` is in the same
directory or provided via the `--background` argument. For example:
```sh
python3 afu_to_png.py computer.db
```
will output a png for all 49 images used to illustrate various computer entries.


## Audio Files

The `.rac` `.vac` and `.mac` files contain audio.
To convert these into .wav files you will first require [sox](http://sox.sourceforge.net) to be installed
and in PATH.
Then run `afu_to_wav.py` with the path to the audio file as the first and only argument.
For example:
```sh
python3 afu_to_wav.py redalert.mac
```
will output `readalert.wav`.


### Finding Voice Files

There are a lot of `.vac` voice files, and finding the one you want can be time consuming.
The subtitles for what the voice says are mostly contained within the `.bst` object and world files,
and there's a utility to output them all to a file.

Run `afu_subtitles.py` with the path to a directory containing all the `.vac` and `.bst` files as the first argument.
It will output `subtitles.json`, which maps `.vac` filenames to subtitles of what the voice says.

It's not perfect yet, but the vast majority are correct.


## Database Files

The `.db` files are databases.
Specifically, `computer.db` contains the data available on the operations panel,
while `astro.db` and `astromap.db` contain data on the sectors, systems, stations, etc.

To convert these into `.json` files, run `afu_to_json.py` with the path to the database file as the first and only argument.
For example:
```sh
python3 afu_to_json.py astro.db
```
will output `astro.db.json`.


## Thanks

A lot of information required for writing this came from
the work of [fuzzie](https://github.com/fuzzie/unity).
