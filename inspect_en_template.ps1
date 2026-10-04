$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('d:\project\hamta\ResearchPaperWritingFormatTemplate (1).doc')
Write-Output ("Sections count: " + $doc.Sections.Count)
for ($i = 1; $i -le $doc.Sections.Count; $i++) {
    $sec = $doc.Sections.Item($i)
    Write-Output ("Section " + $i + ": Cols=" + $sec.PageSetup.TextColumns.Count + ", Width=" + $sec.PageSetup.PageWidth + ", Height=" + $sec.PageSetup.PageHeight)
}
$doc.Close([ref]$false)
$word.Quit()
