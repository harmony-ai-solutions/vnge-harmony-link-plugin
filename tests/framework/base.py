"""
Test Framework Logging Configuration

Provides centralized logging control for the test framework and plugin code.
Supports different log levels and clean test output formatting.
"""
import sys
import os
import logging
import traceback
from contextlib import contextmanager

# Test framework log levels
TEST_LOG_LEVEL_DEBUG = 'DEBUG'
TEST_LOG_LEVEL_INFO = 'INFO'
TEST_LOG_LEVEL_QUIET = 'QUIET'

# Default log levels
DEFAULT_TEST_LOG_LEVEL = TEST_LOG_LEVEL_QUIET
DEFAULT_PLUGIN_LOG_LEVEL = logging.ERROR

# Global test logging configuration
_test_log_level = DEFAULT_TEST_LOG_LEVEL
_plugin_log_level = DEFAULT_PLUGIN_LOG_LEVEL
_current_test_name = None


class TestLogger(object):
    """Custom logger for test framework with configurable output levels"""
    
    def __init__(self, name="TestFramework"):
        self.name = name
    
    def debug(self, message):
        """Log debug message (only shown in DEBUG mode)"""
        if _test_log_level == TEST_LOG_LEVEL_DEBUG:
            print("[DEBUG] [{}] {}".format(self.name, message))
    
    def info(self, message):
        """Log info message (shown in DEBUG and INFO modes)"""
        if _test_log_level in [TEST_LOG_LEVEL_DEBUG, TEST_LOG_LEVEL_INFO]:
            print("[INFO] [{}] {}".format(self.name, message))
    
    def warning(self, message):
        """Log warning message (always shown)"""
        print("[WARNING] [{}] {}".format(self.name, message))
    
    def error(self, message):
        """Log error message (always shown)"""
        print("[ERROR] [{}] {}".format(self.name, message))


class TestRunner(object):
    """Enhanced test runner with clean output formatting"""
    
    def __init__(self, log_level=DEFAULT_TEST_LOG_LEVEL):
        self.log_level = log_level
        self.logger = TestLogger("TestRunner")
        set_test_log_level(log_level)
    
    def run_test_method(self, test_instance, method_name):
        """Run a single test method with clean output and error handling"""
        global _current_test_name
        _current_test_name = "{}.{}".format(test_instance.__class__.__name__, method_name)
        
        try:
            # Get the test method
            test_method = getattr(test_instance, method_name)
            
            # Run the test
            test_method()
            
            # Test passed
            if self.log_level == TEST_LOG_LEVEL_QUIET:
                print("PASS: {}".format(method_name))
            else:
                print("PASS: {} ({})".format(method_name, _current_test_name))
            
            return True
            
        except Exception as e:
            # Test failed - show error with line number
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Find the line number in the test file
            line_number = None
            filename = None
            for frame in traceback.extract_tb(exc_traceback):
                # Handle both tuple format (IronPython) and object format (CPython)
                if hasattr(frame, 'filename'):
                    # Object format
                    frame_filename = frame.filename
                    frame_name = frame.name
                    frame_lineno = frame.lineno
                else:
                    # Tuple format: (filename, line_number, function_name, text)
                    frame_filename = frame[0]
                    frame_lineno = frame[1]
                    frame_name = frame[2]
                
                if 'test_' in frame_filename and method_name in frame_name:
                    line_number = frame_lineno
                    filename = os.path.basename(frame_filename)
                    break
            
            # Format error message
            if line_number and filename:
                error_location = "{}:{}".format(filename, line_number)
                print("FAIL: {} [{}] - {}".format(method_name, error_location, str(e)))
            else:
                print("FAIL: {} - {}".format(method_name, str(e)))
            
            # Show full traceback in debug mode
            if self.log_level == TEST_LOG_LEVEL_DEBUG:
                traceback.print_exc()
            
            return False
        finally:
            _current_test_name = None
    
    def run_test_class(self, test_class_instance):
        """Run all test methods in a test class"""
        class_name = test_class_instance.__class__.__name__
        
        if self.log_level != TEST_LOG_LEVEL_QUIET:
            print("\n--- Running {} ---".format(class_name))
        
        # Get all test methods
        test_methods = [method for method in dir(test_class_instance) if method.startswith('test_')]
        
        passed = 0
        failed = 0
        
        for method_name in test_methods:
            if self.run_test_method(test_class_instance, method_name):
                passed += 1
            else:
                failed += 1
        
        return passed, failed
    
    def run_test_suite(self, test_classes, suite_name="Test Suite"):
        """Run a complete test suite with summary"""
        print("Running {}...".format(suite_name))
        if self.log_level != TEST_LOG_LEVEL_QUIET:
            print("")
        
        total_passed = 0
        total_failed = 0
        
        for test_class in test_classes:
            passed, failed = self.run_test_class(test_class)
            total_passed += passed
            total_failed += failed
        
        # Print summary
        total_tests = total_passed + total_failed
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        print("Total: {}".format(total_tests))
        print("Passed: {}".format(total_passed))
        print("Failed: {}".format(total_failed))
        
        if total_failed == 0:
            print("All tests passed!")
        else:
            print("{} tests failed.".format(total_failed))
        
        return total_passed, total_failed


def set_test_log_level(level):
    """Set the test framework log level"""
    global _test_log_level
    if level in [TEST_LOG_LEVEL_DEBUG, TEST_LOG_LEVEL_INFO, TEST_LOG_LEVEL_QUIET]:
        _test_log_level = level
    else:
        raise ValueError("Invalid test log level: {}. Use DEBUG, INFO, or QUIET.".format(level))


def set_plugin_log_level(level):
    """Set the plugin code log level"""
    global _plugin_log_level
    _plugin_log_level = level
    
    # Configure Python logging for plugin modules
    logging.basicConfig(level=level, format='[%(levelname)s] [%(name)s] %(message)s')


def get_test_log_level():
    """Get current test framework log level"""
    return _test_log_level


def get_plugin_log_level():
    """Get current plugin log level"""
    return _plugin_log_level


def get_logger(name):
    """Get a test framework logger instance"""
    return TestLogger(name)


@contextmanager
def quiet_test_environment():
    """Context manager for running tests with minimal output"""
    original_level = _test_log_level
    set_test_log_level(TEST_LOG_LEVEL_QUIET)
    try:
        yield
    finally:
        set_test_log_level(original_level)


@contextmanager
def debug_test_environment():
    """Context manager for running tests with full debug output"""
    original_level = _test_log_level
    set_test_log_level(TEST_LOG_LEVEL_DEBUG)
    try:
        yield
    finally:
        set_test_log_level(original_level)


# Initialize plugin logging to ERROR level by default
set_plugin_log_level(DEFAULT_PLUGIN_LOG_LEVEL)
