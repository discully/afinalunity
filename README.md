# afinalunity

Tools for extracting files from A Final Unity, the classic Start Trek: The Next Generation game by Spectrum Holobyte.

## Audio Files

The `.rac` `.vac` and `.mac` files contain audio.

To convert these into .wav files you will first require sox to be installed.
Then run `afu_to_wav.sh` with the path to the audio file as the first and only argument.

For example:
```sh
afu_to_wav.sh redalert.mac
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

