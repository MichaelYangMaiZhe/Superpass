# from tkinter import *
# from tkinter import ttk
#
# from main import *
import hashlib
import time
import tkinter
from tkinter import font as tkfont

import PIL.Image
import PIL.ImageTk
import RPi.GPIO as gpio

from main import *


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom


class MyVideoCapture:
    def __init__(self, universal_confirmation_time, universal_process_frequency, resolution=make_480p, register=False,
                 video_source=0, register_pack=None):
        # Open the video source
        # begin interface
        self.known_face_key_ids, self.known_face_labels, self.known_face_encodings, self.known_face_grade = get_data_from_db(
            face_encodings.find())
        self.universal_confirmation_time = universal_confirmation_time
        self.universal_process_frequency = universal_process_frequency
        self.resolution = resolution
        self.register_pack = register_pack
        self.video_source = video_source
        self.register_bar = [self.universal_confirmation_time, self.universal_confirmation_time]
        self.register = register
        self.user_confirmation_time = dict()
        for index, name in enumerate(self.known_face_labels):
            self.user_confirmation_time[name] = [self.universal_confirmation_time, self.universal_confirmation_time]
            # if not self.register:
            #     for log in login_log.find({'parent_key_id': known_face_key_ids[index]}):
            #         pass
        self.process_times = self.universal_process_frequency
        self.face_locations, self.face_names, self.face_grade = [], [], []
        self.vid = cv2.VideoCapture(video_source)
        resolution(self.vid)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR

                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Only process every universal_process_frequency frame of video to save time
                if self.process_times == 0:
                    self.face_locations, self.face_names, self.face_grade = process_face(frame, rgb_small_frame,
                                                                                         self.known_face_labels,
                                                                                         self.known_face_encodings,
                                                                                         self.known_face_grade)
                    self.process_times = self.universal_process_frequency
                else:
                    self.process_times -= 1

                if_continue, username = display_results(frame, self.face_locations, self.face_names, self.face_grade,
                                                        self.user_confirmation_time, self.register, self.register_bar,
                                                        self.register_pack, self.universal_confirmation_time)
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), if_continue, username
            else:
                return ret, None, True, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


# App(tkinter.Tk(), "Tkinter and OpenCV")

# button = ttk.Button(mainframe, text='Start Monitoring', command=start_monitoring)
#
# for child in mainframe.winfo_children():
#     child.grid_configure(padx=5, pady=5)
#
# # feet_entry.focus()
# root.bind('<Return>', calculate)
# app = FullScreenApp(root)
# root.mainloop()

def get_text_settings():
    font = 'size: 15'
    width = 20
    height = 4
    return font, width, height


