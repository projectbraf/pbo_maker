Write-Output "Before Event Commit -> $beforeEventCommit"
Write-Output "After Event Commit -> $afterEventCommit"

Write-Output "Build Tool -> $build_tool"
Write-Output "Private Key -> $private_key"

$changedFiles = git diff --name-only $beforeCommit $afterCommit
Write-Output "Changed Files: $changedFiles"
$changedDirs = $changedFiles | ForEach-Object { $_.Split('/')[0] } | Select-Object -Unique
Write-Output "Changed Folders: $changedDirs"

$symlinkPath = "P:\$projectName"

if (Test-Path "P:\$projectName" -PathType Leaf) {
    Remove-Item $symlinkPath -Force
}

if (Test-Path $symlinkPath -PathType Container) {
  Remove-Item $symlinkPath -Force
}

New-Item -ItemType SymbolicLink -Path "$symlinkPath" -Target .

$changedDirs | ForEach-Object {
  $folder = $_
  if ($folder -like "$addonPrefix*") {
    $packedDir = "$symlinkPath\${folder}"
    Write-Output "Packing Folder: $packedDir"
  }
};