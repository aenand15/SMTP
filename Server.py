import sys, socket
def hi(string):
	#this series of methods is called in main after server says hello
	#parses helo message to see if correct
	if('HELO' in string[0:4]):
		c = 5
		c = domain(string, c)
		if(c != len(string)-1):
			return 1
		else:
			return 0
def domain(string, c):
	if(string[c].isalpha):
		c = c + 1
		e = element(string , c)
		return e
	else:
		return -1
def element(string, c):
	while((c < len(string)) and (string[c].isalpha() or string[c].isdigit())):
		c = c + 1
	if((c < len(string)) and string[c] == '.'):
		c = c + 1
		c = domain(string, c)
	return c

class parser():
	#parser from HW2 looking for errors
	def rcpt(self, string):
		if("RCPT" in string[0:4]):
			cursor = 5
			cursor = self.whitespace(string, cursor)
			return cursor
		else:
			print("Syntax error: command unrecognized")
			return -1
	def mail(self, string):
		if("MAIL" in string[0:4]): 
			cursor = 5
			cursor = self.whitespace(string, cursor)
			return cursor
		else:
			print("Syntax error: command unrecognized")
			return -1
	def whitespace(self, string, cursor):
		while(' ' == string[cursor] and (cursor < len(string))):
			cursor = cursor + 1
			
		return cursor
	def to(self, string, cursor):
		if("TO:" in string[cursor:(cursor+3)]):
			cursor = cursor + 3
			cursor = self.whitespace(string, cursor)
			return cursor
		else:
			print("Syntax error: command unrecognized")
			return -1
	def fro(self, string, cursor):
		if(cursor+5 < len(string) and "FROM:" in string[cursor:(cursor + 5)]):
			cursor = cursor +5
			cursor = self.whitespace(string, cursor)
			return cursor
		else:
			print("Syntax error: command unrecognized")
			return -1
	def path(self, string, cursor):
		if(cursor < len(string) and '<' == string[cursor]):
			cursor = cursor + 1
			c = self.localpart(string, cursor)
			if(cursor < len(string) and '@' == string[c]):
				c = c + 1
				d = self.domain(string, c)
				if(cursor < len(string) and '>' == string[d]):
					d = d + 1
					return d
				elif(d == -1):
					print("Syntax error in parameters or arguments")
					return -1
				else:
					print("Syntax error in parameters or arguments")
					return -1
			elif(c == -1):
				print("Syntax error in parameters or arguments")
				return -1
			else:
				print("Syntax error in parameters or arguments")
				return -1
		else:
			print("Syntax error in parameters or arguments")
			return -1
	def localpart(self, string, cursor):
		if(self.checkascii(string[cursor]) == 1):
			cursor = cursor + 1
			while(cursor < len(string) and self.checkascii(string[cursor]) != 0):
				cursor = cursor + 1
			return cursor
		else:
			return -1
	def domain(self, string, c):
		if(c < len(string) and string[c].isalpha):
			c = c + 1
			e = self.element(string , c)
			return e
		else:
			return -1
	def checkascii(self, string):
		a = ord(string)
		list = [32, 34, 60, 62, 40, 41, 91, 93, 92, 46, 44, 59, 58, 38, 64]
		if(a in list):
			return 0
		else:
			return 1
	def element(self, string, c):
			while(c < len(string) and (string[c].isalpha() or string[c].isdigit())):
				c = c + 1
			if(c < len(string) and string[c] == '.'):
				c = c + 1
				c = self.domain(string, c)
			return c
def forward(elist, message):
	#finds domains then writes in forward file
	i = 1
	while(i < len(elist)):
		s = elist[i]
		beg = s.find("@")
		end = s.find(">")
		x = s[beg+1:end]
		beg = message.find('From')
		end = message.find('.\n')
		f = open("forward/%s" % (x), "a+")
		f.write((message[beg:end-1] + '\n'))
		f.close
		i += 1
if __name__ == "__main__": 
#establish socket
	s = socket.socket()
	host = socket.gethostname()
	port = int(sys.argv[1])
	try:
		s.bind((host, port))
	except socket.error:
		print"socket broke"
		sys.exit()
	s.listen(5)
	while True:
		#infinte calling of arrival which accepts socket
		#and handles client interaction
		#once socket is closed arrival returns 0 causing
		#this loop to be over and start again forever
		client, addr = s.accept()
		state = 0
		try:
			client.send('220 ' + host)
		except socket.error:
			print"socket broke"
			sys.exit()
		string = client.recv(4096)
		emails = []
		hope = hi(string)
		if(hope == 0):
			client.close()
			continue
		try:
			client.send('250 Hello ' + string[5:len(string)] + ', pleased to meet you')
		except socket.error:
			print"socket broke"
			sys.exit()
		x = parser()
		rec = 0
		line = client.recv(4096)
		if('QUIT' in line):
			print"Message failed to send"
			client.close()
			state = 0
		if(len(line) <2):
			client.close()
			state = -1
		tracker = x.mail(line)
		if(tracker != -1):
			tracker = x.fro(line, tracker)
			if(tracker != -1):
				tracker = x.path(line, tracker)
				if(tracker != -1):
					if(tracker == len(line)):
						beg = line.find('<')
						end = line.find('>')
						emails.append(line[beg:(end+1)])
						state = 1
						try:
							client.send("250 " + emails[0] + '... Sender ok')
						except socket.error:
							print"socket broke"
							sys.exit()
					else:
						print"Syntax error in parameters or arguments"
						client.close()
						continue
				else:
					client.close()
					continue
			else:
				client.close()
				continue
		else:
			client.close()
			continue
		line = client.recv(4096)
		if('QUIT' in line):
			print"Message failed to send"
			client.close()
			state = 0
		if(len(line) <2):
			client.close()
			state = 0
		while(state == 1):
			if("R" in line[0:1]):
				x = parser()
				tracker = x.rcpt(line)
				if(tracker != -1):
					tracker = x.to(line, tracker)
					if(tracker != -1):
						tracker = x.path(line, tracker)
						if(tracker != -1):
							if(tracker == len(line)):
								rec = rec + 1
								beg = line.find('<')
								end = line.find('>')
								emails.append(line[beg:(end)+1])
								canBeData = 1
								try:
									client.send("250 " + emails[rec] + '... Recipient ok')
								except socket.error:
									print"socket broke"
									sys.exit()
							else:
								print"Syntax error in parameters or arguements"
								client.close()
								state = 0
								break
						else:
							client.close()
							state = 0
							break
					else:
						client.close()
						state = 0
						break
				else:
					client.close()
					state = 0
					break
			elif("D" in line[0:1] and canBeData == 1):
				state = 2
				if(line == 'DATA\n'):
					client.send('354 Start mail input; end with <CRLF>.<CRLF>')
					line = client.recv(4096)
					if('QUIT' in line):
						print"Message failed to send"
						client.close()
						state = 0
				else:
					state = 0
					print"Bad data command"
					client.close()
				while(state == 2):
					dataMessage = ""
					if(line.find(".\n") == -1):
						print"Syntax error in parameters or arguements"
						state = 0
						client.close()
					else:
						state = 0
						canBeData = 0
						client.send('250 ok')
						incoming = client.recv(4096)
						if('QUIT' not in incoming):
							print"connection interuppted before end"
							client.close()
						else:
							forward(emails, line)
							client.close()
			else:
				print"Bad sequence of commands"
				client.close()
				continue
				state = 0
			if(state != 0):
				line = client.recv(4096)
				if('QUIT' in line):
					print"Message failed to send"
					client.close()
					state = 0
				if(len(line) <2):
					client.close()
					state = 0