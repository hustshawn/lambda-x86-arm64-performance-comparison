"""
Unit tests for the performance metrics collection module.
"""

import unittest
import time
import os
from unittest.mock import Mock, patch, MagicMock
import sys
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import PerformanceMetrics, MetricsContext, create_metrics_collector


class TestPerformanceMetrics(unittest.TestCase):
    """Test cases for PerformanceMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics = PerformanceMetrics(architecture='x86_64', function_name='test-function')
    
    def test_initialization(self):
        """Test metrics initialization."""
        self.assertEqual(self.metrics.architecture, 'x86_64')
        self.assertEqual(self.metrics.function_name, 'test-function')
        self.assertEqual(self.metrics.function_version, '$LATEST')
        self.assertIn('python', self.metrics.runtime)
    
    def test_architecture_detection(self):
        """Test automatic architecture detection."""
        metrics = PerformanceMetrics()
        self.assertIn(metrics.architecture, ['arm64', 'x86_64', 'unknown'])
    
    def test_timer_operations(self):
        """Test timer start/stop functionality."""
        operation = 'test_operation'
        
        # Start timer
        self.metrics.start_timer(operation)
        self.assertIn(operation, self.metrics.start_times)
        
        # Simulate some work
        time.sleep(0.01)  # 10ms
        
        # Stop timer
        execution_time = self.metrics.stop_timer(operation)
        
        # Verify timing
        self.assertGreater(execution_time, 5)  # Should be at least 5ms
        self.assertLess(execution_time, 50)    # Should be less than 50ms
        self.assertNotIn(operation, self.metrics.start_times)
        self.assertIn(operation, self.metrics.metrics_data)
    
    def test_stop_timer_without_start(self):
        """Test stopping timer that wasn't started."""
        execution_time = self.metrics.stop_timer('nonexistent_operation')
        self.assertEqual(execution_time, 0.0)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_memory_capture(self, mock_virtual_memory, mock_process):
        """Test memory usage capture."""
        # Mock process memory info
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100MB in bytes
        
        mock_proc_instance = Mock()
        mock_proc_instance.memory_info.return_value = mock_memory_info
        mock_proc_instance.memory_percent.return_value = 5.0
        mock_process.return_value = mock_proc_instance
        
        # Mock system memory
        mock_sys_memory = Mock()
        mock_sys_memory.total = 1024 * 1024 * 1024 * 8  # 8GB
        mock_sys_memory.available = 1024 * 1024 * 1024 * 4  # 4GB
        mock_sys_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_sys_memory
        
        # Test memory capture
        memory_data = self.metrics.capture_memory_usage()
        
        self.assertEqual(memory_data['memory_used_mb'], 100.0)
        self.assertEqual(memory_data['memory_percent'], 5.0)
        self.assertEqual(memory_data['system_memory_total_mb'], 8192.0)
        self.assertEqual(memory_data['system_memory_available_mb'], 4096.0)
        self.assertEqual(memory_data['system_memory_percent'], 50.0)
    
    def test_peak_memory_tracking(self):
        """Test peak memory usage tracking."""
        # Add some memory samples
        self.metrics.memory_samples = [50.0, 75.0, 100.0, 60.0]
        peak_memory = self.metrics.get_peak_memory_usage()
        self.assertEqual(peak_memory, 100.0)
        
        # Test empty samples
        self.metrics.memory_samples = []
        peak_memory = self.metrics.get_peak_memory_usage()
        self.assertEqual(peak_memory, 0.0)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_record_operation_metrics(self, mock_virtual_memory, mock_process):
        """Test recording comprehensive operation metrics."""
        # Setup mocks
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 50  # 50MB
        
        mock_proc_instance = Mock()
        mock_proc_instance.memory_info.return_value = mock_memory_info
        mock_proc_instance.memory_percent.return_value = 2.5
        mock_process.return_value = mock_proc_instance
        
        mock_sys_memory = Mock()
        mock_sys_memory.total = 1024 * 1024 * 1024 * 4  # 4GB
        mock_sys_memory.available = 1024 * 1024 * 1024 * 2  # 2GB
        mock_sys_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_sys_memory
        
        # Record metrics
        operation = 'test_operation'
        self.metrics.metrics_data[operation] = {'execution_time_ms': 25.5}
        
        metrics = self.metrics.record_operation_metrics(
            operation=operation,
            data_size=1000,
            iterations=5,
            cold_start=True,
            additional_metrics={'custom_metric': 'test_value'}
        )
        
        # Verify metrics
        self.assertEqual(metrics['architecture'], 'x86_64')
        self.assertEqual(metrics['operation'], operation)
        self.assertEqual(metrics['execution_time_ms'], 25.5)
        self.assertEqual(metrics['memory_used_mb'], 50.0)
        self.assertEqual(metrics['data_size'], 1000)
        self.assertEqual(metrics['iterations'], 5)
        self.assertTrue(metrics['cold_start'])
        self.assertEqual(metrics['custom_metric'], 'test_value')
        self.assertEqual(metrics['function_name'], 'test-function')
    
    @patch('boto3.client')
    def test_cloudwatch_metrics_success(self, mock_boto_client):
        """Test successful CloudWatch metrics sending."""
        # Setup mock CloudWatch client
        mock_cw_client = Mock()
        mock_cw_client.put_metric_data.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_boto_client.return_value = mock_cw_client
        
        # Initialize metrics with CloudWatch client
        metrics = PerformanceMetrics(architecture='arm64', function_name='test-function')
        
        # Add test metrics data
        operation = 'test_operation'
        metrics.metrics_data[operation] = {
            'execution_time_ms': 15.5,
            'memory_used_mb': 75.0,
            'peak_memory_mb': 80.0,
            'cold_start': False
        }
        
        # Send metrics
        result = metrics.send_cloudwatch_metrics(operation)
        
        # Verify success
        self.assertTrue(result)
        mock_cw_client.put_metric_data.assert_called_once()
        
        # Verify metric data structure
        call_args = mock_cw_client.put_metric_data.call_args
        self.assertEqual(call_args[1]['Namespace'], 'Lambda/PerformanceComparison')
        self.assertIsInstance(call_args[1]['MetricData'], list)
        self.assertGreater(len(call_args[1]['MetricData']), 0)
    
    def test_cloudwatch_metrics_no_client(self):
        """Test CloudWatch metrics when client is not available."""
        metrics = PerformanceMetrics()
        metrics.cloudwatch = None
        
        result = metrics.send_cloudwatch_metrics('test_operation')
        self.assertFalse(result)
    
    def test_cloudwatch_metrics_no_data(self):
        """Test CloudWatch metrics when no data exists for operation."""
        with patch('boto3.client') as mock_boto_client:
            mock_cw_client = Mock()
            mock_boto_client.return_value = mock_cw_client
            
            metrics = PerformanceMetrics()
            result = metrics.send_cloudwatch_metrics('nonexistent_operation')
            self.assertFalse(result)
    
    def test_get_all_metrics(self):
        """Test getting all collected metrics."""
        operation = 'test_operation'
        self.metrics.metrics_data[operation] = {'execution_time_ms': 10.0}
        
        all_metrics = self.metrics.get_all_metrics()
        
        self.assertEqual(all_metrics['architecture'], 'x86_64')
        self.assertEqual(all_metrics['function_name'], 'test-function')
        self.assertIn('operations', all_metrics)
        self.assertIn(operation, all_metrics['operations'])
    
    def test_reset_metrics(self):
        """Test metrics reset functionality."""
        # Add some data
        self.metrics.metrics_data['test'] = {'execution_time_ms': 10.0}
        self.metrics.start_times['test'] = time.time()
        self.metrics.memory_samples = [50.0, 60.0]
        
        # Reset
        self.metrics.reset_metrics()
        
        # Verify reset
        self.assertEqual(len(self.metrics.metrics_data), 0)
        self.assertEqual(len(self.metrics.start_times), 0)
        self.assertEqual(len(self.metrics.memory_samples), 0)


