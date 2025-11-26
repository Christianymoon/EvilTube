import glob
from pytubefix import YouTube
from pytubefix import Playlist
from tkinter import *
from PIL import Image
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename
import urllib.request
import threading
from concurrent.futures import ThreadPoolExecutor, wait

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

stop_event = threading.Event()
converter_stop_event = threading.Event()

colors = {
    'background': "#000000",
    'enfasis': "#A10000",
    'background2': "#141414"
}

child_windows = []

class Converter(customtkinter.CTkToplevel):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.transient(root)
        self.grab_set()
        child_windows.append(self)
        self.folder_path = None
        self.dest_dir = None
        self.file_path = None
        self.ffmpeg_path = None
        self.iconbitmap("./assets/youtube.ico")
        self.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self))

        self.title("Evil YouTube - Conversor") 
        self.geometry("300x400")
        self.resizable(False, False)
        self.config(background=colors["background"])

        self.frame_buttons = customtkinter.CTkFrame(
            self, fg_color=colors["background2"], bg_color=colors["background"], corner_radius=15
        )
        self.frame_buttons.pack(side='top', expand=True, fill='both', pady=15, padx=15)

        self.open_folder_button = customtkinter.CTkButton(
            # set command parameter
            self.frame_buttons, text="Convertir Ruta", width=100, command=lambda: self.handle_conversor("Path"), fg_color=colors["enfasis"])
        self.open_folder_button.pack(side='left', expand=True)

        self.open_file = customtkinter.CTkButton(
            self.frame_buttons, text="Convertir Archivo", width=100, command=lambda: self.handle_conversor("File"), fg_color=colors["enfasis"], )
        self.open_file.pack(side='left', expand=True)

        self.info_frame = customtkinter.CTkFrame(
            self, fg_color=colors["background2"], bg_color=colors["background"], corner_radius=15
        )
        self.info_frame.pack(side='bottom', expand=True, fill='both', pady=15, padx=15)

        self.instructions = customtkinter.CTkLabel(
            self.info_frame, wraplength=200, text="1.- Selecciona ruta para convertir todos los archivos mp4 de una ruta a mp3, selecciona archivo si solo quieres convertir un archivo \n 2.- Selecciona la Ruta o el archivo mp4\n 3.- Selecciona la ruta de destino", text_color=colors["enfasis"])
        self.instructions.pack(side='top', expand=True, fill="x")

        # INSTALL MANAGER

        self.status_label = customtkinter.CTkLabel(
            self.info_frame, text="")
        self.status_label.pack_forget()

        self.progressbar = customtkinter.CTkProgressBar(
            self.info_frame, orientation="horizontal", progress_color=colors["enfasis"], corner_radius=10, mode='indeterminate')
        self.progressbar.pack_forget()

        # FFMPEG

        self.status_ffmpeg = customtkinter.CTkLabel(
            self.info_frame, text="")
        self.status_ffmpeg.pack_forget()

        self.progressbar_ffmpeg = customtkinter.CTkProgressBar(
            self.info_frame, orientation="horizontal", progress_color=colors["enfasis"], corner_radius=10, mode='indeterminate')
        self.progressbar.pack_forget()

    def close_window(self, _instance):
        converter_stop_event.set()
        if _instance in child_windows:
            print(f"instance obj {_instance} will be deleted")
            child_windows.remove(_instance)
        _instance.destroy()    

    def pick_dir(self):
        self.folder_path = askdirectory(intialdir=None)
        if not self.folder_path:
            messagebox.showinfo('Error', "Operation canceled by user")
            return None 
        return self.folder_path
    
    def pick_file(self):
        self.file_path = askopenfilename()
        if not self.file_path:
            messagebox.showinfo('Error', "Operation canceled by user")
            return None
        return self.file_path
    
    def pick_dest_dir(self):
        self.dest_dir = askdirectory(initialdir=None)
        if not self.dest_dir:
            messagebox.showinfo('Error', 'Operation canceled by user')
            return None
        return self.dest_dir
    
    def verify_ffmpeg(self):
        ffmpeg_local_bin = 'ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'
        if shutil.which(ffmpeg_local_bin) is not None: # Exist 
            self.ffmpeg_path = os.path.abspath(ffmpeg_local_bin)
            return True
        return False
    
    def install_ffmpeg_thread(self):
        t1 = threading.Thread(target=self.install_ffmpeg, daemon=True)
        t1.start()

    def install_ffmpeg(self):
        repository = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

        # Handle UI envents
        self.progressbar_ffmpeg.forget()
        self.status_ffmpeg.forget()
        self.status_label.pack(side="top", fill="x", padx=15, pady=15)
        self.progressbar.pack(side="bottom", fill="x", padx=15, pady=15)

        default_filename = "ffmpeg.zip"
        response = requests.get(repository, stream=True)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', None))
            chunk_size = 100000
            bytes_downloaded = 0
            if total_size is not None:
                self.progressbar.configure(mode='determinate')
            else:
                self.progressbar.start()

            self.status_label.configure(
                text="Descargando FFMPEG porfavor espere...")
            with open(default_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    if total_size is not None:
                        bytes_downloaded += chunk_size
                        percentage = (bytes_downloaded / total_size)
                        self.progressbar.set(percentage)

            # Once installed unzip ffmpeg on the same directory
            self.status_label.configure(
                text="Descomprimiendo FFMPEG...")
            with zipfile.ZipFile('ffmpeg.zip', 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname('ffmpeg.zip'))

            self.status_label.configure(text="Eliminando archivo zip...")
            os.remove("ffmpeg.zip")
            self.status_label.configure(text="Completado")
            if self.verify_ffmpeg():
                messagebox.showinfo("FFMPEG Instalado", "FFMPEG se ha instalado correctamente")
            else:
                messagebox.showinfo("FFMPEG", "Ocurrio un error en la lectura del archivo")

            self.progressbar.stop()
        else:
            messagebox.showerror("Error", f"Ocurrio un error al descargar FFMPEG, codigo http: {response.status_code}")
            self.progressbar.stop()


    def handle_conversor(self, transcode_type):
        if not self.verify_ffmpeg():
            self.install_ffmpeg_thread()
            return
        
        
        self.progressbar.forget()
        self.status_label.forget()

        
        self.status_ffmpeg.configure(text="Convirtiendo")
        

        if transcode_type == "File":
            try:
                mp4_file = self.pick_file()
                if not mp4_file:
                    return
                dest_dir = self.pick_dest_dir()
                if mp4_file and dest_dir:
                    self.instructions.forget()
                    self.status_ffmpeg.pack(side="bottom", fill="x", pady=15, padx=15)
                    self.progressbar_ffmpeg.pack(side="top", fill="x", pady=15, padx=15)
                    self.progressbar_ffmpeg.start()
                    filename = os.path.splitext(os.path.basename(mp4_file))[0]
                    output_file = os.path.join(dest_dir, f"{filename}.mp3")
                    cmd = [
                        self.ffmpeg_path,
                        "-y",
                        "-i", str(mp4_file),
                        "-vn",
                        "-acodec", "libmp3lame",
                        "-ar", "44100",
                        "-ab", "128k",
                        "-f", "mp3",
                        str(output_file)
                    ]
                    self.run_ffmpeg(cmd)

            except Exception as e:
                messagebox.showerror("Error", f"Error mientras se ejecutaba ffmpeg: {e}")

                
        elif transcode_type == "Path":

            target_dir = self.pick_dir()
            dest_dir = self.pick_dest_dir()
            if target_dir and dest_dir:
                self.instructions.forget()
                self.status_ffmpeg.pack(side="bottom", fill="x", pady=15, padx=15)
                self.progressbar_ffmpeg.pack(side="top", fill="x", pady=15, padx=15)
                self.progressbar_ffmpeg.start()

                mp4_list = glob.glob(target_dir + "/*.mp4")
                t1 = threading.Thread(target=self.transcode_all, args=(mp4_list, )).start()
                

    def transcode_all(self, mp4_list):
        def worker(mp4_file):
            filename = os.path.splitext(os.path.basename(mp4_file))[0]
            output_file = os.path.join(self.dest_dir, f"{filename}.mp3")
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", str(mp4_file),
                "-vn",
                "-acodec", "libmp3lame",
                "-ar", "44100",
                "-ab", "128k",
                "-f", "mp3",
                str(output_file)
            ]

            self.run_ffmpeg(cmd, msg=False, use_thread=False)
        
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [executor.submit(worker, mp4_file) for mp4_file in mp4_list]
            wait(futures)


        self.progressbar_ffmpeg.stop()
        messagebox.showinfo("Info", "Archivos transcodificados con exito")
        

    def run_ffmpeg(self, cmd, msg=True, use_thread=True):

        def worker():
            self.current_process = subprocess.Popen(
                cmd,
            )
            status = self.current_process.wait()
            

            if msg:
                if status != 0:
                        messagebox.showerror("Error", "Error del Script ffmpeg")

                if status == 0:
                    self.progressbar_ffmpeg.stop()
                    messagebox.showinfo("Info", "Archivo convertido con exito")


        if use_thread:
            t1 = threading.Thread(target=worker, daemon=True).start()
        else:
            worker()



