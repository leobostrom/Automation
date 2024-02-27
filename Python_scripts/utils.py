import subprocess
import json
from tabulate import tabulate

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
    index = int(input("Ange index för det önskade objektet: ")) - 1

    # Check if the index is valid
    if 0 <= index < len(vm_info_index):
        user_choice = vm_info_index[index][1]  # Sätt namnet på det valda objektet i user_choice
        print("Du valde:", user_choice)
    else:
        print("Ogiltigt index. Var vänlig ange ett giltigt index.")

# Anropa funktionen med PowerShell-kommando som argument
#powershell_command = "Get-VM | Select-Object Name, @{Name='State';Expression={$_.State.ToString()}}, CPUusage, @{Name='MemoryAssigned';Expression={$_.MemoryAssigned / 1MB}} | ConvertTo-Json -Compress"
#vm_info_index = show_list(powershell_command)
#select_vm(vm_info_index)