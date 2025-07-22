#!/usr/bin/env python3
"""
Setup validation script for Lambda Performance Comparison project.

This script validates that all components for development and deployment are properly configured.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import argparse


class SetupValidator:
    """Validates project setup and configuration."""
    
    def __init__(self, project_root: str = None, verbose: bool = True):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.verbose = verbose
        self.errors = []
        self.warnings = []
    
    def log_error(self, message: str):
        """Log an error message."""
        self.errors.append(message)
        if self.verbose:
            print(f"❌ {message}")
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.warnings.append(message)
        if self.verbose:
            print(f"⚠️  {message}")
    
    def log_success(self, message: str):
        """Log a success message."""
        if self.verbose:
            print(f"✅ {message}")
    
    def validate_files(self) -> bool:
        """Validate that all required files exist and are properly formatted."""
        if self.verbose:
            print("🔍 Validating project files...")
        
        required_files = [
            "template.yaml",
            "samconfig.toml", 
            "config/env.json",
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md"
        ]
        
        optional_files = [
            "CHANGELOG.md",
            "DEPLOYMENT_GUIDE.md",
            "LOCAL_TESTING.md",
            "PERFORMANCE_RESULTS.md"
        ]
        
        # Check required files
        missing_required = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_required.append(file_path)
            else:
                self.log_success(f"Required file: {file_path}")
        
        if missing_required:
            self.log_error(f"Missing required files: {missing_required}")
            return False
        
        # Check optional files
        for file_path in optional_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_success(f"Optional file: {file_path}")
            else:
                self.log_warning(f"Optional file missing: {file_path}")
        
        return True
    
    def validate_directory_structure(self) -> bool:
        """Validate project directory structure."""
        if self.verbose:
            print("\n🔍 Validating directory structure...")
        
        required_dirs = [
            "src",
            "tests", 
            "events",
            "docs",
            "scripts"
        ]
        
        optional_dirs = [
            ".github",
            ".github/workflows",
            ".github/ISSUE_TEMPLATE"
        ]
        
        # Check required directories
        missing_required = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists() or not full_path.is_dir():
                missing_required.append(dir_path)
            else:
                self.log_success(f"Required directory: {dir_path}")
        
        if missing_required:
            self.log_error(f"Missing required directories: {missing_required}")
            return False
        
        # Check optional directories
        for dir_path in optional_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                self.log_success(f"Optional directory: {dir_path}")
            else:
                self.log_warning(f"Optional directory missing: {dir_path}")
        
        return True
    
    def validate_source_code(self) -> bool:
        """Validate source code files."""
        if self.verbose:
            print("\n🔍 Validating source code...")
        
        src_dir = self.project_root / "src"
        required_src_files = [
            "lambda_function.py",
            "data_processor.py",
            "metrics.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_name in required_src_files:
            file_path = src_dir / file_name
            if not file_path.exists():
                missing_files.append(f"src/{file_name}")
            else:
                self.log_success(f"Source file: src/{file_name}")
        
        if missing_files:
            self.log_error(f"Missing source files: {missing_files}")
            return False
        
        return True
    
    def validate_tests(self) -> bool:
        """Validate test files."""
        if self.verbose:
            print("\n🔍 Validating test files...")
        
        tests_dir = self.project_root / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        
        if not test_files:
            self.log_warning("No test files found in tests/ directory")
            return True
        
        for test_file in test_files:
            self.log_success(f"Test file: {test_file.relative_to(self.project_root)}")
        
        return True
    
    def validate_events(self) -> bool:
        """Validate event files."""
        if self.verbose:
            print("\n🔍 Validating event files...")
        
        events_dir = self.project_root / "events"
        required_events = [
            "direct-invocation-sort.json",
            "direct-invocation-math.json",
            "direct-invocation-string.json",
            "direct-invocation-memory.json"
        ]
        
        missing_events = []
        for event_file in required_events:
            file_path = events_dir / event_file
            if not file_path.exists():
                missing_events.append(f"events/{event_file}")
            else:
                # Validate JSON format
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    self.log_success(f"Event file: events/{event_file}")
                except json.JSONDecodeError as e:
                    self.log_error(f"Invalid JSON in events/{event_file}: {e}")
                    return False
        
        if missing_events:
            self.log_error(f"Missing event files: {missing_events}")
            return False
        
        return True
    
    def validate_json_files(self) -> bool:
        """Validate JSON file formats."""
        if self.verbose:
            print("\n🔍 Validating JSON files...")
        
        json_files = [
            "config/env.json"
        ]
        
        for file_path in json_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        json.load(f)
                    self.log_success(f"Valid JSON: {file_path}")
                except json.JSONDecodeError as e:
                    self.log_error(f"Invalid JSON in {file_path}: {e}")
                    return False
        
        return True
    
    def validate_sam_template(self) -> bool:
        """Validate SAM template."""
        if self.verbose:
            print("\n🔍 Validating SAM template...")
        
        try:
            result = subprocess.run(
                ["sam", "validate"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_success("SAM template validation passed")
                return True
            else:
                self.log_error(f"SAM template validation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_error("SAM template validation timed out")
            return False
        except FileNotFoundError:
            self.log_warning("SAM CLI not found - skipping template validation")
            return True
        except Exception as e:
            self.log_error(f"SAM template validation error: {e}")
            return False
    
    def validate_python_dependencies(self) -> bool:
        """Validate Python dependencies."""
        if self.verbose:
            print("\n🔍 Validating Python dependencies...")
        
        # Check main dependencies
        src_requirements = self.project_root / "src" / "requirements.txt"
        if src_requirements.exists():
            self.log_success("Found src/requirements.txt")
        else:
            self.log_error("Missing src/requirements.txt")
            return False
        
        # Check test dependencies
        test_requirements = self.project_root / "requirements_test.txt"
        if test_requirements.exists():
            self.log_success("Found requirements_test.txt")
        else:
            self.log_warning("Missing requirements_test.txt")
        
        return True
    
    def validate_scripts(self) -> bool:
        """Validate script files."""
        if self.verbose:
            print("\n🔍 Validating script files...")
        
        scripts_dir = self.project_root / "scripts"
        expected_scripts = [
            "performance_test.py",
            "local_test.py",
            "validate_setup.py"
        ]
        
        missing_scripts = []
        for script_name in expected_scripts:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                missing_scripts.append(f"scripts/{script_name}")
            else:
                # Check if script is executable
                if os.access(script_path, os.X_OK):
                    self.log_success(f"Executable script: scripts/{script_name}")
                else:
                    self.log_success(f"Script file: scripts/{script_name}")
        
        if missing_scripts:
            self.log_error(f"Missing script files: {missing_scripts}")
            return False
        
        return True
    
    def validate_documentation(self) -> bool:
        """Validate documentation files."""
        if self.verbose:
            print("\n🔍 Validating documentation...")
        
        docs_dir = self.project_root / "docs"
        expected_docs = [
            "API_REFERENCE.md",
            "PERFORMANCE_ANALYSIS.md"
        ]
        
        missing_docs = []
        for doc_name in expected_docs:
            doc_path = docs_dir / doc_name
            if not doc_path.exists():
                missing_docs.append(f"docs/{doc_name}")
            else:
                self.log_success(f"Documentation: docs/{doc_name}")
        
        if missing_docs:
            self.log_warning(f"Missing documentation files: {missing_docs}")
        
        return True
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite."""
        if self.verbose:
            print("🧪 Lambda Performance Comparison - Setup Validation")
            print("=" * 60)
        
        validations = [
            ("Project files", self.validate_files),
            ("Directory structure", self.validate_directory_structure),
            ("Source code", self.validate_source_code),
            ("Test files", self.validate_tests),
            ("Event files", self.validate_events),
            ("JSON format", self.validate_json_files),
            ("SAM template", self.validate_sam_template),
            ("Python dependencies", self.validate_python_dependencies),
            ("Script files", self.validate_scripts),
            ("Documentation", self.validate_documentation)
        ]
        
        all_passed = True
        
        for name, validation_func in validations:
            try:
                if not validation_func():
                    all_passed = False
            except Exception as e:
                self.log_error(f"{name} validation failed with exception: {e}")
                all_passed = False
        
        # Print summary
        if self.verbose:
            print(f"\n📊 Validation Summary")
            print("=" * 30)
            print(f"Errors: {len(self.errors)}")
            print(f"Warnings: {len(self.warnings)}")
        
        if all_passed and not self.errors:
            if self.verbose:
                print("\n🎉 All validations passed! Project setup is ready.")
            return True
        else:
            if self.verbose:
                print("\n💥 Some validations failed. Please fix the issues above.")
            return False
    
    def print_usage_summary(self):
        """Print usage summary."""
        print("\n📋 Project Usage Summary")
        print("=" * 50)
        print("1. Build: sam build")
        print("2. Local tests: python scripts/local_test.py --direct")
        print("3. Deploy: sam deploy --guided")
        print("4. Performance test: python scripts/performance_test.py --arm64-url <url> --x86-url <url>")
        print("5. Validate: python scripts/validate_setup.py")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Project Setup Validation")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--summary", action="store_true", help="Show usage summary")
    
    args = parser.parse_args()
    
    validator = SetupValidator(args.project_root, verbose=not args.quiet)
    
    if args.summary:
        validator.print_usage_summary()
        return
    
    success = validator.run_full_validation()
    
    if success:
        validator.print_usage_summary()
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()