#!/usr/bin/python

from __future__ import generators
import feedparser
import os, sys
import datetime
import time
import string
import threading
import select


def chunk(seq, size):
		for i in range(0, len(seq), size):
			yield seq[i:i+size]

size=100
announce = 'Welcome back, Tom.'				
		


#def jarvis():
			

#t=threading.Timer(10, jarvis)

while(True):
	w = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=5f982310970ec5ef5cef46855878ea78&_render=rss')
	e = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=681e3b709b9e01ba828208f7293ad3ef&_render=rss')
	t = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=b576a81bcd739282ce24c9e4c7047b27&_render=rss')
	n = feedparser.parse('http://pipes.yahoo.com/pipes/pipe.run?_id=e189632e9213ee8054da152ee9ceab35&_render=rss')
	weather = w.entries[0].title
	facebook = e.entries[0].title + '.' + e.entries[1].title + '.' + e.entries[2].title
	c=1
	news = ''
	for lines in n.entries:
		news += 'Headline. ' + n.entries[c].title + '..' + 'Description. ' + n.entries[c].description + '.'
		c+=1
		if (c > 3):
			break
						
	completeannounce = announce + '.' + weather + '. Here is your latest news.' + news
	y=0
	split = [x for x in chunk(completeannounce, size)]
	os.system('rm stream*.wav')
	
	print completeannounce
	for segments in split:
		os.system('mplayer -cache 5096 "http://translate.google.com/translate_tts?tl=en&q=%s" -vc null -vo null -ao pcm:fast:waveheader:file=stream%s.wav' % (split[y], str(y)),)
		y +=1
	os.system('sox *.wav out.wav')
	#os.system('mplayer out.wav')
	#t.start()
	time.sleep(10)					
		
	
	
