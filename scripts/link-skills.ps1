#Requires -Version 7.0
# Link only this product's Skills. Full installers retain agent/receipt ownership.
[CmdletBinding()]
param(
    [ValidateSet('claude', 'codex', 'opencode', 'omp')][string]$Runtime = 'claude',
    [string]$RuntimeHome
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$repositorySkills = Join-Path $repoRoot 'skills'
if (-not (Test-Path -LiteralPath $repositorySkills -PathType Container)) {
    throw "Missing product skills directory: $repositorySkills"
}
if (-not $RuntimeHome) {
    $RuntimeHome = switch ($Runtime) {
        'claude' { if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' } }
        'codex' { if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' } }
        'opencode' {
            $configHome = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME '.config' }
            Join-Path $configHome 'opencode'
        }
        'omp' { if ($env:PI_CODING_AGENT_DIR) { $env:PI_CODING_AGENT_DIR } else { Join-Path $HOME '.omp' 'agent' } }
    }
}
$runtimeSkills = Join-Path $RuntimeHome 'skills'
$existingRoot = Get-Item -Force -LiteralPath $runtimeSkills -ErrorAction SilentlyContinue
if ($null -ne $existingRoot -and ($existingRoot.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
    throw "Runtime skills path must be a runtime-owned real directory, not a link: $runtimeSkills"
}
if ($null -ne $existingRoot -and -not $existingRoot.PSIsContainer) {
    throw "Runtime skills path is not a directory: $runtimeSkills"
}
[System.IO.Directory]::CreateDirectory($runtimeSkills) | Out-Null

$comparison = if ($IsWindows) { [StringComparison]::OrdinalIgnoreCase } else { [StringComparison]::Ordinal }
$repositoryPrefix = [System.IO.Path]::GetFullPath($repositorySkills).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar

# Check every wanted destination before adding or removing a link.
foreach ($skill in (Get-ChildItem -LiteralPath $repositorySkills -Directory)) {
    if (-not (Test-Path -LiteralPath (Join-Path $skill.FullName 'SKILL.md') -PathType Leaf)) { continue }
    $destination = Join-Path $runtimeSkills $skill.Name
    $existing = Get-Item -Force -LiteralPath $destination -ErrorAction SilentlyContinue
    if ($null -eq $existing) { continue }
    if (-not $existing.LinkType -or -not $existing.LinkTarget -or
        -not [string]::Equals([System.IO.Path]::GetFullPath($existing.LinkTarget), $skill.FullName, $comparison)) {
        throw "Conflicting Skill entry: $destination"
    }
}

# Remove links this checkout owns that are stale or renamed. Links owned by
# qlblog or other product checkouts are never touched.
Get-ChildItem -Force -LiteralPath $runtimeSkills | ForEach-Object {
    if (-not ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { return }
    if ([string]::IsNullOrEmpty($_.LinkTarget)) { return }
    $target = [System.IO.Path]::GetFullPath($_.LinkTarget)
    if (-not $target.StartsWith($repositoryPrefix, $comparison)) { return }
    if ((Test-Path -LiteralPath (Join-Path $target 'SKILL.md') -PathType Leaf) -and
        ([System.IO.Path]::GetFileName($target) -eq $_.Name)) { return }
    Remove-Item -LiteralPath $_.FullName
    Write-Host "REMOVED stale autota Skill link: $($_.FullName)"
}

$linked = 0
foreach ($skillDirectory in (Get-ChildItem -LiteralPath $repositorySkills -Directory | Sort-Object Name)) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillDirectory.FullName 'SKILL.md') -PathType Leaf)) { continue }
    $destination = Join-Path $runtimeSkills $skillDirectory.Name
    $existing = Get-Item -Force -LiteralPath $destination -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        if (-not ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to replace a real file or directory: $destination"
        }
        if ([string]::IsNullOrEmpty($existing.LinkTarget) -or
            [System.IO.Path]::GetFullPath($existing.LinkTarget) -ne [System.IO.Path]::GetFullPath($skillDirectory.FullName)) {
            throw "Conflicting link exists: $destination"
        }
    } else {
        $kind = if ($IsWindows) { 'Junction' } else { 'SymbolicLink' }
        New-Item -ItemType $kind -Path $destination -Target $skillDirectory.FullName | Out-Null
    }
    $linked++
}

Write-Host "SKILLS_OK ($Runtime; $linked autota Skills; skills-only)"
