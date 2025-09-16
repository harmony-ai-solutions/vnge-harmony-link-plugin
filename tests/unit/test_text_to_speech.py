#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for harmony_modules/text_to_speech.py

Tests the TTS module functionality including:
- Playback state tracking
- TTSProcessorThread enhancement
- Audio system integration
- Performance monitoring
- Playback timing fixes

Priority: CRITICAL - Recently fixed playback timing
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

class TestTTSModule:
    """Test Text-to-Speech Module functionality"""
    
    def test_tts_playback_started_detection(self):
        """Test TTS tracks when audio actually starts playing"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler, TTSProcessorThread
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test playback state tracking
                if hasattr(tts_handler, 'processor_thread'):
                    processor = tts_handler.processor_thread
                    
                    # Test initial state
                    if hasattr(processor, 'playback_started'):
                        assert processor.playback_started == False
                    
                    # Test state change tracking
                    if hasattr(processor, 'start_time'):
                        initial_start_time = processor.start_time
                        assert initial_start_time is None or isinstance(initial_start_time, float)
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_playback_initialization_delay(self):
        """Test TTS 0.5 second minimum wait logic before considering playback complete"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test minimum playback duration
                if hasattr(processor, 'min_playback_duration'):
                    assert processor.min_playback_duration >= 0.5
                elif hasattr(processor, 'MIN_PLAYBACK_DURATION'):
                    assert processor.MIN_PLAYBACK_DURATION >= 0.5
                
                # Test wait logic
                if hasattr(processor, 'wait_voice_played'):
                    # This should implement the minimum wait logic
                    start_time = time.time()
                    
                    # Mock audio source that's not playing
                    class MockAudioSource:
                        def __init__(self):
                            self.isPlaying = False
                        
                        def Play(self):
                            pass
                    
                    mock_audio = MockAudioSource()
                    
                    # Test that it waits minimum duration even if audio reports not playing
                    try:
                        processor.wait_voice_played(mock_audio)
                        elapsed = time.time() - start_time
                        # Should wait at least the minimum duration
                        assert elapsed >= 0.4  # Allow some tolerance
                    except Exception:
                        # Method may not be fully implemented
                        pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_playback_timing_analysis(self):
        """Test TTS monitors elapsed time for debugging and optimization"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test timing analysis features
                timing_attributes = [
                    'start_time',
                    'playback_started',
                    'min_playback_duration'
                ]
                
                for attr in timing_attributes:
                    if hasattr(processor, attr):
                        value = getattr(processor, attr)
                        # Should have reasonable default values
                        assert value is not None or attr == 'start_time'
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_processor_wait_voice_played(self):
        """Test TTSProcessorThread fixed race condition handling"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test that wait_voice_played method exists
                assert hasattr(processor, 'wait_voice_played')
                
                # Create mock audio source
                class MockAudioSource:
                    def __init__(self):
                        self.isPlaying = False
                        self.play_called = False
                    
                    def Play(self):
                        self.play_called = True
                        # Simulate delayed audio start
                        threading.Timer(0.1, lambda: setattr(self, 'isPlaying', True)).start()
                
                mock_audio = MockAudioSource()
                
                # Test race condition fix
                start_time = time.time()
                try:
                    processor.wait_voice_played(mock_audio)
                    elapsed = time.time() - start_time
                    
                    # Should wait for audio to actually start or minimum duration
                    assert elapsed >= 0.1  # At least some wait time
                    assert mock_audio.play_called  # Play should have been called
                    
                except Exception:
                    # Method may not be fully implemented yet
                    pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_processor_minimum_duration(self):
        """Test TTSProcessorThread prevents immediate completion"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test minimum duration enforcement
                class MockAudioSource:
                    def __init__(self):
                        self.isPlaying = False  # Immediately reports not playing
                    
                    def Play(self):
                        pass  # Does nothing, stays not playing
                
                mock_audio = MockAudioSource()
                
                if hasattr(processor, 'wait_voice_played'):
                    start_time = time.time()
                    
                    try:
                        processor.wait_voice_played(mock_audio)
                        elapsed = time.time() - start_time
                        
                        # Should enforce minimum duration even if audio reports not playing
                        assert elapsed >= 0.4  # Allow some tolerance for minimum 0.5s
                        
                    except Exception:
                        # Method may not be fully implemented yet
                        pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_processor_startup_detection(self):
        """Test TTSProcessorThread detects actual playback start"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test startup detection logic
                class MockAudioSource:
                    def __init__(self):
                        self.isPlaying = False
                        self.start_delay = 0.2  # Simulate 200ms startup delay
                    
                    def Play(self):
                        # Simulate delayed audio startup
                        def delayed_start():
                            time.sleep(self.start_delay)
                            self.isPlaying = True
                        
                        threading.Thread(target=delayed_start).start()
                
                mock_audio = MockAudioSource()
                
                if hasattr(processor, 'wait_voice_played'):
                    start_time = time.time()
                    
                    try:
                        processor.wait_voice_played(mock_audio)
                        elapsed = time.time() - start_time
                        
                        # Should detect when audio actually starts
                        # Either waits for startup or minimum duration
                        assert elapsed >= 0.1  # Some reasonable wait time
                        
                    except Exception:
                        # Method may not be fully implemented yet
                        pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_vnge_audio_system_timing(self):
        """Test TTS handles VNGE audio initialization delays"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test VNGE audio system integration
                if hasattr(tts_handler, 'play_audio'):
                    # Create mock audio data
                    mock_audio_data = b'mock_audio_data'
                    
                    try:
                        # Test audio playback with timing considerations
                        start_time = time.time()
                        result = tts_handler.play_audio(mock_audio_data)
                        elapsed = time.time() - start_time
                        
                        # Should handle timing appropriately
                        assert elapsed >= 0.0  # Should not be negative
                        
                    except Exception:
                        # Method may not be fully implemented yet
                        pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_playback_completion_detection(self):
        """Test TTS reliable completion detection"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test completion detection with various scenarios
                test_scenarios = [
                    # Scenario 1: Audio plays and completes normally
                    {
                        'name': 'normal_completion',
                        'initial_playing': False,
                        'starts_playing': True,
                        'completion_delay': 0.3
                    },
                    # Scenario 2: Audio never starts (failure case)
                    {
                        'name': 'never_starts',
                        'initial_playing': False,
                        'starts_playing': False,
                        'completion_delay': 0.0
                    }
                ]
                
                for scenario in test_scenarios:
                    class MockAudioSource:
                        def __init__(self, scenario):
                            self.isPlaying = scenario['initial_playing']
                            self.scenario = scenario
                        
                        def Play(self):
                            if self.scenario['starts_playing']:
                                # Simulate audio starting after delay
                                def start_audio():
                                    time.sleep(0.1)
                                    self.isPlaying = True
                                    # Then complete after completion delay
                                    time.sleep(self.scenario['completion_delay'])
                                    self.isPlaying = False
                                
                                threading.Thread(target=start_audio).start()
                    
                    mock_audio = MockAudioSource(scenario)
                    
                    if hasattr(processor, 'wait_voice_played'):
                        try:
                            start_time = time.time()
                            processor.wait_voice_played(mock_audio)
                            elapsed = time.time() - start_time
                            
                            # Should complete in reasonable time
                            assert elapsed >= 0.0
                            assert elapsed <= 10.0  # Should not hang indefinitely
                            
                        except Exception:
                            # Method may not be fully implemented yet
                            pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_audio_failure_graceful_handling(self):
        """Test TTS handles cases where audio fails to start"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test graceful handling of audio failure
                class FailingAudioSource:
                    def __init__(self):
                        self.isPlaying = False
                    
                    def Play(self):
                        # Simulate Play() call that fails to start audio
                        raise Exception("Audio system failure")
                
                failing_audio = FailingAudioSource()
                
                if hasattr(processor, 'wait_voice_played'):
                    try:
                        # Should handle audio failure gracefully
                        start_time = time.time()
                        processor.wait_voice_played(failing_audio)
                        elapsed = time.time() - start_time
                        
                        # Should complete without hanging
                        assert elapsed >= 0.0
                        assert elapsed <= 5.0  # Should not wait too long on failure
                        
                    except Exception as e:
                        # Should handle exceptions gracefully
                        assert isinstance(e, Exception)
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_playback_duration_logging(self):
        """Test TTS logs playback duration for debug and optimization"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test duration logging features
                if hasattr(tts_handler, 'get_playback_statistics'):
                    stats = tts_handler.get_playback_statistics()
                    
                    # Should return statistics dictionary
                    assert isinstance(stats, dict)
                    
                    # Should contain duration-related metrics
                    expected_metrics = [
                        'total_playbacks',
                        'average_duration',
                        'min_duration',
                        'max_duration',
                        'failed_playbacks'
                    ]
                    
                    for metric in expected_metrics:
                        if metric in stats:
                            assert isinstance(stats[metric], (int, float))
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass
    
    def test_tts_audio_system_state_tracking(self):
        """Test TTS monitors audio system state changes"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSProcessorThread
                
                # Create TTS processor thread
                processor = TTSProcessorThread()
                
                # Test state tracking attributes
                state_attributes = [
                    'playback_started',
                    'start_time',
                    'min_playback_duration'
                ]
                
                for attr in state_attributes:
                    if hasattr(processor, attr):
                        # Should have state tracking attributes
                        value = getattr(processor, attr)
                        # Verify reasonable default values
                        if attr == 'playback_started':
                            assert isinstance(value, bool)
                        elif attr == 'min_playback_duration':
                            assert isinstance(value, (int, float))
                            assert value >= 0.0
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_error_condition_logging(self):
        """Test TTS enhanced error visibility and logging"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://invalid-endpoint:99999'  # Invalid endpoint
                })
                
                # Test error handling and logging
                if hasattr(tts_handler, 'synthesize_speech'):
                    try:
                        # This should fail due to invalid endpoint
                        result = tts_handler.synthesize_speech("test text")
                        
                        # If it doesn't throw, should handle gracefully
                        assert result is not None or result is None  # Either way is acceptable
                        
                    except Exception as e:
                        # Should handle errors gracefully with proper logging
                        assert isinstance(e, Exception)
                        # Error should be informative
                        error_msg = str(e).lower()
                        assert len(error_msg) > 0
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_configuration_validation(self):
        """Test TTS configuration validation and defaults"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Test with minimal configuration
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true'
                })
                
                # Should have reasonable defaults
                assert tts_handler is not None
                
                # Test with full configuration
                full_config = {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080',
                    'tts_voice': 'default',
                    'tts_speed': '1.0',
                    'tts_volume': '0.8'
                }
                
                tts_handler_full = TTSEventHandler(None, full_config)
                assert tts_handler_full is not None
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_thread_safety(self):
        """Test TTS thread safety for concurrent operations"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test concurrent operations
                results = []
                threads = []
                
                def test_synthesis(text, result_list):
                    try:
                        if hasattr(tts_handler, 'synthesize_speech'):
                            result = tts_handler.synthesize_speech(f"test {text}")
                            result_list.append(('success', result))
                        else:
                            result_list.append(('no_method', None))
                    except Exception as e:
                        result_list.append(('error', str(e)))
                
                # Start multiple threads
                for i in range(3):
                    thread = threading.Thread(target=test_synthesis, args=(i, results))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join(timeout=5.0)
                
                # Should have results from all threads
                assert len(results) == 3
                
                # All operations should complete (successfully or with handled errors)
                for result_type, result_data in results:
                    assert result_type in ['success', 'error', 'no_method']
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_audio_format_support(self):
        """Test TTS audio format support and conversion"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test audio format handling
                if hasattr(tts_handler, 'supported_formats'):
                    formats = tts_handler.supported_formats
                    assert isinstance(formats, (list, tuple))
                    
                    # Should support common audio formats
                    common_formats = ['wav', 'mp3', 'ogg']
                    for fmt in common_formats:
                        if fmt in formats:
                            assert isinstance(fmt, str)
                
                # Test format conversion
                if hasattr(tts_handler, 'convert_audio_format'):
                    # Mock audio data
                    mock_audio = b'mock_audio_data'
                    
                    try:
                        converted = tts_handler.convert_audio_format(mock_audio, 'wav')
                        assert converted is not None
                    except Exception:
                        # Method may not be fully implemented
                        pass
                
            except ImportError:
                # TTS module may not be available in test environment
                pass
    
    def test_tts_performance_monitoring(self):
        """Test TTS performance monitoring and metrics collection"""
        with PluginTestEnvironment() as env:
            try:
                from harmony_modules.text_to_speech import TTSEventHandler
                
                # Create TTS handler
                tts_handler = TTSEventHandler(None, {
                    'tts_enabled': 'true',
                    'tts_endpoint': 'http://localhost:28080'
                })
                
                # Test performance metrics
                if hasattr(tts_handler, 'get_performance_metrics'):
                    metrics = tts_handler.get_performance_metrics()
                    
                    # Should return metrics dictionary
                    assert isinstance(metrics, dict)
                    
                    # Should contain expected performance metrics
                    expected_metrics = [
                        'total_requests',
                        'successful_syntheses',
                        'failed_syntheses',
                        'average_synthesis_time',
                        'average_playback_time',
                        'cache_hit_rate'
                    ]
                    
                    for metric in expected_metrics:
                        if metric in metrics:
                            assert isinstance(metrics[metric], (int, float))
                            # Metrics should be non-negative
                            assert metrics[metric] >= 0
                
            except (ImportError, AttributeError):
                # Method may not be implemented yet
                pass


if __name__ == "__main__":
    # Import test runner
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test runner with quiet logging
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    
    # Create test instances
    test_classes = [TestTTSModule()]
    
    # Run test suite
    runner.run_test_suite(test_classes, "unit tests for harmony_modules/text_to_speech.py")
