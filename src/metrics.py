"""
Performance metrics collection module for Lambda performance comparison.

This module provides high-precision timing, memory usage monitoring,
and CloudWatch custom metrics integration for comparing ARM64 vs x86_64 performance.
"""

import time
import psutil
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Collects and manages performance metrics for Lambda functions."""

    def __init__(self, architecture: str = None, function_name: str = None):
        """
        Initialize performance metrics collector.

        Args:
            architecture: Lambda architecture (arm64 or x86_64)
            function_name: Name of the Lambda function
        """
        self.architecture = architecture or self._detect_architecture()
        self.function_name = function_name or os.environ.get(
            "AWS_LAMBDA_FUNCTION_NAME", "unknown"
        )
        self.function_version = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", "$LATEST")
        self.runtime = f"python{'.'.join(map(str, __import__('sys').version_info[:2]))}"

        # Initialize CloudWatch client
        self.cloudwatch = None
        try:
            self.cloudwatch = boto3.client("cloudwatch")
        except Exception as e:
            logger.warning(f"Failed to initialize CloudWatch client: {e}")

        # Metrics storage
        self.metrics_data = {}
        self.start_times = {}
        self.memory_samples = []

    def _detect_architecture(self) -> str:
        """Detect the current architecture."""
        import platform

        machine = platform.machine().lower()
        if "arm" in machine or "aarch64" in machine:
            return "arm64"
        elif "x86_64" in machine or "amd64" in machine:
            return "x86_64"
        else:
            return "unknown"

    def start_timer(self, operation: str) -> None:
        """
        Start high-precision timer for an operation.

        Args:
            operation: Name of the operation being timed
        """
        self.start_times[operation] = time.perf_counter()
        logger.debug(f"Started timer for operation: {operation}")

    def stop_timer(self, operation: str) -> float:
        """
        Stop timer and calculate execution time.

        Args:
            operation: Name of the operation being timed

        Returns:
            Execution time in milliseconds
        """
        if operation not in self.start_times:
            logger.error(f"Timer not started for operation: {operation}")
            return 0.0

        end_time = time.perf_counter()
        execution_time = (
            end_time - self.start_times[operation]
        ) * 1000  # Convert to ms

        # Store the metric
        if operation not in self.metrics_data:
            self.metrics_data[operation] = {}

        self.metrics_data[operation]["execution_time_ms"] = execution_time

        # Clean up
        del self.start_times[operation]

        logger.debug(f"Operation {operation} completed in {execution_time:.2f}ms")
        return execution_time

    def capture_memory_usage(self) -> Dict[str, float]:
        """
        Capture current memory usage metrics.

        Returns:
            Dictionary containing memory usage information
        """
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # Get system memory info
            system_memory = psutil.virtual_memory()

            memory_data = {
                "memory_used_mb": memory_info.rss
                / (1024 * 1024),  # Convert bytes to MB
                "memory_percent": memory_percent,
                "system_memory_total_mb": system_memory.total / (1024 * 1024),
                "system_memory_available_mb": system_memory.available / (1024 * 1024),
                "system_memory_percent": system_memory.percent,
            }

            # Store sample for peak calculation
            self.memory_samples.append(memory_data["memory_used_mb"])

            return memory_data

        except Exception as e:
            logger.error(f"Failed to capture memory usage: {e}")
            return {
                "memory_used_mb": 0.0,
                "memory_percent": 0.0,
                "system_memory_total_mb": 0.0,
                "system_memory_available_mb": 0.0,
                "system_memory_percent": 0.0,
            }

    def get_peak_memory_usage(self) -> float:
        """
        Get peak memory usage from collected samples.

        Returns:
            Peak memory usage in MB
        """
        return max(self.memory_samples) if self.memory_samples else 0.0

    def record_operation_metrics(
        self,
        operation: str,
        data_size: int = 0,
        iterations: int = 1,
        cold_start: bool = False,
        additional_metrics: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Record comprehensive metrics for an operation.

        Args:
            operation: Name of the operation
            data_size: Size of data processed
            iterations: Number of iterations performed
            cold_start: Whether this was a cold start
            additional_metrics: Additional custom metrics

        Returns:
            Complete metrics dictionary
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        memory_info = self.capture_memory_usage()

        metrics = {
            "architecture": self.architecture,
            "operation": operation,
            "execution_time_ms": self.metrics_data.get(operation, {}).get(
                "execution_time_ms", 0.0
            ),
            "memory_used_mb": memory_info["memory_used_mb"],
            "peak_memory_mb": self.get_peak_memory_usage(),
            "memory_percent": memory_info["memory_percent"],
            "cold_start": cold_start,
            "data_size": data_size,
            "iterations": iterations,
            "timestamp": timestamp,
            "function_name": self.function_name,
            "function_version": self.function_version,
            "runtime": self.runtime,
        }

        # Add additional metrics if provided
        if additional_metrics:
            metrics.update(additional_metrics)

        # Store in metrics data
        if operation not in self.metrics_data:
            self.metrics_data[operation] = {}
        self.metrics_data[operation].update(metrics)

        logger.info(
            f"Recorded metrics for {operation}: {json.dumps(metrics, indent=2)}"
        )
        return metrics

    def send_cloudwatch_metrics(
        self, operation: str, namespace: str = "Lambda/PerformanceComparison"
    ) -> bool:
        """
        Send custom metrics to CloudWatch.

        Args:
            operation: Operation name
            namespace: CloudWatch namespace

        Returns:
            True if successful, False otherwise
        """
        if not self.cloudwatch:
            logger.warning("CloudWatch client not available")
            return False

        if operation not in self.metrics_data:
            logger.error(f"No metrics data found for operation: {operation}")
            return False

        metrics = self.metrics_data[operation]

        try:
            # Prepare metric data
            metric_data = []

            # Execution time metric
            if "execution_time_ms" in metrics:
                metric_data.append(
                    {
                        "MetricName": "ExecutionTime",
                        "Value": metrics["execution_time_ms"],
                        "Unit": "Milliseconds",
                        "Dimensions": [
                            {"Name": "Architecture", "Value": self.architecture},
                            {"Name": "Operation", "Value": operation},
                            {"Name": "FunctionName", "Value": self.function_name},
                        ],
                    }
                )

            # Memory usage metric
            if "memory_used_mb" in metrics:
                metric_data.append(
                    {
                        "MetricName": "MemoryUsage",
                        "Value": metrics["memory_used_mb"],
                        "Unit": "Megabytes",
                        "Dimensions": [
                            {"Name": "Architecture", "Value": self.architecture},
                            {"Name": "Operation", "Value": operation},
                            {"Name": "FunctionName", "Value": self.function_name},
                        ],
                    }
                )

            # Peak memory metric
            if "peak_memory_mb" in metrics:
                metric_data.append(
                    {
                        "MetricName": "PeakMemoryUsage",
                        "Value": metrics["peak_memory_mb"],
                        "Unit": "Megabytes",
                        "Dimensions": [
                            {"Name": "Architecture", "Value": self.architecture},
                            {"Name": "Operation", "Value": operation},
                            {"Name": "FunctionName", "Value": self.function_name},
                        ],
                    }
                )

            # Cold start metric
            if "cold_start" in metrics:
                metric_data.append(
                    {
                        "MetricName": "ColdStart",
                        "Value": 1 if metrics["cold_start"] else 0,
                        "Unit": "Count",
                        "Dimensions": [
                            {"Name": "Architecture", "Value": self.architecture},
                            {"Name": "FunctionName", "Value": self.function_name},
                        ],
                    }
                )

            # Send metrics to CloudWatch
            if metric_data:
                response = self.cloudwatch.put_metric_data(
                    Namespace=namespace, MetricData=metric_data
                )
                logger.info(
                    f"Successfully sent {len(metric_data)} metrics to CloudWatch"
                )
                return True
            else:
                logger.warning("No metric data to send to CloudWatch")
                return False

        except ClientError as e:
            logger.error(f"Failed to send metrics to CloudWatch: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending metrics to CloudWatch: {e}")
            return False

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dictionary containing all metrics data
        """
        return {
            "architecture": self.architecture,
            "function_name": self.function_name,
            "function_version": self.function_version,
            "runtime": self.runtime,
            "operations": self.metrics_data,
        }

    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self.metrics_data.clear()
        self.start_times.clear()
        self.memory_samples.clear()
        logger.info("All metrics have been reset")


