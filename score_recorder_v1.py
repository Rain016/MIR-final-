from __future__ import print_function
import threading
import numpy as np

import time
import sys
import time
import rtmidi

import os

import matplotlib
import matplotlib.pyplot as plt
from rtmidi.midiutil import open_midiinput

from pynput import keyboard

import score_grapher_v0
import score_sort_v0

time_start=time.time()
log=''
inputmsglog=[]
inputtiminglog=[]
receivednotelog=[]
scorelog=[] #before arranging order
outputscore=[] #final output




midiout = rtmidi.MidiOut()
print(midiout.get_ports())
midiout.open_port(1)

port = sys.argv[1] if len(sys.argv) > 1 else None
midiin, port_name = open_midiinput(port)

onoff=[]
notes=[]
scorepositions=[]

noteon_notes=[]
noteon_scorepositions=[]

quantize_per_beat=4

def inputreading():
    global running,eventnumber,scorelog
    global quantize_per_beat
    global inputmsglog,inputtiminglog,onoff,notes,scorepositions,noteon_notes,noteon_scorepositions
    print('\n inputreading starts ')
    beattime=range(1,101)
    print(beattime)
    beatplayed=np.zeros(100)

    current_time=0
    firstposition=0 #initiate the variable. this will be overwritten by the time at which the first note is actually played
    eventnumber=0
    while running==1: #and current_time<9:
        time_stamp = time.time()            # Get current time.
        current_time = time_stamp - time_start

        for i in range(100):
            if beattime[i]<=current_time and beatplayed[i]==0:
                midiout.send_message([0x90,108,127])
                print('beat ',i)
                beatplayed[i]=1
        msg = midiin.get_message()
        if msg:
            current_time = time.time() - time_start
            inputmsglog+=[['Keyboard1',msg[0][0],msg[0][1],msg[0][2],current_time]]
            if True:
                onoff+=[msg[0][0]]
                notes+=[msg[0][1]]
                currentposition=round(current_time*quantize_per_beat)/quantize_per_beat
                if firstposition==0:
                    firstposition=currentposition
                scorepositions+=[currentposition-firstposition+3]
                scorelog+=[[eventnumber,msg[0][0],msg[0][1],currentposition-firstposition]]
                eventnumber+=1
            
            if msg[0][0]==144: #only noteon
                noteon_notes+=[msg[0][1]]
                currentposition=round(current_time*quantize_per_beat)/quantize_per_beat
                noteon_scorepositions+=[currentposition-firstposition+3]

         #midiout.send_message(msg[0])
        #  if msg[0][2]>0 and msg[0][0]>143:
        #      inputtiminglog+=[current_time]
            print('input:'+str(msg))


running=1
threading.Thread(target=inputreading).start()

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    global running,outputscore,scorelog,logdirectory
    if key == keyboard.Key.esc:
        #print("pressed ESC")
        running=0 #this stops the threads

        # print(onoff)
        # print(notes)
        # print(scorepositions)
        # print('\n noteon only')
        # print(noteon_notes)
        # print(noteon_scorepositions)

        print('\n score log')
        print(scorelog)


        outputscore=score_sort_v0.sort(quantize_per_beat,scorelog)

        print('\n sorted score log')
        print(outputscore)

        logdirectory="logs/score_recorder_"+str(time.time())
        os.makedirs(logdirectory)

        inputlogfile=open(logdirectory+"/inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()

        scorefile=open(logdirectory+"/outputscore.txt","w")
        scorefile.write(str(outputscore))
        scorefile.close()

        # #plotting
        #score_grapher_v0.graph(quantize_per_beat,outputscore,logdirectory+'/plot.png')

        return False

with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

while True:
    if running==1:
        pass
    else:
        score_grapher_v0.graph(outputscore,logdirectory+'/plot.png')
        break
        


