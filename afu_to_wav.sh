input_name=${1}

# This works for .mac and .vac files.
# The .rac files are stereo, and sox (currently) refuses to deal with 2 channels.
# Instead, you must first pass it through stereo2mono

sox -N -t ima -r 22050 ${input_name} ${input_name}.wav
