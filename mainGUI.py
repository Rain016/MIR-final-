import ast
import time
import threading
import tkinter as tk
import os
import sys
import queue
import numpy as np
import score_sort_v0
import score_grapher_v0
from tkinter import filedialog, scrolledtext, ttk
from rtmidi import MidiIn, MidiOut
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE, ALL_SOUND_OFF,  ALL_NOTES_OFF

def print_to_terminal(message, terminal):
    terminal.insert(tk.END, message)
    terminal.yview(tk.END)

def clear_terminal(terminal):
    terminal.delete(1.0, tk.END)

def open_file_to_terminal1():
    terminal1.delete(1.0, tk.END)
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            try:
                global inputscore
                inputscore = ast.literal_eval(file.read())
                for item in inputscore:
                    print_to_terminal(str(item) + '\n', terminal1)
                print_to_terminal('\n' + 'Sum of notes = ' + str(len(inputscore)) + '\n', terminal1)
                print_to_terminal("Will listen for input score above.\n", terminal1)
            except (ValueError, SyntaxError):
                print_to_terminal("Error: File content is not a valid Python literal.\n", terminal1)
    
    for index,note in enumerate(inputscore):
        if not note[0]==index:
            print_to_terminal("invalid inputscore.\n", terminal1)

def open_file_to_terminal2():
    terminal2.delete(1.0, tk.END)
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            try:
                global outputscore
                outputscore = ast.literal_eval(file.read())
                for item in outputscore:
                    print_to_terminal(str(item) + '\n', terminal2)
                print_to_terminal('\n' + 'Sum of notes = ' + str(len(outputscore)) + '\n', terminal2)
                print_to_terminal("Will play output score above.\n", terminal2)
            except (ValueError, SyntaxError):
                print_to_terminal("Error: File content is not a valid Python literal.\n", terminal2)
    
    for index,note in enumerate(outputscore):
        if not note[0]==index:
            print_to_terminal("invalid outputscore.\n", terminal2)

def save_terminal_output_to_file(terminal):
    content = terminal.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

    if file_path:
        with open(file_path, 'w') as file:
            file.write(content)
        print_to_terminal(f"Terminal content saved to file: {file_path}\n", terminal)

def open_score_recorder():
    score_recorder_window = tk.Toplevel(root)
    score_recorder_window.title("Score Recorder")
    
    global running ,inputmsglog, inputtiminglog, receivednotelog, scorelog, outputscore
    global midi_out, midi_in, onoff, notes, scorepositions, noteon_notes, noteon_scorepositions, quantize_per_beat

    running = 0
    inputmsglog = []
    inputtiminglog = []
    receivednotelog = []
    scorelog = [] #before arranging order
    outputscore = [] #final output
    onoff = []
    notes = []
    scorepositions = []
    noteon_notes = []
    noteon_scorepositions = []
    quantize_per_beat = 4

    def recording():
        global midi_in, midi_out, running
        global quantize_per_beat, scorelog, outputscore, inputmsglog

        time_start = time.time()

        inputmsglog = []
        inputtiminglog = []
        receivednotelog = []
        scorelog = [] #before arranging order
        outputscore = [] #final output
        
        onoff = []
        notes = []
        scorepositions = []

        noteon_notes = []
        noteon_scorepositions = []
        
        print_to_terminal('input reading starts \n', recorder_terminal)
        beattime=range(1,101)
        print_to_terminal(str(f'{beattime} \n\n'), recorder_terminal)
        beatplayed=np.zeros(100)

        current_time=0
        firstposition=0 #initiate the variable. this will be overwritten by the time at which the first note is actually played
        eventnumber=0
        while running==1: #and current_time<9:
            time_stamp = time.time()            # Get current time.
            current_time = time_stamp - time_start

            for i in range(100):
                if beattime[i]<=current_time and beatplayed[i]==0:
                    midi_out.send_message([0x90,108,127])
                    print_to_terminal(str(f'beat {i}\n'), recorder_terminal)
                    beatplayed[i]=1
            msg = midi_in.get_message()
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

            #  midiout.send_message(msg[0])
            #  if msg[0][2]>0 and msg[0][0]>143:
            #      inputtiminglog+=[current_time]
                print_to_terminal('input:'+str(msg)+'\n', recorder_terminal)

    def start_record():
        global running
        if (running == 0):
            running = 1
            threading.Thread(target=recording).start()

    def stop_record():
        global running, scorelog, outputscore, quantize_per_beat
        running = 0
        print_to_terminal("\n" + "Stop recording..." + "\n\n", recorder_terminal)
        print_to_terminal('score log: ', recorder_terminal)
        print_to_terminal(scorelog, recorder_terminal)
        
        outputscore = score_sort_v0.sort(quantize_per_beat, scorelog)
        print_to_terminal('\n\nsorted score log: ', recorder_terminal)
        print_to_terminal(outputscore, recorder_terminal)
        print_to_terminal("\n", recorder_terminal)
        
    def save_record():
        global inputmsglog, outputscore
        print_to_terminal("\nRecording Saved.\n", recorder_terminal)
        
        logdirectory_record = "logs/score_recorder_"+str(time.time())
        os.makedirs(logdirectory_record)
        
        inputlogfile=open(logdirectory_record+"/inputmsglog.txt","w")
        inputlogfile.write(str(inputmsglog))
        inputlogfile.close()
        
        scorefile=open(logdirectory_record+"/outputscore.txt","w")
        scorefile.write(str(outputscore))
        scorefile.close()
        
    def clear_terminal(widget):
        widget.delete(1.0, tk.END)
        
    def print_to_terminal(message, widget):
        widget.insert(tk.END, message)
        widget.see(tk.END)
    

    # Label and ScrolledText for Recorder Terminal
    label_terminal_recorder = tk.Label(score_recorder_window, text='Score Recorder Terminal')
    label_terminal_recorder.grid(row=0, column=0, padx=10, pady=5)

    recorder_terminal = scrolledtext.ScrolledText(score_recorder_window, wrap=tk.WORD, width=60, height=30)
    recorder_terminal.grid(row=1, column=0, padx=10, pady=5)

    # Buttons
    button_start = tk.Button(score_recorder_window, text="Start Recording", width=15, command=start_record)
    button_start.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

    button_stop = tk.Button(score_recorder_window, text="Stop Recording", width=15, command=stop_record)
    button_stop.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

    button_save = tk.Button(score_recorder_window, text="Save to the file", width=15, command=save_record)
    button_save.grid(row=4, column=0, padx=5, pady=10, sticky='ew')
    
    button_clear = tk.Button(score_recorder_window, text="Clear the terminal", width=15, command=lambda: clear_terminal(recorder_terminal))
    button_clear.grid(row=5, column=0, padx=5, pady=10, sticky='ew')

    button_close = tk.Button(score_recorder_window, text="Close", width=15, command=score_recorder_window.destroy)
    button_close.grid(row=6, column=0, padx=5, pady=10, sticky='ew')

