param(
    [string]$TerraformDirectory = "../infrastructure/terraform"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$terraformRoot = (Resolve-Path (Join-Path $PSScriptRoot $TerraformDirectory)).Path
$artifact = Join-Path ([System.IO.Path]::GetTempPath()) "pace-talent-pool.zip"
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("pace-stage-" + [guid]::NewGuid().ToString("N"))
$parameterFile = Join-Path ([System.IO.Path]::GetTempPath()) ("pace-ssm-" + [guid]::NewGuid().ToString("N") + ".json")

try {
    New-Item -ItemType Directory -Path $stage | Out-Null
    Copy-Item -Recurse -LiteralPath (Join-Path $projectRoot "backend") -Destination $stage
    Copy-Item -Recurse -LiteralPath (Join-Path $projectRoot "frontend") -Destination $stage
    Copy-Item -LiteralPath (Join-Path $projectRoot "compose.yaml") -Destination $stage
    Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $artifact -Force

    Push-Location $terraformRoot
    try {
        $bucket = & terraform output -raw deployment_bucket
        if ($LASTEXITCODE -ne 0) { throw "Unable to read deployment_bucket from Terraform." }
        $instance = & terraform output -raw instance_id
        if ($LASTEXITCODE -ne 0) { throw "Unable to read instance_id from Terraform." }
    } finally {
        Pop-Location
    }
    aws s3 cp $artifact "s3://$bucket/releases/pace-talent-pool.zip"
    if ($LASTEXITCODE -ne 0) { throw "Artifact upload failed." }
    $downloadUrl = aws s3 presign "s3://$bucket/releases/pace-talent-pool.zip" --expires-in 3600 --region ap-south-1
    if ($LASTEXITCODE -ne 0) { throw "Unable to create the time-limited artifact URL." }

    $commands = @(
        "set -e",
        "cd /opt/pace-talent-pool",
        "curl -fsSL '$downloadUrl' -o /tmp/pace.zip",
        "find . -mindepth 1 -maxdepth 1 ! -name .env -exec rm -rf {} +",
        "unzip -o /tmp/pace.zip -d . || [ `$? -eq 1 ]",
        "docker compose up -d --build",
        "docker compose ps"
    )
    $parameterJson = @{ commands = $commands } | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($parameterFile, $parameterJson, [System.Text.UTF8Encoding]::new($false))
    $parameterUri = "file://" + $parameterFile.Replace("\", "/")
    $commandId = aws ssm send-command --region ap-south-1 --instance-ids $instance --document-name AWS-RunShellScript --parameters $parameterUri --query Command.CommandId --output text
    if ($LASTEXITCODE -ne 0) { throw "Unable to start remote deployment command." }
    aws ssm wait command-executed --region ap-south-1 --command-id $commandId --instance-id $instance
    if ($LASTEXITCODE -ne 0) { throw "Remote deployment did not complete successfully." }
    aws ssm get-command-invocation --region ap-south-1 --command-id $commandId --instance-id $instance --query "{Status:Status,ResponseCode:ResponseCode}" --output json
    if ($LASTEXITCODE -ne 0) { throw "Unable to retrieve deployment result." }
} finally {
    if (Test-Path -LiteralPath $artifact) { Remove-Item -LiteralPath $artifact -Force }
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    if (Test-Path -LiteralPath $parameterFile) { Remove-Item -LiteralPath $parameterFile -Force }
}
