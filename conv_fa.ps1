
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\project\hamta\فرمت_فارسی_مقالات.doc")
$doc.SaveAs2("D:\project\hamta\template_fa.docx", 16)
$doc.Close([ref]$false)
$word.Quit()
