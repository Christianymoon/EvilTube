from pytubefix import YouTube
from pytubefix import Playlist
from tkinter import *
from PIL import Image
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename
import urllib.request
import threading

import os
import customtkinter
import subprocess
import shutil
import requests
import zipfile

# Source - https://stackoverflow.com/a
# Posted by Noelkd, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-25, License - CC BY-SA 4.0
# Mac Os issue SSL Certificate

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("dark")

colors = {
    'background': "#000000",
    'enfasis': "#A10000",
    'background2': "#141414"
}

class Converter(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.folder_destination_path = None
        self.file_path = None
        self.ffmpeg_path = None

        self.title("Evil YouTube - Conversor") 
        self.geometry("300x400")
        self.resizable(False, False)

        self.frame_buttons = customtkinter.CTkFrame(
            self
        )
        self.frame_buttons.pack(side='top', expand=True, fill='both')

        self.open_folder_button = customtkinter.CTkButton(
            # set command parameter
            self.frame_buttons, text="Select path", width=100, command=self.define_path)
        self.open_folder_button.pack(side='left', expand=True)

        self.open_file = customtkinter.CTkButton(
            self.frame_buttons, text="Select file", width=100, command=self.select_file)
        self.open_file.pack(side='left', expand=True)

        self.info_frame = customtkinter.CTkFrame(
            self
        )
        self.info_frame.pack(side='top', expand=True, fill='both')

        self.instructions = customtkinter.CTkLabel(
            self.info_frame, text="1.- Select a option, convert multiple files or one file\n 2.- Select folder or file\n 3.- Select folder destination")
        self.instructions.pack(side='top', expand=True)

        # INSTALL MANAGER

        self.install_manager_frame = customtkinter.CTkFrame(
            self
        )
        self.install_manager_frame.pack_forget()

        self.status_label = customtkinter.CTkLabel(
            self.install_manager_frame, text=""
        )

        self.status_label.pack_forget()

        self.progressbar = customtkinter.CTkProgressBar(
            self.install_manager_frame, orientation="horizontal", progress_color='red', corner_radius=10, mode='indeterminate')
        self.progressbar.pack_forget()
        self.progressbar.set(0)

        # FFMPEG

        self.status_ffmpeg = customtkinter.CTkLabel(
            self.info_frame, text=""
        )
        self.status_ffmpeg.pack_forget()

        self.progressbar_ffmpeg = customtkinter.CTkProgressBar(
            self.info_frame, orientation="horizontal", progress_color='red', corner_radius=10, mode='indeterminate'
        )

        self.progressbar.pack_forget()

    def define_path(self):
        self.folder_path = askdirectory(intialdir=None)
        if not self.folder_path:
            messagebox.showinfo('Evil YouYube - Conversor',
                                "Operation canceled by user")
            return
        selection = messagebox.askokcancel(
            "Evil YouTube - Conversor", "You want convert all mp4 files to mp3 files for this folder?")
        if selection:
            self.convert_all_mp4_to_mp3()
        else:
            return

    def execute_ffmpeg(self, single_file=False):
        self.progressbar_ffmpeg.pack()
        self.progressbar_ffmpeg.start()
        self.status_ffmpeg.configure(text="Converting")
        self.status_ffmpeg.pack()
        if single_file:
            proc = subprocess.run(
                ['powershell.exe',
                 '.\convertmp4tomp3.ps1',
                 '-FfmpegPath',
                 self.ffmpeg_path,
                 '-File',
                 f'\'{self.file_path}\'',
                 '-DestinationFolderPath',
                 f'\'{self.folder_destination_path}\'']
            )

            if proc.returncode != 0:
                messagebox.showerror(
                    'Error during conversion', 'Error code: 4 script error')
            else:
                messagebox.showinfo('Files converted successfully',
                                    f'files converted sucessfully on {self.folder_destination_path}')

            self.progressbar_ffmpeg.stop()
        else:
            try:
                proc = subprocess.run(
                    ['powershell.exe',
                     '.\convertmp4tomp3.ps1',
                     '-FfmpegPath',
                     self.ffmpeg_path,
                     '-FolderPath',
                     f'\'{self.folder_path}\'',
                     '-DestinationFolderPath',
                     f'\'{self.folder_destination_path}\''])

                if proc.returncode != 0:
                    messagebox.showerror(
                        'Error during conversion', 'Error code: 3, Script error')
                else:
                    messagebox.showinfo(
                        'Files converted successfully', f'Files converted successfully on {self.folder_destination_path}')
            except OSError as e:
                messagebox.showerror('Error during conversion', e)
            finally:
                self.progressbar_ffmpeg.stop()

    def select_file(self):
        self.file_path = askopenfilename()
        if not self.file_path:
            messagebox.showinfo('Evil YouTube - Conversor',
                                "Operation canceled by user")
            return
        selection = messagebox.askokcancel(
            "Evil YouTube - Conversor", f"You want convert {self.file_path} to mp3?")
        if selection:
            self.convert_file_mp4_to_mp3()
        else:
            return

    def convert_all_mp4_to_mp3(self):
        if self.folder_path is None:
            return

        self.folder_destination_path = askdirectory(initialdir=None)

        # Use ffmpeg
        # Check if ffmpeg exists on the system

        relative_ffmpeg_bin = 'ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'

        if shutil.which(relative_ffmpeg_bin) is not None:
            self.ffmpeg_path = f'\'{os.path.abspath(relative_ffmpeg_bin)}\''

            # if shutil.which('ffmpeg.exe') is not None:
            #     self.ffmpeg_path = shutil.which('ffmpeg.exe')
            # Execute powershell script

            t5 = threading.Thread(target=self.execute_ffmpeg)
            t5.start()

        else:
            install_ffmpeg = messagebox.askokcancel(
                "Evil YouTube - Conversor", "Not ffmpeg exist in your system do you want install ffmpeg?")
            if install_ffmpeg:
                t4 = threading.Thread(target=self.install_ffmpeg)
                t4.start()
            else:
                return

    def install_ffmpeg(self):

        self.install_manager_frame.pack(side='top', fill="both", expand=True)
        self.progressbar.pack()
        self.status_label.pack()

        default_filename = "ffmpeg.zip"
        git = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

        response = requests.get(git, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', None))
            chunk_size = 100000
            bytes_downloaded = 0
            if total_size is not None:
                self.progressbar.configure(mode='determinate')
            else:
                self.progressbar.start()

            self.status_label.configure(
                text="Downloading ffmpeg please wait...")
            with open(default_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    if total_size is not None:
                        bytes_downloaded += chunk_size
                        percentage = (bytes_downloaded / total_size)
                        self.progressbar.set(percentage)

            # Once installed unzip ffmpeg on the same directory
            self.status_label.configure(
                text="Unziping ffmpeg on current directory")
            with zipfile.ZipFile('ffmpeg.zip', 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname('ffmpeg.zip'))

            messagebox.showinfo("ffmpeg installed",
                                "ffmpeg has been installed successfully")
            self.progressbar.stop()
        else:
            messagebox.showerror("Failed ffmpeg download",
                                 "ffmpeg can not be installed")
            self.progressbar.stop()

    def convert_file_mp4_to_mp3(self):
        if self.file_path is None:
            return

        self.folder_destination_path = askdirectory(initaldir=None)
        relative_ffmpeg_bin = 'ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'

        if shutil.which(relative_ffmpeg_bin) is not None:
            self.ffmpeg_path = f'\'{os.path.abspath(relative_ffmpeg_bin)}\''
            t6 = threading.Thread(target=self.execute_ffmpeg, kwargs={
                                  'single_file': True})
            t6.start()
        else:
            install_ffmpeg = messagebox.askokcancel(
                "Evil YouTube - Conversor", "Not ffmpeg exist in your system do you want install ffmpeg?")
            if install_ffmpeg:
                t4 = threading.Thread(target=self.install_ffmpeg)
                t4.start()
            else:
                return

def open_conversor():
    app = Converter()
    app.mainloop()

def update_progress(percentage):
    if percentage < 1:
        progressbar.set(percentage)
    else:
        progressbar.set(1)

def new_path():
    global filepath
    path = askdirectory(initialdir="./")
    filepath = path
    # statusbar["text"] = f"Route established in {filepath}"

def on_complete_function(stream, file_path):
    messagebox.showinfo("YouTube Downloader", "Download Completed")

def progress_function(s, chunk, bytes_remaining):
    percentage_complete = int(
        (s.filesize - bytes_remaining) / s.filesize * 100) * .01
    progressbar.set(percentage_complete)

def get_thumbnail(video_obj):
    response = urllib.request.urlopen(video_obj.thumbnail_url)
    thumbnail = Image.open(response)
    container = customtkinter.CTkImage(thumbnail, size=(400, 300))
    image_label.configure(image=container, text="")
    image_label.pack(expand=True, fill="both")

def set_label(video_obj):
    description_label.configure(text=str(video_obj.title) + "\n" + str(video_obj.author) + "\n" + str(video_obj.views) + " visitas")
    description_label.pack(expand=True, fill="x")

def get_video_object(url="", playlist=False):
    try:
        if not playlist:
            video = YouTube(url, on_progress_callback=progress_function)
            video.register_on_complete_callback(on_complete_function)
        else:
            video = YouTube(url)
    except:
        messagebox.showerror(
            "Find error", f"Url: {url} not is a valid youtube url, please set a valid url or check a new app update")
        return 
    get_thumbnail(video)
    # WARNING 4/11/2024 THIS METHOD GET A EXCEPTION pytube.exceptions.PytubeError
    set_label(video)
    filtracion = video.streams.filter(progressive=True,
                                      file_extension="mp4").order_by("resolution").desc()
    return filtracion

def download(filtracion, filepath=""):
    if filtracion == None:
        return
    if selection.get() == 1:
        video = filtracion.last()  # last // low quality
    if selection.get() == 2:
        video = filtracion.first()  # first // high quality
    try:
        video.download(output_path=filepath)
    except ConnectionError:
        messagebox.showerror("Network Error", "Internet connection lost")

def download_playlist():
    video_list = entry_link.get()
    playlist = Playlist(video_list)
    filepath = askdirectory(initialdir=None)
    quantityes = 0

    try:
        if filepath != "":
            for url in playlist.video_urls:

                video = get_video_object(url, playlist=True)
                download(video, filepath=filepath)
                quantityes += 1
                # Use percentage if use a different progressbar
                # total_percentage = ((quantityes / len(playlist.video_urls)) * 100)

                step = quantityes / len(playlist.video_urls)
                progressbar.set(step)
        else:
            messagebox.showerror("Error", "No path established")
    except:
        messagebox.showerror(
            "Playlist error", f"Playlist: {video_list} not is a valid YouTube playlist, please set a valid YouTube playlist or check a new app update")

def button_download_video():
    url = entry_link.get()
    filepath = askdirectory(initialdir=None)
    if filepath != "":
        video = get_video_object(url)
        download(video, filepath=filepath)
    else:
        messagebox.showerror("Error", "No path established")

def preview():
    url = entry_link.get()
    get_video_object(url)

def download_menu():
    if selectionplaylist.get() == 0:
        t2 = threading.Thread(target=button_download_video)
        t2.start()
    if selectionplaylist.get() == 1:
        t3 = threading.Thread(target=download_playlist)
        t3.start()

def error_downloading():
    messagebox.showerror("YouTube Downloader", "Downloading Error")

def close_app():
    message_close = messagebox.askokcancel(
        "YouTube Downloader", "Closing YouTube Downloader")
    if message_close == True:
        root.destroy()

def about_menu():
    message_about = messagebox.showinfo(
        "About", "Support on ChrisVergara7@outlook.com")

# ROOT
root = Tk()
root.title("EvilTube")
root.geometry("800x650")
root.resizable(True, True)
root.config(background=colors["background"])
root.iconbitmap("./assets/youtube.ico")

main_panel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background2"])
main_panel.pack(fill="x", side="top", padx=30, pady=15)

label_link = customtkinter.CTkLabel(main_panel, text="", image=customtkinter.CTkImage(Image.open("./assets/youtube_logo.png"), size=(50, 50)), fg_color=colors["background2"])
label_link.pack(side="left", padx=10, pady=10)

entry_link = customtkinter.CTkEntry(
    main_panel, placeholder_text="Enlace de Youtube", corner_radius=15, width=300, height=50, text_color=colors["enfasis"])
entry_link.pack(expand=True, fill="x", padx=15, pady=15)

progressbar = customtkinter.CTkProgressBar(
    root, width=350, height=15, orientation="horizontal", mode="determinate", corner_radius=10, progress_color=colors["enfasis"])
progressbar.pack(fill="x", padx=30, pady=10)
progressbar.set(0)



selectionplaylist = IntVar()
selectionplaylist.set(0)

parent_paneel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background"])
parent_paneel.pack(padx=15, pady=10, fill="x")

url_type_panel = customtkinter.CTkFrame(parent_paneel, corner_radius=20, fg_color=colors["background2"])
url_type_panel.pack(padx=15, pady=10, side="left", expand=True, fill="x")

url_quality_panel = customtkinter.CTkFrame(parent_paneel, corner_radius=20, fg_color=colors["background2"])
url_quality_panel.pack(padx=15, pady=10, side="right", expand=True, fill="x")

radiobutton_1 = customtkinter.CTkRadioButton(
    url_type_panel, text="Video", variable=selectionplaylist, value=0, fg_color=colors["enfasis"])
radiobutton_1.pack(padx=10, pady=10)

radiobutton_2 = customtkinter.CTkRadioButton(
    url_type_panel, text="Playlist", variable=selectionplaylist, value=1, fg_color=colors["enfasis"])
radiobutton_2.pack(padx=10, pady=10)

selection = IntVar()
selection.set(1)

radiobutton_3 = customtkinter.CTkRadioButton(
    url_quality_panel, text="Alta Calidad", variable=selection, value=1, fg_color=colors["enfasis"])
radiobutton_3.pack(padx=10, pady=10)

radiobutton_4 = customtkinter.CTkRadioButton(
    url_quality_panel, text="Baja Calidad", variable=selection, value=2, fg_color=colors["enfasis"])
radiobutton_4.pack(padx=10, pady=10)

button_panel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background"])
button_panel.pack(fill="x", padx=15, pady=10)

button_download = customtkinter.CTkButton(
    button_panel, text="Descargar", command=download_menu, fg_color=colors["enfasis"])
button_download.pack(side="left", padx=15)
button_preview = customtkinter.CTkButton(
    button_panel, text="Visualizar", command=preview, fg_color=colors["enfasis"])
button_preview.pack(side="right", padx=15)



thumbnail_frame = customtkinter.CTkFrame(root, fg_color=colors["background"], corner_radius=15)
thumbnail_frame.pack(expand=True, fill="x", padx=30, pady=10)

image_frame = customtkinter.CTkFrame(thumbnail_frame, fg_color=colors["background"])
image_frame.pack(side="left", fill="x")

description_frame = customtkinter.CTkFrame(thumbnail_frame, fg_color=colors["background"])
description_frame.pack(side="right", fill="x")

image_label = customtkinter.CTkLabel(image_frame)
description_label = customtkinter.CTkLabel(description_frame)




# barra menus
menu_bar = Menu(root)
root.config(menu=menu_bar, width=300, height=300)
# elements menu bar
FilesMenu = Menu(menu_bar, tearoff=0)
ToolsMenu = Menu(menu_bar, tearoff=0)
AboutMenu = Menu(menu_bar, tearoff=0)
# Add elements
menu_bar.add_cascade(label="Files", menu=FilesMenu)
menu_bar.add_cascade(label="Tools", menu=ToolsMenu)
menu_bar.add_cascade(label="About", menu=AboutMenu)
# add subelements Filemenu
FilesMenu.add_command(label="Path", command=new_path)
FilesMenu.add_separator()  # separator
FilesMenu.add_command(label="Close", command=close_app)
# add subelements Toolsmenu
# none
# add subelements Aboutmenu
AboutMenu.add_command(label="About", command=about_menu)
ToolsMenu.add_command(label="Mp4 to mp3 tool", command=open_conversor)
# Thumbnail label


if __name__ == "__main__":
    root.mainloop()
