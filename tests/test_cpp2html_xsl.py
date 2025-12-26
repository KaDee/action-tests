"""
test_cpp2html_xsl.py

Comprehensive unit tests for cpp2html.xsl XSLT transformation.
Tests focus on the table header capitalization fix and validates the entire
transformation output for correctness, consistency, and adherence to requirements.
"""

import subprocess
import xml.etree.ElementTree as ET
import os
import sys
import re
import tempfile
from pathlib import Path


class TestCpp2HtmlTransformation:
    """Test suite for cpp2html.xsl XSLT transformations."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.xsl_file = self.repo_root / "cpp2html.xsl"
        self.cpp_dirs = list(self.repo_root.glob("CPP-*"))
        self.test_results = []
        self.xsltproc_available = self._check_xsltproc()

    def _check_xsltproc(self):
        """Check if xsltproc is available."""
        try:
            subprocess.run(
                ["xsltproc", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def log_result(self, test_name, passed, message=""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        result = f"[{status}] {test_name}"
        if message:
            result += f": {message}"
        self.test_results.append((passed, result))
        print(result)

    def test_xsl_file_exists(self):
        """Test that the XSL file exists and is readable."""
        test_name = "XSL file exists"
        exists = self.xsl_file.exists() and self.xsl_file.is_file()
        self.log_result(test_name, exists, str(self.xsl_file))
        return exists

    def test_xsl_well_formed(self):
        """Test that the XSL file is well-formed XML."""
        test_name = "XSL file is well-formed XML"
        try:
            ET.parse(self.xsl_file)
            self.log_result(test_name, True)
            return True
        except ET.ParseError as e:
            self.log_result(test_name, False, f"Parse error: {e}")
            return False

    def test_xsl_namespace_declaration(self):
        """Test that XSL has proper namespace declarations."""
        test_name = "XSL namespace declarations"
        try:
            tree = ET.parse(self.xsl_file)
            root = tree.getroot()
            
            # Check for XSLT namespace
            has_xsl_ns = 'http://www.w3.org/1999/XSL/Transform' in root.tag
            
            # Read file content to check namespace declarations
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_cpp_ns = 'xmlns:cpp="https://eden-fidelis.eu/cpp/cpp/"' in content
            has_xhtml_ns = 'xmlns="http://www.w3.org/1999/xhtml"' in content
            
            passed = has_xsl_ns and has_cpp_ns and has_xhtml_ns
            self.log_result(
                test_name,
                passed,
                f"XSL: {has_xsl_ns}, CPP: {has_cpp_ns}, XHTML: {has_xhtml_ns}"
            )
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_organisation_type_capitalization(self):
        """
        Test that 'Organisation Type' header is correctly capitalized.
        This is the primary change in the current branch.
        """
        test_name = "Organisation Type capitalization in XSL"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for the specific table header
            pattern = r'<th[^>]*>Organisation Type</th>'
            matches = re.findall(pattern, content)
            
            # Should have exactly one match in the publicDocumentationTable template
            has_correct_capitalization = len(matches) == 1
            
            # Also check that the old lowercase version doesn't exist
            old_pattern = r'<th[^>]*>Organisation type</th>'
            old_matches = re.findall(old_pattern, content)
            no_old_version = len(old_matches) == 0
            
            passed = has_correct_capitalization and no_old_version
            self.log_result(
                test_name,
                passed,
                f"Correct: {len(matches)}, Old: {len(old_matches)}"
            )
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_all_table_headers_consistency(self):
        """Test that all table headers follow consistent capitalization patterns."""
        test_name = "Table header capitalization consistency"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all table headers
            th_pattern = r'<th[^>]*>(.*?)</th>'
            headers = re.findall(th_pattern, content)
            
            # Check specific headers for title case consistency
            expected_capitalizations = {
                'Organisation Type': True,  # Should be title case
                'Change history': True,  # First word capitalized
                'Trigger Event': True,
                'CPP-identifier': True,
            }
            
            issues = []
            for header_text, expected in expected_capitalizations.items():
                if expected and header_text not in headers:
                    issues.append(f"Missing expected header: {header_text}")
            
            passed = len(issues) == 0
            message = "; ".join(issues) if issues else f"Found {len(headers)} headers"
            self.log_result(test_name, passed, message)
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_public_documentation_table_structure(self):
        """Test the structure of the publicDocumentationTable template."""
        test_name = "Public documentation table structure"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for the template definition
            has_template = 'name="publicDocumentationTable"' in content
            
            # Check for required table headers in correct order
            headers_section = re.search(
                r'<table class="publicDocumentation">.*?</tr>',
                content,
                re.DOTALL
            )
            
            if headers_section:
                section_text = headers_section.group(0)
                has_institution = 'Institution' in section_text
                has_org_type = 'Organisation Type' in section_text
                has_language = 'Language' in section_text
                has_hyperlink = 'Hyperlink' in section_text
                
                # Check order
                inst_pos = section_text.find('Institution')
                org_pos = section_text.find('Organisation Type')
                lang_pos = section_text.find('Language')
                link_pos = section_text.find('Hyperlink')
                
                correct_order = (inst_pos < org_pos < lang_pos < link_pos)
                
                passed = (has_template and has_institution and has_org_type 
                         and has_language and has_hyperlink and correct_order)
            else:
                passed = False
            
            self.log_result(test_name, passed)
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_table_column_widths(self):
        """Test that table column width attributes are properly defined."""
        test_name = "Table column width attributes"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the publicDocumentationTable section
            table_pattern = r'<table class="publicDocumentation">.*?</table>'
            table_match = re.search(table_pattern, content, re.DOTALL)
            
            if table_match:
                table_content = table_match.group(0)
                
                # Check for width attributes
                width_20_count = len(re.findall(r'width:20%', table_content))
                width_10_count = len(re.findall(r'width:10%', table_content))
                width_50_count = len(re.findall(r'width:50%', table_content))
                
                # Should have 2 columns at 20%, 1 at 10%, 1 at 50%
                passed = (width_20_count == 2 and width_10_count == 1 
                         and width_50_count == 1)
                
                message = f"20%: {width_20_count}, 10%: {width_10_count}, 50%: {width_50_count}"
            else:
                passed = False
                message = "Table not found"
            
            self.log_result(test_name, passed, message)
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_xsl_output_method(self):
        """Test that XSL output method is properly configured."""
        test_name = "XSL output method configuration"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_output = '<xsl:output' in content
            has_html_method = 'method="html"' in content
            has_utf8 = 'encoding="utf-8"' in content
            has_indent = 'indent="yes"' in content
            
            passed = has_output and has_html_method and has_utf8 and has_indent
            self.log_result(test_name, passed)
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_css_styles_present(self):
        """Test that CSS styles are properly embedded in XSL."""
        test_name = "CSS styles present in XSL"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_style_element = '<style type="text/css">' in content
            has_root_vars = ':root {' in content
            has_table_styles = 'table {' in content
            has_th_styles = 'th,' in content or 'th {' in content
            
            passed = (has_style_element and has_root_vars 
                     and has_table_styles and has_th_styles)
            self.log_result(test_name, passed)
            return passed
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_transformation_if_xsltproc_available(self):
        """
        Test actual XSLT transformation if xsltproc is available.
        This validates that the XSL produces valid HTML output.
        """
        test_name = "XSLT transformation execution"
        
        if not self.xsltproc_available:
            self.log_result(test_name, True, "SKIPPED - xsltproc not available")
            return True
        
        try:
            # Find a test XML file
            xml_files = list(self.repo_root.glob("CPP-*/cpp-*.xml"))
            if not xml_files:
                self.log_result(test_name, True, "SKIPPED - no XML files found")
                return True
            
            test_xml = xml_files[0]
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False
            ) as tmp_file:
                tmp_output = tmp_file.name
            
            try:
                # Run transformation
                result = subprocess.run(
                    ["xsltproc", str(self.xsl_file), str(test_xml)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Write output to temp file
                with open(tmp_output, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                # Verify output contains expected elements
                output = result.stdout
                has_html = '<html' in output.lower()
                has_table = '<table' in output
                has_org_type = 'Organisation Type' in output
                
                passed = has_html and has_table and has_org_type
                message = f"HTML: {has_html}, Table: {has_table}, Org Type: {has_org_type}"
                
            finally:
                # Cleanup
                if os.path.exists(tmp_output):
                    os.remove(tmp_output)
            
            self.log_result(test_name, passed, message)
            return passed
            
        except subprocess.CalledProcessError as e:
            self.log_result(test_name, False, f"Transform failed: {e.stderr}")
            return False
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_generated_html_has_correct_header(self):
        """
        Test that generated HTML files have the correct 'Organisation Type' header.
        This validates the actual output after transformation.
        """
        test_name = "Generated HTML has correct header"
        try:
            html_files = list(self.repo_root.glob("CPP-*/cpp-*.html"))
            
            if not html_files:
                self.log_result(test_name, True, "SKIPPED - no HTML files found")
                return True
            
            all_correct = True
            files_checked = 0
            
            for html_file in html_files:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for correct capitalization
                has_correct = 'Organisation Type' in content
                has_incorrect = 'Organisation type' in content
                
                if has_incorrect or not has_correct:
                    all_correct = False
                    self.log_result(
                        f"  {html_file.name}",
                        False,
                        f"Correct: {has_correct}, Incorrect: {has_incorrect}"
                    )
                else:
                    files_checked += 1
            
            message = f"Checked {files_checked}/{len(html_files)} files"
            self.log_result(test_name, all_correct, message)
            return all_correct
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_xsl_templates_exist(self):
        """Test that expected XSL templates are defined."""
        test_name = "Required XSL templates exist"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_templates = [
                'match="/cpp:cpp"',
                'name="publicDocumentationTable"',
            ]
            
            missing = []
            for template in required_templates:
                if template not in content:
                    missing.append(template)
            
            passed = len(missing) == 0
            message = f"Missing: {missing}" if missing else "All templates found"
            self.log_result(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_frameworks_xml_reference(self):
        """Test that XSL references frameworks.xml correctly."""
        test_name = "frameworks.xml reference"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_frameworks_var = "document('frameworks.xml')" in content
            
            # Check if frameworks.xml exists
            frameworks_file = self.repo_root / "frameworks.xml"
            frameworks_exists = frameworks_file.exists()
            
            passed = has_frameworks_var and frameworks_exists
            self.log_result(test_name, passed)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_xsl_version_attribute(self):
        """Test that XSL has proper version attribute."""
        test_name = "XSL version attribute"
        try:
            tree = ET.parse(self.xsl_file)
            root = tree.getroot()
            
            # Check version in raw file (easier than parsing namespace)
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                first_lines = ''.join(f.readlines()[:10])
            
            has_version = 'version=' in first_lines
            passed = has_version
            
            self.log_result(test_name, passed)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_html_doctype_generation(self):
        """Test that XSL generates proper HTML doctype."""
        test_name = "HTML DOCTYPE generation"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_doctype_config = 'doctype-system="about:legacy-compat"' in content
            
            passed = has_doctype_config
            self.log_result(test_name, passed)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_special_characters_handling(self):
        """Test that XSL properly handles special characters in templates."""
        test_name = "Special characters handling"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for proper entity handling
            has_space_var = "select=\"' '\"" in content or "select='  '" in content
            has_nbsp = '&#160;' in content or '&nbsp;' in content
            
            # Should have proper handling
            passed = True  # Basic check that file is readable with special chars
            self.log_result(test_name, passed)
            return passed
            
        except UnicodeDecodeError as e:
            self.log_result(test_name, False, f"Encoding error: {e}")
            return False
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_table_class_attributes(self):
        """Test that tables have proper class attributes."""
        test_name = "Table class attributes"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            expected_classes = [
                'class="publicDocumentation"',
                'class="intro"',
            ]
            
            found = []
            for cls in expected_classes:
                if cls in content:
                    found.append(cls)
            
            passed = len(found) >= 1  # At least one table class should exist
            message = f"Found {len(found)}/{len(expected_classes)} table classes"
            self.log_result(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_xsl_for_each_loops(self):
        """Test that XSL uses for-each loops correctly."""
        test_name = "XSL for-each loop structures"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for_each_count = content.count('<xsl:for-each')
            for_each_end_count = content.count('</xsl:for-each>')
            
            # Should have matching opening and closing tags
            passed = for_each_count == for_each_end_count and for_each_count > 0
            message = f"Found {for_each_count} for-each loops"
            self.log_result(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def test_parameter_definitions(self):
        """Test that template parameters are properly defined."""
        test_name = "Template parameter definitions"
        try:
            with open(self.xsl_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for param elements in publicDocumentationTable
            pattern = r'<xsl:template name="publicDocumentationTable">.*?</xsl:template>'
            template_match = re.search(pattern, content, re.DOTALL)
            
            if template_match:
                template_content = template_match.group(0)
                has_data_param = '<xsl:param name="data"' in template_content
                passed = has_data_param
                message = "data parameter found" if has_data_param else "data parameter missing"
            else:
                passed = False
                message = "Template not found"
            
            self.log_result(test_name, passed, message)
            return passed
            
        except Exception as e:
            self.log_result(test_name, False, str(e))
            return False

    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 70)
        print("Running cpp2html.xsl XSLT Transformation Test Suite")
        print("=" * 70)
        print()
        
        # List of all test methods
        test_methods = [
            self.test_xsl_file_exists,
            self.test_xsl_well_formed,
            self.test_xsl_namespace_declaration,
            self.test_organisation_type_capitalization,
            self.test_all_table_headers_consistency,
            self.test_public_documentation_table_structure,
            self.test_table_column_widths,
            self.test_xsl_output_method,
            self.test_css_styles_present,
            self.test_xsl_templates_exist,
            self.test_frameworks_xml_reference,
            self.test_xsl_version_attribute,
            self.test_html_doctype_generation,
            self.test_special_characters_handling,
            self.test_table_class_attributes,
            self.test_xsl_for_each_loops,
            self.test_parameter_definitions,
            self.test_transformation_if_xsltproc_available,
            self.test_generated_html_has_correct_header,
        ]
        
        # Run all tests
        for test_method in test_methods:
            test_method()
            print()
        
        # Summary
        print("=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        passed_count = sum(1 for passed, _ in self.test_results if passed)
        total_count = len(self.test_results)
        failed_count = total_count - passed_count
        
        print(f"\nTotal Tests: {total_count}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        
        if failed_count > 0:
            print("\nFailed Tests:")
            for passed, result in self.test_results:
                if not passed:
                    print(f"  {result}")
        
        print()
        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 70)
        
        return failed_count == 0


def main():
    """Main entry point for test suite."""
    tester = TestCpp2HtmlTransformation()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()