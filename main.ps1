$showedBeforeEventCommit = git show --format=short $beforeCommit
Write-Output "Before Event Commit -> $showedBeforeEventCommit"
$showedAfterEventCommit = git show --format=short $afterCommit
Write-Output "After Event Commit -> $showedAfterEventCommit"

Write-Output "Build Tool -> $build_tool"
Write-Output "Private Key -> $private_key"

Write-Output "Project Name -> $projectName"
Write-Output "Addon Prefix -> $addonPrefix"

$changedFiles = git diff --name-only $beforeCommit $afterCommit
if ($changedFiles.Length -eq 0) {
  Write-Output "No changed files"

  exit 1
}
Write-Output "Changed Files: $changedFiles"
$changedDirs = $changedFiles | ForEach-Object { $_.Split('/')[0] } | Select-Object -Unique
Write-Output "Changed Folders: $changedDirs"

$symlinkPath = "P:\$projectName"

if (Test-Path "P:\$projectName" -PathType Leaf) {
  Remove-Item $symlinkPath -Force
  Write-Output "Removing previous leaf symlink: $symlinkPath"
}

if (Test-Path $symlinkPath -PathType Container) {
  Remove-Item $symlinkPath -Force
  Write-Output "Removing previous container symlink: $symlinkPath"
}

Write-Output "Creating symlink: $symlinkPath"
New-Item -ItemType SymbolicLink -Path "$symlinkPath" -Target .

$changedDirs | ForEach-Object {
  $folder = $_
  $packedDir = "$symlinkPath\${folder}"
  Write-Output "Packing Folder: $packedDir"
};