def open_score_player():  
    global stop_flag_player, play_flag_player
    play_flag_player = False
    stop_flag_player = threading.Event()
    
    def play_in_thread(stop_flag_player):
        global play_flag_player
        startTime = time.time()
        print_to_terminal('Start Time Stamp = ' + str(startTime) + '\n', player_terminal2)
        index = 0
        while not stop_flag_player.is_set():
            try:
                currentTime = time.time()
                if ((startTime + inputlog_player[index][4] - inputlog_player[0][4] + 1) - currentTime <= 0):
                    midi_out.send_message([inputlog_player[index][1], inputlog_player[index][2], inputlog_player[index][3]])
                    print_to_terminal(str(inputlog_player[index][1]) + ',' + str(inputlog_player[index][2]) + ',' + str(inputlog_player[index][3]) + '\n',player_terminal2)
                    index += 1
                    if (index >= len(inputlog_player)):
                        print_to_terminal('Done' + '\n', player_terminal2)
                        play_flag_player = False
                        break
            except (EOFError, KeyboardInterrupt):
                print_to_terminal('Exit' + '\n', player_terminal2)
                play_flag_player = False
                break

    def play_player():
        global play_flag_player
        stop_flag_player.clear()
        if (play_flag_player == False):
            play_flag_player = True
            threading.Thread(target=play_in_thread, args=(stop_flag_player,)).start()    
    
    def stop_player():
        global play_flag_player
        stop_flag_player.set()
        play_flag_player = False
        if midi_out:
            channel = 0
            for note in range(128):
                midi_out.send_message([NOTE_OFF | channel , note, 0])    
     
    def close_player():
        global play_flag_player
        stop_flag_player.set()
        play_flag_player = False
        if midi_out:
            channel = 0
            for note in range(128):
                midi_out.send_message([NOTE_OFF | channel , note, 0])
        score_player_window.destroy()

    def open_file_to_player_terminal():
        player_terminal1.delete(1.0, tk.END)
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                try:
                    global inputlog_player
                    inputlog_player = ast.literal_eval(file.read())
                    for item in inputlog_player:
                        print_to_terminal(str(item) + '\n', player_terminal1)
                    print_to_terminal('\n' + 'Sum of notes = ' + str(len(inputlog_player)) + '\n', player_terminal1)
                except (ValueError, SyntaxError):
                    print_to_terminal("Error: File content is not a valid Python literal.\n", player_terminal1)    
        # Bring the "Score Player" window to the top
        score_player_window.lift()
    
    score_player_window = tk.Toplevel(root)
    score_player_window.title("Score Player") 
    score_player_window.protocol("WM_DELETE_WINDOW", close_player)  # Capture the window close event

    # Label and ScrolledText for Player Terminal
    player_label1 = tk.Label(score_player_window, text='Terminal 1')
    player_label1.grid(row=0, column=0, padx=10, pady=5)

    player_terminal1 = scrolledtext.ScrolledText(score_player_window, wrap=tk.WORD, width=60, height=30)
    player_terminal1.grid(row=1, column=0, padx=10, pady=5)
    
    player_label2 = tk.Label(score_player_window, text='Terminal 2')
    player_label2.grid(row=0, column=2, padx=10, pady=5)   
    
    player_terminal2 = scrolledtext.ScrolledText(score_player_window, wrap=tk.WORD, width=60, height=30)
    player_terminal2.grid(row=1, column=2, padx=10, pady=5)
    
    #Player Frame
    player_frame = tk.Frame(score_player_window)
    player_frame.grid(row=1, column=1, padx=10, pady=10)
    
    player_button1 = tk.Button(player_frame, text="Play", width=15, command=play_player)
    player_button1.grid(row=0, column=0, padx=5, pady=10, sticky='ew')

    player_button2 = tk.Button(player_frame, text="Stop", width=15, command=stop_player)
    player_button2.grid(row=1, column=0, padx=5, pady=10, sticky='ew')
 
    player_button3 = tk.Button(player_frame, text="Close", width=15, command=close_player)
    player_button3.grid(row=2, column=0, padx=5, pady=10, sticky='ew')   
    
    # Buttons
    button_1 = tk.Button(score_player_window, text="Open File to Terminal 1", width=15, command=open_file_to_player_terminal)
    button_1.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

    button_2 = tk.Button(score_player_window, text="Save Terminal 2 to File", width=15,  command=lambda: save_terminal_output_to_file(player_terminal2))
    button_2.grid(row=2, column=2, padx=5, pady=10, sticky='ew')

    button_3 = tk.Button(score_player_window, text="Clear Terminal 1", width=15, command=lambda:clear_terminal(player_terminal1))
    button_3.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

    button_4 = tk.Button(score_player_window, text="Clear Terminal 2", width=15, command=lambda:clear_terminal(player_terminal2))
    button_4.grid(row=3, column=2, padx=5, pady=10, sticky='ew')

