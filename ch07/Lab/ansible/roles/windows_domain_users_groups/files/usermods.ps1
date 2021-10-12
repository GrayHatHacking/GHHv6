 Import-Module ActiveDirectory
#Bring up an Active Directory command prompt so we can use this later on in the script
#Get a reference to the RootDSE of the current domain
$rootdse = Get-ADRootDSE
#Get a reference to the current domain
$domain = Get-ADDomain
cd AD:\

#Create a hashtable to store the GUID value of each schema class and attribute
$guidmap = @{}
Get-ADObject -SearchBase ($rootdse.SchemaNamingContext) -LDAPFilter `
"(schemaidguid=*)" -Properties lDAPDisplayName,schemaIDGUID | 
% {$guidmap[$_.lDAPDisplayName]=[System.GUID]$_.schemaIDGUID}

#Create a hashtable to store the GUID value of each extended right in the forest
$extendedrightsmap = @{}
Get-ADObject -SearchBase ($rootdse.ConfigurationNamingContext) -LDAPFilter `
"(&(objectclass=controlAccessRight)(rightsguid=*))" -Properties displayName,rightsGuid | 
% {$extendedrightsmap[$_.displayName]=[System.GUID]$_.rightsGuid}
#Create a new OU called Administrative Groups and make a group in it
New-ADOrganizationalUnit -Name "Administrative Groups"
New-ADGroup "CloudSync Users" -Path "OU=Administrative Groups,DC=ghh,DC=local" -GroupScope Global -GroupCategory Security
#Git sid and acl of the root OU
$sid = New-Object System.Security.Principal.SecurityIdentifier(Get-ADGroup "CloudSync Users").SID
$acl = Get-ACL $domain.distinguishedname
#Add Replicate changes all to root DN for CloudSync Users group
$acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule `
$sid,"ExtendedRight","Allow",'1131f6aa-9c07-11d1-f79f-00c04fc2dcd2',"None","00000000-0000-0000-0000-000000000000"))
Set-Acl -Path $domain.distinguishedname -AclObject $acl
$acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule `
$sid,"ExtendedRight","Allow",'1131f6ad-9c07-11d1-f79f-00c04fc2dcd2',"None","00000000-0000-0000-0000-000000000000"))
Set-Acl -Path $domain.distinguishedname -AclObject $acl
$acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule `
$sid,"ExtendedRight","Allow",'89e95b76-444d-4c62-991a-0facbeda640c',"None","00000000-0000-0000-0000-000000000000"))
Set-Acl -Path $domain.distinguishedname -AclObject $acl

#Get the ACL for Administrative Groups
$acl = Get-ACL "OU=Administrative Groups,DC=ghh,DC=local"
#Make a Password Admin user
new-ADuser PasswordAdmin -enabled $true -Description "Password Reset Admin" -AccountPassword (ConvertTo-SecureString "Passw+ord127" -AsPlaintext -Force )
#Set that user so that they can manage membership and passwords of groups in that OU 
 $sid = New-Object System.Security.Principal.SecurityIdentifier(Get-ADUser PasswordAdmin).SID

$acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule `
$sid,"WriteProperty","Allow", "bf9679c0-0de6-11d0-a285-00aa003049e2","Descendents",$guidmap["group"]))
 
$acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule `
$sid,"WriteProperty","Allow", "00299570-246d-11d0-a768-00aa006e0529","Descendents",$guidmap["user"]))
 Set-Acl -Path "OU=Administrative Groups,DC=ghh,DC=local" -AclObject $acl 
 New-ADComputer -Enabled $true -Name Password
 setspn -s www/Password PasswordAdmin
Add-ADGroupMember -Identity "CloudSync Users" -members "PasswordAdmin"
 
