"""
Data processing module with computational workloads designed to stress CPU and memory.
Implements multiple algorithms to highlight performance differences between ARM64 and x86_64.
"""

import random
import math
import time
import hashlib
from typing import List, Dict, Any
from decimal import Decimal, getcontext


class DataProcessor:
    """Core data processing class with various computational workloads."""

    def __init__(self):
        # Set high precision for decimal calculations
        getcontext().prec = 50

    def sort_intensive_workload(
        self, data_size: int = 10000, iterations: int = 1
    ) -> Dict[str, Any]:
        """
        CPU-intensive sorting workload using multiple algorithms.
        Tests integer operations and memory access patterns.
        """
        results: Dict[str, Any] = {
            "operation": "sort_intensive",
            "data_size": data_size,
            "iterations": iterations,
            "algorithms_tested": [],
        }

        for i in range(iterations):
            # Generate random integer data
            data = [random.randint(1, 100000) for _ in range(data_size)]

            # Test multiple sorting algorithms
            # Quick sort (recursive, stack intensive)
            start_time = time.perf_counter()
            quick_sorted = self._quicksort(data.copy())
            quick_time = time.perf_counter() - start_time

            # Merge sort (memory intensive)
            start_time = time.perf_counter()
            merge_sorted = self._mergesort(data.copy())
            merge_time = time.perf_counter() - start_time

            # Heap sort (in-place, cache-friendly)
            start_time = time.perf_counter()
            heap_sorted = self._heapsort(data.copy())
            heap_time = time.perf_counter() - start_time

            # Built-in sort (optimized)
            start_time = time.perf_counter()
            builtin_sorted = sorted(data.copy())
            builtin_time = time.perf_counter() - start_time

            results["algorithms_tested"].append(
                {
                    "iteration": i + 1,
                    "quicksort_time": quick_time,
                    "mergesort_time": merge_time,
                    "heapsort_time": heap_time,
                    "builtin_time": builtin_time,
                    "results_match": (
                        quick_sorted == merge_sorted == heap_sorted == builtin_sorted
                    ),
                }
            )

        return results

    def mathematical_computation_workload(
        self, complexity: int = 1000, iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Mathematical computation workload with floating-point and decimal operations.
        Tests FPU performance and precision arithmetic.
        """
        results: Dict[str, Any] = {
            "operation": "mathematical_computation",
            "complexity": complexity,
            "iterations": iterations,
            "computations": [],
        }

        for i in range(iterations):
            computation_results = {}

            # Floating-point intensive calculations
            start_time = time.perf_counter()
            pi_estimate = self._calculate_pi_leibniz(complexity)
            pi_time = time.perf_counter() - start_time
            computation_results["pi_calculation"] = {
                "time": pi_time,
                "result": pi_estimate,
                "accuracy": abs(pi_estimate - math.pi),
            }

            # Matrix multiplication (memory and CPU intensive)
            start_time = time.perf_counter()
            matrix_result = self._matrix_multiplication(complexity // 10)
            matrix_time = time.perf_counter() - start_time
            computation_results["matrix_multiplication"] = {
                "time": matrix_time,
                "matrix_size": complexity // 10,
                "result_sum": sum(sum(row) for row in matrix_result),
            }

            # Prime number generation (integer operations)
            start_time = time.perf_counter()
            primes = self._sieve_of_eratosthenes(complexity)
            prime_time = time.perf_counter() - start_time
            computation_results["prime_generation"] = {
                "time": prime_time,
                "primes_found": len(primes),
                "largest_prime": max(primes) if primes else 0,
            }

            # High-precision decimal calculations
            start_time = time.perf_counter()
            factorial_result = self._high_precision_factorial(
                min(complexity // 100, 100)
            )
            factorial_time = time.perf_counter() - start_time
            computation_results["high_precision_factorial"] = {
                "time": factorial_time,
                "input": min(complexity // 100, 100),
                "result_length": len(str(factorial_result)),
            }

            results["computations"].append({"iteration": i + 1, **computation_results})

        return results

    def string_processing_workload(
        self, text_size: int = 10000, iterations: int = 1
    ) -> Dict[str, Any]:
        """
        String processing workload with pattern matching and text manipulation.
        Tests string operations and memory allocation patterns.
        """
        results: Dict[str, Any] = {
            "operation": "string_processing",
            "text_size": text_size,
            "iterations": iterations,
            "processing_results": [],
        }

        for i in range(iterations):
            # Generate random text data
            text = self._generate_random_text(text_size)
            processing_result = {}

            # String hashing (CPU intensive)
            start_time = time.perf_counter()
            hash_results = self._hash_text_multiple_algorithms(text)
            hash_time = time.perf_counter() - start_time
            processing_result["hashing"] = {"time": hash_time, **hash_results}

            # Pattern matching and replacement
            start_time = time.perf_counter()
            pattern_results = self._pattern_matching_workload(text)
            pattern_time = time.perf_counter() - start_time
            processing_result["pattern_matching"] = {
                "time": pattern_time,
                **pattern_results,
            }

            # String compression simulation
            start_time = time.perf_counter()
            compression_results = self._string_compression_simulation(text)
            compression_time = time.perf_counter() - start_time
            processing_result["compression"] = {
                "time": compression_time,
                **compression_results,
            }

            # Text analysis (word counting, frequency analysis)
            start_time = time.perf_counter()
            analysis_results = self._text_analysis(text)
            analysis_time = time.perf_counter() - start_time
            processing_result["text_analysis"] = {
                "time": analysis_time,
                **analysis_results,
            }

            results["processing_results"].append(
                {"iteration": i + 1, **processing_result}
            )

        return results

    def memory_intensive_workload(
        self, memory_size_mb: int = 10, iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Memory-intensive workload to test memory bandwidth and allocation patterns.
        """
        results: Dict[str, Any] = {
            "operation": "memory_intensive",
            "memory_size_mb": memory_size_mb,
            "iterations": iterations,
            "memory_operations": [],
        }

        for i in range(iterations):
            memory_result = {}

            # Large array allocation and manipulation
            start_time = time.perf_counter()
            array_size = (memory_size_mb * 1024 * 1024) // 8  # 8 bytes per float
            large_array = [random.random() for _ in range(array_size)]
            allocation_time = time.perf_counter() - start_time

            # Memory access patterns
            start_time = time.perf_counter()
            sequential_sum = sum(large_array)
            sequential_time = time.perf_counter() - start_time

            start_time = time.perf_counter()
            random_sum = sum(
                large_array[random.randint(0, len(large_array) - 1)]
                for _ in range(len(large_array) // 10)
            )
            random_time = time.perf_counter() - start_time

            # Memory copying operations
            start_time = time.perf_counter()
            array_copy = large_array.copy()
            copy_time = time.perf_counter() - start_time

            memory_result = {
                "iteration": i + 1,
                "allocation_time": allocation_time,
                "sequential_access_time": sequential_time,
                "random_access_time": random_time,
                "copy_time": copy_time,
                "sequential_sum": sequential_sum,
                "random_sum": random_sum,
                "arrays_equal": large_array == array_copy,
            }

            results["memory_operations"].append(memory_result)

            # Clean up to avoid memory issues
            del large_array, array_copy

        return results

    # Helper methods for sorting algorithms
    def _quicksort(self, arr: List[int]) -> List[int]:
        """Quick sort implementation (recursive, stack intensive)."""
        if len(arr) <= 1:
            return arr

        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]

        return self._quicksort(left) + middle + self._quicksort(right)

    def _mergesort(self, arr: List[int]) -> List[int]:
        """Merge sort implementation (memory intensive)."""
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = self._mergesort(arr[:mid])
        right = self._mergesort(arr[mid:])

        return self._merge(left, right)

    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        """Merge helper for merge sort."""
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _heapsort(self, arr: List[int]) -> List[int]:
        """Heap sort implementation (in-place, cache-friendly)."""

        def heapify(arr, n, i):
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and arr[left] > arr[largest]:
                largest = left

            if right < n and arr[right] > arr[largest]:
                largest = right

            if largest != i:
                arr[i], arr[largest] = arr[largest], arr[i]
                heapify(arr, n, largest)

        n = len(arr)

        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i)

        # Extract elements from heap
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            heapify(arr, i, 0)

        return arr

    # Helper methods for mathematical computations
    def _calculate_pi_leibniz(self, iterations: int) -> float:
        """Calculate pi using Leibniz formula (floating-point intensive)."""
        pi_estimate = 0.0
        sign = 1

        for i in range(iterations):
            pi_estimate += sign / (2 * i + 1)
            sign *= -1

        return pi_estimate * 4

    def _matrix_multiplication(self, size: int) -> List[List[float]]:
        """Matrix multiplication (memory and CPU intensive)."""
        # Create two random matrices
        matrix_a = [[random.random() for _ in range(size)] for _ in range(size)]
        matrix_b = [[random.random() for _ in range(size)] for _ in range(size)]

        # Multiply matrices
        result = [[0.0 for _ in range(size)] for _ in range(size)]

        for i in range(size):
            for j in range(size):
                for k in range(size):
                    result[i][j] += matrix_a[i][k] * matrix_b[k][j]

        return result

    def _sieve_of_eratosthenes(self, limit: int) -> List[int]:
        """Generate prime numbers using Sieve of Eratosthenes."""
        if limit < 2:
            return []

        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False

        for i in range(2, int(math.sqrt(limit)) + 1):
            if sieve[i]:
                for j in range(i * i, limit + 1, i):
                    sieve[j] = False

        return [i for i in range(2, limit + 1) if sieve[i]]

    def _high_precision_factorial(self, n: int) -> Decimal:
        """Calculate factorial with high precision using Decimal."""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")

        result = Decimal(1)
        for i in range(2, n + 1):
            result *= Decimal(i)

        return result

    # Helper methods for string processing
    def _generate_random_text(self, size: int) -> str:
        """Generate random text for string processing tests."""
        words = [
            "the",
            "quick",
            "brown",
            "fox",
            "jumps",
            "over",
            "lazy",
            "dog",
            "python",
            "lambda",
            "function",
            "performance",
            "test",
            "data",
            "processing",
            "algorithm",
            "memory",
            "cpu",
            "benchmark",
        ]

        text_parts = []
        current_size = 0

        while current_size < size:
            word = random.choice(words)
            if current_size + len(word) + 1 <= size:
                text_parts.append(word)
                current_size += len(word) + 1
            else:
                break

        return " ".join(text_parts)

    def _hash_text_multiple_algorithms(self, text: str) -> Dict[str, str]:
        """Hash text using multiple algorithms."""
        return {
            "md5": hashlib.md5(text.encode()).hexdigest(),
            "sha1": hashlib.sha1(text.encode()).hexdigest(),
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "sha512": hashlib.sha512(text.encode()).hexdigest(),
        }

    def _pattern_matching_workload(self, text: str) -> Dict[str, Any]:
        """Pattern matching and replacement operations."""
        import re

        # Define patterns to search for
        patterns = [
            r"\b\w{4,}\b",  # Words with 4+ characters
            r"\b[aeiou]\w*",  # Words starting with vowels
            r"\w*ing\b",  # Words ending with 'ing'
            r"\b\w*test\w*\b",  # Words containing 'test'
        ]

        results = {}
        total_matches = 0

        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            results[f"pattern_{i+1}"] = {
                "pattern": pattern,
                "matches_found": len(matches),
                "unique_matches": len(set(matches)),
            }
            total_matches += len(matches)

        # String replacement operations
        modified_text = text
        replacements = [
            ("the", "THE"),
            ("and", "AND"),
            ("test", "TEST"),
            ("data", "DATA"),
        ]

        replacement_count = 0
        for old, new in replacements:
            count = modified_text.count(old)
            modified_text = modified_text.replace(old, new)
            replacement_count += count

        results["replacements"] = {
            "total_replacements": replacement_count,
            "final_text_length": len(modified_text),
        }
        results["total_matches"] = total_matches

        return results

    def _string_compression_simulation(self, text: str) -> Dict[str, Any]:
        """Simulate string compression by counting character frequencies."""
        char_freq: Dict[str, int] = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1

        # Calculate compression ratio estimate
        total_chars = len(text)
        unique_chars = len(char_freq)

        # Simple compression ratio calculation
        compression_ratio = unique_chars / total_chars if total_chars > 0 else 0

        return {
            "original_length": total_chars,
            "unique_characters": unique_chars,
            "most_frequent_char": (
                max(char_freq, key=lambda x: char_freq[x]) if char_freq else ""
            ),
            "compression_ratio_estimate": compression_ratio,
            "character_frequencies": dict(
                sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }

    def _text_analysis(self, text: str) -> Dict[str, Any]:
        """Perform text analysis including word counting and frequency analysis."""
        words = text.lower().split()

        # Word frequency analysis
        word_freq: Dict[str, int] = {}
        for word in words:
            # Remove punctuation
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        # Calculate statistics
        total_words = len(words)
        unique_words = len(word_freq)
        avg_word_length = (
            sum(len(word) for word in words) / total_words if total_words > 0 else 0
        )

        # Find most common words
        most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "average_word_length": avg_word_length,
            "most_common_words": most_common,
            "vocabulary_richness": unique_words / total_words if total_words > 0 else 0,
        }


def process_workload(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for data processing operations.

    Args:
        operation: Type of workload to run
        **kwargs: Parameters specific to each operation

    Returns:
        Dictionary containing processing results and metadata
    """
    processor = DataProcessor()

    start_time = time.perf_counter()

    if operation == "sort_intensive":
        result = processor.sort_intensive_workload(
            data_size=kwargs.get("data_size", 10000),
            iterations=kwargs.get("iterations", 1),
        )
    elif operation == "mathematical_computation":
        result = processor.mathematical_computation_workload(
            complexity=kwargs.get("complexity", 1000),
            iterations=kwargs.get("iterations", 1),
        )
    elif operation == "string_processing":
        result = processor.string_processing_workload(
            text_size=kwargs.get("text_size", 10000),
            iterations=kwargs.get("iterations", 1),
        )
    elif operation == "memory_intensive":
        result = processor.memory_intensive_workload(
            memory_size_mb=kwargs.get("memory_size_mb", 10),
            iterations=kwargs.get("iterations", 1),
        )
    else:
        raise ValueError(f"Unknown operation: {operation}")

    total_time = time.perf_counter() - start_time

    result["total_execution_time"] = total_time
    result["timestamp"] = time.time()

    return result
