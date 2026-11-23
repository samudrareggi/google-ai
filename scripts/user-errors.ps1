#Requires -Version 5.1
# Friendly terminal messages. This file never runs ADB or Google Play actions.
function Get-UserIssue {
    param([string]$Code)
    if ([string]::IsNullOrWhiteSpace($Code)) { $Code = "unknown" }
    switch ($Code.ToLowerInvariant()) {
        { $_ -in @("payment_security_blocked", "checkout_security_blocked") } {
            return [pscustomobject]@{
                Title = "Google Play blocked this payment (OR-REH-04)"
                Action = "Check account security and Google Payments alerts. Do not retry paid steps yet."
            }
        }
        "already_subscribed" {
            return [pscustomobject]@{
                Title = "This Google AI Pro plan is already active"
                Action = "No extra months were confirmed. Check the renewal date in Google Play; do not repeat this step."
            }
        }
        "ineligible" {
            return [pscustomobject]@{
                Title = "This account is not eligible for the selected offer"
                Action = "Review the terms in Google Play. -Force cannot make the offer eligible."
            }
        }
        "manual_subscribe_required" {
            return [pscustomobject]@{
                Title = "Google Play requires Slide to subscribe"
                Action = "Review the account, charge today and renewal terms. If you agree, use the slider in Google Play and verify the subscription there."
            }
        }
        "today_price_unverified" {
            return [pscustomobject]@{
                Title = "Could not confirm the amount due today"
                Action = "Review the checkout price on your Android screen. No Subscribe tap was confirmed."
            }
        }
        "trial_duration_unverified" {
            return [pscustomobject]@{
                Title = "Could not confirm the trial length"
                Action = "Review the duration shown by Google Play. The script stopped before confirming."
            }
        }
        "backup_payment_methods_prompt" {
            return [pscustomobject]@{
                Title = "Google Play asks about backup payment methods"
                Action = "Decide on that optional setting in Google Play. It is not subscription confirmation."
            }
        }
        "processing" {
            return [pscustomobject]@{
                Title = "Google Play is still processing"
                Action = "Check subscriptions and payment history before attempting any checkout again."
            }
        }
        "subscribe_button_not_found" {
            return [pscustomobject]@{
                Title = "The checkout button was not found"
                Action = "Check the Google Play screen. No Subscribe action was confirmed."
            }
        }
        "checkout_account_mismatch" {
            return [pscustomobject]@{
                Title = "Checkout is using a different account"
                Action = "Verify the billing account in Google Play. If it is different, close checkout and check offers again."
            }
        }
        "checkout_account_unverified" {
            return [pscustomobject]@{
                Title = "Checkout account could not be verified"
                Action = "Review the billing account and terms directly on the Google Play checkout screen."
            }
        }
        "offer_not_available" {
            return [pscustomobject]@{
                Title = "The selected offer is not available"
                Action = "Check available offers using -Step 1. Do not assume the trial applies to this account."
            }
        }
        { $_ -in @("offer_query_failed", "offers_unavailable") } {
            return [pscustomobject]@{
                Title = "Could not load Google AI offers"
                Action = "Open Google One and Google Play, check the connection, then run -Step 1."
            }
        }
        "account_unavailable" {
            return [pscustomobject]@{
                Title = "Could not identify the Google Play account"
                Action = "Open the Play Store profile, then retry or specify -Email with the expected account."
            }
        }
        "account_mismatch" {
            return [pscustomobject]@{
                Title = "Google Play is using a different account"
                Action = "Select the intended account in the Play Store. No checkout was started."
            }
        }
        "device_missing" {
            return [pscustomobject]@{
                Title = "MuMu is not connected"
                Action = "Start MuMu, enable ADB debugging, and retry -Step 0."
            }
        }
        "device_ambiguous" {
            return [pscustomobject]@{
                Title = "More than one Android device is connected"
                Action = "Rerun with -Serial followed by an exact ID from adb devices."
            }
        }
        "app_missing" {
            return [pscustomobject]@{
                Title = "Google Play or Google One is missing"
                Action = "Install or enable the required app on the selected MuMu device."
            }
        }
        "python_missing" {
            return [pscustomobject]@{
                Title = "Python is not available"
                Action = "Install Python 3.10 or later, reopen PowerShell, and try again."
            }
        }
        "adb_missing" {
            return [pscustomobject]@{
                Title = "Android Debug Bridge (ADB) is unavailable"
                Action = "Run python setup_env.py or install Android SDK platform-tools."
            }
        }
        "runtime_lookup_failed" {
            return [pscustomobject]@{
                Title = "Could not inspect the Android device"
                Action = "Restart Google Play and MuMu if needed, then run -Step 0 -Debug."
            }
        }
        "report_missing" {
            return [pscustomobject]@{
                Title = "The tool did not return a result"
                Action = "Check the local debug log. Verify Google Play before retrying any payment step."
            }
        }
        "checkout_not_confirmed" {
            return [pscustomobject]@{
                Title = "The purchase was not confirmed"
                Action = "Check Google Play Subscriptions before retrying. No extension is verified."
            }
        }
        { $_ -in @("checkout_not_visible", "price_unverified", "unknown") } {
            return [pscustomobject]@{
                Title = "Could not confirm the checkout"
                Action = "Check the Google Play screen and subscription history before trying again."
            }
        }
        default {
            return [pscustomobject]@{
                Title = "Could not complete this step"
                Action = "Check the Android screen and local debug log before retrying."
            }
        }
    }
}

function Get-FailureCode {
    param([string]$ErrorMessage)
    if ($ErrorMessage -match '(?i)Python not found') { return "python_missing" }
    if ($ErrorMessage -match '(?i)adb\.exe was not found|ADB device discovery failed') { return "adb_missing" }
    if ($ErrorMessage -match '(?i)No online ADB devices|selected serial.*not online') { return "device_missing" }
    if ($ErrorMessage -match '(?i)Cannot select a single Android device|Invalid device number') { return "device_ambiguous" }
    if ($ErrorMessage -match '(?i)Android package missing|Android package.*unavailable') { return "app_missing" }
    if ($ErrorMessage -match '(?i)Play account mismatch|Play Store account changed|Invalid Play Store account') { return "account_mismatch" }
    if ($ErrorMessage -match '(?i)Cannot identify the active Google Play account|No valid email') { return "account_unavailable" }
    if ($ErrorMessage -match '(?i)Offer query did not complete|Could not refresh the offer list') { return "offer_query_failed" }
    if ($ErrorMessage -match '(?i)No report produced') { return "report_missing" }
    if ($ErrorMessage -match '(?i)Runtime lookup failed|No machine-readable runtime result') { return "runtime_lookup_failed" }
    return "unknown"
}

function Show-UserIssue {
    param(
        [string]$Code,
        [string]$Details = "",
        [bool]$DebugMode = $false
    )
    $issue = Get-UserIssue -Code $Code
    Write-Host ""
    Write-Host ("  ! {0}" -f $issue.Title) -ForegroundColor Yellow
    Write-Host ("    Next: {0}" -f $issue.Action) -ForegroundColor Gray
    if ($DebugMode) {
        Write-Host ("    Code: {0}" -f $Code) -ForegroundColor DarkGray
        if ($Details) { Write-Host ("    Details: {0}" -f $Details) -ForegroundColor DarkGray }
    }
}
