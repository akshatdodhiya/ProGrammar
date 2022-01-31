"""

App Name: Pro Grammar for MACOS
Version: 1.2
Developer: Akshat Dodhiya
Developer's GitHub Profile: https://github.com/akshatdodhiya
Website: https://akshatdodhiya.blogspot.com | https://akshatdodhiya.tech

"""

# TODO: Add difficulty level choice for user
# TODO: Resolve error when the app is tried to run offline -->
#  self.tk.call(_tkinter.TclError: image "pyimage1" doesn't exist
# TODO: Add a textbox for the user to enter words in it and then
#  automatically check for spellings and give marks accordingly
# TODO: Add a feature to view the meaning of the words while displaying the spellings in the end

import os
import time
import random
import webbrowser
from tkinter import *
from tkinter.messagebox import *
from selenium import webdriver
from gtts.tts import gTTS
from playsound import playsound, PlaysoundException
import requests
from PIL import ImageTk
from requests.exceptions import ConnectionError
import sys

online_mode = 0  # Mode in which user will get spellings, online -> 1 and offline -> 0


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def check_internet():
    """
    Checks internet connection of the user and sets he app mode likewise
    """
    global online_mode
    try:
        requests.get("https://google.com/").status_code
    except ConnectionError:
        online_mode = 0
        msg_window = Tk()
        msg_window.withdraw()
        showinfo(title="No Internet!", message="Switching to offline mode... :)")
    else:
        online_mode = 1


class Intro:
    """
    Intro class to show the introduction and starting animation of the app
    """

    def __init__(self):
        # Create main window and show intro of the app
        self.intro = Tk()
        self.intro.config(bg="black")
        self.intro.title("Pro Grammar - Improve your grammar")
        self.intro.iconbitmap(resource_path("Images/Icon.ico"))
        self.intro.title("Loading your app")
        self.intro.attributes("-fullscreen", True)
        self.intro.focus_force()

        self.frameCnt = 25
        self.frames = [ImageTk.PhotoImage(master=self.intro, file=resource_path('Images/intro.gif'),
                                  format='gif -index %i' % i) for i in range(self.frameCnt)]

        self.label = Label(self.intro)
        self.label.pack(expand=YES, fill=BOTH)
        self.intro.after(0, self.update, 0)

        playsound(resource_path(r"Sound Effects/intro.mp3").replace(" ", "%20"), False)
        self.intro.mainloop()

    def update(self, ind):
        frame = self.frames[ind]
        ind += 1
        if ind == self.frameCnt:
            self.frames.clear()
            self.label.destroy()
            self.loading_screen()

        else:
            self.label.configure(image=frame)
            self.intro.after(125, self.update, ind)

    def loading_screen(self):
        self.intro.config(bg="black")
        playsound(resource_path("Sound Effects/loading.mp3").replace(" ", "%20"), False)
        self.intro.title("Loading your app")
        self.intro.attributes("-fullscreen", True)
        self.intro.focus_force()

        # Loading text
        Label(self.intro, text="Loading your app :)", font="Times", bg="black", fg="#FFBD09").place(x=490, y=320)
        Label(self.intro, text="© Akshat Dodhiya", font=("Times", 20), bg="black", fg="#FFBD09").place(x=550, y=550)

        # Loading block
        for i in range(16):
            Label(self.intro, bg="#1F2732", width=2, height=1).place(x=(i + 22) * 22, y=350)

        # Update intro to see animation
        self.intro.update()
        self.intro.focus_force()
        self.play_animation()

        self.intro.mainloop()

    # Animation
    def play_animation(self):
        for _ in range(3):
            for j in range(16):
                # Make block yellow
                Label(self.intro, bg="#FFBD09", width=2, height=1).place(x=(j + 22) * 22, y=350)
                time.sleep(0.06)
                self.intro.update_idletasks()

                # Make blocks normal again
                Label(self.intro, bg="#1F2732", width=2, height=1).place(x=(j + 22) * 22, y=350)

        # Destroy window after task is completed
        self.intro.destroy()