def midi_output_select():
    # Create a new window to select output port
    output_port_window = tk.Toplevel(root)
    output_port_window.title("Select MIDI Output Port")
    output_port_window.geometry("300x150")

    # Variable to store selected port
    selected_port = tk.StringVar(root)

    # Check if there are available MIDI output ports
    if not output_ports:
        # If no output ports are available, display a message
        selected_port.set("No available MIDI Output Ports")  
    else:
        selected_port.set(output_ports[0])  # Set default value

    # Combobox for selecting output port
    output_port_combobox = ttk.Combobox(output_port_window, textvariable=selected_port, values=output_ports, state="readonly", width=40)
    output_port_combobox.pack()

    # Function to handle selection change
    def on_select(event):
        selected_port_name = selected_port.get()
        entry_current_midi_output_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_output_port.insert(tk.END, selected_port_name)  # Insert selected port name into Entry
        print_to_terminal(f"Selected MIDI output port: {selected_port_name}" + '\n',terminal3)        
        # Close the previously opened MIDI output port
        if hasattr(midi_out, 'close_port'):
            midi_out.close_port()

        # Open the selected MIDI output port
        midi_out.open_port(output_ports.index(selected_port_name))
    
    # Bind event to selection change
    output_port_combobox.bind("<<ComboboxSelected>>", on_select)

def midi_input_select():
    # Create a new window to select input port
    input_port_window = tk.Toplevel(root)
    input_port_window.title("Select MIDI Input Port")
    input_port_window.geometry("300x150")

    # Variable to store selected port
    selected_port = tk.StringVar(root)

    # Check if there are available MIDI input ports
    if not input_ports:
        # If no input ports are available, display a message
        selected_port.set("No available MIDI Input Ports")
    else:    
        selected_port.set(input_ports[0])  # Set default value

    # Combobox for selecting input port
    input_port_combobox = ttk.Combobox(input_port_window, textvariable=selected_port, values=input_ports, state="readonly", width=40)
    input_port_combobox.pack()

    # Function to handle selection change
    def on_select(event):
        selected_port_name = selected_port.get()
        entry_current_midi_input_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_input_port.insert(tk.END, selected_port_name)  # Insert selected port name into Entry
        print_to_terminal(f"Selected MIDI input port: {selected_port_name}" + '\n', terminal3)
        
        # Close the previously opened MIDI input port
        if hasattr(midi_in, 'close_port'):
            midi_in.close_port()

        # Open the selected MIDI output port
        midi_in.open_port(input_ports.index(selected_port_name))

    # Bind event to selection change
    input_port_combobox.bind("<<ComboboxSelected>>", on_select)

