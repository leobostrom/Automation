import time
import csv
import subprocess
#import convert_csv_to_yaml
main_menu_text = """
 ________________________________________________________
|                                                        |
|                MLM User Management Tool                |
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
        System = input("""
What Operating System will the user be using?
1. Windows
2. Linux
""")
        OS = ""
        if System == "1":
            OS = "Windows"
        elif System == "2":
            OS = "Linux"
        confirm_data(fname, lname, ou, OS, phone)
        
## Asks the user to confirm the data input in gather_data
def confirm_data(fname, lname, ou, OS, phone):
    confirmation = input(f"You are creating user {fname} {lname} as {ou}, using {OS}. Is this correct? Y/N : ")
    if confirmation.lower() == "y":
        if OS == "Windows":
            powershell_script(fname, lname, ou, OS, phone)
        elif OS == "Linux":
            generate_csv(fname, lname, ou, phone)
            #convert_csv_to_yaml()
    elif confirmation.lower() == "n":
            print("""
Cancelling user creation.
Returning to main menu in 3 seconds.
""")
            time.sleep(3)
            main()
    main()
        
def powershell_script(fname, lname, ou, OS, phone):
    powershell_login = f'New-PsSession -Computername mlm-dc -Credential New-Object System.Management.Automation.PSCredential("mlm.lab\administrator, Linux4Ever)'
    userdir = f'\\\\10.6.67.151\\E\\Shared\\{ou}\\{fname.lower()}.{lname.lower()}'
    powershell_aduser = f'New-ADUser -Name "{fname} {lname}" -DisplayName "{fname} {lname}" -SamAccountName "{fname[0].lower()}{lname.lower()}" -OfficePhone "{phone}" -UserPrincipalName "{fname[0].lower()}{lname.lower()}@mlm.lab" -GivenName "{fname}" -Surname "{lname}" -Description "{ou}" -AccountPassword (ConvertTo-SecureString "Linux4Ever" -AsPlainText -Force) -Enabled $true -Path "OU={ou},DC=mlm,DC=lab" -ChangePasswordAtLogon $true –PasswordNeverExpires $false -Server MLM-DC.mlm.lab'
    powershell_addir = f'If (-not(Test-Path -Path "{userdir}")) {{ New-Item -Path "{userdir}" -ItemType Directory }}'
    subprocess.run(["powershell", "-Command", powershell_login])
    subprocess.run(["powershell", "-Command", powershell_aduser])
    subprocess.run(["powershell", "-Command", powershell_addir])
    print(f"User {fname} {lname} successfully created. Returning to main menu in 5 seconds.")
    time.sleep(5)
    main()

        

## Generates the CSV-file to be used with powershell
def generate_csv(fname, lname, ou, phone):
    with open('users.csv', 'a', newline='', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        if csvfile.tell() == 0:
            writer.writerow(["Firstname", "Lastname", "Category", "Password", "Phone"])
        writer.writerow([fname, lname, ou, "Linux4Ever", phone])
    csv_generated()
    
def csv_generated():
    print("""
CSV-file generated successfully
Returning to main menu in 5 seconds
    """)
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
