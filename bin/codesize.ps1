Param(
    [parameter(mandatory=$true)]
    $targets,
    $target_include = "*",
    $exclude_pattern,
    [Switch]
    $trim,
    [Switch]
    $csv,
    [Switch]
    $resolve
)

# Count lines of $filepath
function file_length($filePath, $trimEmptyLine, $excludePattern){
    $fileText = if($trimEmptyLine) { Get-Content $filePath | Where-Object { $_.Trim() -ne ""} }else{ Get-Content $filePath }
    $fileText = if($excludePattern) { $fileText | Select-String -NotMatch -Pattern $excludePattern }else{ $fileText }
    $fileText.Length
}

# Measure length of $filepath
function file_size($filePath){
    (Get-Item $filePath).Length
}

function csv_string($name, $lines, $size){
    ($name + ", Line, " + $lines + ", Size, " + $size)
}

function wclike_string($name, $lines, $size){
    (" " + $lines + " " + $size + " " + $name)
}

function format_data($csv_mode, $name, $lines, $size){
    if($csv_mode){
        csv_string $name $lines $size
    }else{
        wclike_string $name $lines $size
    }
}

$targetFiles = Get-ChildItem -Recurse -File -Include $target_include -Path $targets

$allLines = 0
$allSize = 0
foreach($file in $targetFiles){
    $fileLines = (file_length $file $trim $exclude_pattern)
    $fileSize = (file_size $file)

    $allLines += $fileLines
    $allSize += $fileSize

    $name = $file.toString()
    if(!$resolve){
        $name = (Resolve-Path $file -Relative).toString()
    }

    Write-Output (format_data $csv $name $fileLines $fileSize)
}

Write-Output (format_data $csv "All" $allLines $allSize)
