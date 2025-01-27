from DownloadMusic import MusicDownload

from tkinter import *
from tkinter import ttk, StringVar, CENTER, TOP
from tkinter.messagebox import askyesno
from mutagen import File

import pygame
import random as rnd
import time
import os
import math
import threading
import keyboard


class MusicPlayerApp:  # Main class for the application
    def __init__(self):
        # Initialize the main window
        self.root = Tk()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1/100)        
        self.root.title("Music Player")
        self.root.geometry("800x600")
        # Setup frame for layout
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.pack(fill='both', expand=True)
        
        # Create UI components (Player controls) 
        self.FileMenu = FileMenu(self.frm)       
        self.playerControls = PlayerControls(self.frm,self.FileMenu)        
        self.volumeControl = VolumeControl(self.frm)
        

        # Bind window resize event to dynamically adjust button and slider positions
        self.root.bind("<Configure>", self.update_pos)
        self.playerControls.show_playlist()
        self.root.bind("<ButtonRelease-1>", self.volumeControl.get_vol)                

    def update_pos(self, event=None):
        # Update window size
        self.width = self.root.winfo_width()
        self.length = self.root.winfo_height()

        # Resize and reposition the elements dynamically
        self.playerControls.update_positions()
        self.volumeControl.update_slider_position()                
    def start(self):        
        self.root.mainloop()
class download:
    def __init__(self) -> None:
        self.md = MusicDownload()  
    def inputWindow(self):
        self.root = Toplevel() 
        self.root.title("Download")
        self.root.geometry("400x200")
        
        self.frm = ttk.Frame(self.root, padding=10)
        self.frm.pack(fill='both', expand=True)
        
        self.input_text = StringVar()
        
        # Entry widget for user input
        self.text = ttk.Entry(self.frm, textvariable=self.input_text, justify=CENTER)
        self.text.focus_force()  # Focus on the text entry
        self.text.pack(side=TOP, ipadx=30, ipady=6)

        # Button that triggers the confirmation dialog and download
        self.save = ttk.Button(self.root, text='Save', command=self.confirm_save)
        self.save.pack(side=TOP, pady=10)
        
        self.root.mainloop()

    def confirm_save(self):
        if askyesno('Confirm', 'Do you want to save?'):
            music = self.input_text.get()  # Retrieve the current input
            print(f"Music input: '{music}'")  # Debug output to check input
            self.download(music)  

    def download(self, music):
        if music:
            print(f"Downloading: {music}")
            self.md.download(music)
        else:
            print("No input provided for downloading.")  

