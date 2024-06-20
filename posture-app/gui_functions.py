import cv2
from pygame import mixer
import PySimpleGUI as sg
import time
from icecream import ic

def draw_posture_indicators(image, l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y, l_ear_x, l_ear_y, l_hip_x, l_hip_y, color):
    """
    ### Annotate the frame with circle and lines representing the calculated landmarks

    Args: 
    * image: Any cv2 image
    * l_shldr_x,l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y, l_ear_x, l_ear_y, l_hip_x, l_hip_y: X,Y variables from used landmarks
    * color : (R,G,B) color chosen to draw connecting lines

    Example: 
    `draw_posture_indicators(image, l_shldr_x, l_shldr_y, r_shldr_x, r_shldr_y, l_ear_x, l_ear_y, l_hip_x, l_hip_y, color)`
    """

    YELLOW = (0, 255, 255)
    PINK = (255, 0, 255)

    cv2.circle(image, (l_shldr_x, l_shldr_y), 7, YELLOW, -1)
    cv2.circle(image, (l_ear_x, l_ear_y), 7, YELLOW, -1)
    # cv2.circle(image, (l_shldr_x, l_shldr_y - 100), 7, YELLOW, -1)
    cv2.circle(image, (r_shldr_x, r_shldr_y), 7, PINK, -1)
    cv2.circle(image, (l_hip_x, l_hip_y), 7, YELLOW, -1)
    cv2.circle(image, (l_hip_x, l_hip_y - 100), 7, YELLOW, -1)

    cv2.line(image, (l_shldr_x, l_shldr_y), (l_ear_x, l_ear_y), color, 4)
    cv2.line(image, (l_shldr_x, l_shldr_y), (r_shldr_x, r_shldr_y), color, 4)
    # cv2.line(image, (l_shldr_x, l_shldr_y), (l_shldr_x, l_shldr_y - 100), color, 4)
    cv2.line(image, (l_hip_x, l_hip_y), (l_shldr_x, l_shldr_y), color, 4)
    cv2.line(image, (l_hip_x, l_hip_y), (l_hip_x, l_hip_y - 100), color, 4)

