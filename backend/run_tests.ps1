# Test Runner Script for Windows PowerShell
# Smart Voice Interviewer Backend Tests

param(
    [ValidateSet('all', 'unit', 'integration', 'database', 'auth', 'interview', 'profile', 'general', 'coverage', 'quick', 'slow')]
    [string]$Suite = 'all',
    
    [switch]$Verbose,
    [string]$Keyword,
    [string]$File,
    [switch]$Pdb,
    [switch]$LastFailed
)

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  Smart Voice Interviewer - Test Runner" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Build pytest command
$cmd = "pytest"

# Add test suite/marker
switch ($Suite) {
    'all' {
        $cmd += " tests/"
        Write-Host "Running all tests..." -ForegroundColor Green
    }
    'coverage' {
        $cmd += " --cov --cov-report=html --cov-report=term-missing tests/"
        Write-Host "Running tests with coverage report..." -ForegroundColor Green
    }
    'quick' {
        $cmd += " -m 'not slow' tests/"
        Write-Host "Running quick tests (excluding slow tests)..." -ForegroundColor Green
    }
    'unit' {
        $cmd += " -m unit tests/"
        Write-Host "Running unit tests..." -ForegroundColor Green
    }
    'integration' {
        $cmd += " -m integration tests/"
        Write-Host "Running integration tests..." -ForegroundColor Green
    }
    'database' {
        $cmd += " -m database tests/"
        Write-Host "Running database tests..." -ForegroundColor Green
    }
    'auth' {
        $cmd += " -m auth tests/"
        Write-Host "Running authentication tests..." -ForegroundColor Green
    }
    'interview' {
        $cmd += " -m interview tests/"
        Write-Host "Running interview tests..." -ForegroundColor Green
    }
    'profile' {
        $cmd += " -m profile tests/"
        Write-Host "Running profile tests..." -ForegroundColor Green
    }
    'general' {
        $cmd += " tests/test_general.py"
        Write-Host "Running general endpoint tests..." -ForegroundColor Green
    }
    'slow' {
        $cmd += " -m slow tests/"
        Write-Host "Running slow tests..." -ForegroundColor Green
    }
}

# Add file filter
if ($File) {
    $cmd = "pytest tests/$File"
    Write-Host "Running tests from: $File" -ForegroundColor Green
}

# Add keyword filter
if ($Keyword) {
    $cmd += " -k $Keyword"
    Write-Host "Filtering tests by keyword: $Keyword" -ForegroundColor Yellow
}

# Add verbose flag
if ($Verbose) {
    $cmd += " -v"
}

# Add debugger flag
if ($Pdb) {
    $cmd += " --pdb"
    Write-Host "PDB debugger enabled" -ForegroundColor Yellow
}

# Add last failed flag
if ($LastFailed) {
    $cmd += " --lf"
    Write-Host "Running only last failed tests" -ForegroundColor Yellow
}

Write-Host "`nExecuting: $cmd`n" -ForegroundColor Gray

# Run the command
Invoke-Expression $cmd
$exitCode = $LASTEXITCODE

# Print summary
Write-Host "`n============================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "  ✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "  ❌ Some tests failed." -ForegroundColor Red
}
Write-Host "============================================================`n" -ForegroundColor Cyan

# Exit with same code
exit $exitCode
