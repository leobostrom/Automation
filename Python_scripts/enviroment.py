from utils import *
from tabulate import tabulate
import subprocess

def start_enviroment(): 
    clear_screen()
    vm = {}
    num_vms = int(input("Enter the number of VMs to create: "))
    clear_screen()
    msg = ("Enter new cluster IP-address: ")
    nlb_ip = set_ip(msg)
    
    for _ in range(num_vms):
        VMName = input("Enter a VM name: ")
        msg = ("Enter IP-address: ")
        ip = set_ip(msg)
        vm[VMName] = ip
    vm_list = list(vm.keys())
    print(vm_list)
    nlb_master = next(iter(vm.keys()))
    print(nlb_master)
    
    for VMName, ip in vm.items():
        print(f"Creating Virtual machine: {VMName}")
        create_vm(VMName)
        time.sleep(1)
        print(f"Starting: {VMName}")
        ps_scripts = f"Start-VM -Name {VMName}"
        run_powershell(ps_scripts)
    print("Waiting for Virtual Machines to set up Windows Server 2022")
    time.sleep(120)
    
    for VMName, ip in vm.items():
        vm_status = check_vm_status(VMName)
        configure_vm_network(VMName, ip, vm_status)
        print(f"Setting up network configuration for'{VMName}' : '{ip}' ")
        time.sleep(5)

    for VMName, ip in vm.items():
        web_server(VMName)

    for vm in vm_list:
        print(vm)
        config_nlb(nlb_ip, vm, nlb_master)
        time.sleep(30)
        create_website(vm)

def config_nlb(nlb_ip, vm, nlb_master):
        ps_script = f"""
        $User = "{username}"
        $PWord = ConvertTo-SecureString -String "{password}" -AsPlainText -Force
        $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
        Invoke-Command -VMName {vm} -Credential $Credential -ScriptBlock {{
            if ("{vm}" -eq "{nlb_master}") {{
                # NLB Configuration for NLB_Master
                New-NlbCluster -InterfaceName "Ethernet" -ClusterName "nlbcluster.local" -ClusterPrimaryIP {nlb_ip} -OperationMode Multicast    
                Get-NlbClusterPortRule | Remove-NlbClusterPortRule -Force
                Get-NlbCluster | Add-NlbClusterPortRule -StartPort 80 -EndPort 80 -Affinity None
         }} else {{
                # NLB Configuration for other VMs
                Get-NlbCluster {nlb_master} | Add-NlbClusterNode -NewNodeName {vm} -NewNodeInterface "Ethernet"    
            }}
            Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Enabled True -Profile Any    
            
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
            <title>ML Test Site</title>
        </head>
        <body>
            <h1>Welcome to our test website!</h1>
            <p>You are connected to server: {vm}</p>
        </body>
        </html>
    """

    # Sökväg till målfilen på servern
    remote_path = f'\\\\{vm}\\c$\\inetpub\\wwwroot\\index.html'

    try:
        # Kontrollera om filen redan finns, om inte, skapa den
        ps_command_check_file = f"""
        if (-not (Test-Path "{remote_path}")) {{
            New-Item -Path "{remote_path}" -ItemType "file" -Force | Out-Null
        }}
        """

        # Konstruera PowerShell-kommandot med variabler för användarnamn och lösenord
        ps_scripts = f"""
              
        {ps_command_check_file}
        Set-Content -Path {remote_path} -Value '{html_content}'
        """

        # Kör PowerShell-kommandot med subprocess
        run_powershell(ps_scripts)

        print(f"Webbsida skapad på {vm}")

    except subprocess.CalledProcessError as e:
        print(f"Misslyckades med att skapa webbsida på {vm}: {e}")