def midi_output_test():
    print_to_terminal("MIDI Output Test" + '\n', terminal3)
    midi_out.send_message([0x90, 60, 64])
    time.sleep(0.1)
    midi_out.send_message([0x80, 60, 0])
    midi_out.send_message([0x90, 64, 64])
    time.sleep(0.1)
    midi_out.send_message([0x80, 64, 0])
    midi_out.send_message([0x90, 67, 64])
    time.sleep(0.1)
    midi_out.send_message([0x80, 67, 0])
    midi_out.send_message([0x90, 72, 64])
    time.sleep(0.1)
    midi_out.send_message([0x80, 72, 0])

def midi_input_test():
    global stop_flag_midi_input_test
    stop_flag_midi_input_test = threading.Event()
    
    def midi_input_test_close():
        stop_flag_midi_input_test.set()  # Set the stop flag to stop the thread
        print_to_terminal("MIDI Input Test Done" + '\n', terminal3)
        midi_input_test.destroy()  # Destroy the window  

    def midi_input_test_stop():
        stop_flag_midi_input_test.set()
        print_to_terminal("Stop" + '\n', midi_input_test_terminal)

    def midi_input_test_run():
        stop_flag_midi_input_test.clear()
        threading.Thread(target=midi_input_test_run_in_thread, args=(stop_flag_midi_input_test,)).start()
    
    def midi_input_test_run_in_thread(stop_flag_midi_input_test):
        print_to_terminal("Start" + '\n', midi_input_test_terminal)
        while not stop_flag_midi_input_test.is_set():
            msg = midi_in.get_message()
            if msg:
                print_to_terminal(f"{msg}" + '\n', midi_input_test_terminal)
    
    print_to_terminal("MIDI Input Test" + '\n', terminal3)
    midi_input_test = tk.Toplevel(root)
    midi_input_test.title("MIDI Input Test")
    midi_input_test.protocol("WM_DELETE_WINDOW", midi_input_test_close)  # Capture the window close event
    
    # Label and ScrolledText for Recorder Terminal
    midi_input_test_label = tk.Label(midi_input_test, text='MIDI Input Test Terminal')
    midi_input_test_label.grid(row=0, column=0, padx=10, pady=5)

    midi_input_test_terminal = scrolledtext.ScrolledText(midi_input_test, wrap=tk.WORD, width=60, height=30)
    midi_input_test_terminal.grid(row=1, column=0, padx=10, pady=5)

    # Buttons
    midi_input_test_Button1 = tk.Button(midi_input_test, text="Start", width=15, command=midi_input_test_run)
    midi_input_test_Button1.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

    midi_input_test_Button2 = tk.Button(midi_input_test, text="Stop", width=15, command=midi_input_test_stop)
    midi_input_test_Button2.grid(row=3, column=0, padx=5, pady=10, sticky='ew')
    
    midi_input_test_Button2 = tk.Button(midi_input_test, text="Close", width=15, command=midi_input_test_close)
    midi_input_test_Button2.grid(row=4, column=0, padx=5, pady=10, sticky='ew')

def midi_reset():
    print_to_terminal("Reset MIDI settings" + '\n', terminal3)
    midi_init()

def midi_init():
    # MIDI Initialization
    global midi_out, midi_in, output_ports, input_ports
    midi_out = MidiOut()
    midi_in = MidiIn()
    output_ports = midi_out.get_ports()
    input_ports = midi_in.get_ports()

    # Check if there are available MIDI output ports
    if not output_ports:
        # If no output ports are available, display a message in terminal3
        print_to_terminal("No available MIDI Output Ports" + '\n', terminal3)
        entry_current_midi_output_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_output_port.insert(tk.END, "No available MIDI Output Ports")  # Insert "No available MIDI Output Ports" into Entry
    else:
        # If output ports are available, proceed with retrieving the default output port
        default_output_port = output_ports[0]
        # Open the default MIDI output port
        midi_out.open_port(output_ports.index(default_output_port))
        print_to_terminal(f"Default MIDI output port: {default_output_port}" + '\n', terminal3)
        entry_current_midi_output_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_output_port.insert(tk.END, default_output_port)  # Insert default output port name into Entry

    # Check if there are available MIDI input ports
    if not input_ports:
        # If no input ports are available, display a message in terminal3
        print_to_terminal("No available MIDI Input Ports" + '\n', terminal3)
        entry_current_midi_input_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_input_port.insert(tk.END, "No available MIDI Input Ports")  # Insert "No available MIDI Input Ports" into Entry
    else:
        # If input ports are available, proceed with retrieving the default input port
        default_input_port = input_ports[0]
        # Open the default MIDI input port
        midi_in.open_port(input_ports.index(default_input_port))
        print_to_terminal(f"Default MIDI input port: {default_input_port}" + '\n', terminal3)
        entry_current_midi_input_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_input_port.insert(tk.END, default_input_port)  # Insert default input port name into Entry