class MetricsContext:
    """Context manager for automatic timing and metrics collection."""

    def __init__(
        self,
        metrics: PerformanceMetrics,
        operation: str,
        data_size: int = 0,
        iterations: int = 1,
        cold_start: bool = False,
    ):
        """
        Initialize metrics context.

        Args:
            metrics: PerformanceMetrics instance
            operation: Operation name
            data_size: Size of data being processed
            iterations: Number of iterations
            cold_start: Whether this is a cold start
        """
        self.metrics = metrics
        self.operation = operation
        self.data_size = data_size
        self.iterations = iterations
        self.cold_start = cold_start

    def __enter__(self):
        """Start timing when entering context."""
        self.metrics.start_timer(self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record metrics when exiting context."""
        self.metrics.stop_timer(self.operation)
        self.metrics.record_operation_metrics(
            self.operation,
            data_size=self.data_size,
            iterations=self.iterations,
            cold_start=self.cold_start,
        )


def create_metrics_collector(
    architecture: str = None, function_name: str = None
) -> PerformanceMetrics:
    """
    Factory function to create a PerformanceMetrics instance.

    Args:
        architecture: Lambda architecture (arm64 or x86_64)
        function_name: Name of the Lambda function

    Returns:
        PerformanceMetrics instance
    """
    return PerformanceMetrics(architecture=architecture, function_name=function_name)
