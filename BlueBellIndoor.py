#!/usr/bin/python

from __future__ import generators
from pprint import pprint
import feedparser
import time
import csv
import bluetooth
import os, sys
import datetime
import smtplib
import string
import select


def chunk(seq, size):
		for i in range(0, len(seq), size):
			yield seq[i:i+size]
		
		
class MyDiscoverer (bluetooth.DeviceDiscoverer) :
    def pre_inquiry (self):
        self.done = False
    def device_discovered(self, address, device_class, name):
        print "%s - %s" % (address , name)
        if address not in self.discovered_list:
            self.discovered_list.append(address)
    def inquiry_complete(self):
        self.done = True
    def discover_my_devices(self):
        self.discovered_list = []
        self.find_devices(lookup_names = False, duration=5)
        while True:
            can_read, can_write, has_exc = select.select ([self ], [ ], [ ]) 
            if self in can_read:                             
                self.process_event()                                
            if self.done:
                break
        return self.discovered_list

size = 100
ownerdata={}				# static list of house owners
ghostlist={} 				# dictionary of people who have recently left and how long they've been gone
presence={} 				# dictionary of people who have already been announced and when they were last seen
peoplepresent=[] 			# list of people found
timestamp=[] 				# list timestamps that lists when people are found or when they leave
timelimit="0:01:00:000000" 	# time limit of when to remove someone from presence (the length of time someone can be gone before they can be reannounced)
FROM = "bluebellsmtp@gmail.com"
smtptolist = []
TO = ','.join(smtptolist)


for row in csv.reader(open('OwnerList')): #import static list of owners
	ownerdata[row[0]] = row[1:]

log = open("log.txt", "a")

print "Device List Loaded."
print

while(True):
	snafu=0								#reset timestamp on every loop
	announce=""							#reset announce string on every loop
	devicesfound = MyDiscoverer().discover_my_devices() 	# search for nearby BT MAC Addresses at 5 second interval
	snafu = datetime.datetime.now() 						# get current date/time
	
	print "-------------"
	print "DevicesFound: %s" %(str(devicesfound), )
	pprint('Presence Dictionary: %s' %(presence))
	pprint('Ghostlist: %s' %(ghostlist))
	print "-------------"

	log.write(str(snafu))
	log.write('\n-------------\n')
	log.write('DevicesFound: %s\n' %(str(devicesfound), ))
	log.write('Presence Dictionary: %s\n' %(str(presence), ))
	log.write('GhostList: %s\n' % (str(ghostlist), ))
	log.write('-------------\n')

	for personpresent in presence: 					# for every person that has recently been present
		if personpresent in devicesfound: 			# if they are currently in the house
			if personpresent in ghostlist: 			# and if they are in the ghostlist
				print "-------------"
				print "%s has returned" %(personpresent, )
				print "-------------"
				del ghostlist[personpresent]  		# remove them from the ghostlist
			else:
				pass
		else:
			ghostlist[personpresent] = snafu 		# otherwise, update the ghostlist timestamp
			
	
	
	for devicefound in devicesfound: 				# for every bluetooth device found
			if devicefound in ownerdata:			# if they are the owner
				timestamp.append(snafu) 			#add/update timestamp to snafu list
				peoplepresent.append(devicefound) 	#add device to present list
				if devicefound in presence:
					pass
				else:
					announce += "Welcome home, " + ownerdata[devicefound][0] + "." # create a text string listing the owners present

	
	presence = dict((zip(peoplepresent, timestamp))) # create the presence dictionary based on the people found and a timestamp
	
	for persongone in ghostlist: 									#for every person not currently present
		delta = str(ghostlist[persongone] - presence[persongone])	#determine how long they've been gone
		if delta > timelimit:										#if they've been gone > x
			if persongone in presence:		
				del presence[persongone]			#remove them from presence so that they can be reannounced when they return
				
			else:
				pass
		else:
			pass
			
	if (len(announce) > 0):		# if people present have not yet been announced

		w = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=5f982310970ec5ef5cef46855878ea78&_render=rss')
		e = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=681e3b709b9e01ba828208f7293ad3ef&_render=rss')
		t = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=b576a81bcd739282ce24c9e4c7047b27&_render=rss')
		n = feedparser.parse('http://www.npr.org/rss/rss.php?id=1001')
		weather = w.entries[0].title
		facebook = e.entries[0].title + ' ' + e.entries[1].title + ' ' + e.entries[2].title
		c=1
		#print t
		news = ''
		for lines in n.entries:
			news += 'Headline. ' + n.entries[c].title + '..' + 'Description. ' + n.entries[c].description + '.'
			c+=1
			if (c > 4):
				break
			
			
		completeannounce = announce + '.' + weather + '.' + news
		y=0
		split = [x for x in chunk(completeannounce, size)]
		print split
		for segments in split:
			os.system('mplayer -cache 5096 "http://translate.google.com/translate_tts?tl=en&q=%s" -vc null -vo null -ao pcm:fast:waveheader:file=stream%s.wav' % (split[y], str(y)),)
			#os.system('mplayer "http://translate.google.com/translate_tts?tl=en&q=%s"' % split[y], )
			y +=1
		os.system('sox *.wav out.wav')
		os.system('mplayer out.wav')		
					
		
	
	
