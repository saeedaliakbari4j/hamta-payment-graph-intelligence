$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open('d:\project\hamta\ResearchPaperWritingFormatTemplate (1).doc')
$doc.SaveAs2('d:\project\hamta\template_en.docx', 16)
$doc.Close([ref]$false)
$word.Quit()
