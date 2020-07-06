Param(
    [parameter(mandatory=$true)]
    $cpuusageon,
    [parameter(mandatory=$true)]
    $outputFile,
    [parameter(mandatory=$true)]
    $interval,
    [parameter(mandatory=$true)]
    $cmd,
    $arg
)

$loadoutput = "output.csv"
$timeoutput = $null
if(($outputFile -is [array]) -And ($outputFile.Length -eq 2)){
    $loadoutput = $outputFile[0]
    $timeoutput = $outputFile[1]
}else{
    $loadoutput = $outputFile
}

$tp = if($arg) {Start-Process -FilePath $cmd -ArgumentList $arg -PassThru}else{Start-Process -FilePath $cmd -PassThru}

$tp_id = $tp.id
$count = 0

do {
    $starttime = Get-Date
    $ps = Get-Process -Id $tp_id
    if($cpuusageon){
        $cpuusage = -1
        try {
            Get-Counter -ListSet Process -ErrorAction Stop | Out-Null
            $perfmon_instance = ((Get-Counter "\Process(*)\ID Process" -ErrorAction Stop).CounterSamples | ? {$_.RawValue -eq $tp_id}).Path
            $cpuusage = ((Get-Counter ($perfmon_instance -replace "\\id process$","\% Processor Time") -ErrorAction Stop).CounterSamples).CookedValue
        }catch [Exception] {
            $cpuusage = -1
        }
        if($cpuusage -gt 0){
            $cpuusage = $cpuusage / ($env:NUMBER_OF_PROCESSORS / 2)
        }
        $ps |
          Add-Member -MemberType NoteProperty -Name 'time' -Value $count -PassThru |
          Add-Member -MemberType NoteProperty -Name 'CPU_Usage' -Value $cpuusage -PassThru |
          Export-Csv -Path $loadoutput -Append -NoTypeInformation -Encoding UTF8
    }else{
        $ps |
          Add-Member -MemberType NoteProperty -Name 'time' -Value $count -PassThru |
          Export-Csv -Path $loadoutput -Append -NoTypeInformation -Encoding UTF8
    }

    $endtime = Get-Date
    $runningtime = ($endtime - $starttime).TotalSeconds * 1000
    $totalinterval = $interval - $runningtime
    if($totalinterval -gt 0) {
        Start-Sleep -m $totalinterval
        $count = $count + $interval
    }else{
        $count = $count + $runningtime
    }
}while(!$tp.HasExited)

$run_time = $tp.ExitTime - $tp.StartTime
if($timeoutput -eq $null){
    echo $run_time
}else{
    echo $run_time | Export-Csv -Path $timeoutput -Append -NoTypeInformation
}

