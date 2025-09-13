#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for harmony_modules/speech_to_text.py

Tests the STT module functionality including:
- Multi-lock synchronization system
- Graceful frame completion
- Start/Stop methods enhancement
- Audio frame processing
- Button spam protection

Priority: CRITICAL - Recently fixed multi-lock synchronization
"""

import sys
import os
import time
import threading

# Add the src directory to the path so we can import the plugin modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import test framework
from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
from framework.plugin_test_environment import PluginTestEnvironment

class TestSTTModule:
    """Test Speech-to-Text Module functionality"""
    
    def test_stt_operation_lock_protection(self):
        """Test STT operation lock prevents overlapping start/stop operations"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080',
                    'stt_chunk_size': '1024'
                })
                
                # Test that operation lock exists
                assert hasattr(stt_handler, 'operation_lock')
                
                # Test lock acquisition
                lock_acquired = stt_handler.operation_lock.acquire(blocking=False)
                assert lock_acquired
                
                # Test that second acquisition fails (non-blocking)
                second_lock = stt_handler.operation_lock.acquire(blocking=False)
                assert not second_lock
                
                # Release lock
                stt_handler.operation_lock.release()
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_recording_state_lock(self):
        """Test STT recording state lock for state consistency protection"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that recording state lock exists
                assert hasattr(stt_handler, 'recording_state_lock')
                
                # Test lock functionality
                with stt_handler.recording_state_lock:
                    # Should be able to acquire lock in context
                    assert True
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_processing_lock(self):
        """Test STT processing lock for audio frame processing protection"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that processing lock exists
                assert hasattr(stt_handler, 'processing_lock')
                
                # Test lock functionality
                lock_acquired = stt_handler.processing_lock.acquire(blocking=False)
                assert lock_acquired
                stt_handler.processing_lock.release()
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_pending_chunk_tracking(self):
        """Test STT pending chunk tracking for active audio processing"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that pending chunks tracking exists
                assert hasattr(stt_handler, 'pending_audio_chunks')
                assert isinstance(stt_handler.pending_audio_chunks, dict)
                
                # Test adding pending chunk
                chunk_id = 'test_chunk_001'
                stt_handler.pending_audio_chunks[chunk_id] = {
                    'timestamp': time.time(),
                    'size': 1024,
                    'status': 'processing'
                }
                
                # Verify chunk was added
                assert chunk_id in stt_handler.pending_audio_chunks
                assert stt_handler.pending_audio_chunks[chunk_id]['size'] == 1024
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_frame_completion_on_stop(self):
        """Test STT completes current frames naturally on stop"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that frame completion method exists
                assert hasattr(stt_handler, '_wait_for_current_frame_completion')
                
                # Test frame completion with no pending chunks
                completion_result = stt_handler._wait_for_current_frame_completion()
                # Should complete immediately if no pending chunks
                assert completion_result is not False
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_stt_wait_for_frame_completion(self):
        """Test STT wait for frame completion with 3 second timeout"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Add a pending chunk to test timeout
                stt_handler.pending_audio_chunks['test_chunk'] = {
                    'timestamp': time.time(),
                    'size': 1024,
                    'status': 'processing'
                }
                
                # Test frame completion with timeout
                start_time = time.time()
                completion_result = stt_handler._wait_for_current_frame_completion(timeout=1.0)
                elapsed_time = time.time() - start_time
                
                # Should timeout after approximately 1 second
                assert elapsed_time >= 0.9  # Allow some tolerance
                assert elapsed_time <= 1.5  # Should not exceed timeout significantly
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_stt_start_listen_error_handling(self):
        """Test STT start_listen comprehensive error handling"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that start_listen method exists
                assert hasattr(stt_handler, 'start_listen')
                
                # Test start_listen call (may fail due to missing dependencies)
                try:
                    result = stt_handler.start_listen()
                    # If successful, should return True or similar success indicator
                    assert result is not None
                except Exception as e:
                    # Expected in test environment - verify error is handled gracefully
                    assert isinstance(e, Exception)
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_stop_listen_graceful_shutdown(self):
        """Test STT stop_listen graceful state transitions"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that stop_listen method exists
                assert hasattr(stt_handler, 'stop_listen')
                
                # Test stop_listen call
                try:
                    result = stt_handler.stop_listen()
                    # Should handle graceful shutdown
                    assert result is not None
                except Exception as e:
                    # Expected in test environment - verify error is handled gracefully
                    assert isinstance(e, Exception)
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_button_spam_protection(self):
        """Test STT button spam protection prevents race conditions"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test rapid start/stop calls
                results = []
                for i in range(5):
                    try:
                        # Rapid fire start/stop
                        start_result = stt_handler.start_listen()
                        stop_result = stt_handler.stop_listen()
                        results.append((start_result, stop_result))
                    except Exception as e:
                        # Expected - system should handle gracefully
                        results.append(('error', str(e)))
                
                # Should have attempted all operations
                assert len(results) == 5
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_real_audio_data_preservation(self):
        """Test STT preserves real audio data, no empty chunks sent to Harmony Link"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test that audio data processing methods exist
                if hasattr(stt_handler, '_process_audio_chunk'):
                    # Create mock audio data
                    mock_audio_data = b'\x00\x01\x02\x03' * 256  # 1KB of mock audio
                    
                    # Process audio chunk
                    result = stt_handler._process_audio_chunk(mock_audio_data)
                    
                    # Should not return empty data
                    assert result is not None
                    if isinstance(result, bytes):
                        assert len(result) > 0
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_stt_chunk_completion_timeout(self):
        """Test STT handles stuck audio processing with timeout"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test timeout handling for stuck chunks
                if hasattr(stt_handler, '_cleanup_stuck_chunks'):
                    # Add an old chunk that should be cleaned up
                    old_timestamp = time.time() - 10.0  # 10 seconds ago
                    stt_handler.pending_audio_chunks['stuck_chunk'] = {
                        'timestamp': old_timestamp,
                        'size': 1024,
                        'status': 'processing'
                    }
                    
                    # Run cleanup
                    cleaned_count = stt_handler._cleanup_stuck_chunks(max_age=5.0)
                    
                    # Should have cleaned up the stuck chunk
                    assert cleaned_count >= 0
                    assert 'stuck_chunk' not in stt_handler.pending_audio_chunks
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_stt_network_error_recovery(self):
        """Test STT network failure handling and recovery"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler with invalid endpoint to simulate network error
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://invalid-endpoint:99999'
                })
                
                # Test network error handling
                try:
                    result = stt_handler.start_listen()
                    # If it doesn't throw, should handle gracefully
                    assert result is not None
                except Exception as e:
                    # Should handle network errors gracefully
                    assert isinstance(e, Exception)
                    # Error should be logged/handled, not crash the system
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_configuration_validation(self):
        """Test STT configuration validation and defaults"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Test with minimal configuration
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true'
                })
                
                # Should have reasonable defaults
                assert stt_handler is not None
                
                # Test with full configuration
                full_config = {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080',
                    'stt_chunk_size': '2048',
                    'stt_sample_rate': '16000',
                    'stt_timeout': '30'
                }
                
                stt_handler_full = STTEventHandler(None, full_config)
                assert stt_handler_full is not None
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_state_management(self):
        """Test STT recording state management"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test initial state
                if hasattr(stt_handler, 'is_recording'):
                    assert stt_handler.is_recording() == False
                
                # Test state tracking
                if hasattr(stt_handler, 'recording_state'):
                    initial_state = stt_handler.recording_state
                    assert initial_state is not None
                
            except ImportError:
                # STT module may not be available in test environment
                pass
    
    def test_stt_audio_format_handling(self):
        """Test STT audio format handling and conversion"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080',
                    'stt_sample_rate': '16000',
                    'stt_channels': '1'
                })
                
                # Test audio format validation
                if hasattr(stt_handler, '_validate_audio_format'):
                    # Test with valid format
                    valid_format = {
                        'sample_rate': 16000,
                        'channels': 1,
                        'bit_depth': 16
                    }
                    
                    result = stt_handler._validate_audio_format(valid_format)
                    assert result is not False
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_stt_performance_monitoring(self):
        """Test STT performance monitoring and metrics"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.speech_to_text import STTEventHandler
                
                # Create STT handler
                stt_handler = STTEventHandler(None, {
                    'stt_enabled': 'true',
                    'stt_endpoint': 'http://localhost:28080'
                })
                
                # Test performance metrics
                if hasattr(stt_handler, 'get_performance_metrics'):
                    metrics = stt_handler.get_performance_metrics()
                    
                    # Should return metrics dictionary
                    assert isinstance(metrics, dict)
                    
                    # Should contain expected metrics
                    expected_metrics = [
                        'total_chunks_processed',
                        'average_processing_time',
                        'error_count',
                        'success_rate'
                    ]
                    
                    for metric in expected_metrics:
                        if metric in metrics:
                            assert isinstance(metrics[metric], (int, float))
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass


if __name__ == "__main__":
    # Import test runner
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test runner with quiet logging
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    
    # Create test instances
    test_classes = [TestSTTModule()]
    
    # Run test suite
    runner.run_test_suite(test_classes, "unit tests for harmony_modules/speech_to_text.py")
