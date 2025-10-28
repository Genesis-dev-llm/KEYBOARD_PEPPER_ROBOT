"""
Configuration Validator
Ensures all settings are within safe ranges.
"""

import logging
from . import config

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates configuration values."""
    
    @staticmethod
    def validate_all():
        """Validate all config values."""
        issues = []
        
        # Speed validation
        if config.BASE_LINEAR_SPEED_DEFAULT > 0.55:
            issues.append(f"Base speed too high: {config.BASE_LINEAR_SPEED_DEFAULT} (max safe: 0.55)")
        
        if config.SMOOTHING_FACTOR > 0.3:
            issues.append(f"Smoothing factor high: {config.SMOOTHING_FACTOR} (responsive: <0.2)")
        
        # Update rate
        if config.BASE_UPDATE_HZ < 20:
            issues.append(f"Update rate too low: {config.BASE_UPDATE_HZ}Hz (min: 20Hz)")
        
        # Dance safety
        if config.MOONWALK_LEAN_ANGLE > 0.12:
            issues.append(f"Moonwalk lean unsafe: {config.MOONWALK_LEAN_ANGLE} (max safe: 0.12)")
        
        # Log results
        if issues:
            logger.warning("⚠️ Configuration Issues Found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
            return False
        else:
            logger.info("✓ Configuration validated successfully")
            return True
    
    @staticmethod
    def clamp_to_safe():
        """Clamp all values to safe ranges."""
        config.BASE_LINEAR_SPEED_DEFAULT = min(config.BASE_LINEAR_SPEED_DEFAULT, 0.5)
        config.BASE_ANGULAR_SPEED_DEFAULT = min(config.BASE_ANGULAR_SPEED_DEFAULT, 0.7)
        config.SMOOTHING_FACTOR = min(config.SMOOTHING_FACTOR, 0.2)
        config.MOONWALK_LEAN_ANGLE = min(config.MOONWALK_LEAN_ANGLE, 0.10)
        logger.info("✓ Configuration clamped to safe values")

# Validate on import
ConfigValidator.validate_all()