class TestMetricsContext(unittest.TestCase):
    """Test cases for MetricsContext context manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics = PerformanceMetrics(architecture='arm64', function_name='test-function')
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_context_manager(self, mock_virtual_memory, mock_process):
        """Test context manager functionality."""
        # Setup mocks
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 30  # 30MB
        
        mock_proc_instance = Mock()
        mock_proc_instance.memory_info.return_value = mock_memory_info
        mock_proc_instance.memory_percent.return_value = 1.5
        mock_process.return_value = mock_proc_instance
        
        mock_sys_memory = Mock()
        mock_sys_memory.total = 1024 * 1024 * 1024 * 2  # 2GB
        mock_sys_memory.available = 1024 * 1024 * 1024 * 1  # 1GB
        mock_sys_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_sys_memory
        
        operation = 'context_test'
        
        # Use context manager
        with MetricsContext(self.metrics, operation, data_size=500, iterations=3, cold_start=True):
            time.sleep(0.01)  # Simulate work
        
        # Verify metrics were recorded
        self.assertIn(operation, self.metrics.metrics_data)
        metrics_data = self.metrics.metrics_data[operation]
        self.assertGreater(metrics_data['execution_time_ms'], 0)
        self.assertEqual(metrics_data['data_size'], 500)
        self.assertEqual(metrics_data['iterations'], 3)
        self.assertTrue(metrics_data['cold_start'])


class TestFactoryFunction(unittest.TestCase):
    """Test cases for factory function."""
    
    def test_create_metrics_collector(self):
        """Test factory function."""
        metrics = create_metrics_collector(architecture='arm64', function_name='factory-test')
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertEqual(metrics.architecture, 'arm64')
        self.assertEqual(metrics.function_name, 'factory-test')
    
    def test_create_metrics_collector_defaults(self):
        """Test factory function with defaults."""
        metrics = create_metrics_collector()
        
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertIn(metrics.architecture, ['arm64', 'x86_64', 'unknown'])


if __name__ == '__main__':
    unittest.main()