import ast
import time
import sys
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON

port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    midiout, port_name = open_midioutput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

with open('inputmsglog.txt', 'r') as file:
    content = file.read()
    inputlog = ast.literal_eval(content)
startTime = time.time()
print('Sum of notes     = ', len(inputlog))
print('Start Time Stamp = ', startTime)

index = 0
while True:
    try:
        currentTime = time.time()
        if((startTime + inputlog[index][4] - inputlog[0][4] + 1) - currentTime <= 0):
            midiout.send_message([inputlog[index][1], inputlog[index][2], inputlog[index][3]])
            print(index, inputlog[index][1], inputlog[index][2], inputlog[index][3])
            index += 1
            if (index >= len(inputlog)):
                print('Done')
                sys.exit()
    except (EOFError, KeyboardInterrupt):
        print('Exit')
        sys.exit()