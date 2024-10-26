from tkinter import *
from tkinter import ttk

import pygame
import random as rnd
import time
import os
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


class PlayerControls:  # Handles play, pause, next, previous buttons
    def __init__(self, parent_frame,parent_file_menu):
        self.parent_frame = parent_frame
        self.fileMenu = parent_file_menu
        self.buttons = []
        self.button_positions = [(0.0, 0.8), (0.0, 0.83), (0.0, 0.86),(0.0, 0.89), (0.0, 0.92)]
        
        self.current_Song = None        
        self.isPlaying = True 
        self.ispaused = False
        self.random_file = []
        self.num = 0
        pygame.mixer.music.load(self.get_file_to_play())
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
        self.create_Button("Next", command=self.next)
        self.create_Button("Back", command=self.back)
        self.create_Button("Quit", command=self.quit)
         
    def get_file_to_play(self):
        files = self.fileMenu.list_files() #get all the files in the downloaded_music folder
        random_index = rnd.randint(0, len(files) - 1) # get a randome number
        self.random_file.append(files[random_index]) #save the file location so that if the user want to go back to the previous song they can       
        return self.random_file[self.num]
     
    def button_state(self):
        if self.isPlaying and not self.ispaused: #if a song is playing and the pause button wasnt clicked
            if not pygame.mixer.music.get_busy():  # Check if the music is still playing                
                self.is_playing = False # if no music is playing set the flag for playing music to false
            pygame.mixer.music.unpause() #if a song is playing and the pause button wasnt clicked then play music
        elif self.ispaused: #is the pause button was clicked 
            pygame.mixer.music.pause() #pause the music
            
        self.parent_frame.after(500, self.button_state) #repeat this every 500 miliseconds
                          
    def play(self):  #function for the play button      
        self.ispaused = False #when the play button is clicked set the ispaused flag to false
        self.isPlaying = True #and the isplaying flag to true so that music can play                                                                      
    def pause(self): #function for the pause button       
        if self.isPlaying: #the pause button should only work while music is being played
            self.ispaused = True #if music is being played set the paused flag to true                  
    def next(self): #function for the next button       
        self.num +=1 #decrease the value of the num variable so that a new file loaction can be saved
        pygame.mixer.music.load(self.get_file_to_play()) #get the new file location and load it into the mixer
        pygame.mixer.music.play() #play the new file location music              
    def back(self): #decrease the value of the num variable so that the previous song can be played        
        if self.num > 0: #as the value of num cant be -0 we have to make sure its always greater then 0 when reducing its value
            self.num-=1 #if its greater then reduce the value
            pygame.mixer.music.load(self.get_file_to_play())
            pygame.mixer.music.play()
        else:
            self.ispaused = False 
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
        self.folder_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Downloaded_Music'))          
        self.files = self.read_files(self.folder_path)        
        self.current_file = None  
                              
    @staticmethod
    def read_files(folder_path):
        files = []
        for entry in os.listdir(folder_path):
            if entry.lower().endswith(('.ogg', '.wav','.mp3')):
                files.append(os.path.join(folder_path, entry))
        return files
    
    def list_files(self): 
        print("files")       
        return self.files
    
class NowPlayingDisplay:  # Displays current song information (title, artist)
    pass
    
if __name__ == "__main__":
    # Initialize and start the music player app
    app = MusicPlayerApp()
    app.start()
