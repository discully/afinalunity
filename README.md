# afinalunity

Tools for extracting files from A Final Unity, the classic Star Trek: The Next Generation game by Spectrum Holobyte.

Information on the different files in A Final Unity is documented in [FILES.md](FILES.md),
and [ASTRO.md](ASTRO.md) contains information specifically on the astrogation files.

The `AFU` directory contains the python module, and the various `afu_*.py` files are applications
which perform various tasks:
 * afu_to_png - Exports `.png` images
 * afu_to_json - Exports information as `.json` files
 * afu_to_wav - Converts audio files to `.wav`
 * afu_astro - Combines `astro.db` with either a `SAVEGAME` file or `ast_stat.dat` to produce a `.json` with additional information about the game space
 * afu_scan_all - Edits a `SAVEGAME` file to make all star systems visible and scanned
 * afu_subtitles - Outputs a file containing subtitles for what is said in voice audio files
 * afu_ojects - Identifies the name of the object in a file, or searches for object files which match a name

 More details on each of those applications is provided below.

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

The `.rac` `.vac` and `.mac` files contain audio. The `afu_to_wav.py` applications converst them to `.wav`.

The application requires the [audioop-lts](https://github.com/AbstractUmbra/audioop) module to be installed.

Then run `afu_to_wav.py` with the path(s) to one or more audio file as the arguments.
For example:
```sh
python3 afu_to_wav.py redalert.mac
```
will output `readalert.mac.wav`.


### Finding Voice Files

There are a lot of `.vac` voice files, and finding the one you want can be time consuming.
The subtitles for what the voice says are mostly contained within the `.bst` object and world files,
and there's a utility to output them all to a file.

Run `afu_subtitles.py` with the path to a directory containing all the `.vac` and `.bst` files as the first argument.
```sh
python3 afu_subtitles.py path/to/bst_and_vac
```
It will output `subtitles.json`, which maps `.vac` filenames to subtitles of what the voice says.

It's not perfect yet, but the vast majority are correct.


## Video Files

The `.fvf` files contain the cutscene videos. 

Support is still in active development.
Note that `labarriv.fvf` does not currently work.
Whilst the other files do run, I haven't verified that they do so correctly.
Hence, video support is still in development.

The `afu_to_json.py` application will output a `.json` file describing a video file's structure,
and the `afu_to_wav.py` applciation will output a `.wav` file with the video's audio in it.
The end goal will be to convert the entire video, but that is a work in progress.


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


## Object Files

The `.bst` files are objects representing characters, items, events, etc., but there are over 2500.
To find and idenitfy the right `.bst` file you can use the `afu_objects.py` utility.

### Identifying Object Files
To identify a given `.bst` file, run `afu_object.py` with the path to the file as the first and only argument.
For example:
```sh
python3 afu_objects.py path/to/o_5f0105.bst
```
will output:
```sh
o_5f0105.bst    'Admiral Williams'          {'id': 5, 'screen': 1, 'world': 95, 'unused': 0}
```

### Searching Object Files
To find `.bst` files with a given name, run `afu_object.py` with the path to the directory containing object files and a search term.
For example:
```sh
python afu_object.py path/do/bst_directory --name admiral
```
will output:
```sh
o_020b0f.bst    'Admiral Brodnack'          {'id': 15, 'screen': 11, 'world': 2, 'unused': 0}
o_060402.bst    'Admiral Brodnack'          {'id': 2, 'screen': 4, 'world': 6, 'unused': 0}
o_5f0105.bst    'Admiral Williams'          {'id': 5, 'screen': 1, 'world': 95, 'unused': 0}
o_5f0106.bst    'Admiral Reddreck'          {'id': 6, 'screen': 1, 'world': 95, 'unused': 0}
```
The `--name` search term is case insensitive, and will match any object which contains that text in its name.

## SAVEGAME Files

The SAVEGAME files are found in the install directory.
SAVEGAME.0 is the default save for starting the game.
Those numbered 1-9 are the slots you can save progress in.
There is very early support for SAVEGAME files in afu_to_json.py.

For example:
```sh
python3 afu_to_json.py SAVEGAME.6
```
will output `SAVEGAME.6.json`.

It will export some information, but what's there isn't very complete or necessarily correct.

### Investigating Star Systems

Many of the star systems are invisible in astrogation or are unscanned until the Enterprise travels
to those systems, so you can't see what planets/moons they contain without doing a lot of travelling!
The `afu_scan_all.py` application will edit a SAVEGAME file so that all systems are visible and scanned.

For example:
```sh
python3 afu_scan_all.py SAVEGAME/SAVEGAME.5
```
will make all systems in `SAVEGAME.5` available to the player next time it's loaded.

## Astrogation

The primary information about the in-game space is stored in `astro.db`, but that doesn't contain everything
you might want to know. Some information is stored as state in a `SAVEGAME` file, or ast_stat.dat if you
want the state at the start of the game. The rest of the information is generated at run-time.

The `afu_astro.py` application will allow you to export all of this information to one `.json` file. You
need to provide it the path to `astro.db` along with either a `SAVEGAME` file or `ast_stat.dat`.

For example:
```sh
python3 afu_astro.py astro.db SAVEGAME/SAVEGAME.3
```
or:
```sh
python3 afu_astro.py astro.db ast_stat.dat
```

The resulting `astro.json` file is relatively large. So you can also filter it down by specifying
the name of what you'd like to export:
```sh
python3 afu_astro.py astro.db ast_stat.dat --name "Steger Delta"
```


## Thanks

A lot of information required for writing this came from
the work of [fuzzie](https://github.com/fuzzie/unity).

I got started with video files from [Kostya's wiki description](https://wiki.multimedia.cx/index.php/FVF).
