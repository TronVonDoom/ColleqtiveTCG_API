# Reorganize Pokemon TCG images into language-specific folders
# Moving from: tcg-images/pokemon/{cards,sets,series,icons}
# Moving to:   tcg-images/pokemon/en/{cards,sets,series,icons}

Write-Host "`n[REORGANIZE] Pokemon TCG Images - Multi-Language Support" -ForegroundColor Cyan
Write-Host "=" -NoNewline
for ($i = 0; $i -lt 79; $i++) { Write-Host "=" -NoNewline }
Write-Host ""
Write-Host ""

$apiBase = "C:\Users\TronVonDoom\Documents\GitHub\ColleqtiveTCG_API\tcg-images\pokemon"
$newLangFolder = "$apiBase\en"

# Check if old structure exists
$oldFolders = @("cards", "sets", "series", "icons")
$foldersExist = $false

foreach ($folder in $oldFolders) {
    if (Test-Path "$apiBase\$folder") {
        $foldersExist = $true
        break
    }
}

if (-not $foldersExist) {
    Write-Host "[ERROR] No old folder structure found. Images may already be organized." -ForegroundColor Red
    Write-Host "        Looking for folders in: $apiBase" -ForegroundColor Gray
    exit 1
}

# Check if new structure already exists
if (Test-Path $newLangFolder) {
    Write-Host "[WARNING] en folder already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite/merge? (y/n)"
    if ($response -ne 'y') {
        Write-Host "[CANCELLED] Reorganization cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host "[INFO] Current structure:" -ForegroundColor Yellow
Get-ChildItem -Path $apiBase -Directory | Select-Object Name | Format-Table -HideTableHeaders

Write-Host "`n[CREATE] Creating new language folder structure..." -ForegroundColor Cyan
New-Item -Path $newLangFolder -ItemType Directory -Force | Out-Null
Write-Host "         [OK] Created: pokemon\en\" -ForegroundColor Green

Write-Host "`n[MOVE] Moving folders to pokemon\en\..." -ForegroundColor Cyan

$moved = 0
$failed = 0

foreach ($folder in $oldFolders) {
    $source = "$apiBase\$folder"
    $destination = "$newLangFolder\$folder"
    
    if (Test-Path $source) {
        Write-Host "       Moving: $folder..." -NoNewline
        
        try {
            # Count files before move
            $fileCount = (Get-ChildItem -Path $source -Recurse -File).Count
            
            # Move the folder
            Move-Item -Path $source -Destination $destination -Force
            
            Write-Host " [OK] ($fileCount files)" -ForegroundColor Green
            $moved++
        }
        catch {
            Write-Host " [FAILED] $_" -ForegroundColor Red
            $failed++
        }
    }
    else {
        Write-Host "       Skipping: $folder (not found)" -ForegroundColor Gray
    }
}

Write-Host "`n[INFO] New structure:" -ForegroundColor Yellow
Get-ChildItem -Path $newLangFolder -Directory | Select-Object Name | Format-Table -HideTableHeaders

# Count total files in new structure
$totalFiles = (Get-ChildItem -Path $newLangFolder -Recurse -File).Count
$totalSize = (Get-ChildItem -Path $newLangFolder -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1GB

Write-Host "`n[SUMMARY]" -ForegroundColor Green
Write-Host "  * Folders moved: $moved" -ForegroundColor White
Write-Host "  * Folders failed: $failed" -ForegroundColor White
Write-Host "  * Total files: $totalFiles" -ForegroundColor White
Write-Host "  * Total size: $([math]::Round($totalSize, 2)) GB" -ForegroundColor White

Write-Host "`n[STRUCTURE] New folder layout:" -ForegroundColor Cyan
Write-Host "  tcg-images\" -ForegroundColor Gray
Write-Host "  +-- pokemon\" -ForegroundColor Gray
Write-Host "      +-- en\" -ForegroundColor Yellow
Write-Host "          +-- cards\" -ForegroundColor Green
Write-Host "          +-- sets\" -ForegroundColor Green
Write-Host "          +-- series\" -ForegroundColor Green
Write-Host "          +-- icons\" -ForegroundColor Green

Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "  1. Test the website to ensure images load correctly"
Write-Host "  2. Add new language folders (e.g., ja, es, fr) as needed"
Write-Host "  3. Update any download scripts to use the new structure"

Write-Host "`n[COMPLETE] Reorganization complete!" -ForegroundColor Green
Write-Host ""
