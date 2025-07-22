"""
Integration tests for metrics module with data processor.
"""

import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import PerformanceMetrics, MetricsContext
from data_processor import DataProcessor


class TestMetricsIntegration(unittest.TestCase):
    """Integration tests for metrics with data processing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics = PerformanceMetrics(architecture='x86_64', function_name='test-integration')
        self.processor = DataProcessor()
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_metrics_with_sort_workload(self, mock_virtual_memory, mock_process):
        """Test metrics collection during sort workload."""
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
        
        # Test with context manager
        operation = 'sort_intensive'
        with MetricsContext(self.metrics, operation, data_size=1000, iterations=1):
            result = self.processor.sort_intensive_workload(data_size=1000, iterations=1)
        
        # Verify metrics were collected
        self.assertIn(operation, self.metrics.metrics_data)
        metrics_data = self.metrics.metrics_data[operation]
        
        self.assertEqual(metrics_data['operation'], operation)
        self.assertEqual(metrics_data['data_size'], 1000)
        self.assertEqual(metrics_data['iterations'], 1)
        self.assertGreater(metrics_data['execution_time_ms'], 0)
        self.assertEqual(metrics_data['memory_used_mb'], 50.0)
        
        # Verify data processor result
        self.assertEqual(result['operation'], 'sort_intensive')
        self.assertEqual(result['data_size'], 1000)
        self.assertEqual(result['iterations'], 1)
        self.assertIn('algorithms_tested', result)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_metrics_with_mathematical_workload(self, mock_virtual_memory, mock_process):
        """Test metrics collection during mathematical workload."""
        # Setup mocks
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 75  # 75MB
        
        mock_proc_instance = Mock()
        mock_proc_instance.memory_info.return_value = mock_memory_info
        mock_proc_instance.memory_percent.return_value = 3.5
        mock_process.return_value = mock_proc_instance
        
        mock_sys_memory = Mock()
        mock_sys_memory.total = 1024 * 1024 * 1024 * 4  # 4GB
        mock_sys_memory.available = 1024 * 1024 * 1024 * 2  # 2GB
        mock_sys_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_sys_memory
        
        # Test manual timing
        operation = 'mathematical_computation'
        self.metrics.start_timer(operation)
        
        result = self.processor.mathematical_computation_workload(complexity=100, iterations=1)
        
        execution_time = self.metrics.stop_timer(operation)
        metrics = self.metrics.record_operation_metrics(
            operation=operation,
            data_size=100,
            iterations=1,
            cold_start=False
        )
        
        # Verify metrics
        self.assertGreater(execution_time, 0)
        self.assertEqual(metrics['operation'], operation)
        self.assertEqual(metrics['data_size'], 100)
        self.assertEqual(metrics['iterations'], 1)
        self.assertFalse(metrics['cold_start'])
        self.assertEqual(metrics['memory_used_mb'], 75.0)
        
        # Verify data processor result
        self.assertEqual(result['operation'], 'mathematical_computation')
        self.assertEqual(result['complexity'], 100)
        self.assertEqual(result['iterations'], 1)
        self.assertIn('computations', result)
    
    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_multiple_operations_tracking(self, mock_virtual_memory, mock_process):
        """Test tracking multiple operations with metrics."""
        # Setup mocks
        mock_memory_info = Mock()
        mock_memory_info.rss = 1024 * 1024 * 60  # 60MB
        
        mock_proc_instance = Mock()
        mock_proc_instance.memory_info.return_value = mock_memory_info
        mock_proc_instance.memory_percent.return_value = 3.0
        mock_process.return_value = mock_proc_instance
        
        mock_sys_memory = Mock()
        mock_sys_memory.total = 1024 * 1024 * 1024 * 4  # 4GB
        mock_sys_memory.available = 1024 * 1024 * 1024 * 2  # 2GB
        mock_sys_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_sys_memory
        
        operations = [
            ('sort_intensive', {'data_size': 500, 'iterations': 1}),
            ('string_processing', {'text_size': 1000, 'iterations': 1})
        ]
        
        for operation, params in operations:
            # Extract data_size for MetricsContext
            data_size = params.get('data_size', params.get('text_size', 0))
            iterations = params.get('iterations', 1)
            
            with MetricsContext(self.metrics, operation, data_size=data_size, iterations=iterations):
                if operation == 'sort_intensive':
                    self.processor.sort_intensive_workload(**params)
                elif operation == 'string_processing':
                    self.processor.string_processing_workload(**params)
        
        # Verify all operations were tracked
        all_metrics = self.metrics.get_all_metrics()
        self.assertEqual(len(all_metrics['operations']), 2)
        
        for operation, _ in operations:
            self.assertIn(operation, all_metrics['operations'])
            metrics_data = all_metrics['operations'][operation]
            self.assertGreater(metrics_data['execution_time_ms'], 0)
            self.assertEqual(metrics_data['memory_used_mb'], 60.0)
    
    def test_metrics_factory_integration(self):
        """Test using metrics factory with data processor."""
        from metrics import create_metrics_collector
        
        metrics = create_metrics_collector(architecture='arm64', function_name='factory-test')
        
        # Simple operation test
        operation = 'test_operation'
        metrics.start_timer(operation)
        
        # Simulate some work
        result = self.processor.sort_intensive_workload(data_size=100, iterations=1)
        
        execution_time = metrics.stop_timer(operation)
        
        # Verify integration
        self.assertGreater(execution_time, 0)
        self.assertEqual(metrics.architecture, 'arm64')
        self.assertEqual(metrics.function_name, 'factory-test')
        self.assertEqual(result['operation'], 'sort_intensive')


if __name__ == '__main__':
    unittest.main()