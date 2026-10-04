$docxPath = "d:\project\hamta\From_Transactional_Data_to_Organizational_Intelligence.docx"
$docPath = "d:\project\hamta\From_Transactional_Data_to_Organizational_Intelligence.doc"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    $doc.SaveAs([ref]$docPath, [ref]0) # 0 = wdFormatDocument (.doc)
    $doc.Close([ref]$false)
    Write-Output "Successfully exported to .doc format: $docPath"
} catch {
    Write-Error $_
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
