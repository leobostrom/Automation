from utils import *
from enviroment import *


main_menu_text = """
 ________________________________________________________
|                                                        |
|                        ML IT                           |
|________________________________________________________|
|                                                        |
|                   Select an option                     |
|________________________________________________________|
|                                                        |
|  1: Show Virtual Machines                              |
|  2: Create Virtual Machine                             |
|  3: Create Test Environment                            |
|  4: Change Configurations                              |
|  5: Delete Virtual Machine                             |
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

def main_menu():
    print(main_menu_text)

def user_option():
    try:
        option = int(input("Enter your choice: "))
        if option < 1 or option > 8:
            raise ValueError
        return option
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 8.")
        return user_option()

def main():
    main_menu()
    while True:
        option = user_option()
        if option == 1:
            list_vm()
            pause()
        elif option == 2:
            list_vm()
            create_one_vm()
            list_vm()
            pause()
        elif option == 3:
            start_enviroment()
            pause()
        elif option == 4:
            selected_vm = select()
            if selected_vm == None:
                clear_screen()
                main()
            ip = set_ip()
            configure_vm_network(selected_vm, ip)
            pause()
        elif option == 5:
            selected_vm = select()
            if selected_vm == None:
                clear_screen()
                main()
            remove_vm(selected_vm)
            list_vm()
            pause()
        elif option == 6:
            selected_vm = select()
            if selected_vm == None:
                clear_screen()
                main()
            manage_vm(selected_vm)
            list_vm()
            pause()
        elif option == 7:
            selected_vm = select()
            if selected_vm == None:
                clear_screen()
                main()
            manage_vm_checkpoints(selected_vm)
            pause()
        elif option == 8:
            exit_menu()
            exit()

        main_menu()  # Show main menu again

if __name__ == "__main__":
    main()
