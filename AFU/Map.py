from AFU.File import File


def icon(file_path):
	f = File(file_path)
	icons = {}
	while f.peek() != 0x1a:
		s = f.readLine()
		if not s.startswith('#'):
			id = int(s[:6].replace('o', '0'), 16)
			fname = s[7:19]
			comment = s.split('#')[1].strip()
			if id != 0:
				icons[id] = {
					"file": fname,
					"comment": comment,
				}
	return icons


def movie(file_path):
	f = File(file_path)
	movies = {}
	while f.peek() != 0x1a:
		s = f.readLine()
		if s and not s.startswith('#'):
			id = int(s[:4].strip())
			fname = s[4:18].strip()
			title = s[18:].strip()
			movies[id] = {
				"file": fname,
				"title": title,
			}
	return movies


def phaser(file_path):
	f = File(file_path)
	ids = []
	comment = ""
	while f.peek() != 0x1a:
		s = f.readLine()
		if s:
			if s.startswith('#'):
				comment += s[1:].strip()
			else:
				ids.append(int(s, 16))
	return {
		"comment": comment,
		"ids": ids,
	}