class PlayerControls:  # Handles play, pause, next, previous buttons
    def __init__(self, parent_frame,parent_file_menu):
        self.download = download()
        self.parent_frame = parent_frame
        self.fileMenu = parent_file_menu
        self.buttons = []
        self.button_positions = [(0.0, 0.8), (0.0, 0.83),(0.0, 0.86), (0.0, 0.89),(0.0, 0.92), (0.0, 0.95),(0.0,0.6)]        
        
        self.current_Song = None               
        self.isPlaying = True 
        self.ispaused = False
        self.isFastForward = False
        self.random_file = []
        self.num = 0
        self.new_position=0 
                
        self.song = self.get_file_to_play()
        pygame.mixer.music.load(self.song)
        pygame.mixer.music.play()                
        
        self.create_display()
        self.button_state()
        
    def create_Button(self, text, command):
        button = ttk.Button(self.parent_frame, text=text, command=command)        
        self.buttons.append(button)

    def create_display(self):
        # Add buttons for player controls, with positions and sizes as percentages of window size
        self.create_Button("Play", command=self.play)
        self.create_Button("Pause",command=self.pause)        
        self.create_Button("FastForward",command=self.fast_forward)
        self.create_Button("Next", command=self.next)
        self.create_Button("Back", command=self.back)
        self.create_Button("Quit", command=self.quit)  
        self.create_Button("download",command=self.download.inputWindow)  
    #functions to display playlists      
    def get_playlists(self):
        playlists = self.fileMenu.read_playlist() 
        return playlists           
    def show_playlist(self):
        self.selected_option = StringVar()
        self.selected_option.set("Select an option") 
        
        options = self.get_playlists()
        optionMenu = ttk.OptionMenu(self.parent_frame,self.selected_option,options[0],*options)   
        optionMenu.pack(pady=20)
        self.selected_option.trace("w",self.update_song_list)
    def update_song_list(self,*args):        
        selected_value = self.selected_option.get()
        self.fileMenu.update_song_path(selected_value)        
        self.fileMenu.list_files()
    #functions for playing music and music buttons
    def get_audio_length(self, file_path):
        audio = File(file_path)
        if audio is not None and audio.info is not None:
            return audio.info.length  # Length in seconds
        return 0  # Return 0 if length can't be determined         
        
    def get_file_to_play(self):
        files = self.fileMenu.list_files() #get all the files in the downloaded_music folder
        random_index = rnd.randint(0, len(files) - 1) # get a randome number
        self.song = files[random_index]
        self.random_file.append(files[random_index]) #save the file location so that if the user want to go back to the previous song they can                
        return self.random_file[self.num]
     
    def button_state(self):   
        self.end_of_song()     
        if self.isPlaying and not self.ispaused: #if a song is playing and the pause button wasnt clicked            
            if not pygame.mixer.music.get_busy():  # Check if the music is still playing                
                self.isPlaying = False # if no music is playing set the flag for playing music to false
            pygame.mixer.music.unpause() #if a song is playing and the pause button wasnt clicked then play music
        elif self.ispaused: #is the pause button was clicked 
            pygame.mixer.music.pause() #pause the music          
        self.parent_frame.after(500, self.button_state) #repeat this every 500 miliseconds   
                              
    def play(self):
        print("Playing song")
        if self.ispaused:  # If the song was paused, simply unpause it
            pygame.mixer.music.unpause()
            self.ispaused = False
        elif not self.isPlaying:  # If no song is currently playing, load and play a new song
            self.isPlaying = True
            song_path = self.get_file_to_play()
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            # Set the start time and song length
            self.start_time = time.time()
            self.current_song_length = pygame.mixer.Sound(song_path).get_length()             
                                                                      
    def pause(self): #function for the pause button       
        if self.isPlaying: #the pause button should only work while music is being played
            self.ispaused = True #if music is being played set the paused flag to true                  
    def next(self): #function for the next button       
        self.num +=1 #decrease the value of the num variable so that a new file loaction can be saved
        self.new_position = 0
        pygame.mixer.music.load(self.get_file_to_play()) #get the new file location and load it into the mixer
        pygame.mixer.music.play() #play the new file location music              
    def back(self): #decrease the value of the num variable so that the previous song can be played        
        if self.num > 0: #as the value of num cant be -0 we have to make sure its always greater then 0 when reducing its value
            self.num-=1 #if its greater then reduce the value
            pygame.mixer.music.load(self.get_file_to_play())
            pygame.mixer.music.play()
        else:
            self.ispaused = False 
    def fast_forward(self):
        if self.isPlaying:  # Ensure fast forward only works while music is playing
            self.isFastForward = True
            # Increment the absolute position by 10 seconds
            self.new_position += 10
            song_length = math.ceil(self.get_audio_length(self.song))
            
            # Ensure the new position doesn't exceed the song length
            if self.new_position < song_length-10:
                #pygame.mixer.music.stop()  # Stop current playback
                pygame.mixer.music.play(start=self.new_position)  # Restart from new position
            else:
                print("Cannot fast forward beyond the song length.")
                
    def end_of_song(self):
        if self.isPlaying:
            song_length = math.ceil(self.get_audio_length(self.song))
            
            # Track position based on the manual `new_position`
            if self.isFastForward:
                # If we fast-forwarded, keep the new position as current position
                current_position = self.new_position
                self.isFastForward = False  # Reset the fast-forward flag
            else:
                # Otherwise, update based on `get_pos()`
                current_position = self.new_position + (pygame.mixer.music.get_pos() // 1000) 
            print(f"current {current_position} length {song_length}")           
            # Check if the end of the song is reached
            if current_position >= song_length-1 or current_position < 0:
                pygame.mixer.music.stop()
                print("song stopped")                
                self.next()  # Move to the next song                     
    def update_positions(self):        
        for i, button in enumerate(self.buttons):#loop through all buttons
            x_percent, y_percent = self.button_positions[i] #get their positions reletive to the screen
            button.place_configure(relx=x_percent, rely=y_percent, relwidth=0.1, relheight=0.03) #set their new positions
    def quit(self):#function for the quit button
        exit() #terminates the program


class VolumeControl:  # Manages volume slider and mute button
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame                
        self.volume_slider = None 
        self.volume = 1              
        self.create_volume_slider()        

    def create_volume_slider(self):
        # Create a slider for volume control
        self.volume_slider = Scale(self.parent_frame, from_=0, to=100, orient=HORIZONTAL,label="Volume") 
        self.volume_slider.set(self.volume)                
    def get_vol(self, event=None):
        """used to update the volume based on the slider value"""
        self.volume = self.volume_slider.get() 
        if 0 <= self.volume <= 100:                       
            pygame.mixer.music.set_volume(self.volume / 100.0)
        else:
            print("Volume must be between 0 and 100\n")                      
    def update_slider_position(self):
        # Dynamically adjust the slider position based on window size
        self.volume_slider.place_configure(relx=0.8, rely=0.9, relwidth=0.1)   

class FileMenu:  # Handles file operations (e.g., loading songs, saving playlists)
    def __init__(self,parent_frame):
        self.parent_frame = parent_frame
        self.folder_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'playlists','Downloaded_Music'))          
        self.files = self.read_files(self.folder_path)        
        self.current_file = None  
        
    def update_song_path(self,playlist):
        self.files = []
        self.folder_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'playlists',playlist)) 
        self.files = self.read_files(self.folder_path)
        
    def read_playlist(self): 
        folder_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'playlists')) 
        playlists=[]      
        for entry in os.listdir(folder_path):
            playlists.append(entry)     
        return playlists  
                               
    @staticmethod
    def read_files(folder_path):
        files = []
        for entry in os.listdir(folder_path):
            if entry.lower().endswith(('.ogg', '.wav','.mp3','webm')):
                files.append(os.path.join(folder_path, entry))
        return files    
    def list_files(self):                
        return self.files 
         
class NowPlayingDisplay:  # Displays current song information (title, artist)
    pass
class ShortcutManager: #allow the player to have the ability to change keybinds for different functions
    def __init__(self) -> None:
        pass
    def setHotkey(self,key,command):
        keyboard.add_hotkey(key,command)
    pass
if __name__ == "__main__":
    # Initialize and start the music player app
    app = MusicPlayerApp()
    app.start()