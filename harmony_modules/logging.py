# Harmony Link Plugin for VNGE
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This file contains a logging wrapper system for the Harmony Link Plugin.
# It provides configurable log levels, message truncation, and consistent formatting.

import ConfigParser
import os
import time

# Log levels (in order of severity)
LOG_LEVEL_TRACE = 0
LOG_LEVEL_DEBUG = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_WARNING = 3
LOG_LEVEL_ERROR = 4
LOG_LEVEL_CRITICAL = 5

# Log level names
LOG_LEVEL_NAMES = {
    LOG_LEVEL_TRACE: "TRACE",
    LOG_LEVEL_DEBUG: "DEBUG",
    LOG_LEVEL_INFO: "INFO", 
    LOG_LEVEL_WARNING: "WARNING",
    LOG_LEVEL_ERROR: "ERROR",
    LOG_LEVEL_CRITICAL: "CRITICAL"
}

# String to log level mapping
LOG_LEVEL_MAP = {
    "TRACE": LOG_LEVEL_TRACE,
    "DEBUG": LOG_LEVEL_DEBUG,
    "INFO": LOG_LEVEL_INFO,
    "WARNING": LOG_LEVEL_WARNING,
    "ERROR": LOG_LEVEL_ERROR,
    "CRITICAL": LOG_LEVEL_CRITICAL
}

# Global configuration cache
_config_cache = None
_config_loaded = False


def _load_logging_config():
    """Load logging configuration from harmony.ini"""
    global _config_cache, _config_loaded
    
    if _config_loaded:
        return _config_cache
    
    try:
        # Load config from harmony.ini
        config = ConfigParser.SafeConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'harmony.ini')
        config.read(config_path)
        
        # Default values
        defaults = {
            'log_level': 'INFO',
            'show_timestamps': 'true',
            'show_module_names': 'true',
            'truncation_length': '200'
        }
        
        # Load values with defaults
        _config_cache = {}
        for key, default_value in defaults.items():
            try:
                if config.has_option('Logging', key):
                    _config_cache[key] = config.get('Logging', key)
                else:
                    _config_cache[key] = default_value
            except:
                _config_cache[key] = default_value
        
        # Convert log level string to integer
        log_level_str = _config_cache['log_level'].upper()
        _config_cache['log_level_int'] = LOG_LEVEL_MAP.get(log_level_str, LOG_LEVEL_INFO)
        
        # Convert boolean strings
        _config_cache['show_timestamps_bool'] = _config_cache['show_timestamps'].lower() == 'true'
        _config_cache['show_module_names_bool'] = _config_cache['show_module_names'].lower() == 'true'
        
        # Convert truncation length to integer
        try:
            _config_cache['truncation_length_int'] = int(_config_cache['truncation_length'])
            # Ensure minimum length
            if _config_cache['truncation_length_int'] < 50:
                _config_cache['truncation_length_int'] = 50
        except:
            _config_cache['truncation_length_int'] = 200
            
        _config_loaded = True
        
    except Exception as e:
        # Fallback to defaults if config loading fails
        _config_cache = {
            'log_level': 'INFO',
            'log_level_int': LOG_LEVEL_INFO,
            'show_timestamps': 'true',
            'show_timestamps_bool': True,
            'show_module_names': 'true', 
            'show_module_names_bool': True,
            'truncation_length': '200',
            'truncation_length_int': 200
        }
        _config_loaded = True
        print("Warning: Failed to load logging config, using defaults: {0}".format(str(e)))
    
    return _config_cache


