import os
import subprocess
import json
from tabulate import tabulate
import time


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_vm():
    clear_screen()
    powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
    vm_info_index = show_list(powershell_command)    
    return vm_info_index

def create_vm():
    VMName = input("Enter a VM name: ")
    
    RAM = "4GB"
    SwitchName = "Internet"
    CPUCount = 2
    MotherVHD = "C:\\Production\\VHD\\Motherdisk.vhdx"
    DataVHD = f"C:\\Production\\VHD\\{VMName}.vhdx"

    # PowerShell commands
    commands = [
        f'New-VHD -ParentPath "{MotherVHD}" -Path "{DataVHD}" -Differencing',
        f'New-VM -VHDPath "{DataVHD}" -MemoryStartupBytes {RAM} -Name "{VMName}" -SwitchName "{SwitchName}"',
        f'Set-VM -Name "{VMName}" -ProcessorCount {CPUCount}',
        f'Set-VMMemory "{VMName}" -DynamicMemoryEnabled $true'
    ]

    # Execute PowerShell commands
    for command in commands:
        subprocess.run(['powershell', '-Command', command], capture_output=True)

    print(f"Virtual machine {VMName} created successfully.")


def show_list(powershell_command):
    # Run the PowerShell command
    result = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)

    # Convert the JSON result to a Python dictionary
    vm_info = json.loads(result.stdout)

    # Add index to each element in the list
    vm_info_index = [(i+1, *vm.values()) for i, vm in enumerate(vm_info)]

    # Display data as a table using tabulate
    headers = ["Index"] + list(vm_info[0].keys())
    print(tabulate(vm_info_index, headers=headers, tablefmt="fancy_grid"))
    return vm_info_index


def select_vm(vm_info_index):
    # Allow the user to select an object
    index = int(input("Enter the index of the desired object: ")) - 1

    # Check if the index is valid
    if 0 <= index < len(vm_info_index):
        user_choice = vm_info_index[index][1]  # Sätt namnet på det valda objektet i user_choice
        print("You chose:", user_choice)
        return(user_choice)
    else:
        print("Invalid index. Please choose a valid index.")

# Anropa funktionen med PowerShell-kommando som argument
#powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
#vm_info_index = show_list(powershell_command)
#select_vm(vm_info_index)
      
