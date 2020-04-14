from AFU import File


def terminal(file_path):
	f = File.File(file_path)
	records = []
	
	while not f.eof():
		if f.peek() == 0x1A:
			break
		
		line = f.readLine()
		
		if len(line) == 0 or line.startswith("#"):
			continue
		
		header = line.split()
		record = {
			"id": int(header[0]),
			"x": int(header[1]),
			"y": int(header[2]),
			"hx": int(header[3]),
			"hy": int(header[4]),
			"font": int(header[5]),
		}
		
		text = ""
		if len(header) > 6:
			text = " ".join(header[6:])
		else:
			text = f.readLine().lstrip("@")
		
		while not text.endswith("@"):
			text += "\n" + f.readLine()
		
		record["text"] = text.strip("@")
		records.append(record)
	return records
