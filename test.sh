#!/usr/bin/env bash
set -e

echo "=================================================="
echo "🧪 Running SimpleNutri Automated Verification Suite"
echo "=================================================="

PYTHON_EXEC="python3"
if [ -f "backend/.venv/bin/python3" ]; then
  PYTHON_EXEC="backend/.venv/bin/python3"
fi

PYTEST_EXEC="pytest"
if [ -f "backend/.venv/bin/pytest" ]; then
  PYTEST_EXEC="backend/.venv/bin/pytest"
fi

echo "▶ Step 1/3: Validating Full ICMR-NIN IFCT 2017 Dataset..."
$PYTHON_EXEC backend/scripts/validate_data.py

echo ""
echo "▶ Step 2/3: Verifying SQLite Database & Mobile Bundle Sync..."
$PYTHON_EXEC backend/scripts/export_offline_db.py

echo ""
echo "▶ Step 3/3: Running All 38 Automated Pytest Unit & Integration Tests..."
$PYTEST_EXEC backend/tests/ -v

echo ""
echo "=================================================="
echo "✅ All Automated Tests & Integrity Checks PASSED!"
echo "=================================================="
