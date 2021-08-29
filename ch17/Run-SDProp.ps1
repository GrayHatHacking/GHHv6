$dom = Get-ADDomain
$RootDSE = New-Object System.DirectoryServices.DirectoryEntry("LDAP://$($dom.PDCEmulator)/RootDSE")
$RootDSE.UsePropertyCache = $false
$RootDSE.Put($TaskName, "1") # RunProtectAdminGroupsTask & fixupinheritance
$RootDSE.SetInfo()