def toggle_button_images():
    """
    
    """
    # The base64 strings for the button images
    toggle_btn_off = b"iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAED0lEQVRYCe1WTWwbRRR+M/vnv9hO7BjHpElMKSlpqBp6gRNHxAFVcKM3qgohQSqoqhQ45YAILUUVDRxAor2VAweohMSBG5ciodJUSVqa/iikaePEP4nj2Ovdnd1l3qqJksZGXscVPaylt7Oe/d6bb9/svO8BeD8vA14GvAx4GXiiM0DqsXv3xBcJU5IO+RXpLQvs5yzTijBmhurh3cyLorBGBVokQG9qVe0HgwiXLowdy9aKsY3g8PA5xYiQEUrsk93JTtjd1x3siIZBkSWQudUK4nZO1w3QuOWXV+HuP/fL85klAJuMCUX7zPj4MW1zvC0Ej4yMp/w++K2rM9b70sHBYCjo34x9bPelsgp/XJksZ7KFuwZjr3732YcL64ttEDw6cq5bVuCvgy/sje7rT0sI8PtkSHSEIRIKgCQKOAUGM6G4VoGlwiqoVd2Za9Vl8u87bGJqpqBqZOj86eEHGNch+M7otwHJNq4NDexJD+59RiCEQG8qzslFgN8ibpvZNsBifgXmFvJg459tiOYmOElzYvr2bbmkD509e1ylGEZk1Y+Ssfan18n1p7vgqVh9cuiDxJPxKPT3dfGXcN4Tp3dsg/27hUQs0qMGpRMYjLz38dcxS7Dm3nztlUAb38p0d4JnLozPGrbFfBFm79c8hA3H2AxcXSvDz7/+XtZE1kMN23hjV7LTRnKBh9/cZnAj94mOCOD32gi2EUw4FIRUMm6LGhyiik86nO5NBdGRpxYH14bbjYfJteN/OKR7UiFZVg5T27QHYu0RBxoONV9W8KQ7QVp0iXdE8fANUGZa0QAvfhhXlkQcmjJZbt631oIBnwKmacYoEJvwiuFgWncWnXAtuVBBEAoVVXWCaQZzxmYuut68b631KmoVBEHMUUrJjQLXRAQVSxUcmrKVHfjWWjC3XOT1FW5QrWpc5IJdQhDKVzOigEqS5dKHMVplnNOqrmsXqUSkn+YzWaHE9RW1FeXL7SKZXBFUrXW6jIV6YTEvMAUu0W/G3kcxPXP5ylQZs4fa6marcWvvZfJu36kuHjlc/nMSuXz+/ejxgqPFpuQ/xVude9eu39Jxu27OLvBGoMjrUN04zrNMbgVmOBZ96iPdPZmYntH5Ls76KuxL9NyoLA/brav7n382emDfHqeooXyhQmARVhSnAwNNMx5bu3V1+habun5nWdXhwJZ2C5mirTesyUR738sv7g88UQ0rEkTDlp+1wwe8Pf0klegUenYlgyg7bby75jUTITs2rhCAXXQ2vwxz84vlB0tZ0wL4NEcLX/04OrrltG1s8aOrHhk51SaK0us+n/K2xexBxljcsm1n6x/Fuv1PCWGiKOaoQCY1Vb9gWPov50+fdEqd21ge3suAlwEvA14G/ucM/AuppqNllLGPKwAAAABJRU5ErkJggg=="
    toggle_btn_on = b"iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABmJLR0QA/wD/AP+gvaeTAAAD+UlEQVRYCe1XzW8bVRCffbvrtbP+2NhOD7GzLm1VoZaPhvwDnKBUKlVyqAQ3/gAkDlWgPeVQEUCtEOIP4AaHSI0CqBWCQyXOdQuRaEFOk3g3IMWO46+tvZ+PeZs6apq4ipON1MNafrvreTPzfvub92bGAOEnZCBkIGQgZOClZoDrh25y5pdjruleEiX+A+rCaQo05bpuvJ/+IHJCSJtwpAHA/e269g8W5RbuzF6o7OVjF8D3Pr4tSSkyjcqfptPDMDKSleW4DKIggIAD5Yf+Oo4DNg6jbUBlvWLUNutAwZu1GnDjzrcXzGcX2AHw/emFUV6Sfk0pqcKpEydkKSo9q3tkz91uF5aWlo1Gs/mYc+i7tz4//19vsW2AU9O381TiioVCQcnlRsWeQhD3bJyH1/MiFLICyBHiuzQsD1arDvypW7DR9nzZmq47q2W95prm+I9fXfqXCX2AF2d+GhI98Y8xVX0lnxvl2UQQg0csb78ag3NjEeD8lXZ7pRTgftmCu4864OGzrq+5ZU0rCa3m+NzXlzvoAoB3+M+SyWQuaHBTEzKMq/3BMbgM+FuFCDBd9kK5XI5PJBKqLSev+POTV29lKB8rT0yMD0WjUSYLZLxzNgZvIHODOHuATP72Vwc6nQ4Uiw8MUeBU4nHS5HA6TYMEl02wPRcZBJuv+ya+UCZOIBaLwfCwQi1Mc4QXhA+PjWRkXyOgC1uIhW5Qd8yG2TK7kSweLcRGKKVnMNExWWBDTQsH9qVmtmzjiThQDs4Qz/OUSGTwcLwIQTLW58i+yOjpXDLqn1tgmDzXzRCk9eDenjo9yhvBmlizrB3V5dDrNTuY0A7opdndStqmaQLPC1WCGfShYRgHdLe32UrV3ntiH9LliuNrsToNlD4kruN8v75eafnSgC6Luo2+B3fGKskilj5muV6pNhk2Qqg5v7lZ51nBZhNBjGrbxfI1+La5t2JCzfD8RF1HTBGJXyDzs1MblONulEqPDVYXgwDIfNx91IUVbAbY837GMur+/k/XZ75UWmJ77ou5mfM1/0x7vP1ls9XQdF2z9uNsPzosXPNFA5m0/EX72TBSiqsWzN8z/GZB08pWq9VeEZ+0bjKb7RTD2i1P4u6r+bwypo5tZUumEcDAmuC3W8ezIqSGfE6g/sTd1W5p5bKjaWubrmWd29Fu9TD0GlYlmTx+8tTJoZeqYe2BZC1/JEU+wQR5TVEUPptJy3Fs+Vkzgf8lemqHumP1AnYoMZSwsVEz6o26i/G9Lgitb+ZmLu/YZtshfn5FZDPBCcJFQRQ+8ih9DctOFvdLIKHH6uUQnq9yhFu0bec7znZ+xpAGmuqef5/wd8hAyEDIQMjAETHwP7nQl2WnYk4yAAAAAElFTkSuQmCC"
    return toggle_btn_off, toggle_btn_on

def alert_user():

    try:
        mixer.init()
        # mixer.music.load("bell-notif.wav")
        mixer.music.load("buzz-notif.mp3")
        # try:
        #     mixer.music.load(audio_file)
        # except FileNotFoundError as e:
        #     print("file not found", e)
        mixer.music.set_volume(0.2)
        mixer.music.play(fade_ms=10)
    except FileNotFoundError as e:
        sg.Popup(f"{e}")
