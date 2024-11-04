Write-Output "Before Event Commit -> $beforeEventCommit"
Write-Output "After Event Commit -> $afterEventCommit"

Write-Output "Build Tool -> $build_tool"
Write-Output "Private Key -> $private_key"

python make.py $beforeEventCommit $afterEventCommit $build_tool $private_key