$docxPath = "d:\project\hamta\FA_From_Transactional_Data_to_Organizational_Intelligence.docx"
$pdfPath = "d:\project\hamta\FA_From_Transactional_Data_to_Organizational_Intelligence.pdf"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    $doc.SaveAs([ref]$pdfPath, [ref]17) # 17 = wdFormatPDF
    $pages = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    $doc.Close([ref]$false)
    Write-Output "Successfully exported FA PDF with $pages pages"
} catch {
    Write-Error $_
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