def run_real_accomp():
    global stop_flag_accomp
    stop_flag_accomp = threading.Event()
    stop_flag_accomp.clear()
    
    print_to_terminal("Running\n", terminal3)
    
    global lastinputIndex, lastinputscorepositionIndex, outputinterpretation
    inputinterpretation=[event+[0,0] for event in inputscore]
    outputinterpretation=[event+[0,0] for event in outputscore]
    
    def close_running():
        stop_flag_accomp.set()
        threading.Thread(target=input_reading, args=(stop_flag_accomp,)).join
        threading.Thread(target=calculating, args=(stop_flag_accomp,)).join
        threading.Thread(target=worker, args=(stop_flag_accomp,)).join
        inputq.join()
        print_to_terminal('Exit\n', terminal3)
        running_window.destroy()    
    
    running_window = tk.Toplevel(root)
    running_window.title("Running Window") 
    running_window.protocol("WM_DELETE_WINDOW", close_running)  # Capture the window close event
    
    # Label and ScrolledText for Player Terminal
    running_window_label = tk.Label(running_window, text='Running Window')
    running_window_label.grid(row=0, column=0, padx=10, pady=5)

    running_window_terminal = scrolledtext.ScrolledText(running_window, wrap=tk.WORD, width=60, height=30)
    running_window_terminal.grid(row=1, column=0, padx=10, pady=5)
    
    # Buttons
    running_window_button = tk.Button(running_window, text="Close", width=15, command=close_running)
    running_window_button.grid(row=2, column=0, padx=5, pady=10, sticky='ew')
    
    #make a list of all unique inputscorepositions
    inputscorepositions=[-1]
    for note in inputinterpretation:
        if not note[3]==inputscorepositions[-1]:
            inputscorepositions+=[note[3]]
    inputscorepositions.append(10000) #to avoid error when processing the last note
    #print(inputscorepositions)
    
    lastinputIndex=-1
    lastinputscorepositionIndex=0

    global q
    q = []

    def NoteOn(note):
        midi_out.send_message([0x90,note[1],note[2]])

    def NoteOff(note):
        midi_out.send_message([0x80,note[1],note[2]])

    def worker(stop_flag_accomp):
        print_to_terminal('worker starts\n',running_window_terminal)
        global q
        global OutputNoteIndex
        global log,workerlog,workertiminglog,outputlog,noteon_outputtiminglog,noteon_realoutputlog,noteoff_outputtiminglog,noteoff_realoutputlog
        alreadyplayed=np.zeros(1000)
        while not stop_flag_accomp.is_set():
            current_time = time.time()
            #print('q lenght',len(q))
            for i in range(len(q)):               # If there is data in queue.
                #workerlog+='\n'+str(current_time)+' queue has '+str(len(q))+'elements, looking at #'+str(i)
                try:
                    note = q[i]
        #            workerlog+='\n'+str(current_time)+' processing element #'+str(i)+'= '+str(note)+' OutputNoteIndex is '+str(OutputNoteIndex)
                    if (note[3] <= (current_time)):       # Check the time stamp
                                                                # of the data.
                        q.pop(i)
                        #workerlog+='\n'+str(current_time)+' popped from queue element #'+str(i)
                        if alreadyplayed[note[5]]==0: #don't play a note already played
                            #TO FIX: don't play a note whose position is before that of the last note played.
                            if note[0] == 'note_on':
                                NoteOn(note)
                                #print('OUTPUT',current_time,note)
                                #print(alreadyplayed[note[5]])
                                alreadyplayed[note[5]]=1
                                noteon_outputtiminglog+=[note[3]] #[[note[3],note[5]]]
                                noteon_realoutputlog+=[current_time] #[[current_time,note[5]]]                            
                            if note[0] == 'note_off':
                                NoteOff(note)
                                #print('OUTPUT',current_time,note)
                                alreadyplayed[note[5]]=1
                                noteoff_outputtiminglog+=[note[3]] #[[note[3],note[5]]]
                                noteoff_realoutputlog+=[current_time] #[[current_time,note[5]]]   
                            #OutputNoteIndex=note[5]+1
                            # alreadyplayed[note[5]]=1
                            # print('alreadyplayed',note[5])
                            
                            # if note[5]>OutputNoteIndex:
                            #     print(str(current_time)," ERROR: Expecting OutputNoteIndex ",OutputNoteIndex," already arrived at ", str(note))
    #                        log+='\n'+str(current_time)+' output from queue'+str(note)
    #                        workerlog+='\n'+str(current_time)+' worker outputs'+str(note)
    #                        outputlog+='\n'+str(current_time)+str(note)                        
                except:
                    pass
    framerate=100

    global theta1, theta2, theta3, Omega2, Omega3
    theta1=np.zeros(200*framerate)
    theta2=np.zeros(200*framerate)
    theta3=np.zeros(200*framerate)

    reactiontime=10 #in frames

    Omega2=0.002
    Omega3=0.002
    theta2[0]=0
    theta2[1]=Omega2
    theta3[0]=0
    theta3[1]=Omega2

    K21=0.06
    K23=0.06
    K32=0.06

    inputq = queue.Queue()
    def calculating(stop_flag_accomp):
        starttime=time.time_ns()/1000000000
        global q
        global lastinputIndex,lastinputscorepositionIndex
        global theta1,theta2,theta3
        global outputinterpretation
        global arduinoarray
        while not stop_flag_accomp.is_set():
            if not inputq.empty():
                current_time=time.time_ns()/1000000000
                msg = inputq.get() #format: [144/128, note number, velocity, time in ns]
                #figure out which input note msg corresponds to. 
                foundmatch=0
                if msg[0]==144: 
                    for note in inputinterpretation:
                        backlimit=inputscorepositions[lastinputscorepositionIndex]-0.01
                        forwardlimit=inputscorepositions[lastinputscorepositionIndex+1]+0.51
                        if note[1]==144 and note[3]>=backlimit and note[3]<=forwardlimit: 
                            if note[2]==msg[1] and note[4:]==[0,0]: #i.e. if it's the right note and hasn't been played yet
                                note[4]=msg[3]/1000000000
                                note[5]=msg[2]
                                lastinputIndex=max(lastinputIndex,note[0])
                                lastinputscorepositionIndex=inputscorepositions.index(inputinterpretation[lastinputIndex][3])
                                #print('lastinputscorepositionIndex',lastinputscorepositionIndex)
                                foundmatch=1
                                #print(str(time.time_ns())+'received '+str(msg)+' matched to '+str(note))
                                break
                if msg[0]==128:
                    for note in reversed(inputinterpretation): #find the last time that note was played
                        if note[1]==144 and note[2]==msg[1] and not note[4:]==[0,0]:
                            for offnote in inputinterpretation[note[0]:]: #search forward to find the nearest noteoff event
                                if offnote[1]==128 and offnote[2]==msg[1]:
                                    if not offnote[4:]==[0,0]:
                                        print_to_terminal('already got this noteoff\n', running_window_terminal)
                                    offnote[4]=msg[3]/1000000000
                                    offnote[5]=msg[2]
                                    foundmatch=1
                                    #print(str(time.time_ns())+'received '+str(msg)+' matched to '+str(offnote))
                                    break
                            break
                if foundmatch==0: #i.e. didn't find a match
                    print_to_terminal('could not match '+ str(msg) + '\n', running_window_terminal)
                elif msg[0]==144:
                    #model
                    #create piecewise linear theta1
                    points=[[0,-1]]
                    for position in inputscorepositions:
                        timing=[]
                        for note in inputinterpretation:
                            if note[1]==144 and note[3]==position and not note[4:]==[0,0]:
                                timing+=[note[4]-starttime]
                            if note[3]>position:
                                break
                        if position>inputscorepositions[lastinputscorepositionIndex]+1:
                            break
                        if not len(timing)==0:
                            points+=[[np.mean(timing),position]]
                    points.sort(key = lambda x: x[0])
                    #print('points',points)
                    for i in range(1,len(points)):
                        for t in range(int(points[i-1][0]*framerate),int(points[i][0]*framerate)):
                            theta1[t]=points[i-1][1]+(t/framerate-points[i-1][0])*(points[i][1]-points[i-1][1])/(points[i][0]-points[i-1][0])
                            if t<100:
                                currentspeed2=Omega2
                                currentspeed3=Omega2
                            if t>99:
                                currentspeed2=(theta2[t]-theta2[t-100])/100
                                currentspeed3=(theta3[t]-theta3[t-100])/100
                            theta2[t+1]=theta2[t]+currentspeed2+K21*(theta1[t]-theta2[t])+K23*(theta3[t]-theta2[t])
                            theta3[t+1]=theta3[t]+currentspeed3+K32*(theta2[t]-theta3[t])
                    #predict output timings
                    lastcalculatedtheta3frame=int(points[-1][0]*framerate)
                    theta3slope=theta3[lastcalculatedtheta3frame]-theta3[lastcalculatedtheta3frame-1]
                    theta3yIntercept=theta3[lastcalculatedtheta3frame]-theta3slope*lastcalculatedtheta3frame
                    #print(theta3slope,' ',theta3yIntercept)
                    # print(inputinterpretation)
                    velocity_range=[]
                    for inputnote in inputinterpretation:
                        # if not inputnote[5]==0:
                        #     print(inputnote[0],inputnote[1],inputnote[3],note[3])
                        if inputnote[1]==144 and not inputnote[5]==0: #and inputnote[3]>=note[3]-1 #search for already played notes starting from 1 beat ago
                            while len(velocity_range)>4:
                                velocity_range.pop(0)
                            velocity_range+=[inputnote[5]]
                            # print(velocity_range)
                    current_desired_velocity=int(min(127,1*np.mean(velocity_range)))
                    for note in outputinterpretation:
                        outputtime=starttime+(note[3]-theta3yIntercept)/theta3slope/framerate-0.1
                        note[4]=outputtime
                        note[5]=current_desired_velocity
                        # if note[4]<time.time_ns()/1000000000+reactiontime/framerate and note[4]>time.time_ns()/1000000000:
                        #     pass
                        # else:
                        #     note[4]=outputtime
                        #     if note[4]<time.time_ns()/1000000000+reactiontime/framerate and note[4]>time.time_ns()/1000000000:
                        #         note[4]=time.time_ns()/1000000000+reactiontime/framerate
                        #figure out velocity (running average)
                    #now outputting to worker
                    q_temp=[]
                    for note in outputinterpretation:                
                        backlimit=inputscorepositions[lastinputscorepositionIndex]-0.01
                        forwardlimit=inputscorepositions[lastinputscorepositionIndex]+1.01
                        if note[3]>backlimit and note[3]<forwardlimit:
                            if note[1]==144:
                                outputmsg=['note_on',note[2],current_desired_velocity,note[4],'accompaniment',note[0],note[3]]
                            if not note[1]==144:
                                outputmsg=['note_off',note[2],current_desired_velocity,note[4]-0.001,'accompaniment',note[0],note[3]]
                            q_temp+=[outputmsg]
                    #print(q_temp)
                    q_temp_offloaded=np.zeros(len(q_temp))
                    for i in range(len(q_temp)):
                        for j in range(len(q)):
                            note=q[j]
                            note_temp=q_temp[i]
                            if [note[0],note[5]]==[note_temp[0],note_temp[5]]:
                                if note[3]>current_time+reactiontime/framerate: #only replace if it's after reaction period.
        #                            log+='\n'+str(current_time)+": replacing q["+str(j)+']='+str(q[j])+' by q_temp['+str(i)+']='+str(q_temp[i])
                                    q[j]=q_temp[i]
                                # else:
                                #     print(str(current_time),' tried to replace ',note,' by ' ,note_temp, ' before reactiontime runs out')
                                q_temp_offloaded[i]+=1
                        if q_temp_offloaded[i]==0: #it's a prediction for a note never yet predicted
                            q+=[q_temp[i]]
                        if q_temp_offloaded[i]>1:
                            print(str(current_time),"at input beat: ",inputscorepositions[lastinputscorepositionIndex]," ERROR: duplicate ",str(q_temp[i]))
                inputq.task_done()
        
    def input_reading(stop_flag_accomp):
        while not stop_flag_accomp.is_set():
            try:
                msg = midi_in.get_message()
                if msg:
                    if msg[0][0] == NOTE_ON or msg[0][0] == NOTE_OFF:
                        inputq.put((msg[0][0], msg[0][1], msg[0][2], time.time_ns()))
            except (EOFError, KeyboardInterrupt):
                pass
    
    threading.Thread(target=input_reading, args=(stop_flag_accomp,)).start()  
    threading.Thread(target=calculating, args=(stop_flag_accomp,)).start()
    threading.Thread(target=worker, args=(stop_flag_accomp,)).start()

