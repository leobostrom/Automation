import ctypes
import ipaddress
import os
import subprocess
import json
from tabulate import tabulate
import time


username = 'administrator'
password = 'Linux4Ever'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input('\nPress ENTER to continue...')
    clear_screen()

def list_vm():
    clear_screen()
    powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
    headers = ["Index", "VM Name", "State", "CPU Usage", "Memmory Usage"]
    vm_info_index = show_list(powershell_command, headers)
    return vm_info_index

def show_list(powershell_command, headers):
    # Run the PowerShell command
    result = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)

    # Check if the command was successful and produced output
    if result.returncode == 0 and result.stdout.strip():
        # Convert the JSON result to a Python dictionary
        vm_info = json.loads(result.stdout)

        # If vm_info is a dictionary, convert it to a list with one element
        if isinstance(vm_info, dict):
            vm_info = [vm_info]

        # Add index to each element in the list
        vm_info_index = [(i+1, *vm.values()) for i, vm in enumerate(vm_info)]

        # Display data as a table using tabulate
        print(tabulate(vm_info_index, headers=headers, tablefmt="fancy_grid"))
        return vm_info_index
    else:
        print("No data available.")
        return []  # Return an empty list if no data is available

def select():
    vm_info_index = list_vm()
    selected_vm = select_vm(vm_info_index)
    return selected_vm

def create_vm(VMName):
    
    RAM = "4GB"
    SwitchName = "Internet"
    CPUCount = 2
    MotherVHD = "C:\\Production\\VHD\\Motherdisk.vhdx"
    DataVHD = f"C:\\Production\\VHD\\{VMName}.vhdx"

    # PowerShell commands
    ps_scripts = [
        f'New-VHD -ParentPath "{MotherVHD}" -Path "{DataVHD}" -Differencing',
        f'New-VM -VHDPath "{DataVHD}" -MemoryStartupBytes {RAM} -Name "{VMName}" -SwitchName "{SwitchName}"',
        f'Set-VM -Name "{VMName}" -ProcessorCount {CPUCount}',
        f'Set-VMMemory "{VMName}" -DynamicMemoryEnabled $true'
    ]
    # Execute PowerShell commands
    for command in ps_scripts:
        run_powershell(command)


def manage_vm(user_choice):
    vm_name = user_choice
    print(f"Managing VM '{vm_name}'...")

    # Choose an action (1 for start, 2 for stop, 3 for restart, 4 to exit)
    action = int(input("Enter 1 to start, 2 to stop, 3 to restart the VM, or 4 to exit: "))

    ps_scripts = f'''
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

    run_powershell(ps_scripts)

def create_one_vm():
    VMName = input("Enter a VM name: ")
    create_vm(VMName)
    print(f"Virtual machine {VMName} created successfully.")
    ps_scripts = f"Start-VM -Name {VMName}"
    run_powershell(ps_scripts)

def web_server(VMName):     
        
    ps_scripts = f"""
    $User = "{username}"
    $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
    $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

    Invoke-Command -VMName {VMName} -Credential $Credential -ScriptBlock {{
    Install-WindowsFeature -Name Web-Server -IncludeManagementTools
    Install-WindowsFeature -Name NLB -IncludeManagementTools
}}"""
    run_powershell(ps_scripts)

def select_vm(vm_info_index):
    while True:
        try:
            index_input = input("Enter the index of the desired object (or '0' to cancel): ")
            if index_input == '0':
                return None
            if not index_input:
                print("No index provided. Please enter a valid index.")
                continue
            index = int(index_input) - 1
            if 0 <= index < len(vm_info_index):
                user_choice = vm_info_index[index][1]  
                print("You chose:", user_choice)
                return user_choice
            else:
                print("Invalid index. Please choose a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def set_ip():
    while True:
        ip_address = input("Enter IP address: ")
        if is_valid_ip(ip_address):
            return ip_address
        else:
            print("Invalid IP address. Please enter a valid IP address.")

def configure_vm_network(VMName, ip):
    print(f"Configuring VM '{VMName}'...")

    ps_script = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
        $VMName = "{VMName}"

        Invoke-Command -VMName $VMName -Credential $Credential -ScriptBlock {{
            $VMName = "{VMName}"      
            $IPAdd = "{ip}"
            $Gateway = "10.6.67.1"
            $DNSAdd = "10.6.67.2"
            
            Rename-Computer -NewName $VMName -Confirm:$False
            Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled
            Remove-NetRoute -InterfaceAlias "Ethernet" -Confirm:$false
            New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress $IPAdd -PrefixLength 24 -DefaultGateway $Gateway
            Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses $DNSAdd
            Restart-Computer
        }}
    '''
    run_powershell(ps_script)