class App(Intro):
    def __init__(self, restart=False):
        if online_mode:
            options = webdriver.ChromeOptions()
            options.headless = True
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            self.driver = webdriver.Chrome(options=options, service_log_path=os.devnull)
            self.driver.get('https://wordcounter.net/random-word-generator')  # Website to generate words
            self.word_list = []  # list to store all the generated words

        if os.path.exists(resource_path("Audio")):
            self.clean_residuals(quit_program=False)

        if not restart:
            Intro.__init__(self)

        # -------------------------------

        self.root = Tk()
        # self.root = Toplevel()

        self.frame = Frame(master=self.root)
        self.frame.config(bg="#3a3d3b")
        self.frame2 = Frame(self.root)
        self.frame2.config(bg="#3a3d3b")
        self.menu = Menu(self.root)
        self.label_text = Label(self.root, text="Enter the number of words you want to practice:", font=("Times", 25),
                                bg="#3a3d3b", fg="#FFBD09").pack(padx=50, pady=20)
        self.no_of_words = Entry(self.root, width=50, takefocus=True)
        self.no_of_words.focus_set()
        self.reg = self.no_of_words.register(self.callback)
        self.no_of_words.config(validate="key", validatecommand=(self.reg, '%P'))
        self.no_of_words.pack(pady=15)
        self.img_start = ImageTk.PhotoImage(file=resource_path("Images/start.png"))
        self.btn_start = Button(self.root, command=self.get_words)
        self.btn_start.config(image=self.img_start)
        self.btn_start["bg"] = "#3a3d3b"
        self.btn_start["border"] = "3"
        self.btn_start["state"] = DISABLED

        self.root.bind("<Return>", lambda _: self.get_words())
        self.root.bind("<Alt-Key-F4>", lambda _: self.clean_residuals(quit_program=True))

        # Assets to be used afterwards
        self.btn_read = Button(self.root, height=3, width=20, text="Read Again", font=("Arial", 15), bg="#FFBD09",
                               command=lambda: self.speak(again=True))

        self.btn_prev = Button(self.root, height=3, width=20, text="Previous", font=("Arial", 15), bg="#FFBD09",
                               command=lambda: self.speak(back=True))

        self.btn_next = Button(self.root, height=3, width=20, text="Next", font=("Arial", 15), bg="#FFBD09",
                               command=self.speak)
        self.btn_end = Button(self.root, height=3, width=20, text="Skip others and End", font=("Arial", 15),
                              bg="#FFBD09", command=lambda: self.show_spellings())

        self.img_quit = ImageTk.PhotoImage(file=resource_path("Images/quit.png"))
        self.btn_quit_icon = Button(self.root, image=self.img_quit,
                                    command=lambda: self.clean_residuals(quit_program=True))

        self.img_restart = ImageTk.PhotoImage(file=resource_path("Images/restart.png"))
        self.btn_restart = Button(self.root, image=self.img_restart,
                                  command=self.restart_app)

        self.spellings_editor = Text(self.root, background="#3a3d3b", foreground="white", font="Arial")
        # ------------------------------------------------------------------
        self.watermark = Label(self.frame, text="MADE WITH ❤ BY AKSHAT DODHIYA", font=("New Roman", 20), bg="#3a3d3b",
                               fg="orange")
        self.separator = Label(self.frame, text="  |  ", font=("New Roman", 24), bg="#3a3d3b", fg="black")
        self.connect = Label(self.frame, text="Connect: ", font=("New Roman", 20), bg="#3a3d3b", fg="white")
        self.separator2 = Label(self.frame, text="  |  ", font=("New Roman", 24), bg="#3a3d3b", fg="black")
        self.watermark2_text = Label(self.frame, text="DESIGNER: ", font=("New Roman", 20),
                                     bg="#3a3d3b", fg="white")

        self.img_git = ImageTk.PhotoImage(file=resource_path("Images/github.png"))
        self.btn_git = Button(self.frame, image=self.img_git,
                              command=lambda: webbrowser.open("https://github.com/akshatdodhiya"))

        self.img_insta = ImageTk.PhotoImage(file=resource_path("Images/instagram.png"))
        self.btn_insta = Button(self.frame, image=self.img_insta,
                                command=lambda: webbrowser.open("https://www.instagram.com/akshat.dodhiya/"))

        self.img_yt = ImageTk.PhotoImage(file=resource_path("Images/youtube.png"))
        self.btn_yt = Button(self.frame, image=self.img_yt,
                             command=lambda:
                             webbrowser.open("https://www.youtube.com/channel/UCFbGYXuQKVt9rzNNaJq92EA"))

        self.img_watermark2 = ImageTk.PhotoImage(file=resource_path("Images/watermark2.png"))
        self.btn_watermark2 = Button(self.frame, image=self.img_watermark2,
                                     command=lambda:
                                     webbrowser.open("https://www.youtube.com/channel/UCZiR2OBqTGcUPhdhsIw9Ljg"))
        # -------------------------------

        self.get_gui()
        self.word_number = 0
        self.root.mainloop()

    def callback(self, usr_input):
        """
        Call back method to enable or disable the start button as per user's input
        """
        if usr_input.isdigit():
            self.switch()
            return True

        elif usr_input == "":
            self.switch(1)
            return True

        else:
            return False

    def switch(self, enable=0):
        if self.btn_start["state"] == DISABLED:
            self.btn_start["state"] = NORMAL
        if enable == 1:
            self.btn_start["state"] = DISABLED

    def get_gui(self):
        self.root.title("Pro Grammar - Improve your grammar")
        # self.root.withdraw()
        self.root.iconbitmap("Images/Icon.ico")
        self.root.config(menu=self.menu, bg="#3a3d3b")
        self.root.geometry("400x550")
        self.root.attributes("-fullscreen", True)
        self.root.focus_force()

        self.btn_start.pack(pady=15)

        self.frame.pack(side=BOTTOM, fill=Y)

        self.watermark.pack(in_=self.frame, side=LEFT, fill=Y)
        self.separator.pack(in_=self.frame, side=LEFT, fill=Y)
        self.connect.pack(in_=self.frame, side=LEFT, fill=Y)

        self.btn_git["bg"] = "#3a3d3b"
        self.btn_git["border"] = "0"
        self.btn_git.pack(in_=self.frame, side=LEFT, fill=Y)

        self.btn_insta["bg"] = "#3a3d3b"
        self.btn_insta["border"] = "0"
        self.btn_insta.pack(in_=self.frame, side=LEFT, fill=Y)

        self.btn_yt["bg"] = "#3a3d3b"
        self.btn_yt["border"] = "0"
        self.btn_yt.pack(in_=self.frame, side=LEFT, fill=Y)

        self.btn_watermark2["bg"] = "#3a3d3b"
        self.btn_watermark2["border"] = "0"
        self.btn_watermark2.pack(in_=self.frame, side=LEFT, fill=Y)

        self.separator2.pack(in_=self.frame, side=LEFT, fill=Y)
        self.watermark2_text.pack(in_=self.frame, side=LEFT, fill=Y)
        self.btn_watermark2.pack(in_=self.frame, side=LEFT, fill=Y)

    def get_words(self):
        self.btn_start.destroy()
        self.btn_start.update()
        self.store_words()

    def store_words(self):
        """
        A function to get all the words from the url and appends the words to the list 'word_list'
        :return: None
        """
        # Input from the user to get number of words
        # self.root.attributes("-disabled", True)

        if online_mode:
            no_of_words = abs(int(self.no_of_words.get()))
            textbox = self.driver.find_element_by_xpath('//*[@id="random_words_count"]')
            textbox.send_keys(no_of_words)
            # Find the generate button to generate words
            btn = self.driver.find_element_by_xpath('//*[@id="random-words"]')
            btn.click()  # Click on generate button to generate words
            # Run loop for each span (words) from the generated output
            for i in range(1, no_of_words + 1):
                # Get all the span text from the output
                self.word_list.append(self.driver.find_element_by_xpath(f'//*[@id="wordList"]/span[{i}]').text)
        else:
            with open("WordList.txt", "r") as file:  # Open the wordList file to pick random words from
                # Get the absolute integer value of user's input for number of words
                no_of_words = abs(int(self.no_of_words.get()))
                words = file.readlines()

                # Get line numbers for picking words from wordlist
                line_numbers = [random.randint(0, 3871) for _ in range(1, no_of_words + 1)]

                # Read the words on specific line numbers in wordlist and append them in self.word_list
                # only if the space is not included in the word
                self.word_list = [words[line].strip() for line in line_numbers]

        if not os.path.exists(resource_path("Audio")):
            os.mkdir(resource_path("Audio"))

        i = 0  # initializing variable to set file name
        for word in self.word_list:
            tts = gTTS(text=word, tld="co.in", lang="en")
            tts.save(resource_path(f"Audio/{i}.mp3"))
            i += 1

        # self.root.attributes("-disabled", False)
        if online_mode:
            self.driver.quit()
        self.add_buttons()

    def add_buttons(self):
        """
        Add read again, previous, next and quit buttons and read the first word automatically
        :return: None
        """
        self.speak(again=True)
        self.btn_read.pack(pady=7)
        self.btn_prev.pack(pady=7)
        self.root.bind("<Left>", lambda _: self.speak(back=True))
        self.btn_next.pack(pady=7)
        self.root.bind("<Right>", lambda _: self.speak())
        self.btn_end.pack(pady=7)
        self.root.bind("<<Alt-Key-F4>>", lambda _: self.clean_residuals(quit_program=True))

    def speak(self, again=False, back=False):
        """
        A function to speak all the words from the list 'word_list'
        :return: None
        """
        if again:
            # Speak the same spelling again
            playsound(resource_path(f"Audio/{self.word_number}.mp3").replace(" ", "%20"))
        elif back:
            # Speak the previous spelling
            try:
                if len(self.word_list) > self.word_number > 0:
                    self.word_number -= 1
                    playsound(resource_path(f"Audio/{self.word_number}.mp3").replace(" ", "%20"))
            except PlaysoundException:
                self.btn_prev.config(state=DISABLED)

        else:
            # Speak the next spelling only if present
            try:
                if (len(self.word_list) - 1) > self.word_number:
                    self.word_number += 1
                    playsound(resource_path(f"Audio/{self.word_number}.mp3").replace(" ", "%20"))
                    self.btn_prev.config(state=NORMAL)
                else:
                    self.btn_next.config(state=DISABLED)
                    self.show_spellings()

            except PlaysoundException:
                self.btn_next.config(state=DISABLED)
                self.show_spellings()

    def show_spellings(self):
        """
        1) Destroy the buttons to display the spellings i.e to be checked
        2) Create a text editor with write properties disabled to display spellings
        :return:
        """
        self.no_of_words.destroy()
        self.btn_read.destroy()
        self.btn_prev.destroy()
        self.btn_next.destroy()
        self.btn_end.destroy()

        scroll_bar = Scrollbar(self.root)

        scroll_bar.pack(side=RIGHT,
                        fill=Y)
        self.spellings_editor.config(state='disabled')
        self.spellings_editor.pack()

        self.root.bind("<Up>", lambda _: self.spellings_editor.yview_scroll(-1, "units"))
        self.root.bind("<Down>", lambda _: self.spellings_editor.yview_scroll(1, "units"))
        scroll_bar.config(command=self.spellings_editor.yview)

        self.frame2.pack(side=LEFT, fill=Y)

        self.btn_restart["bg"] = "#3a3d3b"
        self.btn_restart["border"] = "0"
        self.btn_restart.pack(in_=self.frame2, side=LEFT, fill=Y, padx=310)

        self.btn_quit_icon["bg"] = "#3a3d3b"
        self.btn_quit_icon["border"] = "0"
        self.btn_quit_icon.pack(in_=self.frame2, side=LEFT, fill=Y, padx=290)

        for word in self.word_list:
            self.spellings_editor.config(state='normal')
            time.sleep(0.2)
            self.spellings_editor.insert("end", word.capitalize() + "\t\t")
            time.sleep(0.15)
            self.spellings_editor.config(state='disabled')

    def clean_residuals(self, quit_program=False):
        """
        Delete all the files one by one fro audio directory for a fresh start or clean end
        :param quit_program: True if user wants to quit the program
        :return: None
        """
        for root, dirs, files in os.walk(resource_path("Audio"), topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        else:
            # Remove the directory after removing the files from it
            if os.path.exists(resource_path("Audio")):
                os.rmdir(resource_path("Audio"))

        if quit_program:
            # Destroy the main window when the application needs to be exit

            if online_mode:
                self.driver.quit()  # Exit the chrome driver when the program is closed
            self.root.destroy()
            playsound(resource_path("Sound Effects/quit.mp3").replace(" ", "%20"))
            exit(0)  # Clean exit

    def restart_app(self):
        self.root.destroy()
        App(restart=True)


if __name__ == '__main__':
    check_internet()
    start_app = App
    start_app()
