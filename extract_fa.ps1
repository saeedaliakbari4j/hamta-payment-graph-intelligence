$docPath = (Get-ChildItem -Path "d:\project\hamta" -Filter "*.doc" | Where-Object { $_.Name -notlike "From_*" -and $_.Name -notlike "Research*" } | Select-Object -First 1).FullName
Write-Output "Found"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docPath)
    $out = @()
    foreach ($p in $doc.Paragraphs) {
        $t = $p.Range.Text.Trim()
        if ($t.Length -gt 0) {
            $out += ("[" + $p.Style.NameLocal + " | " + $p.Range.Font.Name + " " + $p.Range.Font.Size + " | align=" + $p.Alignment + "] " + $t)
        }
    }
    $ps = $doc.PageSetup
    $out += ("PageWidth=" + $ps.PageWidth + " Height=" + $ps.PageHeight + " L=" + $ps.LeftMargin + " R=" + $ps.RightMargin + " T=" + $ps.TopMargin + " B=" + $ps.BottomMargin + " Cols=" + $ps.TextColumns.Count)
    [System.IO.File]::WriteAllLines("d:\project\hamta\template_fa.txt", $out, [System.Text.Encoding]::UTF8)
    $doc.Close([ref]$false)
} catch {
    Write-Error $_
} finally {
    $word.Quit()
}
