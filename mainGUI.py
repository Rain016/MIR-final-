import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from rtmidi import MidiIn, MidiOut

def open_file_to_terminal1():
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filepath:
        with open(filepath, "r") as file:
            content = file.read()
            terminal_output1.delete("1.0", tk.END)
            terminal_output1.insert(tk.END, content)

def open_file_to_terminal2():
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filepath:
        with open(filepath, "r") as file:
            content = file.read()
            terminal_output2.delete("1.0", tk.END)
            terminal_output2.insert(tk.END, content)

def clear_terminal1():
    terminal_output1.delete("1.0", tk.END)

def clear_terminal2():
    terminal_output2.delete("1.0", tk.END)

def play_midi():
    print_to_log("Playing MIDI...")

def stop_midi():
    print_to_log("Stopping MIDI...")

def reset_midi():
    print_to_log("Resetting MIDI...")

def select_input_port():
    # Get available MIDI input ports
    midi_in = MidiIn()
    input_ports = midi_in.get_ports()

    # Create a new window to select input port
    input_port_window = tk.Toplevel(root)
    input_port_window.title("Select MIDI Input Port")

    # Variable to store selected port
    selected_port = tk.StringVar(root)
    selected_port.set(input_ports[0])  # Set default value

    # Combobox for selecting input port
    input_port_combobox = ttk.Combobox(input_port_window, textvariable=selected_port, values=input_ports, state="readonly")
    input_port_combobox.pack()

    # Function to handle selection change
    def on_select(event):
        selected_port_name = selected_port.get()
        entry_current_midi_input_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_input_port.insert(tk.END, selected_port_name)  # Insert selected port name into Entry
        print_to_log(f"Selected MIDI input port: {selected_port_name}")

    # Bind event to selection change
    input_port_combobox.bind("<<ComboboxSelected>>", on_select)


def select_output_port():
    # Get available MIDI output ports
    midi_out = MidiOut()
    output_ports = midi_out.get_ports()

    # Create a new window to select output port
    output_port_window = tk.Toplevel(root)
    output_port_window.title("Select MIDI Output Port")

    # Variable to store selected port
    selected_port = tk.StringVar(root)
    selected_port.set(output_ports[0])  # Set default value

    # Combobox for selecting output port
    output_port_combobox = ttk.Combobox(output_port_window, textvariable=selected_port, values=output_ports, state="readonly")
    output_port_combobox.pack()

    # Function to handle selection change
    def on_select(event):
        selected_port_name = selected_port.get()
        entry_current_midi_output_port.delete(0, tk.END)  # Clear existing content
        entry_current_midi_output_port.insert(tk.END, selected_port_name)  # Insert selected port name into Entry
        print_to_log(f"Selected MIDI output port: {selected_port_name}")

    # Bind event to selection change
    output_port_combobox.bind("<<ComboboxSelected>>", on_select)

def print_to_log(message):
    log_output.insert(tk.END, message + "\n")
    log_output.see(tk.END)

def clear_realtime_logs():
    log_output.delete("1.0", tk.END)

def save_realtime_logs_to_file():
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if filepath:
        with open(filepath, "w") as file:
            file.write(log_output.get("1.0", tk.END))

def open_score_recorder():
    score_recorder_window = tk.Toplevel(root)
    score_recorder_window.title("Score Recorder")

    # Label and ScrolledText for Recorder Terminal
    label_terminal_recorder = tk.Label(score_recorder_window, text='Score Recorder Terminal')
    label_terminal_recorder.grid(row=0, column=0, padx=10, pady=5)

    recorder_terminal = scrolledtext.ScrolledText(score_recorder_window, wrap=tk.WORD, width=60, height=30)
    recorder_terminal.grid(row=1, column=0, padx=10, pady=5)

    # Buttons
    button_run = tk.Button(score_recorder_window, text="Run", width=15)
    button_run.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

    button_stop = tk.Button(score_recorder_window, text="Stop", width=15)
    button_stop.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

    button_save = tk.Button(score_recorder_window, text="Save", width=15)
    button_save.grid(row=4, column=0, padx=5, pady=10, sticky='ew')

    button_close = tk.Button(score_recorder_window, text="Close", width=15, command=score_recorder_window.destroy)
    button_close.grid(row=5, column=0, padx=5, pady=10, sticky='ew')

def open_score_player():
    score_player_window = tk.Toplevel(root)
    score_player_window.title("Score Player")
    
    # Label and ScrolledText for Player Terminal
    label_terminal_recorder = tk.Label(score_player_window, text='Score Recorder Terminal')
    label_terminal_recorder.grid(row=0, column=0, padx=10, pady=5)

    recorder_terminal = scrolledtext.ScrolledText(score_player_window, wrap=tk.WORD, width=60, height=30)
    recorder_terminal.grid(row=1, column=0, padx=10, pady=5)

    # Buttons
    button_run = tk.Button(score_player_window, text="Play", width=15)
    button_run.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

    button_stop = tk.Button(score_player_window, text="Stop", width=15)
    button_stop.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

    button_close = tk.Button(score_player_window, text="Close", width=15, command=score_player_window.destroy)
    button_close.grid(row=4, column=0, padx=5, pady=10, sticky='ew')