def show_about_dialog():
    about_dialog = tk.Toplevel(root)
    about_dialog.title("About")
    about_dialog.geometry("300x100")
    about_label = tk.Label(about_dialog, text="Musical Partner\n你的練琴好夥伴\nVersion 0.1\nCopyright © 2024\nNTHU AHG Music Group")
    about_label.pack(padx=10, pady=10)

root = tk.Tk()
root.title("Musical Partner - 你的練琴好夥伴")

# Menu Bar
menu_bar = tk.Menu(root)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Load Score to Melody", command=open_file_to_terminal1)
file_menu.add_command(label="Load Score to Accomp.", command=open_file_to_terminal2)
file_menu.add_command(label="Save Output Logs to File", command=lambda: save_terminal_output_to_file(terminal3))
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# MIDI Settings Menu
midi_settings = tk.Menu(menu_bar, tearoff=0)
midi_settings.add_command(label="Select MIDI Output Port", command=midi_output_select)
midi_settings.add_command(label="Select MIDI Input Port", command=midi_input_select)
midi_settings.add_command(label="Reset MIDI Settings", command=midi_reset)
menu_bar.add_cascade(label="MIDI Settings", menu=midi_settings)

# Tools Menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
tools_menu.add_command(label="MIDI Recorder", command=open_score_recorder)
tools_menu.add_command(label="MIDI Player", command=open_score_player)
menu_bar.add_cascade(label="Tools", menu=tools_menu)

# Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about_dialog)
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

# Label and ScrolledText for Terminal 1
label_terminal1 = tk.Label(root, text='Melody Monitor')
label_terminal1.grid(row=0, column=0, padx=10, pady=5)

terminal1 = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
terminal1.config(state=tk.NORMAL)
terminal1.grid(row=1, column=0, padx=10, pady=5)

# Label and ScrolledText for Terminal 2
label_terminal2 = tk.Label(root, text='Accompaniment Monitor')
label_terminal2.grid(row=0, column=1, padx=10, pady=5)

terminal2 = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
terminal2.config(state=tk.NORMAL)
terminal2.grid(row=1, column=1, padx=10, pady=10)

# Label and ScrolledText for Log Output
label_terminal3 = tk.Label(root, text='Output Logs')
label_terminal3.grid(row=0, column=2, padx=10, pady=5)

terminal3 = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
terminal3.config(state=tk.NORMAL)
terminal3.grid(row=1, column=2, padx=10, pady=5)

# Buttons
button_open1 = tk.Button(root, text="Load Score to Melody", width=30, command=open_file_to_terminal1)
button_open1.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

button_open2 = tk.Button(root, text="Load Score to Accompaniment", width=30, command=open_file_to_terminal2)
button_open2.grid(row=2, column=1, padx=5, pady=10, sticky='ew')

