#!/usr/bin/env python3
"""
Unit tests for performance testing utilities.
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path to import performance_test
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from performance_test import (
    TestDataGenerator,
    LambdaPerformanceTester,
    TestResult,
    PerformanceStats,
)


class TestTestDataGenerator(unittest.TestCase):
    """Test cases for TestDataGenerator class."""

    def test_generate_numeric_data(self):
        """Test numeric data generation."""
        data = TestDataGenerator.generate_numeric_data(100)

        self.assertEqual(len(data), 100)
        self.assertTrue(all(isinstance(x, int) for x in data))
        self.assertTrue(all(1 <= x <= 10000 for x in data))

        # Test reproducibility with same seed
        data2 = TestDataGenerator.generate_numeric_data(100)
        self.assertEqual(data, data2)

    def test_generate_string_data(self):
        """Test string data generation."""
        data = TestDataGenerator.generate_string_data(10, 50)

        self.assertEqual(len(data), 10)
        self.assertTrue(all(isinstance(s, str) for s in data))
        self.assertTrue(all(len(s) == 50 for s in data))

    def test_generate_mixed_data(self):
        """Test mixed data structure generation."""
        data = TestDataGenerator.generate_mixed_data(20)

        self.assertIsInstance(data, dict)
        self.assertIn("numbers", data)
        self.assertIn("strings", data)
        self.assertIn("nested", data)

        self.assertEqual(len(data["numbers"]), 10)  # size // 2
        self.assertEqual(len(data["strings"]), 10)  # size // 2
        self.assertIn("values", data["nested"])
        self.assertIn("metadata", data["nested"])


class TestLambdaPerformanceTester(unittest.TestCase):
    """Test cases for LambdaPerformanceTester class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("boto3.client"):
            self.tester = LambdaPerformanceTester(region="us-east-1")

    def test_create_test_payload(self):
        """Test test payload creation."""
        payload = self.tester.create_test_payload("sort_numbers", 100, 2)

        self.assertEqual(payload["operation"], "sort_numbers")
        self.assertEqual(payload["data_size"], 100)
        self.assertEqual(payload["iterations"], 2)
        self.assertIn("payload", payload)
        self.assertEqual(len(payload["payload"]), 100)

    def test_create_test_payload_different_operations(self):
        """Test payload creation for different operations."""
        # Test string processing
        payload = self.tester.create_test_payload("process_strings", 50)
        self.assertTrue(all(isinstance(s, str) for s in payload["payload"]))

        # Test mixed processing
        payload = self.tester.create_test_payload("mixed_processing", 20)
        self.assertIsInstance(payload["payload"], dict)
        self.assertIn("numbers", payload["payload"])
        self.assertIn("strings", payload["payload"])

    def test_invoke_lambda_function_success(self):
        """Test successful Lambda function invocation."""
        # Mock successful Lambda response
        mock_response = {"StatusCode": 200, "Payload": Mock()}

        mock_payload_data = {
            "result": {"processed": True},
            "performance": {
                "execution_time_ms": 150.5,
                "memory_used_mb": 64.2,
                "cold_start": False,
            },
        }

        mock_response["Payload"].read.return_value = json.dumps(
            mock_payload_data
        ).encode()

        self.tester.lambda_client.invoke.return_value = mock_response

        payload = {"operation": "test", "data_size": 100, "iterations": 1}
        result = self.tester.invoke_lambda_function("test-function-arm64", payload)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.architecture, "arm64")
        self.assertEqual(result.execution_time_ms, 150.5)
        self.assertEqual(result.memory_used_mb, 64.2)
        self.assertFalse(result.cold_start)

    def test_invoke_lambda_function_error(self):
        """Test Lambda function invocation error handling."""
        # Mock Lambda client to raise exception
        self.tester.lambda_client.invoke.side_effect = Exception("Connection error")

        payload = {"operation": "test", "data_size": 100, "iterations": 1}
        result = self.tester.invoke_lambda_function("test-function", payload)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.error_message, "Connection error")

    def test_calculate_statistics(self):
        """Test statistical analysis calculation."""
        # Create sample test results
        results = [
            TestResult(
                architecture="arm64",
                function_name="test-arm64",
                operation="sort",
                data_size=100,
                iterations=1,
                execution_time_ms=100.0,
                memory_used_mb=50.0,
                cold_start=False,
                timestamp="2024-01-01T00:00:00",
                status="success",
            ),
            TestResult(
                architecture="arm64",
                function_name="test-arm64",
                operation="sort",
                data_size=100,
                iterations=1,
                execution_time_ms=120.0,
                memory_used_mb=55.0,
                cold_start=True,
                timestamp="2024-01-01T00:01:00",
                status="success",
            ),
            TestResult(
                architecture="x86_64",
                function_name="test-x86",
                operation="sort",
                data_size=100,
                iterations=1,
                execution_time_ms=110.0,
                memory_used_mb=60.0,
                cold_start=False,
                timestamp="2024-01-01T00:02:00",
                status="success",
            ),
            TestResult(
                architecture="x86_64",
                function_name="test-x86",
                operation="sort",
                data_size=100,
                iterations=1,
                execution_time_ms=130.0,
                memory_used_mb=65.0,
                cold_start=True,
                timestamp="2024-01-01T00:03:00",
                status="success",
            ),
        ]

        stats = self.tester.calculate_statistics(results)

        # Should have 2 stat groups (arm64 and x86_64 for same operation/size)
        self.assertEqual(len(stats), 2)

        # Find ARM64 stats
        arm64_stats = next(s for s in stats if s.architecture == "arm64")
        self.assertEqual(arm64_stats.sample_count, 2)
        self.assertEqual(arm64_stats.mean_execution_time, 110.0)  # (100 + 120) / 2
        self.assertEqual(arm64_stats.cold_start_percentage, 50.0)  # 1 out of 2

        # Find x86_64 stats
        x86_stats = next(s for s in stats if s.architecture == "x86_64")
        self.assertEqual(x86_stats.sample_count, 2)
        self.assertEqual(x86_stats.mean_execution_time, 120.0)  # (110 + 130) / 2

    def test_compare_architectures(self):
        """Test architecture comparison functionality."""
        # Create sample performance stats
        stats = [
            PerformanceStats(
                architecture="arm64",
                operation="sort",
                data_size=100,
                sample_count=5,
                mean_execution_time=100.0,
                median_execution_time=98.0,
                std_dev_execution_time=5.0,
                min_execution_time=90.0,
                max_execution_time=110.0,
                mean_memory_usage=50.0,
                cold_start_percentage=20.0,
            ),
            PerformanceStats(
                architecture="x86_64",
                operation="sort",
                data_size=100,
                sample_count=5,
                mean_execution_time=120.0,
                median_execution_time=118.0,
                std_dev_execution_time=8.0,
                min_execution_time=105.0,
                max_execution_time=135.0,
                mean_memory_usage=60.0,
                cold_start_percentage=20.0,
            ),
        ]

        comparisons = self.tester.compare_architectures(stats)

        self.assertEqual(len(comparisons), 1)

        comparison = list(comparisons.values())[0]
        self.assertEqual(comparison["operation"], "sort")
        self.assertEqual(comparison["data_size"], 100)
        self.assertEqual(comparison["winner"], "ARM64")  # ARM64 is faster (100 < 120)
        self.assertAlmostEqual(
            comparison["execution_time_diff_percent"], -16.67, places=1
        )


