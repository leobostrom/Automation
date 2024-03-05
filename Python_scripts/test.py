from utils import *
from tabulate import tabulate
from subprocess import Popen, PIPE
import re
import subprocess



def add_computer(): 
    vm = {}
    num_vms = int(input("Enter the number of VMs to create: "))
    nlb_ip = input("Enter new cluster IP-address: ")
    
    for _ in range(num_vms):
        VMName = input("Enter a VM name: ")
        ip = input("Enter IP-address: ")
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

    for vm in vm_list:
        print(vm)
        config_nlb(nlb_ip, vm, nlb_master)
        create_website(vm)

def config_nlb(nlb_ip, vm, nlb_master):
        ps_script = f"""
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
        Invoke-Command -VMName {vm} -Credential $Credential -ScriptBlock {{
            if ("{vm}" -eq "{nlb_master}") {{
                # NLB Configuration for NLB_Master
                New-NlbCluster -InterfaceName "Ethernet" -ClusterName "NLBCluster" -ClusterPrimaryIP {nlb_ip} -OperationMode Multicast
                Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Enabled True -Profile Public    
         }} else {{
                # NLB Configuration for other VMs
                    Get-NlbCluster {nlb_master} | Add-NlbClusterNode -NewNodeName {vm} -NewNodeInterface "Ethernet"
                    Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Enabled True -Profile Public    
            }}
                
            }}
        """

        
        run_powershell(ps_script)
        
def create_website(vm):
        # HTML-innehållet för webbsidan
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Min enkla webbsida</title>
    </head>
    <body>
        <h1>Välkommen till min enkla webbsida!</h1>
        <p>Du är ansluten till server: {vm}</p>VV
    </body>
    </html>
    """

    # Sökväg till målfilen på servern
    remote_path = f'\\\\{vm}\\c$\\inetpub\\wwwroot\\iisstart.html'

    try:
        # Konstruera PowerShell-kommandot med variabler för användarnamn och lösenord
        powershell_command = f"""
        Set-Content -Path "{remote_path}" -Value "{html_content}" 
        """

        # Kör PowerShell-kommandot med subprocess
        subprocess.run(["powershell.exe", "-Command", powershell_command], check=True)

        print(f"Webbsida skapad på {vm}")

    except subprocess.CalledProcessError as e:
        print(f"Misslyckades med att skapa webbsida på {vm}: {e}")

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

