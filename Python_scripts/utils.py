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

def list_vm():
    clear_screen()
    powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
    vm_info_index = show_list(powershell_command)    
    return vm_info_index
def select():
    vm_info_index = list_vm()
    selected_vm = select_vm(vm_info_index)
    return selected_vm

def create_one_vm():
    VMName = input("Enter a VM name: ")
    create_vm(VMName)
    print(f"Virtual machine {VMName} created successfully.")

def create_more_vm():
    num_vms = int(input("Enter the number of VMs to create: "))
    for _ in range(num_vms):
        VMName = input("Enter a VM name: ")
        create_vm(VMName)
        print("Creating Virtual machine...")
        time.sleep(10)
        ps_scripts = f"Start-VM -Name {VMName}"
        run_powershell(ps_scripts)
        time.sleep(30)
        print(f"Virtual machine {VMName} created successfully.")
        ip_address = configure_vm_network(VMName)
        time.sleep(5)
        print(f"IP address have been sucessfully set {ip_address}")
        print("Installing Microsoft Internet Information Services (IIS)")
        web_server(VMName)
        print("Installation sucessfull")
        
def web_server(VMName):     
        
    ps_scripts = f"""
    $User = "{username}"
    $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
    $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

    Invoke-Command -VMName {VMName} -Credential $Credential -ScriptBlock {{
    Install-WindowsFeature -Name Web-Server -IncludeManagementTools
}}"""
    run_powershell(ps_scripts)

def create_vm(VMName):
    
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


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def configure_vm_network(user_choice):
    vm_name = user_choice
    print(f"Configuring VM '{vm_name}'...")
    
    while True:
        ip_address = input("Enter the IP Address: ")
        if is_valid_ip(ip_address):
            print(f"Setting '{ip_address}' for '{vm_name}' ")
            return ip_address
            break
        else:
            print("Invalid IP address. Please enter a valid IP address.")
    
    ps_script = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
        $VMName = "{vm_name}"

        Invoke-Command -VMName $VMName -Credential $Credential -ScriptBlock {{
            $VMName = "{vm_name}"      
            $IPAdd = "{ip_address}"
            $Gateway = "10.6.67.1"
            $DNSAdd = "10.6.67.2"
            
            Rename-Computer -NewName $VMName -Confirm:$False
            Set-NetIPInterface -InterfaceAlias "Ethernet" -Dhcp Enabled
            Remove-NetRoute -InterfaceAlias "Ethernet" -Confirm:$false
            New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress $IPAdd -PrefixLength 24 -DefaultGateway $Gateway
            Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses $DNSAdd
        }}
    '''
    run_powershell(ps_script)
    

def run_powershell(ps_script):
    subprocess.run(["powershell.exe", "-Command", ps_script])



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

def manage_vm(user_choice):
    vm_name = user_choice
    print(f"Managing VM '{vm_name}'...")

    # Choose an action (1 for start, 2 for stop, 3 for restart, 4 to exit)
    action = int(input("Enter 1 to start, 2 to stop, 3 to restart the VM, or 4 to exit: "))

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