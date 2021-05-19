import os
import time
import webbrowser
from tkinter import *
from tkinter.messagebox import *
from selenium import webdriver
from gtts.tts import gTTS
from playsound import playsound, PlaysoundException
import requests
from requests.exceptions import ConnectionError
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def check_internet():
    try:
        requests.get("https://google.com/").status_code
    except ConnectionError:
        msg_window = Tk()
        msg_window.withdraw()
        showerror(title="No Internet Error!", message="Your device is not connected to internet, " +
                                                      "Please connect to the internet!")
        return False
    else:
        return True


# TODO: Change the name and logo of intro window and add gui to App() class
# TODO: Add difficulty level choice for user
# TODO: Add watermark2 (sujal) button with yt channel link


class Intro:
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
        self.frames = [PhotoImage(file=resource_path('Images/intro.gif'), format='gif -index %i' % i)
                       for i in range(self.frameCnt)]

        self.label = Label(self.intro)
        self.label.pack(expand=YES, fill=BOTH)
        self.intro.after(0, self.update, 0)

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
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(executable_path=resource_path(r'Driver\chromedriver.exe'),
                                       options=options, service_log_path=os.devnull)
        self.driver.get('https://wordcounter.net/random-word-generator')  # Website to generate words
        self.word_list = []  # list to store all the generated words

        if os.path.exists(resource_path("Audio")):
            self.clean_residuals(quit_program=False)

        if not restart:
            Intro.__init__(self)

        # -------------------------------
        self.root = Tk()
        self.frame = Frame(self.root)
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
        self.img_start = PhotoImage(file=resource_path("Images/start.png"))
        self.btn_start = Button(self.root, image=self.img_start, command=self.get_words)
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
        self.btn_quit = Button(self.root, height=3, width=20, text="Quit", font=("Arial", 15), bg="#FFBD09",
                               command=lambda: self.clean_residuals(quit_program=True))

        self.img_quit = PhotoImage(file=resource_path("Images/quit.png"))
        self.btn_quit_icon = Button(self.root, image=self.img_quit,
                                    command=lambda: self.clean_residuals(quit_program=True))

        self.img_restart = PhotoImage(file=resource_path("Images/restart.png"))
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

        self.img_git = PhotoImage(file=resource_path("Images/github.png"))
        self.btn_git = Button(self.frame, image=self.img_git,
                              command=lambda: webbrowser.open("https://github.com/akshatdodhiya"))

        self.img_insta = PhotoImage(file=resource_path("Images/instagram.png"))
        self.btn_insta = Button(self.frame, image=self.img_insta,
                                command=lambda: webbrowser.open("https://www.instagram.com/akshat.dodhiya/"))

        self.img_yt = PhotoImage(file=resource_path("Images/youtube.png"))
        self.btn_yt = Button(self.frame, image=self.img_yt,
                             command=lambda:
                             webbrowser.open("https://www.youtube.com/channel/UCFbGYXuQKVt9rzNNaJq92EA"))

        self.img_watermark2 = PhotoImage(file=resource_path("Images/watermark2.png"))
        self.btn_watermark2 = Button(self.frame, image=self.img_watermark2,
                                     command=lambda:
                                     webbrowser.open("https://www.youtube.com/channel/UCZiR2OBqTGcUPhdhsIw9Ljg"))
        # -------------------------------

        self.get_gui()
        # self.get_words()
        self.word_number = 0
        self.root.mainloop()

    def callback(self, usr_input):
        if usr_input.isdigit():
            self.switch()
            return True

        elif usr_input is "":
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
        self.root.attributes("-disabled", True)
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

        if not os.path.exists(resource_path("Audio")):
            os.mkdir(resource_path("Audio"))

        i = 0  # initializing variable to set file name
        for word in self.word_list:
            tts = gTTS(text=word, tld="co.in", lang="en")
            tts.save(resource_path(f"Audio/{i}.mp3"))
            i += 1

        self.root.attributes("-disabled", False)
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
        self.btn_quit.pack(pady=7)
        self.root.bind("<<Alt-Key-F4>>", lambda _: self.clean_residuals(quit_program=True))

    def speak(self, again=False, back=False):
        """
        A function to speak all the words from the list 'word_list'
        :return: None
        """
        if again:
            # Speak the same spelling again
            playsound(resource_path(f"Audio/{self.word_number}.mp3"))
        elif back:
            # Speak the previous spelling
            try:
                if len(self.word_list) > self.word_number > 0:
                    self.word_number -= 1
                    playsound(resource_path(f"Audio/{self.word_number}.mp3"))
            except PlaysoundException:
                self.btn_prev.config(state=DISABLED)

        else:
            # Speak the next spelling only if present
            try:
                if len(self.word_list) > self.word_number:
                    self.word_number += 1
                    playsound(resource_path(f"Audio/{self.word_number}.mp3"))
                    self.btn_prev.config(state=NORMAL)
            except PlaysoundException:
                self.btn_next.config(state=DISABLED)
                self.show_spellings()

    def show_spellings(self):
        """
        1) Destroy the buttons to display the spellings i.e to be checked
        2) Create a text editor with write properties disabled to display spellings
        :return:
        """
        self.btn_read.destroy()
        self.btn_prev.destroy()
        self.btn_next.destroy()
        self.btn_quit.destroy()

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
            time.sleep(0.1)
            self.spellings_editor.insert("end", word.capitalize() + "\t\t")
            time.sleep(0.07)
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
            self.driver.quit()  # Exit the chrome driver when the program is closed
            self.root.destroy()
            exit(0)  # Clean exit

    def restart_app(self):
        self.root.destroy()
        App(restart=True)


if __name__ == '__main__':
    if check_internet():
        start_app = App
        start_app()
