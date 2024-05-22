# gui_functions.py

import PySimpleGUI as sg

def app_window():
    sg.Window(title="Hello World", layout=[[]], margins= (100, 50)).read()




def main():
    app_window()

if __name__ =="__main__":
    main()