$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null  # log em UTF-8 no console

# ====== CONFIG ======
$AUTOMACAO = "C:\Users\Jucieli\Desktop\automacao_senior"
$REPO      = "C:\Users\Jucieli\Desktop\painel-produtivo"

$SRC_XLSX  = Join-Path $AUTOMACAO "movimentos_estoque_dados.xlsx"
$DST_XLSX  = Join-Path $REPO      "movimentos_estoque_dados.xlsx"

$PY_SENIOR = Join-Path $AUTOMACAO "senior_rpa.py"

$LOGFILE   = Join-Path $AUTOMACAO ("log_30min_" + (Get-Date -Format "yyyyMMdd") + ".txt")

function Log($msg) {
  $line = ("[{0}] {1}" -f (Get-Date -Format "dd/MM/yyyy HH:mm:ss"), $msg)
  Add-Content -Path $LOGFILE -Value $line -Encoding UTF8
  Write-Host $line
}

function RunGit {
  param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]] $GitArgs
  )

  Log ("git " + ($GitArgs -join " "))

  $out = & git @GitArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    Log ("ERRO git " + ($GitArgs -join " ") + " => " + ($out -join "`n"))
    throw "Falha no git " + ($GitArgs -join " ")
  }
  return $out
}

Log "=== INÍCIO ==="

# ====== 1) Rodar exportação Senior ======
Log "Rodando Senior RPA: $PY_SENIOR"
Push-Location $AUTOMACAO
try {
  $p = Start-Process -FilePath "python" -ArgumentList "`"$PY_SENIOR`"" -Wait -PassThru -NoNewWindow
  Log "Senior RPA finalizou com code: $($p.ExitCode)"
  if ($p.ExitCode -ne 0) {
    throw "Senior RPA retornou erro (ExitCode=$($p.ExitCode)). Veja prints erro_senior_*.png"
  }
}
finally {
  Pop-Location
}

# ====== 2) Validar XLSX atualizado ======
if (!(Test-Path $SRC_XLSX)) {
  throw "Arquivo não existe: $SRC_XLSX"
}

$mtime = (Get-Item $SRC_XLSX).LastWriteTime
Log "Última modificação do XLSX (automacao): $mtime"

$maxDelayMin = 20
if ($mtime -lt (Get-Date).AddMinutes(-$maxDelayMin)) {
  throw "XLSX parece antigo (>$maxDelayMin min). Não vou subir para GitHub."
}

# ====== 3) Preparar repo (auto-cura) ANTES de copiar ======
Push-Location $REPO
try {
  # Se tiver rebase travado, aborta
  $rebase1 = Join-Path $REPO ".git\rebase-merge"
  $rebase2 = Join-Path $REPO ".git\rebase-apply"
  if (Test-Path $rebase1 -or Test-Path $rebase2) {
    Log "Rebase travado detectado → abortando"
    & git rebase --abort 2>$null | Out-Null
  }

  RunGit fetch origin

  # Força repo ficar igual ao remoto (ideal para automação)
  RunGit reset --hard origin/main
  RunGit clean -fd
}
finally {
  Pop-Location
}

# ====== 4) Copiar XLSX para o repo ======
Log "Copiando para repo: $DST_XLSX"
Copy-Item $SRC_XLSX $DST_XLSX -Force

# ====== 5) Prova (HASH) ======
$srcHash = (Get-FileHash $SRC_XLSX -Algorithm MD5).Hash
$dstHash = (Get-FileHash $DST_XLSX -Algorithm MD5).Hash
Log "HASH SRC (automacao): $srcHash"
Log "HASH DST (repo):      $dstHash"

# ====== 6) Commit + push ======
Push-Location $REPO
try {
  RunGit add movimentos_estoque_dados.xlsx

  $changes = & git status --porcelain 2>&1
  Log ("git status --porcelain => " + ($changes -join " | "))

  if ($changes) {
    $msg = "Atualização automática de dados " + (Get-Date -Format "dd/MM/yyyy HH:mm:ss")
    Log "Commitando: $msg"
    RunGit commit -m $msg

    Log "Último commit:"
    $last = & git log -1 --oneline 2>&1
    Log ($last -join "`n")

    Log "Fazendo push..."
    $pushOut = & git push origin main 2>&1
    Log ($pushOut -join "`n")

    if ($LASTEXITCODE -ne 0) {
      throw "Push falhou (veja log acima)."
    }

    Log "OK: push concluído."
  } else {
    Log "Sem mudanças para commit (arquivo igual)."
  }
}
finally {
  Pop-Location
}

Log "=== FIM OK ==="
