# DUPLICATE FILE CLEANUP SCRIPT
# Total Expected Savings: ~4-5 GB
# This script will DELETE duplicates and keep only ONE copy

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "DUPLICATE FILE CLEANUP - PRIORITIZED BY SIZE" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$totalSaved = 0
$filesDeleted = 0

# Function to safely delete file
function Remove-Duplicate {
    param($filePath, $sizeMB)
    
    if (Test-Path $filePath) {
        try {
            Remove-Item -Path $filePath -Force
            Write-Host "[OK] DELETED: $filePath" -ForegroundColor Green
            $script:totalSaved += $sizeMB
            $script:filesDeleted++
            return $true
        } catch {
            Write-Host "[FAIL] $filePath - $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "[SKIP] NOT FOUND: $filePath" -ForegroundColor Yellow
        return $false
    }
}

Write-Host "TOP PRIORITY - HUGE SPACE WASTERS" -ForegroundColor Red
Write-Host ""

# 1. SOCOFing.zip - SAVE 1.57 GB
Write-Host "[1/20] SOCOFing.zip duplicates (Save 1.57 GB)..." -ForegroundColor Yellow
Remove-Duplicate "SOCOFing (1).zip" 785.4
Remove-Duplicate "SOCOFing (2).zip" 785.4

# 2. Green and Brown Professional Business Report - SAVE 463 MB
Write-Host "[2/20] Green and Brown Professional Business Report (Save 463 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Green and Brown Professional Business Report Presentation (1).pdf" 92.33
Remove-Duplicate "Copy of Green and Brown Professional Business Report Presentation.pdf" 92.71
Remove-Duplicate "Copy of Green and Brown Professional Business Report Presentation (1).pdf" 92.71
Remove-Duplicate "Copy of Green and Brown Professional Business Report Presentation (2).pdf" 92.71
Remove-Duplicate "Copy of Green and Brown Professional Business Report Presentation (3).pdf" 96.01

# 3. Adobe Scan 02 Oct 2024 (1) - SAVE 401 MB
Write-Host "[3/20] Adobe Scan 02 Oct 2024 (1) duplicates (Save 401 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (1).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (2).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (3).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (4).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (5).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (6).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (7).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (8).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (9).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (10).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (11).pdf" 33.43
Remove-Duplicate "Adobe Scan 02 Oct 2024 (1) (12).pdf" 33.43

# 4. Adobe Scan 09 Nov 2024 - SAVE 172 MB
Write-Host "[4/20] Adobe Scan 09 Nov 2024 duplicates (Save 172 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Adobe Scan 09 Nov 2024 (1).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (2).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (3).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (4).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (5).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (6).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (7).pdf" 21.43
Remove-Duplicate "Adobe Scan 09 Nov 2024 (8).pdf" 21.43

# 5. Adobe Scan 02 Oct 2024 (2) - SAVE 160 MB
Write-Host "[5/20] Adobe Scan 02 Oct 2024 (2) duplicates (Save 160 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (1).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (2).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (3).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (4).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (5).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (6).pdf" 22.82
Remove-Duplicate "Adobe Scan 02 Oct 2024 (2) (7).pdf" 22.82

# 6. unstopsmarthire.exe - SAVE 160 MB
Write-Host "[6/20] unstopsmarthire.exe duplicates (Save 160 MB)..." -ForegroundColor Yellow
Remove-Duplicate "unstopsmarthire-2.2.0 (1).exe" 79.85
Remove-Duplicate "unstopsmarthire-2.0.0 (1).exe" 79.78

# 7. Antigravity.exe - SAVE 152 MB
Write-Host "[7/20] Antigravity.exe duplicates (Save 152 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Antigravity (1).exe" 152.36

# 8. MASTERING CLOUD COMPUTING.pdf - SAVE 105 MB
Write-Host "[8/20] MASTERING CLOUD COMPUTING duplicates (Save 105 MB)..." -ForegroundColor Yellow
Remove-Duplicate "MASTERING CLOUD COMPUTING (2).pdf" 34.96
Remove-Duplicate "MASTERING CLOUD COMPUTING (1).pdf" 34.9
Remove-Duplicate "MASTERING CLOUD COMPUTING (1) (1).pdf" 34.9

# 9. UML 2 and the Unified Process.pdf - SAVE 73 MB
Write-Host "[9/20] UML 2 and the Unified Process duplicates (Save 73 MB)..." -ForegroundColor Yellow
Remove-Duplicate "UML 2 and the Unified Process... ( PDFDrive ) (1).pdf" 72.85

# 10. 6d1a5300-1055-44d0-8186-ca0576f8f00a.zip - SAVE 69 MB
Write-Host "[10/20] 6d1a5300 zip duplicates (Save 69 MB)..." -ForegroundColor Yellow
Remove-Duplicate "6d1a5300-1055-44d0-8186-ca0576f8f00a (1).zip" 68.88

Write-Host ""
Write-Host "MEDIUM PRIORITY - GOOD SAVINGS" -ForegroundColor Yellow
Write-Host ""

# 11. Dynamic-MCP.pptx - SAVE 59 MB
Write-Host "[11/20] Dynamic-MCP.pptx duplicates (Save 59 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Dynamic-MCP (1).pptx" 21.21
Remove-Duplicate "Dynamic-MCP (1) (1).pptx" 21.21

# 12. base.obj - SAVE 57 MB
Write-Host "[12/20] base.obj duplicates (Save 57 MB)..." -ForegroundColor Yellow
Remove-Duplicate "base (1).obj" 57.2

# 13. ap.zip - SAVE 89 MB
Write-Host "[13/20] ap.zip duplicates (Save 89 MB)..." -ForegroundColor Yellow
Remove-Duplicate "ap (1).zip" 44.41
Remove-Duplicate "ap (2).zip" 44.41

# 14. hackzip.zip - SAVE 56 MB
Write-Host "[14/20] hackzip.zip duplicates (Save 56 MB)..." -ForegroundColor Yellow
Remove-Duplicate "hackzip (1).zip" 27.93
Remove-Duplicate "hackzip (2).zip" 27.93

# 15. Memora-Restoring-Connection-Through-Memory.pptx - SAVE 41 MB
Write-Host "[15/20] Memora presentation duplicates (Save 41 MB)..." -ForegroundColor Yellow
Remove-Duplicate "Memora-Restoring-Connection-Through-Memory (1).pptx" 40.68

# 16. mod2RS.pdf - SAVE 79 MB
Write-Host "[16/20] mod2RS.pdf duplicates (Save 79 MB)..." -ForegroundColor Yellow
Remove-Duplicate "mod2RS (1).pdf" 39.69
Remove-Duplicate "mod2RS (2).pdf" 39.69

# 17. mod1RS.pdf - SAVE 57 MB
Write-Host "[17/20] mod1RS.pdf duplicates (Save 57 MB)..." -ForegroundColor Yellow
Remove-Duplicate "mod1RS (1).pdf" 19.17
Remove-Duplicate "mod1RS (2).pdf" 19.17
Remove-Duplicate "mod1RS (3).pdf" 19.17

# 18. projectAB.zip - SAVE 60 MB
Write-Host "[18/20] projectAB.zip duplicates (Save 60 MB)..." -ForegroundColor Yellow
Remove-Duplicate "projectAB (1).zip" 29.73
Remove-Duplicate "projectAB (2).zip" 29.73

# 19. node-v20.11.1-x64.msi - SAVE 25 MB
Write-Host "[19/20] node installer duplicate (Save 25 MB)..." -ForegroundColor Yellow
Remove-Duplicate "node-v20.11.1-x64 (1).msi" 25.4

# 20. POM MODULE 3.pptx - SAVE 13 MB
Write-Host "[20/20] POM MODULE 3 duplicates (Save 13 MB)..." -ForegroundColor Yellow
Remove-Duplicate "POM MODULE 3 (1).pptx" 3.2
Remove-Duplicate "POM MODULE 3 (2).pptx" 3.2
Remove-Duplicate "POM MODULE 3 (3).pptx" 3.2
Remove-Duplicate "POM MODULE 3 (4).pptx" 3.2

# Final Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Files Deleted: $filesDeleted" -ForegroundColor Yellow
Write-Host "Space Saved: $([math]::Round($totalSaved/1024, 2)) GB" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Files marked for review were NOT deleted:" -ForegroundColor Yellow
Write-Host "  - Dynamic-MCP (2).pptx (different size - 17.24 MB)" -ForegroundColor Cyan
Write-Host "  - projectAB (3).zip (different size - 1.63 MB)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
