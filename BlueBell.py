#!/usr/bin/python

import time
import csv
import bluetooth
import os, sys
import datetime
import smtplib
import string
import select
from pprint import pprint

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
        self.find_devices(lookup_names = False, duration=15)
        while True:
            can_read, can_write, has_exc = select.select ([self ], [ ], [ ]) 
            if self in can_read:                             
                self.process_event()                                
            if self.done:
                break
        return self.discovered_list

peopledata={} 				# static list of known people
ownerdata={}				# static list of house owners
ghostlist={} 				# dictionary of people who have recently left and how long they've been gone
presence={} 				# dictionary of people who have already been announced and when they were last seen
peoplepresent=[] 			# list of people found
timestamp=[] 				# list timestamps that lists when people are found or when they leave
timelimit="0:01:00:000000" 	# time limit of when to remove someone from presence (the length of time someone can be gone before they can be reannounced)
FROM = "#"
smtptolist = ['#','#']
TO = ','.join(smtptolist)

for row in csv.reader(open('NameList')): #import static list of known people
	peopledata[row[0]] = row[1:]

for row in csv.reader(open('OwnerList')): #import static list of owners
	ownerdata[row[0]] = row[1:]

log = open("log.txt", "a")

print "Device List Loaded."
print

while(True):
	snafu=0								#reset timestamp on every loop
	owner=[]							#reset owner presence on every loop
	announce=""							#reset announce string on every loop
	ownerannounce = ""					#reset ownerannouce string on every loop
	devicesfound = MyDiscoverer().discover_my_devices() 	# search for nearby BT MAC Addresses at 5 second interval
	snafu = datetime.datetime.now() 						# get current date/time
	
	print "-------------"
	print "DevicesFound: %s" %(str(devicesfound), )
	#print "Presence Dictionary: %s" %(str(presence), )
	#print "GhostList: %s" % (str(ghostlist), )
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
				owner.append(devicefound)			# add the device to the owner list
				ownerannounce += ownerdata[devicefound][0] + " and " # create a text string listing the owners present
				
			if devicefound in peopledata: 			#if they are in your known people list
				timestamp.append(snafu) 			#add/update timestamp to snafu list
				peoplepresent.append(devicefound) 	#add device to present list
				if devicefound in presence: 		# if the device is already present
					pass							#do nothing
				else:								#otherwise...welcome them and notify the owners!
					announce += peopledata[devicefound][0] + " and "
					#os.system('mplayer ~/Dropbox/apps/bluebell/dev/music/%s -endpos 15' % (peopledata[devicefound][1], ))					
					print "-------------"
					print "%s added to presence" %(devicefound, )				
					print "-------------"
			else:
				pass
	
	presence = dict((zip(peoplepresent, timestamp))) # create the presence dictionary based on the people found and a timestamp
	
	for persongone in ghostlist: 									#for every person not currently present
		delta = str(ghostlist[persongone] - presence[persongone])	#determine how long they've been gone
		#print delta
		if delta > timelimit:										#if they've been gone > x
			if persongone in presence:		
				#print "-------------"
				#print "%s removed from presence" %(personpresent, )			
				#print "-------------"
				del presence[persongone]			#remove them from presence so that they can be reannounced when they return
				
			else:
				pass
		else:
			pass
			
	if (len(announce) > 0):		# if people present have not yet been announced
		if(len(owner) == 1):	# check if there is only one owner home
			ownerannounce = ownerannounce[:-4]
			ownerannounce = ownerannounce + " is home and will be with you shortly " 
		if(len(owner) == 0):	# check if there is only one owner home
			ownerannounce = " Noone is currently home. But they have been notified of your presence " 
		if (len(owner) > 1):	#check if there is more than one owner home
			ownerannounce = ownerannounce[:-4]
			ownerannounce = ownerannounce + " are home and will be with you shortly "
		announce = announce[:-4]
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.ehlo()
		server.starttls()
		server.ehlo
		server.login('#', '#')
		server.set_debuglevel(1)
		BODY = string.join((
			"From: %s" % FROM,
			"To: %s" % TO,
			"Subject: At your door: %s " % (announce, ),
			"",
			), "\r\n")
		server.sendmail(FROM, smtptolist, BODY)
		server.close()
		announce = "Welcome " + announce + ".  "
		completeannounce = announce + ownerannounce
		#completeannounce = completeannounce.replace(' ','%20')
		os.system('mplayer "http://translate.google.com/translate_tts?tl=en&q=%s"' % completeannounce, )
		#os.system('btplay "http://translate.google.com/translate_tts?tl=en&q=%s"' % completeannounce, )
		#time.sleep(5)
		#os.system('btplay "http://translate.google.com/translate_tts?tl=en&q=%s"' % ownerannounce, )
		#print announce
		#print ownerannounce			
		
	
	
