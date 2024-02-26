#Set these variables for your VM & VHD’s
$VMName= “SRVDC1”
$RAM= 8GB
$SwitchName= “Internet”
$CPUCount= 2
$VHDSize= 140GB
$MotherVHD = “C:\Production\Motherdisk.vhdx”
$DataVHDPath= “C:\Production\$VMName.vhdx”
$DataVHDSize= 400GB

#Deploy the new virtual machine
New-VHD -ParentPath $MotherVHD -Path $DataVHDPath -Differencing
New-VM -VHDPath $DataVHDPath -MemoryStartupBytes $RAM -Name $VMName -SwitchName $SwitchName
Set-VM -Name $VMName -ProcessorCount $CPUCount
Set-VMMemory $VMName -DynamicMemoryEnabled $true