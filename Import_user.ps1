$Users = Import-Csv -Path "\\10.6.67.150\test\sample1.csv"
foreach ($User in $Users)
{
    $Fname = $User.'fname'
    $Lname = $User.'lname'
    $OU = $User.'ou'
    $Password = $User.'password'
    $Phone = $User.'phone'
    $Name = $Fname + " " + $Lname
    $Path = "OU=" + $OU + ",DC=mlm,DC=lab"
    $SAM = $Fname + "." + $Lname
        $SAM = $SAM.ToLower()
    $UPN = $SAM + "@mlm.lab"
    $Description = $User.'ou'
    $UserDir = "\\10.6.67.151\E\Shared\$OU\$SAM"
        
    #Creates the user in Active Directory
    New-ADUser -Name $Name -DisplayName $Name -SamAccountName $SAM -OfficePhone $Phone -UserPrincipalName $UPN -GivenName $Fname -Surname $Lname -Description $Description -AccountPassword (ConvertTo-SecureString $Password -AsPlainText -Force) -Enabled $true -Path "$Path" -ChangePasswordAtLogon $true –PasswordNeverExpires $false -server MLM-DC.mlm.lab
    
    #Checks to see if a home catalog exists, if not it creates it under the appropriate OU
    If (-not(Test-Path -Path $UserDir)) {
    New-Item -Path "$UserDir" -ItemType Directory
    }
    #Sets full control for users.
    $Acl = Get-Acl $UserDir
    $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule("$UPN", "FullControll", "ContainerInherit,ObjectInherit", "None", "Allow")
    $Acl.AddAccessRule($Rule)
    Set-Acl -Path $UserDir -AclObject $Acl
    } 