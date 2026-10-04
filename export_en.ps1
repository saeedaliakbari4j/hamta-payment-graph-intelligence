$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\project\hamta\From_Transactional_Data_to_Organizational_Intelligence.docx")
$doc.Repaginate()
Write-Output ("PAGES=" + $doc.ComputeStatistics(2))
$doc.SaveAs2("D:\project\hamta\From_Transactional_Data_to_Organizational_Intelligence.doc", 0)
$doc.SaveAs2("D:\project\hamta\From_Transactional_Data_to_Organizational_Intelligence.pdf", 17)
$doc.Close([ref]$false)
$word.Quit()
