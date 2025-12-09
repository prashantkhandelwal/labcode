# Usage: .\SplitFiles.ps1 -FilesPerFolder 20

param (
    [int]$FilesPerFolder = 10  # Default count per folder
)

# Get all files in the current directory (excluding folders)
$files = Get-ChildItem -File

# Total number of files
$totalFiles = $files.Count

# Calculate number of folders needed
$folderCount = [math]::Ceiling($totalFiles / $FilesPerFolder)

# Loop through and create folders + move files
for ($i = 0; $i -lt $folderCount; $i++) {
    $folderName = "Batch_$($i + 1)"
    New-Item -ItemType Directory -Path $folderName -Force | Out-Null

    $startIndex = $i * $FilesPerFolder
    $endIndex = [math]::Min($startIndex + $FilesPerFolder, $totalFiles)

    $filesToMove = $files[$startIndex..($endIndex - 1)]

    foreach ($file in $filesToMove) {
        Move-Item -Path $file.FullName -Destination $folderName
    }
}

Write-Host "✅ Done! Split $totalFiles files into $folderCount folders with $FilesPerFolder files each."