def configure_vm_network(user_choice):
    vm_name = user_choice
    print(f"Configuring VM '{vm_name}'...")
    
    ip_address = input("Enter what IP Address: ")
    print(f"Setting '{ip_address}' for '{vm_name}' ")

    # Replace 'Username' and 'Password' with your actual username and password
    username = 'administrator'
    password = 'Linux4Ever'
    
    ps_script = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

        $VMName= "{vm_name}"
        $IPAdd= "{ip_address}"
        $Gateway= "10.6.67.1"
        $DNSAdd= "10.6.67.2"
        $VMName= "{vm_name}"
        Rename-Computer -NewName $VMName -Confirm:$False

        Write-Host "IP Address: $IPAdd"
        Write-Host "VM Name: $VMName"

        Invoke-Command -VMName $VMName -Credential $Credential -ScriptBlock {{
            Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled
            Remove-NetRoute -InterfaceAlias "Ethernet" -Confirm:$false
            New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress $using:IPAdd -PrefixLength 24 -DefaultGateway $using:Gateway
            Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses $using:DNSAdd
        }}
    '''

    subprocess.run(["powershell.exe", "-Command", ps_script])


def create_more_vm():
    num_vms = int(input("Enter the number of VMs to create: "))

    for _ in range(num_vms):
        VMName = input("Enter a VM name: ")

        RAM = "4GB"
        SwitchName = "Internet"
        CPUCount = 2
        MotherVHD = "C:\\Production\\VHD\\Motherdisk.vhdx"
        DataVHD = f"C:\\Production\\VHD\\{VMName}.vhdx"

        # PowerShell commands
        commands = [
            f'New-VHD -ParentPath "{MotherVHD}" -Path "{DataVHD}" -Differencing',
            f'New-VM -VHDPath "{DataVHD}" -MemoryStartupBytes {RAM} -Name "{VMName}" -SwitchName "{SwitchName}"',
            f'Set-VM -Name "{VMName}" -ProcessorCount {CPUCount}',
            f'Set-VMMemory "{VMName}" -DynamicMemoryEnabled $true'
        ]

        # Execute PowerShell commands
        for command in commands:
            subprocess.run(['powershell', '-Command', command], capture_output=True)

        print(f"Virtual machine {VMName} created successfully.")

def remove_vm(user_choice):
    vm_name = user_choice
    print(f"Removing VM '{vm_name}'")

    username = 'administrator'
    password = 'Linux4Ever'

    # Check if the VM is running
    ps_check_running = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

        $VMName = "{vm_name}"
        $VMStatus = Get-VM -Name $VMName | Select-Object -ExpandProperty State
        Write-Output $VMStatus
    '''

    result = subprocess.run(["powershell.exe", "-Command", ps_check_running], capture_output=True, text=True)
    vm_status = result.stdout.strip()

    if vm_status.lower() == "running":
        print(f"Shutting down VM '{vm_name}'")
        ps_shutdown_vm = f'''
            $User = "{username}"
            $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
            $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

            $VMName = "{vm_name}"
            Stop-VM -Name $VMName -Force
        '''

        subprocess.run(["powershell.exe", "-Command", ps_shutdown_vm])

    # remove the VM
    ps_remove_vm = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

        $VMName = "{vm_name}"
        Remove-VM -Name $VMName -Force
    '''

    subprocess.run(["powershell.exe", "-Command", ps_remove_vm])
    print(f"VM '{vm_name}' removed.")

def manage_vm(user_choice):
    vm_name = user_choice
    print(f"Managing VM '{vm_name}'...")

    # Choose an action (1 for start, 2 for stop, 3 for restart, 4 to exit)
    action = int(input("Enter 1 to start, 2 to stop, 3 to restart the VM, or 4 to exit: "))

    # Replace 'Username' and 'Password' with your actual username and password
    username = 'administrator'
    password = 'Linux4Ever'

    ps_script = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

        $VMName= "{vm_name}"

        switch ({action}) {{
            1 {{ Start-VM -Name $VMName }}
            2 {{ Stop-VM -Name $VMName -Force }}
            3 {{ Restart-VM -Name $VMName -Force }}
            4 {{ exit }}
            default {{ Write-Host "Invalid action. Please enter a valid action." }}
        }}
    '''

    subprocess.run(["powershell.exe", "-Command", ps_script])

    subprocess.run(["powershell.exe", "-Command", ps_script])

def manage_vm_checkpoints(vm_name):
    print(f"Managing checkpoints for VM '{vm_name}'...")

    while True:
        # Choose a checkpoint action (1 for create, 2 for restore, 3 for list, 4 to exit)
        checkpoint_action = int(input("Enter 1 to create checkpoint, 2 to restore checkpoint, 3 to list checkpoints, or 4 to exit: "))

        if checkpoint_action == 1:
            checkpoint_name = input("Enter the name for the checkpoint: ")
            subprocess.run(["powershell.exe", "-Command", f'Checkpoint-VM -Name {vm_name} -SnapshotName "{checkpoint_name}"'])
            print(f"Checkpoint '{checkpoint_name}' created.")
        elif checkpoint_action == 2:
            subprocess.run(["powershell.exe", "-Command", f'Restore-VMCheckpoint -VMName {vm_name}'])
            print("Checkpoint restored.")
        elif checkpoint_action == 3:
            subprocess.run(["powershell.exe", "-Command", f'Get-VMSnapshot -VMName {vm_name} | Format-Table -AutoSize'])
        elif checkpoint_action == 4:
            break
        else:
            print("Invalid checkpoint action. Please enter a valid action.")



def exit_menu():
    print("\nExiting the Menu...")
    time.sleep(1)  # Add a delay for dramatic effect
    print("See you on the other side of the code")
    print("🚀🐍✨")