button_save_to_file = tk.Button(root, text="Save Output Logs to File", width=30, command=lambda: save_terminal_output_to_file(terminal3))
button_save_to_file.grid(row=2, column=2, padx=5, pady=10, sticky='ew')

button_clear1 = tk.Button(root, text="Clear Melody Monitor", width=20, command=lambda: clear_terminal(terminal1))
button_clear1.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

button_clear2 = tk.Button(root, text="Clear Accompaniment Monitor", width=20, command=lambda: clear_terminal(terminal2))
button_clear2.grid(row=3, column=1, padx=5, pady=10, sticky='ew')

button_clear3 = tk.Button(root, text="Clear Output Logs", width=25, command=lambda: clear_terminal(terminal3))
button_clear3.grid(row=3, column=2, padx=5, pady=10, sticky='ew')

button_run = tk.Button(root, text="Run", width=15, command=run_real_accomp)
button_run.grid(row=4, column=1, padx=5, pady=10, sticky='ew')

button_score_recorder = tk.Button(root, text="Score Recorder", width=15, command=open_score_recorder)
button_score_recorder.grid(row=4, column=2, padx=5, pady=10, sticky='ew')

button_score_player = tk.Button(root, text="Score Player", width=15, command=open_score_player)
button_score_player.grid(row=5, column=2, padx=5, pady=10, sticky='ew')

button_exit = tk.Button(root, text="Exit", width=15, command=root.quit)
button_exit.grid(row=5, column=1, padx=5, pady=10, sticky='ew')

#Frame 1
frame1 = tk.Frame(root)
frame1.grid(row=4, column=0, padx=10, pady=10)

label_current_midi_output_port = tk.Label(frame1, text="Current MIDI Output Port : ")
label_current_midi_output_port.grid(row=0, column=0)

entry_current_midi_output_port = tk.Entry(frame1, width=40)
entry_current_midi_output_port.grid(row=0, column=1,)

button_current_midi_output_port = tk.Button(frame1, text="Test", command=midi_output_test)
button_current_midi_output_port.grid(row=0, column=2, padx=5, pady=5)

#Frame 2
frame2 = tk.Frame(root)
frame2.grid(row=5, column=0, padx=10, pady=10)

label_current_midi_input_port = tk.Label(frame2, text="Current MIDI Input Port : ")
label_current_midi_input_port.grid(row=0, column=0)

entry_current_midi_input_port = tk.Entry(frame2, width=40)
entry_current_midi_input_port.grid(row=0, column=1)

button_current_midi_input_port = tk.Button(frame2, text="Test", command=midi_input_test)
button_current_midi_input_port.grid(row=0, column=2, padx=5, pady=5)

midi_init()

root.mainloop()