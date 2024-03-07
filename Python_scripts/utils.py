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
    start_vm(VMName)
 
def start_vm(VMName):
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

def set_ip(msg):
    while True:
        ip_address = input(msg)
        if is_valid_ip(ip_address):
            return ip_address
        else:
            print("Invalid IP address. Please enter a valid IP address.")

def configure_vm_network(VMName, ip, vm_status):
    print(f"Configuring VM '{VMName}'...")
    if vm_status.lower() == "off":
        print("Strarting VM")
        start_vm(VMName)
        time.sleep(45)
    
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

def shutdown_vm(vm_name):
    print(f"Shutting down VM '{vm_name}'")

    ps_shutdown_vm = f'''
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord

        $VMName = "{vm_name}"
        Stop-VM -Name $VMName -Force
    '''

    subprocess.run(["powershell.exe", "-Command", ps_shutdown_vm])
    print(f"VM '{vm_name}' shut down.")

def check_vm_status(vm_name):
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
    return vm_status

def remove_vm(vm_name, vm_status):
    print(f"Removing VM '{vm_name}'")
    if vm_status.lower() == "running":
        shutdown_vm(vm_name)

    # Remove the VM
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

def exit_menu():
    print("\nExiting the Menu...")
    time.sleep(1)  # Add a delay for dramatic effect
    print("See you on the other side of the code")
    print("🚀🐍✨")
