import subprocess
import sys




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
## Gather input data for adding new user.
def create_vm():
    # Get input from the user
    VMName = input("Enter VM Name: ")

def powershell_script(fname, lname, ou, OS, phone):
    powershell_login = f'New-PsSession -Computername mlm-dc -Credential New-Object System.Management.Automation.PSCredential("mlm.lab\administrator, Linux4Ever)'
    userdir = f'\\\\10.6.67.151\\E\\Shared\\{ou}\\{fname.lower()}.{lname.lower()}'
    powershell_aduser = f'New-ADUser -Name "{fname} {lname}" -DisplayName "{fname} {lname}" -SamAccountName "{fname[0].lower()}{lname.lower()}" -OfficePhone "{phone}" -UserPrincipalName "{fname[0].lower()}{lname.lower()}@mlm.lab" -GivenName "{fname}" -Surname "{lname}" -Description "{ou}" -AccountPassword (ConvertTo-SecureString "Linux4Ever" -AsPlainText -Force) -Enabled $true -Path "OU={ou},DC=mlm,DC=lab" -ChangePasswordAtLogon $true –PasswordNeverExpires $false -Server MLM-DC.mlm.lab'
    powershell_addir = f'If (-not(Test-Path -Path "{userdir}")) {{ New-Item -Path "{userdir}" -ItemType Directory }}'
    subprocess.run(["powershell", "-Command", powershell_login])
    subprocess.run(["powershell", "-Command", powershell_aduser])
    subprocess.run(["powershell", "-Command", powershell_addir])
    print(f"User {fname} {lname} successfully created. Returning to main menu in 5 seconds.")
    
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
            create_vm()
        elif option == 2:
            exit()
            
main()


"Hello world"