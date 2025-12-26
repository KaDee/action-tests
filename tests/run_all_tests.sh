#!/bin/bash
# run_all_tests.sh - Execute all test suites for cpp2html.xsl

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "========================================="
echo "XSLT Test Suite Runner"
echo "========================================="
echo ""

# Track overall success
OVERALL_SUCCESS=0

# Run main XSL tests
echo "Running XSL transformation tests..."
echo "========================================="
if python3 tests/test_cpp2html_xsl.py; then
    echo "✓ XSL tests passed"
else
    echo "✗ XSL tests failed"
    OVERALL_SUCCESS=1
fi

echo ""
echo ""

# Run HTML output validation tests
echo "Running HTML output validation tests..."
echo "========================================="
if python3 tests/test_html_output_validation.py; then
    echo "✓ HTML validation tests passed"
else
    echo "✗ HTML validation tests failed"
    OVERALL_SUCCESS=1
fi

echo ""
echo "========================================="
echo "Overall Test Results"
echo "========================================="

if [ $OVERALL_SUCCESS -eq 0 ]; then
    echo "✓ All test suites passed successfully!"
    exit 0
else
    echo "✗ Some test suites failed"
    exit 1
fi