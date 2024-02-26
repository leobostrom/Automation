#Set these variables for your VM & VHD’s
$VMName= “SRVDC”
$RAM= 8GB
$SwitchName= “Internet”
$CPUCount= 2
$VHDPath= “C:\Production\SRVDC-C.vhdx”
$VHDSize= 140GB
$DataVHDPath= “C:\Production\SRVDC-E.vhdx”
$DataVHDSize= 400GB

#Deploy the new virtual machine
New-VM -NewVHDPath $VHDPath -NewVHDSizeBytes $VHDSize -Generation 1 -MemoryStartupBytes $RAM -Name $VMName -SwitchName $SwitchName
Set-VM -Name $VMName -ProcessorCount $CPUCount

#Add a VHD for file/data partition
New-VHD -Path $DataVHDPath -SizeBytes $DataVHDSize -Dynamic
Add-VMHardDiskDrive –ControllerType SCSI -ControllerNumber 0 -VMName $VMName -Path $DataVHDPath