#!/usr/bin/env python3
import time
import yaml
import subprocess

main_menu_text = """
 ________________________________________________________
|                                                        |
|     MLM User Management Tool     Linux Version         |
|________________________________________________________|
|                                                        |
|                   Select an option                     |
|________________________________________________________|
|                                                        |
|  1: Add a single new user                              |
|  2: Exit                                               |
|________________________________________________________|
"""

data = {}

## Gather input data for adding new user.
def gather_data():
    while True:
        print("You are about to add a new user. Make sure to follow the steps. Please wait... ")
        time.sleep(2)
        fname = input("First name: ")
        lname = input("Last name: ")
        category = input("""
Is the user a Staff member or a Student?
1. Staff
2. Student
""")
        phone = ""
        if category == "1":
            ou = "Staff"
            phonepromt = input("Would you like to add a phone number? Y/N :")
            if phonepromt.lower() == "y":
                phone = input("Phone number: ")
        elif category == "2":
            ou = "Student"
        confirm_data(fname, lname, ou, phone)

## Asks the user to confirm the data input in gather_data
def confirm_data(fname, lname, ou, phone):
    confirmation = input(f"You are creating user {fname} {lname} as {ou}. Is this correct? Y/N : ")
    if confirmation.lower() == "y":
        generate_yaml(fname, lname, ou, phone)
    elif confirmation.lower() == "n":
            print(""")

Cancelling user creation.
Returning to main menu in 3 seconds.
""")
            time.sleep(3)
            main()
    main()

def generate_yaml(fname, lname, ou, phone):
    user = {"Firstname": fname, "Lastname": lname, "Group": ou, "Password": "Linux4Ever", "Phone": phone}
    data[f'user{len(data)+1}'] = user
    with open('users.yml', 'w') as f:
        yaml.dump(data, f)
        print("""
YAML-file generated successfully
    """)
    run_ansible()

def run_ansible():
    print("Running Ansible playbook...")
    try:
        subprocess.run(['ansible-playbook', 'import.yml', '--ask-become-pass'], check=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ansible playbook run successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Ansible playbook failed with error: {e.stderr}")
    time.sleep(5)
    main()

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
            gather_data()
        elif option == 2:
            exit()

main()