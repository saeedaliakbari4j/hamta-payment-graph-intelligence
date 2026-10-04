$docPath = "d:\project\hamta\ResearchPaperWritingFormatTemplate (1).doc"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docPath)
    $text = $doc.Content.Text
    Set-Content -Path "d:\project\hamta\template_text.txt" -Value $text -Encoding UTF8
    Write-Output "Extracted length: $($text.Length)"
    $doc.Close([ref]$false)
} catch {
    Write-Error $_
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
