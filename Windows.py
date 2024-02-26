import time
import csv
import subprocess
#import convert_csv_to_yaml
main_menu_text = """
 ________________________________________________________
|                                                        |
|        MLM User Management Tool  Windows Version       |
|________________________________________________________|
|                                                        |
|                   Select an option                     |
|________________________________________________________|
|                                                        |
|  1: Add a single new user                              |
|  2: Exit                                               |
|________________________________________________________|
"""

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
        powershell_script(fname, lname, ou, phone)
    elif confirmation.lower() == "n":
            print("""
Cancelling user creation.
Returning to main menu in 3 seconds.
""")
            time.sleep(3)
            main()
    main()
        
def powershell_script(fname, lname, ou, phone):
    userdir = f'\\\\10.6.67.151\\E\\Shared\\{ou}\\{fname.lower()}.{lname.lower()}'
    powershell_aduser = f'New-ADUser -Name "{fname} {lname}" -DisplayName "{fname} {lname}" -SamAccountName "{fname.lower()}{lname.lower()}" -OfficePhone "{phone}" -UserPrincipalName "{fname[0].lower()}{lname.lower()}@mlm.lab" -GivenName "{fname}" -Surname "{lname}" -Description "{ou}" -AccountPassword (ConvertTo-SecureString "Linux4Ever" -AsPlainText -Force) -Enabled $true -Path "OU={ou},DC=mlm,DC=lab" -ChangePasswordAtLogon $true –PasswordNeverExpires $false -Server MLM-DC.mlm.lab'
    powershell_mkdir = f'If (-not(Test-Path -Path "{userdir}")) {{ New-Item -Path "{userdir}" -ItemType Directory }}'
    subprocess.run(["powershell", "-Command", powershell_aduser])
    subprocess.run(["powershell", "-Command", powershell_mkdir])
    print(f"User {fname} {lname} successfully created. Returning to main menu in 5 seconds.")
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
