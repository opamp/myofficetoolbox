Param(
    [parameter(mandatory=$true)]
    $outputFile,
    [parameter(mandatory=$true)]
    $interval,
    [parameter(mandatory=$true)]
    $cmd,
    $arg)

$loadoutput = "output.csv"
$timeoutput = $null

if(($outputFile -is [array]) -And ($outputFile.Length -eq 2)){
    $loadoutput = $outputFile[0]
    $timeoutput = $outputFile[1]
}else{
    $loadoutput = $outputFile
}

$tp = if($arg){ Start-Process -FilePath $cmd -ArgumentList $arg -PassThru }else{ Start-Process -FilePath $cmd -PassThru }
$tp_id = $tp.id

$count = 0
do{
    Get-Process -Id $tp_id | Add-Member -MemberType NoteProperty -Name 'time' -Value $count -PassThru |Export-Csv -Path $loadoutput -Append -NoTypeInformation -Encoding UTF8
    Start-Sleep -m $interval
    $count = $count + $interval
}while(!$tp.HasExited)

$run_time = $tp.ExitTime - $tp.StartTime

if($timeoutput -eq $null){
    echo $run_time
}else{
    echo $run_time | Export-Csv -Path $timeoutput -Append -NoTypeInformation -Encoding UTF8
}
