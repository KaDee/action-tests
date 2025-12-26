# Test Suite for cpp2html.xsl

This directory contains comprehensive unit and validation tests for the `cpp2html.xsl` XSLT transformation stylesheet.

## Overview

The test suite validates:
1. **XSL Structure**: Well-formedness, namespace declarations, template definitions
2. **Capitalization Fix**: The primary change - "Organisation Type" header capitalization
3. **XSLT Transformation**: Actual transformation execution and output validation
4. **HTML Output**: Generated HTML structure, accessibility, and content validation

## Test Files

### `test_cpp2html_xsl.py`
Main test suite focusing on XSL file validation and transformation logic.

**Test Coverage:**
- XSL file existence and well-formedness
- Namespace declarations (XSLT, CPP, XHTML)
- "Organisation Type" capitalization (PRIMARY TEST)
- Table header consistency across all tables
- Public documentation table structure
- Column width attributes (20%, 20%, 10%, 50%)
- XSL output method configuration
- CSS styles embedding
- Template definitions and parameters
- XSLT transformation execution (if xsltproc available)
- Generated HTML validation

### `test_html_output_validation.py`
Supplementary test suite for HTML output validation.

**Test Coverage:**
- HTML file existence
- HTML structure validity (DOCTYPE, html, head, body tags)
- "Organisation Type" capitalization in output
- Table structure and formatting
- CSS styles in output
- UTF-8 encoding
- Accessibility (proper th elements)
- Hyperlink formatting
- Tag integrity (no broken tags)
- Consistent table styling

## Running the Tests

### Prerequisites

**Required:**
- Python 3.7+
- Standard library modules only (no external dependencies required)

**Optional (for full test coverage):**
- `xsltproc` - For actual XSLT transformation tests
  ```bash
  sudo apt-get install xsltproc  # Debian/Ubuntu
  brew install libxslt            # macOS
  ```

### Execute Tests

Run the main test suite:
```bash
cd tests
python3 test_cpp2html_xsl.py
```

Run HTML output validation:
```bash
cd tests
python3 test_html_output_validation.py
```

Run all tests:
```bash
cd tests
./run_all_tests.sh
```

Or from repository root:
```bash
python3 tests/test_cpp2html_xsl.py
python3 tests/test_html_output_validation.py
```

### Expected Output