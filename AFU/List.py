from AFU import File


def lst(file_path):
	f = File.File(file_path)
	n = f.readUInt32()
	entries = []
	while not f.eof():
		entries.append(f.readString())
	assert(n == len(entries))
	return entries
