$VMName= "SRVDC"
$IPAdd= ”192.168.70.21"
$Gateway= ”192.168.70.1"
$DNSAdd= ”192.168.70.4"

Invoke-Command -VMName $VMName -ScriptBlock {

#Set time zone, rename computer, install the Essentials role
$TimeZone= “Central Standard Time”
$VMName= "SRVDC"
TZUtil /s $TimeZone
Rename-Computer -NewName $VMName -Confirm:$False

#Configure the network settings
New-NetIPAddress -InterfaceAlias “Ethernet” -IPAddress $IPAdd -PrefixLength 24 -DefaultGateway $Gateway
Set-DnsClientServerAddress -InterfaceAlias “Ethernet” -ServerAddresses $DNSAdd

}