root = tk.Tk()
root.title("你的音樂好夥伴")

# Menu Bar
menu_bar = tk.Menu(root)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Input Port Menu
input_port_menu = tk.Menu(menu_bar, tearoff=0)
input_port_menu.add_command(label="Select MIDI Input Port", command=select_input_port)
menu_bar.add_cascade(label="Input Port", menu=input_port_menu)

# Output Port Menu
output_port_menu = tk.Menu(menu_bar, tearoff=0)
output_port_menu.add_command(label="Select MIDI Output Port", command=select_output_port)
menu_bar.add_cascade(label="Output Port", menu=output_port_menu)

# Tools Menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
tools_menu.add_command(label="MIDI Recorder", command=open_score_recorder)
tools_menu.add_command(label="MIDI Player", command=open_score_player)
menu_bar.add_cascade(label="Tools", menu=tools_menu)

# Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About")
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

# Label and ScrolledText for Terminal 1
label_terminal1 = tk.Label(root, text='Melody Monitor')
label_terminal1.grid(row=0, column=0, padx=10, pady=5)

terminal_output1 = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
terminal_output1.config(state=tk.NORMAL)
terminal_output1.grid(row=1, column=0, padx=10, pady=5)

# Label and ScrolledText for Terminal 2
label_terminal2 = tk.Label(root, text='Accompaniment Monitor')
label_terminal2.grid(row=0, column=1, padx=10, pady=5)

terminal_output2 = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
terminal_output2.config(state=tk.NORMAL)
terminal_output2.grid(row=1, column=1, padx=10, pady=10)

# Label and ScrolledText for Log Output
label_terminal_recorder = tk.Label(root, text='Realtime Monitor')
label_terminal_recorder.grid(row=0, column=2, padx=10, pady=5)

log_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=30)
log_output.config(state=tk.NORMAL)
log_output.grid(row=1, column=2, padx=10, pady=5)

# Buttons
button_open1 = tk.Button(root, text="Load Sheet Music to Melody Monitor", width=30, command=open_file_to_terminal1)
button_open1.grid(row=2, column=0, padx=5, pady=10, sticky='ew')

button_open2 = tk.Button(root, text="Load Sheet Music to Accompaniment Monitor", width=30, command=open_file_to_terminal2)
button_open2.grid(row=2, column=1, padx=5, pady=10, sticky='ew')

button_save_to_file = tk.Button(root, text="Save Realtime Monitor to File", width=30, command=save_realtime_logs_to_file)
button_save_to_file.grid(row=2, column=2, padx=5, pady=10, sticky='ew')

button_clear1 = tk.Button(root, text="Clear Melody Monitor", width=20, command=clear_terminal1)
button_clear1.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

button_clear2 = tk.Button(root, text="Clear Accompaniment Monitor", width=20, command=clear_terminal2)
button_clear2.grid(row=3, column=1, padx=5, pady=10, sticky='ew')

button_clear3 = tk.Button(root, text="Clear Realtime Monitor", width=25, command=clear_realtime_logs)
button_clear3.grid(row=3, column=2, padx=5, pady=10, sticky='ew')

button_reset_midi = tk.Button(root, text="Reset MIDI", width=15, command=reset_midi)
button_reset_midi.grid(row=4, column=0, padx=5, pady=9, sticky='ew')

button_play = tk.Button(root, text="Play", width=15, command=play_midi)
button_play.grid(row=4, column=1, padx=5, pady=10, sticky='ew')

button_score_recorder = tk.Button(root, text="Score Recorder", width=15, command=open_score_recorder)
button_score_recorder.grid(row=4, column=2, padx=5, pady=10, sticky='ew')

button_stop = tk.Button(root, text="Stop", width=15, command=stop_midi)
button_stop.grid(row=5, column=1, padx=5, pady=10, sticky='ew')

button_score_player = tk.Button(root, text="Score Player", width=15, command=open_score_player)
button_score_player.grid(row=5, column=2, padx=5, pady=10, sticky='ew')

button_exit = tk.Button(root, text="Exit", width=15, command=root.quit)
button_exit.grid(row=6, column=1, padx=5, pady=10, sticky='ew')

#Frame 1
frame1 = tk.Frame(root)
frame1.grid(row=5, column=0, padx=10, pady=10)

label_current_midi_input_port = tk.Label(frame1, text="Current MIDI Input Port : ")
label_current_midi_input_port.grid(row=0, column=0)

entry_current_midi_input_port = tk.Entry(frame1, width=40)
entry_current_midi_input_port.grid(row=0, column=1)

frame2 = tk.Frame(root)
frame2.grid(row=6, column=0, padx=10, pady=10)

label_current_midi_output_port = tk.Label(frame2, text="Current MIDI Output Port : ")
label_current_midi_output_port.grid(row=0, column=2)

entry_current_midi_output_port = tk.Entry(frame2, width=40)
entry_current_midi_output_port.grid(row=0, column=3,)

root.mainloop()