#Set these variables for your VM & VHD’s
$VMName= “SRVDC1”
$RAM= 8GB
$SwitchName= “Internet”
$CPUCount= 2
$MotherVHD = “C:\Production\Motherdisk.vhdx”
$DataVHD= “C:\Production\$VMName.vhdx”

#Deploy the new virtual machine
New-VHD -ParentPath $MotherVHD -Path $DataVHD -Differencing
New-VM -VHDPath $DataVHD -MemoryStartupBytes $RAM -Name $VMName -SwitchName $SwitchName
Set-VM -Name $VMName -ProcessorCount $CPUCount
Set-VMMemory $VMName -DynamicMemoryEnabled $true