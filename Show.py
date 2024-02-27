import subprocess
import json

# Definiera PowerShell-kommandot för att hämta information om virtuella maskiner och spara resultatet i JSON-format
powershell_command = 'Get-VM | Select-Object Name, State, MemoryAssigned, ProcessorCount | ConvertTo-Json -Compress'

# Kör PowerShell-kommandot och fånga resultatet
result = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)

# Konvertera JSON-resultatet till en Python-dictionary
vm_info = json.loads(result.stdout)

# Visa innehållet i dictionarayen
print(vm_info)