class Timer:
    # Static variables
    paused_duration = 0
    pause = False
    running = False
    start_time = 0
    remaining_time = 0
    current_time = 0
    pomodoro = ["Timer","Short Break","Timer","Short Break","Timer","Long Break","Done"]
    time_left = 0
    pause_start_time = 0
    elapsed_time = 0

    def __init__(self, window: sg.Window) -> None:
        self.window = window 
    def __format_time(self,seconds):
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    def __reset_pomodoro(self) -> list:
        return ["Timer","Short Break","Timer","Short Break","Timer","Long Break","Done"]
    
    def next_timer(self, values):
        timer_type = Timer.pomodoro.pop(0)
        if timer_type is not None:
            Timer.remaining_time = self.__get_remaining_time(values, timer_type) # pop's which timer type is next
            Timer.paused_duration = 0
            Timer.start_time = time.time()
            Timer.running = True


    def check_buttons(self, values, event: str, auto_next=False, auto_start=False):
        # ic(auto_next and Timer.remaining_time == 0)

        # simply, (sitting) and (work timer is next) and (timer not running)
        try:
            if (auto_start and Timer.pomodoro[0] == "Timer" and not Timer.running):
                self.next_timer(values)
            if (auto_next and not Timer.running and Timer.pomodoro[0]=="Short Break" or Timer.pomodoro[0]=="Long Break"):
                self.next_timer(values)
            if (event == "Next"):
                self.next_timer(values)
                # print(f"start time:{Timer.start_time} | running: {Timer.running} | remaining time: {Timer.remaining_time} | timer_type: {timer_type}")
        except IndexError:
            event == "Reset"
        
        if event == "Start":
            
            # ic(Timer.remaining_time)
            # ic("start pressed")
            # ic(Timer.pomodoro[0])
            self.window["-DONE-KEY-"].update("")
            
            if not Timer.running:
                Timer.start_time = time.time()
                Timer.running = True
                Timer.remaining_time = self.__get_remaining_time(values,Timer.pomodoro.pop(0)) # pop's which timer type is next
                # ic("not running:", Timer.pomodoro[0])
                # ic(f"start time:{Timer.start_time} | running: {Timer.running} | remaining time: {Timer.remaining_time}")

        if event == "(Un)Pause":
            Timer.pause = not Timer.pause
            # ic("(un)pause pressed")
            # if button is paused while timer is self.running
            if Timer.running and Timer.pause:
                Timer.pause_start_time = time.time()
                Timer.running = False
                # ic(f"pause start time:{Timer.pause_start_time} | pause: {Timer.pause} | paused duration: {Timer.paused_duration}")
            elif not Timer.running and not Timer.pause:
                Timer.paused_duration += time.time() - Timer.pause_start_time
                Timer.running = True
                # ic(f"pause start time:{Timer.pause_start_time} | pause: {Timer.pause} | paused duration: {Timer.paused_duration}")


        if event == "Reset":
            # ic("Reset")
            Timer.running = False
            Timer.remaining_time = 0
            Timer.pomodoro = self.__reset_pomodoro()
            self.window["-DISPLAYTIMER-"].update(self.__format_time(Timer.remaining_time))
            Timer.paused_duration = 0
            Timer.pause = False
            Timer.start_time = 0
            Timer.elapsed_time = 0
            Timer.pause_start_time = 0
            Timer.time_left = 0
            # ic(f"pomodoro:{Timer.pomodoro} | running: {self.window} ")


    def __get_remaining_time(self, values, timer_type) -> int:
        try:
            if timer_type == "Timer":
                return int(values["-TIMER-"]) * 60
                # return float(values["-TIMER-"]) * 60
            elif timer_type == "Short Break":
                return int(values["-SHORTBREAK-"]) * 60
                # return float(values["-SHORTBREAK-"]) * 60
            elif timer_type == "Long Break":
                return int(values["-LONGBREAK-"]) * 60
                # return float(values["-LONGBREAK-"]) * 60
            elif timer_type == "Done":
                # what to do when done with the timer
                # sg.popup("You completed a work cycle!")
                self.window["-DONE-KEY-"].update("You completed a work cycle!")
                return -1
                
        except ValueError as e:
            sg.popup(f"Please select a valid number of minutes \n{e}")
    
    def update_timer(self):
        # ic("inside Timer.update_timer()")
        if Timer.running:
            try:
                Timer.elapsed_time = time.time() - Timer.start_time - Timer.paused_duration
                Timer.time_left = Timer.remaining_time - Timer.elapsed_time
                # ic(f"current_time {time.time()}| elapsed time:{Timer.elapsed_time} | time_left: {Timer.time_left}")
            except TypeError as e:
                sg.Popup(f"type error: {e}")

        if Timer.time_left <= 0:
            Timer.running = False
            Timer.time_left = 0
        # print(f"display timer: {self.__format_time(time_left)}")
        self.window["-DISPLAYTIMER-"].update(self.__format_time(Timer.time_left))

def main():
    pass
        

if __name__ == "__main__":
    main()
    