class SampleApp(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        FullScreenApp(self)
        self.title = 'Lock'
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageMonitor, PageTwo, HintPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == 'PageMonitor':
            frame.start_updating(False)

    def display_words(self, words, func):
        frame = self.frames['HintPage']
        frame.display(words, func)
        frame.tkraise()


class StartPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        label = tkinter.Label(self,
                              text="Click the Button\n↓\nFacial Recognition\n↓\nEnter your PIN\n↓\nUnlocked!\nOr go on to \nhttp://10.54.24.83/",
                              font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tkinter.Button(self, text="Go to page monitor", font=get_text_settings()[0],
                                 width=get_text_settings()[1], height=get_text_settings()[2],
                                 command=lambda: controller.show_frame("PageMonitor"))
        button1.pack()


class PageMonitor(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.if_continue = True
        self.if_continue_force = True
        self.controller = controller
        button = tkinter.Button(self, text="Go to the start page",
                                command=self.start_updating)
        button.pack()

        self.video_source = 0
        self.universal_confirmation_time = 10
        self.universal_process_frequency = 2
        # open video source (by default this will try to open the computer web-cam)
        self.vid = MyVideoCapture(self.universal_confirmation_time, self.universal_process_frequency, make_480p, False,
                                  self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(self, width=300, height=360)
        self.canvas.pack()

        # Button that lets the user take a snapshot

        self.delay = 100
        # After it is called once, the update method will be automatically called every delay milliseconds

    def update(self):
        # Get a frame from the video source
        ret, frame, self.if_continue, username = self.vid.get_frame()
        if ret:
            small_frame_for_display = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(small_frame_for_display))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        if self.if_continue and self.if_continue_force:
            self.after(self.delay, lambda: self.update())
        elif not self.if_continue and username is not None:
            global expected_pin
            global expected_user
            expected_user = username
            expected_pin = face_encodings.find_one({'name': username})['pin']
            self.controller.show_frame('PageTwo')
        else:
            self.controller.show_frame("StartPage")

    def start_updating(self, reverse=True):
        print('yes!')
        if not reverse:
            self.if_continue = True
            self.if_continue_force = True
            self.update()
        else:
            self.if_continue_force = False


class HintPage(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

    def display(self, words, func):
        try:
            self.label['text'] = words
        except AttributeError:
            self.label = tkinter.Label(self, text=words, font='size: 20')
            self.label.pack(side="top", fill="x", pady=10)
        self.after(2000, self.controller.show_frame, func)


class PageTwo(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        keys = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['Last⌫', 'All⌫', '←'],
            ['Open']
        ]

        # create global variable for pin
        pin = ''  # empty string

        self.pin = str()

        # place to display pin
        self.e = tkinter.Entry(self, show="*")
        self.e.grid(row=0, column=0, columnspan=3, ipady=5)

        # create buttons using `keys`
        for y, row in enumerate(keys, 1):
            for x, key in enumerate(row):
                # `lambda` inside `for` has to use `val=key:code(val)`
                # instead of direct `code(key)`
                b = tkinter.Button(self, text=key, command=lambda val=key: self.code(val))
                b.config(height=2, width=7)
                if key == 'Open':
                    x += 1
                b.grid(row=y, column=x, ipadx=10, ipady=10)

    def code(self, value):

        # inform function to use external/global variable

        if value == 'Last⌫':
            # remove last number from `pin`
            self.pin = self.pin[:-1]
            # remove all from `entry` and put new `pin`
            self.e.delete('0', 'end')
            self.e.insert('end', self.pin)

        elif value == 'All⌫':
            self.pin = str()
            self.e.delete('0', 'end')

        elif value == '←':
            self.pin = str()
            self.e.delete('0', 'end')
            self.controller.show_frame('StartPage')

        elif value == 'Open':
            # check pin
            global expected_pin
            sha = hashlib.sha256(str(self.pin).encode("utf-8")).hexdigest()
            md_pass = hashlib.md5(str(sha).encode("utf-8")).hexdigest()
            # sha = hashlib.sha256(str(pin).encode("utf-8")).hexdigest()
            # md_pass = hashlib.md5(str(sha).encode("utf-8")).hexdigest()
            self.pin = str()
            self.e.delete('0', 'end')
            if md_pass == expected_pin:
                print("PIN OK")
                self.controller.display_words('Thank you!\nLock should be opened!', 'StartPage')
                open_lock(expected_user)

            else:
                print("PIN ERROR!", self.pin)
                self.controller.display_words('Wrong PIN entered!', 'PageTwo')

        else:
            # add number to pin
            self.pin += value
            # add number to `entry`
            self.e.insert('end', value)

        print("Current:", self.pin)


def open_lock(user):
    login_log.insert_one({'time': time.strftime('%y/%m/%d %H:%M:%S'), 'user': user})
    print('Unlocked!!')
    gpio.setmode(gpio.BCM)  # choose BCM or BOARD
    port_or_pin = 5
    gpio.setup(port_or_pin, gpio.OUT)  # set a port/pin as an output
    gpio.output(port_or_pin, 1)  # set port/pin value to 1/GPIO.HIGH/True
    time.sleep(5)
    gpio.output(port_or_pin, 0)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
