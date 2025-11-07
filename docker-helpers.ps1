# NewsIQ Docker Helper Scripts for Windows PowerShell
# Source this file or run individual commands

# Build images
function Build-NewsIQ {
    docker-compose build
}

# Start services
function Start-NewsIQ {
    docker-compose up -d
    Write-Host "✓ NewsIQ started!"
    Write-Host "  Frontend: http://localhost:3000"
    Write-Host "  Backend:  http://localhost:8000"
    Write-Host "  Docs:     http://localhost:8000/docs"
}

# Stop services
function Stop-NewsIQ {
    docker-compose down
    Write-Host "✓ NewsIQ stopped!"
}

# Restart services
function Restart-NewsIQ {
    docker-compose restart
    Write-Host "✓ NewsIQ restarted!"
}

# View logs
function Show-NewsIQLogs {
    docker-compose logs -f
}

# View backend logs only
function Show-BackendLogs {
    docker-compose logs -f backend
}

# View frontend logs only
function Show-FrontendLogs {
    docker-compose logs -f frontend
}

# Show running containers
function Show-NewsIQStatus {
    docker-compose ps
}

# Rebuild and restart
function Rebuild-NewsIQ {
    docker-compose up -d --build
    Write-Host "✓ NewsIQ rebuilt and restarted!"
}

# Clean everything (including volumes)
function Clean-NewsIQ {
    $response = Read-Host "This will delete all data including ChromaDB. Continue? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        docker-compose down -v
        Write-Host "✓ NewsIQ cleaned (all data removed)!"
    } else {
        Write-Host "Cancelled."
    }
}

# Backup ChromaDB
function Backup-ChromaDB {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupFile = "chroma-backup-$timestamp.tar.gz"
    docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup alpine tar czf /backup/$backupFile -C /data .
    Write-Host "✓ Backup created: $backupFile"
}

# Restore ChromaDB
function Restore-ChromaDB {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BackupFile
    )
    
    if (-not (Test-Path $BackupFile)) {
        Write-Host "Error: Backup file '$BackupFile' not found!"
        return
    }
    
    $response = Read-Host "This will replace current data. Continue? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        docker-compose down
        docker run --rm -v newsiq_chroma-data:/data -v ${PWD}:/backup alpine sh -c "rm -rf /data/* && tar xzf /backup/$BackupFile -C /data"
        docker-compose up -d
        Write-Host "✓ Backup restored and services restarted!"
    } else {
        Write-Host "Cancelled."
    }
}

# Show help
function Show-NewsIQHelp {
    Write-Host @"
NewsIQ Docker Helper Commands:

  Build-NewsIQ           - Build Docker images
  Start-NewsIQ           - Start all services
  Stop-NewsIQ            - Stop all services
  Restart-NewsIQ         - Restart all services
  Show-NewsIQLogs        - View logs from all services
  Show-BackendLogs       - View backend logs only
  Show-FrontendLogs      - View frontend logs only
  Show-NewsIQStatus      - Show running containers
  Rebuild-NewsIQ         - Rebuild and restart all services
  Clean-NewsIQ           - Stop and remove everything (including data)
  Backup-ChromaDB        - Backup ChromaDB data
  Restore-ChromaDB       - Restore ChromaDB data from backup
  Show-NewsIQHelp        - Show this help message

Example usage:
  PS> Start-NewsIQ
  PS> Show-NewsIQLogs
  PS> Backup-ChromaDB
  PS> Stop-NewsIQ

"@
}

# Show help on load
Write-Host "NewsIQ Docker Helper loaded! Type 'Show-NewsIQHelp' for available commands."
