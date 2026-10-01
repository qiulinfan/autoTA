#Requires -Version 7.0
# Preserve the existing Claude Code entry point and home override.
[CmdletBinding()]
param([string]$ClaudeHome)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'link-skills.ps1') -Runtime claude -RuntimeHome $ClaudeHome
