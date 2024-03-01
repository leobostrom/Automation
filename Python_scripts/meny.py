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
|  5: Delete Virtual machines                            |
|  6: Manage Virtual Machines                            |
|  7: Manage Checkpoints                                 |
|  8: Exit                                               |
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
        
        elif option == 3:
            create_more_vm()
        
        elif option == 4:
            selected_vm = select()
            configure_vm_network(selected_vm)
            pause()
            main()
        elif option == 5:
            selected_vm = select()
            remove_vm(selected_vm)
            list_vm()
            pause()
            main()
        elif option == 6:
            selected_vm = select()
            manage_vm(selected_vm)
            list_vm()
            pause()
            main()
        elif option == 7:
            selected_vm = select()
            manage_vm_checkpoints(selected_vm)
            main()

        elif option == 8:
           exit_menu()
           exit()

main()
