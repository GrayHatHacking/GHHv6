$dom = Get-ADDomain
$RootDSE = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$($dom.PDCEmulator)/RootDSE")
$RootDSE.UsePropertyCache = $false
$RootDSE.Put("RunProtectAdminGroupsTask", "1") 
$RootDSE.SetInfo()
$RootDSE = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$($dom.PDCEmulator)/RootDSE")
$RootDSE.UsePropertyCache = $false
$RootDSE.Put("fixupinheritance","1")
$RootDSE.SetInfo()