def open_conversor():
    app = Converter(root)

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
    except Exception as e:
        messagebox.showerror(
            "Find error", f"Url: {url} not is a valid youtube url, please set a valid url or check a new app update: {e}")
        return 
    get_thumbnail(video)
    # 4/11/2024 THIS METHOD GET A EXCEPTION pytube.exceptions.PytubeError
    # 25/11/2025 use pytubefix instead
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
    except Exception as e:
        messagebox.showerror("Network Error", f"{e}")

def download_playlist():
    video_list = entry_link.get()
    playlist = Playlist(video_list)
    filepath = askdirectory(initialdir=None)
    quantityes = 0

    if filepath != "":
        for url in playlist.video_urls:
            if stop_event.is_set():
                break
            try:
                video = get_video_object(url, playlist=True)
                download(video, filepath=filepath)
                quantityes += 1
                step = quantityes / len(playlist.video_urls)
                progressbar.set(step)
            except Exception as e:
                res = messagebox.askokcancel("Error", "El video no puede ser descargado por restriccion de edad ¿deseas omitirlo y continuar?")
                if not res:
                    return 
                continue
                
    else:
        messagebox.showerror("Error", "No se establecio ruta de descarga")

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
        t2 = threading.Thread(target=button_download_video, daemon=True)
        t2.start()
    if selectionplaylist.get() == 1:
        t3 = threading.Thread(target=download_playlist, daemon=True)
        t3.start()

