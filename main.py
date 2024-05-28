# main.py
from icecream import ic
from PySimpleGUI import running_mac,running_windows
def main(arg):
    print(arg)

    # Linux, Windows, Mac respective calls

    if running_windows:
        ic("this should work")
    elif running_mac:
        ic("not tested yet")
    else:
        ic("this OS is not supported")


if __name__ =="__main__":
    main("word")