def remove_vm(user_choice):
    vm_name = user_choice
    print(f"Removing VM '{vm_name}'")

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


def run_powershell(ps_script):
    subprocess.run(['powershell', '-Command', ps_script], capture_output=True)

def manage_vm_checkpoints_menu(vm_name):
    print(f"""
 ________________________________________________________
|                                                        |
|                 Checkpoint Management                  |
|________________________________________________________|
|                                                        |
| For VM: {vm_name.ljust(46)}|
|________________________________________________________|
|                                                        |
|  1: Create a checkpoint                                |
|  2: Restore a checkpoint                               |
|  3: List checkpoints                                   |
|  4: Remove a checkpoint                                |
|  5: Exit                                               |
|________________________________________________________|
""")

def list_checkpoints(vm_name):
    clear_screen()
    powershell_command = f"Get-VMSnapshot -VMName {vm_name} "+"| Select-Object Name, @{Name='CreationTime';Expression={$_.CreationTime.ToString('yyyy-MM-dd HH:mm:ss')}} | ConvertTo-Json -Compress"
    headers = ["Index", "Checkpoint Name", "Creation Time"]
    return show_list(powershell_command, headers)


def select_checkpoint(vm_name):
    checkpoints = list_checkpoints(vm_name)
    if not checkpoints:
        print("There are no checkpoints available for this VM.")
        return None
    
    while True:
        try:
            index_input = input("Enter the index of the checkpoint (or '0' to cancel): ")
            if index_input == '0':
                return None
            if not index_input:
                print("No index provided. Please enter a valid index.")
                continue
            checkpoint_index = int(index_input) - 1
            if 0 <= checkpoint_index < len(checkpoints):
                return checkpoints[checkpoint_index][1]  # Get the checkpoint name from the tuple
            else:
                print("Invalid checkpoint index. Please choose a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def create_checkpoint(vm_name):
    checkpoint_name = input("Enter the name for the checkpoint: ")
    subprocess.run(["powershell.exe", "-Command", f'Checkpoint-VM -Name {vm_name} -SnapshotName "{checkpoint_name}"'])
    print(f"Checkpoint '{checkpoint_name}' created.")
    pause()

def restore_checkpoint(vm_name):
    clear_screen()
    checkpoint_name = select_checkpoint(vm_name)
    if checkpoint_name:
        subprocess.run(["powershell.exe", "-Command", f'Restore-VMSnapshot -VMName {vm_name} -Name "{checkpoint_name}"'])
        print(f"Checkpoint '{checkpoint_name}' restored.")
        pause()

def remove_checkpoint(vm_name):
    clear_screen()
    checkpoint_name = select_checkpoint(vm_name)
    if checkpoint_name:
        subprocess.run(["powershell.exe", "-Command", f'Remove-VMSnapshot -VMName {vm_name} -Name "{checkpoint_name}"'])
        print(f"Checkpoint '{checkpoint_name}' removed.")
        pause()

def manage_vm_checkpoints(vm_name):
    print(f"Managing checkpoints for VM '{vm_name}'...")
    pause()
    while True:
        manage_vm_checkpoints_menu(vm_name)
        # Prompt the user for an action
        checkpoint_action = int(input("Enter your choice: "))

        # Process the user's choice
        if checkpoint_action == 1:
            create_checkpoint(vm_name)
        elif checkpoint_action == 2:
            restore_checkpoint(vm_name)
        elif checkpoint_action == 3:
            clear_screen()
            list_checkpoints(vm_name)
            pause()
        elif checkpoint_action == 4:
            remove_checkpoint(vm_name)
        elif checkpoint_action == 5:
            break
        else:
            print("Invalid checkpoint action. Please enter a valid action.")

def exit_menu():
    print("\nExiting the Menu...")
    time.sleep(1)  # Add a delay for dramatic effect
    print("See you on the other side of the code")
    print("🚀🐍✨")