def error_downloading():
    messagebox.showerror("YouTube Downloader", "Downloading Error")

def close_app():
    message_close = messagebox.askokcancel(
        "YouTube Downloader", "Closing YouTube Downloader")
    if message_close == True:
        stop_event.set()
        root.destroy()

def about_menu():
    message_about = messagebox.showinfo(
        "About", "Support on ChrisVergara7@outlook.com")

# ROOT
root = customtkinter.CTk()
root.title("EvilTube")
root.geometry("800x650")
root.resizable(True, True)
root.config(background=colors["background"])
root.iconbitmap("./assets/youtube.ico")

main_panel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background2"], bg_color=colors["background"])
main_panel.pack(fill="x", side="top", padx=30, pady=15)

label_link = customtkinter.CTkLabel(main_panel, text="", image=customtkinter.CTkImage(Image.open("./assets/youtube_logo.png"), size=(50, 50)), fg_color=colors["background2"])
label_link.pack(side="left", padx=10, pady=10)

entry_link = customtkinter.CTkEntry(
    main_panel, placeholder_text="Enlace de Youtube", corner_radius=15, width=300, height=50, text_color=colors["enfasis"], fg_color=colors["background2"])
entry_link.pack(expand=True, fill="x", padx=15, pady=15)

progressbar = customtkinter.CTkProgressBar(
    root, width=350, height=15, orientation="horizontal", mode="determinate", corner_radius=10, progress_color=colors["enfasis"])
progressbar.pack(fill="x", padx=30, pady=10)
progressbar.set(0)



selectionplaylist = IntVar()
selectionplaylist.set(0)

parent_paneel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background"], bg_color=colors["background"])
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

button_panel = customtkinter.CTkFrame(root, corner_radius=15, fg_color=colors["background"], bg_color=colors["background"])
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
    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()