class HarmonyLogger:
    """
    Logging wrapper class that provides configurable log levels, 
    message truncation, and consistent formatting.
    """
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.config = _load_logging_config()
    
    def _should_log(self, level):
        """Check if message should be logged based on current log level"""
        return level >= self.config['log_level_int']
    
    def _truncate_message(self, message, max_length):
        """Truncate message if it exceeds max_length"""
        if len(message) <= max_length:
            return message
        
        # Simple split: half at start, half at end
        half_length = max_length // 2
        start_chars = half_length
        end_chars = max_length - half_length
        
        truncated_count = len(message) - max_length
        
        return "{0}...truncated {1} chars...{2}".format(
            message[:start_chars],
            truncated_count, 
            message[-end_chars:]
        )
    
    def _format_message(self, level, message):
        """Format message with timestamp and module name if configured"""
        # Convert message to string and apply truncation
        message_str = str(message)
        truncated_message = self._truncate_message(message_str, self.config['truncation_length_int'])
        
        # Build formatted message
        parts = []
        
        # Add timestamp if enabled
        if self.config['show_timestamps_bool']:
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            parts.append("[{0}]".format(timestamp))
        
        # Add log level
        level_name = LOG_LEVEL_NAMES.get(level, "UNKNOWN")
        parts.append("[{0}]".format(level_name))
        
        # Add module name if enabled
        if self.config['show_module_names_bool'] and self.module_name:
            # Clean up module name (remove harmony_modules prefix if present)
            clean_module = self.module_name
            if clean_module.startswith('harmony_modules.'):
                clean_module = clean_module[16:]  # Remove 'harmony_modules.' prefix
            elif clean_module.startswith('__main__'):
                clean_module = 'harmony'
            parts.append("[{0}]".format(clean_module))
        
        # Add the actual message
        if parts:
            return "{0} {1}".format(" ".join(parts), truncated_message)
        else:
            return truncated_message
    
    def _log(self, level, message, *args):
        """Internal logging method"""
        if not self._should_log(level):
            return
        
        # Format message with arguments if provided
        if args:
            try:
                formatted_message = message % args
            except:
                # If formatting fails, just concatenate
                formatted_message = str(message) + " " + " ".join(str(arg) for arg in args)
        else:
            formatted_message = message
        
        # Format and print the message
        final_message = self._format_message(level, formatted_message)
        print(final_message)
    
    def trace(self, message, *args):
        """Log trace message"""
        self._log(LOG_LEVEL_TRACE, message, *args)

    def debug(self, message, *args):
        """Log debug message"""
        self._log(LOG_LEVEL_DEBUG, message, *args)
    
    def info(self, message, *args):
        """Log info message"""
        self._log(LOG_LEVEL_INFO, message, *args)
    
    def warning(self, message, *args):
        """Log warning message"""
        self._log(LOG_LEVEL_WARNING, message, *args)
    
    def error(self, message, *args):
        """Log error message"""
        self._log(LOG_LEVEL_ERROR, message, *args)
    
    def critical(self, message, *args):
        """Log critical message"""
        self._log(LOG_LEVEL_CRITICAL, message, *args)


# Global logger cache to avoid recreating loggers
_logger_cache = {}


def get_logger(module_name=None):
    """
    Get a logger instance for the specified module.
    
    Args:
        module_name: Name of the module (usually __name__)
    
    Returns:
        HarmonyLogger instance
    """
    if module_name is None:
        module_name = "harmony"
    
    # Use cache to avoid recreating loggers
    if module_name not in _logger_cache:
        _logger_cache[module_name] = HarmonyLogger(module_name)
    
    return _logger_cache[module_name]


# Convenience function for quick logging without creating logger instance
def log_info(message, *args):
    """Quick info logging function"""
    logger = get_logger("harmony")
    logger.info(message, *args)


def log_error(message, *args):
    """Quick error logging function"""
    logger = get_logger("harmony")
    logger.error(message, *args)


def log_warning(message, *args):
    """Quick warning logging function"""
    logger = get_logger("harmony")
    logger.warning(message, *args)


def log_debug(message, *args):
    """Quick debug logging function"""
    logger = get_logger("harmony")
    logger.debug(message, *args)

def log_trace(message, *args):
    """Quick trace logging function"""
    logger = get_logger("harmony")
    logger.trace(message, *args)
