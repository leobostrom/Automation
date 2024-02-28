import sys
import ctypes
from utils import *

main_menu_text = """
 ________________________________________________________
|                                                        |
|                        ML IT                           |
|________________________________________________________|
|                                                        |
|                   Select an option                     |
|________________________________________________________|
|                                                        |
|  1: Show Virtual machines                              |
|  2: Create Virtual machines                            |
|  3: Create test enviroment                             |
|  4: Change configurations                              |
|  5:                                                    |
|  6:                                                    |
|  7: Exit                                               |
|                                                        |
|________________________________________________________|
"""
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def pause():
    input(f'\nPress ENTER to continue') 
    clear_screen()


## Runs the main menu
def main_menu():
    print(main_menu_text)

## Accepts user inputs for the main menu
def user_option():
    return int(input())

## This runs the program
def main():
    main_menu()
    while True:
        option = user_option()
        if option == 1:
            list_vm()
            pause()
            main()

        elif option == 2:         
            list_vm()
            create_vm()
            list_vm()
            pause()
            main()

        elif option == 7:
            print("Quiting...")
            exit()

main()
