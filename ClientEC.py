import socket, sys, base64
def fromCheck():
	#read in and check MailFrom
	#send back address
	line = sys.stdin.readline()
	done = 0
	if not line:
		sys.exit()
	while(done == 0):
		cursor = localpart(line, 0)
		if(cursor == len(line) or line[cursor] != '@'):
			print"Error in localpart"
			print"From:"
			line = sys.stdin.readline()
			if not line:
				sys.exit()
		else:
			cursor = domain(line, cursor)
			if(cursor != (len(line)-1)):
				print"Error in domain"
				print"From:"
				line = sys.stdin.readline()
				if not line:
					sys.exit()
			else:
				done = 1
	return line.rstrip()
def rcptCheck():
	#read in recipients
	#send list of recipients back
	line = sys.stdin.readline()
	handled = 0
	addresses = []
	starter = 0
	cursor = 0
	if not line:
		sys.exit()
	while(handled == 0):
		if(cursor < len(line)):
			cursor = localpart(line, starter)
		if(cursor < len(line) and line[cursor] == '@'):
			cursor = domain(line, cursor)
			addresses.append(line[starter:cursor])
			if(cursor < len(line) and line[cursor] == ','):
				starter = whitespace(line, cursor+1)
			elif(cursor == len(line)-1):
				handled = 1
				i = 0
				while(i < len(addresses)):
					x = "RCPT TO: <"
					x += addresses[i]
					x += ">"
					addresses[i] = x
					i += 1
				return addresses
		else:
			print"Error in recipient address"
			print"To:"
			line = sys.stdin.readline()
			if not line:
				sys.exit()
			del addresses[:]
			addressess = []
			cursor = 0
			starter = 0
def whitespace(string, cursor):
	while(' ' == string[cursor]):
		cursor = cursor + 1		
	return cursor
def dataCompilation():
	#puts together subject and message
	line = sys.stdin.readline()
	d = "\n"
	if not line:
		sys.exit()
	while(line != ".\n"):
		d = d + line
		line = sys.stdin.readline()
		if not line:
			sys.exit()
	#d += ".\n" relic of the past lol
	d += '--tcntoun\n'
	return d
def localpart(string, cursor):
		if(checkascii(string[cursor]) == 1):
			cursor = cursor + 1
			while(cursor < len(string) and checkascii(string[cursor]) != 0):
				cursor = cursor + 1
			return cursor
		else:
			return -1
def checkascii(string):
	a = ord(string)
	list = [32, 34, 60, 62, 40, 41, 91, 93, 92, 46, 44, 59, 58, 38, 64]
	if(a in list):
		return 0
	else:
		return 1
def domain(string, c):
	if(string[c].isalpha):
		c = c + 1
		e = element(string , c)
		return e
	else:
		return -1
def element(string, c):
		while(string[c].isalpha() or string[c].isdigit()):
			c = c + 1
		if(string[c] == '.'):
			c = c + 1
			c = domain(string, c)
		return c
def createBody(mf, rcs, mess):
	#compiles the whole body
	complete = "From: "
	beg = mf.find('<')
	end = mf.find('>')
	complete = complete + mf[beg+1:end] + "\n"
	i = 0
	while(i < len(rcs)):
		beg = rcs[i].find('<')
		end = rcs[i].find('>')
		thisOne = rcs[i][beg+1:end]
		complete = complete + "To: " + thisOne + "\n"
		i +=1
	complete += mess
	return complete
def encodedAttach(string):
	x = 'Content-Transfer-Encoding: base64\nContent-Type: image/jpeg\n\n'
	string = string.rstrip()
	with open(string, 'rb') as f:
		fil = f.read()
		x += base64.b64encode(fil)
	x+='\n--tcntoun--\n'
	x += '.\n'	
	return x

if __name__ == "__main__":
	host = sys.argv[1]
	port = int(sys.argv[2])
	print"From:"
	mailFrom = "MAIL FROM: <"
	f = fromCheck()
	mailFrom = mailFrom + f + ">"
	#from should now be in <> format
	print"To:"
	rcpts = rcptCheck()
	#list of recipients in <> format
	print"Subject:"
	line = sys.stdin.readline()
	if not line:
		sys.exit()
	message = "Subject: "
	message = message + line
	message = message + 'MIME-Version: 1.0\nContent-Type: multipart/mixed; boundary = tcntoun\n'
	message = message + '\n--tcntoun\nContent-Transfer-Encoding: quoted-printable\nContent-Type: text/plain\n'
	print"Message:"
	md = dataCompilation()
	message = message + md
	print"Attachment: "
	line = sys.stdin.readline()
	attach = encodedAttach(line)
	message = message + attach
	s = socket.socket()
	#host = socket.gethostname()
	try:
		s.connect((host, port))
	except socket.error:
		print"Socket connection failed"
		sys.exit()
	incoming = s.recv(4096)
	if('220' not in incoming):
		print"Could not connect"
		try:
			s.send("QUIT")
		except socket.error:
			print"Socket connection failed"
		s.close()
		sys.exit()
	try:
		s.send("HELO " + host)
	except socket.error:
		print"Socket broke"
		sys.exit()
	incoming = s.recv(4096)
	if('250' not in incoming):
		print"Could not connect"
		try:
			s.send("QUIT")
		except socket.error:
			print"Socket connection failed"
		s.close()
		sys.exit()
	try:
		s.send(mailFrom)
	except socket.error:
		print"socket broke"
		sys.exit()
	incoming = s.recv(4096)
	if('250' not in incoming):
		print"Error in from address"
		try:
			s.send("QUIT")
		except socket.error:
			print"Socket connection failed"
		s.close()
		sys.exit()
	i = 0
	while(i < len(rcpts)):
		lis = rcpts[i]
		i +=1
		try:
			s.send(lis)
		except socket.error:
			print"Socket broke"
			sys.exit()
		incoming = s.recv(4096)
		if('250' not in incoming):
			print"Error in recipient address"
			try:
				s.send("QUIT")
			except socket.error:
				print"Socket connection failed"
				s.close()
				sys.exit()
	try:
		s.send("DATA\n")
	except socket.error:
		print"socket broke"
		sys.exit()
	incoming = s.recv(4096)
	if('354' not in incoming):
		print"Error when trying to send data"
		try:
			s.send("QUIT")
		except socket.error:
			print"Socket connection failed"
		s.close()
		sys.exit()
	data = createBody(mailFrom, rcpts, message)
	try:
		s.send(data)
	except socket.error:
		print"socket broke"
		sys.exit()
	incoming = s.recv(4096)
	if('250' not in incoming):
		print"Data not sent"
		try:
			s.send("QUIT")
		except socket.error:
			print"Socket connection failed"
		s.close()
		sys.exit()
	try:
		s.send("QUIT\n")
	except socket.error:
		print"connection interrupted before close"
		sys.exit()
	s.close()
	sys.exit()
