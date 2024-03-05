from utils import *
from tabulate import tabulate
from subprocess import Popen, PIPE
import re
import subprocess



def add_computer(): 
    vm = {}
    num_vms = int(input("Enter the number of VMs to create: "))
    nlb_ip = input("Enter new cluster ipaddress: ")
    
    for _ in range(num_vms):
        VMName = input("Enter a VM name: ")
        ip = input("Enter ipaddress: ")
        vm[VMName] = ip
    vm_list = list(vm.keys())
    print(vm_list)
    nlb_master = next(iter(vm.keys()))
    print(nlb_master)
    time.sleep(20)

    
    for VMName, ip in vm.items():
        print(f"Creating Virtual machine: {VMName}")
        create_vm(VMName)
        time.sleep(1)
        print(f"Starting: {VMName}")
        ps_scripts = f"Start-VM -Name {VMName}"
        run_powershell(ps_scripts)
    print("Waiting for Hyper-V to set up virtual machines")
    time.sleep(120)
    
    for VMName, ip in vm.items():
        configure_vm_network(VMName, ip)
        print(f"Setting '{ip}' for '{VMName}' ")
    time.sleep(20)


    for VMName, ip in vm.items():
        web_server(VMName)

    config_nlb(nlb_ip, vm_list, nlb_master)

def config_nlb(nlb_ip, vm_list, nlb_master):
    for vm in vm_list:
        ps_script = f"""
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
        $NLB_IP = "{nlb_ip}"
        $VMName = "{vm}"
        $NLB_Master = "{nlb_master}"

         {{
            Invoke-Command -VMName $VMName -Credential $Credential -ScriptBlock {{
                try {{
                    # NLB Configuration for each VM
                    New-NlbCluster -InterfaceName "Ethernet" -ClusterName "NLBCluster" -ClusterPrimaryIP $using:NLB_IP -OperationMode Multicast
                    Get-NlbCluster $using:NLB_Master | Add-NlbClusterNode -NewNodeName $using:VMName -NewNodeInterface "Ethernet"
                }} catch {{
                    Write-Host "An error occurred: $_"
                }}
            }}
        }}"""
        run_powershell(ps_script)
        
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
        
    


# Call the function to test it
add_computer()

