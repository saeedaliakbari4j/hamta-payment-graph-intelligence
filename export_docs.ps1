$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\project\hamta\راهنمای_جامع_کدها_و_معماری_پروژه.docx")
$doc.Repaginate()
Write-Output ("PAGES=" + $doc.ComputeStatistics(2))
$doc.SaveAs2("D:\project\hamta\راهنمای_جامع_کدها_و_معماری_پروژه.pdf", 17)
$doc.Close([ref]$false)
$word.Quit()
