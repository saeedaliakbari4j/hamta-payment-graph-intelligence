Get-Process -Name WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

$docxPath = "d:\project\hamta\FA_From_Transactional_Data_to_Organizational_Intelligence.docx"
$docPath = "d:\project\hamta\FA_From_Transactional_Data_to_Organizational_Intelligence.doc"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    $doc.SaveAs([ref]$docPath, [ref]0)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported FA .doc: $docPath"
} catch {
    Write-Error $_
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
