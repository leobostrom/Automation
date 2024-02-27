import subprocess
import json
import pandas as pd

def show_list(powershell_command):
    # Kör PowerShell-kommandot och fånga resultatet
    result = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)
    
    # Konvertera JSON-resultatet till en Python-dictionary
    vm_info = json.loads(result.stdout)

    # Konvertera dictionaryn till en pandas
    df = pd.DataFrame(vm_info)

    # Fixar index
    df.index = df.index + 1

    # Visa DataFrame som tabell med kolumner
    print(df)

# Anropa funktionen med ditt PowerShell-kommando som argument
#powershell_command = 'Get-VM | Select-Object Name, State, CPUusage, Memoryusage | ConvertTo-Json -Compress'
#show_list(powershell_command)