class TestDataStructures(unittest.TestCase):
    """Test cases for data structures."""

    def test_test_result_creation(self):
        """Test TestResult data class creation."""
        result = TestResult(
            architecture="arm64",
            function_name="test-function",
            operation="sort",
            data_size=100,
            iterations=1,
            execution_time_ms=150.5,
            memory_used_mb=64.0,
            cold_start=True,
            timestamp="2024-01-01T00:00:00",
            status="success",
        )

        self.assertEqual(result.architecture, "arm64")
        self.assertEqual(result.execution_time_ms, 150.5)
        self.assertTrue(result.cold_start)
        self.assertEqual(result.status, "success")

    def test_performance_stats_creation(self):
        """Test PerformanceStats data class creation."""
        stats = PerformanceStats(
            architecture="x86_64",
            operation="process_strings",
            data_size=500,
            sample_count=10,
            mean_execution_time=200.0,
            median_execution_time=195.0,
            std_dev_execution_time=15.0,
            min_execution_time=180.0,
            max_execution_time=230.0,
            mean_memory_usage=80.0,
            cold_start_percentage=30.0,
        )

        self.assertEqual(stats.architecture, "x86_64")
        self.assertEqual(stats.sample_count, 10)
        self.assertEqual(stats.mean_execution_time, 200.0)
        self.assertEqual(stats.cold_start_percentage, 30.0)


if __name__ == "__main__":
    unittest.main()
