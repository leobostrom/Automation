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
            powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
            show_list(powershell_command)
            
        elif option == 2:
            create_vm()
        elif option == 7:
            print("Quiting...")
            exit()

main()
