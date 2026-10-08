$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\project\hamta\scratch\test_brackets.docx")
$doc.SaveAs2("D:\project\hamta\scratch\test_brackets.pdf", 17)
$doc.Close([ref]$false)
$word.Quit()
Write-Output "Done converting test_brackets.pdf"
