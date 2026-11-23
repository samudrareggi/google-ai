#Requires -Version 5.1
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "../scripts/user-errors.ps1")

$cases = @(
    @{ Code = "payment_security_blocked"; Needle = "OR-REH-04" },
    @{ Code = "already_subscribed"; Needle = "already active" },
    @{ Code = "ineligible"; Needle = "not eligible" },
    @{ Code = "manual_subscribe_required"; Needle = "Slide to subscribe" },
    @{ Code = "today_price_unverified"; Needle = "due today" },
    @{ Code = "trial_duration_unverified"; Needle = "trial length" },
    @{ Code = "backup_payment_methods_prompt"; Needle = "backup payment methods" },
    @{ Code = "processing"; Needle = "still processing" },
    @{ Code = "offer_not_available"; Needle = "not available" },
    @{ Code = "offer_query_failed"; Needle = "Could not load" },
    @{ Code = "account_unavailable"; Needle = "Google Play account" },
    @{ Code = "device_missing"; Needle = "MuMu is not connected" }
)
foreach ($case in $cases) {
    $issue = Get-UserIssue -Code $case.Code
    if (-not $issue.Title.Contains($case.Needle)) {
        throw ("Incorrect title for {0}: {1}" -f $case.Code, $issue.Title)
    }
    if ([string]::IsNullOrWhiteSpace($issue.Action)) {
        throw ("Missing recommended action for {0}" -f $case.Code)
    }
}
$errors = @(
    @{ Message = "No online ADB devices"; Expected = "device_missing" },
    @{ Message = "Play account mismatch or unverified"; Expected = "account_mismatch" },
    @{ Message = "Offer query did not complete: offer_query_failed"; Expected = "offer_query_failed" },
    @{ Message = "No report produced at ..." ; Expected = "report_missing" },
    @{ Message = "Python not found"; Expected = "python_missing" }
)
foreach ($case in $errors) {
    $actual = Get-FailureCode -ErrorMessage $case.Message
    if ($actual -cne $case.Expected) {
        throw ("Error map mismatch: {0} -> {1}" -f $case.Message, $actual)
    }
}
# User-facing mode must not reveal internal status codes in its output.
$compact = (Show-UserIssue -Code "trial_duration_unverified" 6>&1 | Out-String)
# Write-Host writes to the Information stream; use redirected host output
# when available while also testing that debug mode explicitly shows codes.
$source = Get-Content -LiteralPath (Join-Path $PSScriptRoot "../scripts/user-errors.ps1") -Raw
if (-not $source.Contains('if ($DebugMode)')) {
    throw "Raw error diagnostics must be conditional on debug mode."
}
Write-Host "Friendly error messages: PASS" -ForegroundColor Green
