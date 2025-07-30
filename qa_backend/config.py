"""Configuration settings for respiratory data analysis."""

from typing import Tuple, Dict, Any


# === Breath Detection Configuration ===
class BreathDetectionConfig:
    """Configuration for breath detection algorithms."""
    
    # Primary breath detection thresholds
    POSITIVE_FLOW_THRESHOLD: Tuple[float, float] = (1.0, 5.0)  # (min, peak) in L/min
    POSITIVE_PRESSURE_THRESHOLD: float = 1.0  # cmH2O
    NEGATIVE_FLOW_THRESHOLD: Tuple[float, float] = (1.0, 2.0)  # (mean, peak) in L/min
    NEGATIVE_PRESSURE_THRESHOLD: float = 0.1  # cmH2O
    
    # Breath phase detection
    INSP_END_SKIP: int = 31  # samples to skip before searching for insp_end
    INSP_END_PLATEAU_LEN: int = 5  # look-ahead samples for plateau detection
    INSP_END_FLOW_THRESH: float = 1.0  # L/min: flow threshold for plateau
    
    EXP_START_LEN: int = 5  # samples for exp_start detection window
    EXP_START_FLOW_THRESH: float = -4.0  # L/min: negative flow threshold
    
    PLATEAU_REFINE_THRESH: float = 0.5  # L/min: flow threshold for plateau refinement
    
    # Breath refinement
    ZERO_TOLERANCE: float = 0.5  # L/min: tolerance around zero for refinement
    BACK_WINDOW_START: int = 40  # samples to look backward from coarse start
    FORWARD_WINDOW_END: int = 20  # samples to look forward from coarse end
    
    # Safety parameters
    MIN_LOOKAHEAD_SAMPLES: int = 50  # minimum samples needed ahead for detection
    MIN_BREATH_SEPARATION: int = 40  # minimum samples between breath start and end search


# === SOTAIR Analysis Configuration ===
class SOTAIRConfig:
    """Configuration for SOTAIR (Sustained Opening of The Airway with Inspiratory Relief) analysis."""
    
    GRADIENT_THRESHOLD: float = -1000  # Flow gradient threshold
    TIME_GAP_THRESHOLD: float = 0.25  # Time gap threshold in seconds
    GRADIENT_CALCULATION_POINTS: int = 3  # Number of points for gradient calculation


# === QA Validation Configuration ===
class QAValidationConfig:
    """Configuration for QA validation thresholds."""
    
    # Volume thresholds (in mL)
    MAX_EXPIRATORY_VOLUME: float = 2000.0  # Maximum reasonable expiratory volume
    MIN_INSPIRATORY_VOLUME: float = 50.0   # Minimum reasonable inspiratory volume
    
    # Pressure thresholds (in cmH2O)
    MAX_PEAK_PRESSURE: float = 100.0  # Maximum reasonable peak pressure
    MIN_PEAK_PRESSURE: float = 0.1    # Minimum reasonable peak pressure
    
    # Flow thresholds (in L/min)
    MAX_PEAK_FLOW: float = 200.0  # Maximum reasonable peak flow
    MIN_PEAK_FLOW: float = 1.0    # Minimum reasonable peak flow
    
    # Timing thresholds (in seconds)
    MAX_INSPIRATORY_TIME: float = 10.0  # Maximum reasonable inspiratory time
    MIN_INSPIRATORY_TIME: float = 0.1   # Minimum reasonable inspiratory time


# === File I/O Configuration ===
class FileIOConfig:
    """Configuration for file input/output operations."""
    
    # File encoding
    DEFAULT_ENCODING: str = "utf-8"
    
    # Expected column names in Sensirion files
    EXPECTED_COLUMNS = {
        'time': 'Time',
        'timestamp': 'Timestamp', 
        'flow': 'Flow',
        'pressure': 'Pressure',
        'note': 'Note',
        'breath_count': 'Breath Count'
    }
    
    # File format markers
    BREATH_TABLE_MARKER: str = "Breath Count,Time (s)"
    DATA_START_MARKER: str = "Time,Timestamp,Flow,Pressure"
    
    # TSI device warning
    TSI_DEVICE_IDENTIFIER: str = "TSI"
    DEVICE_NAME_HEADER: str = "Device Name"


# === Export Configuration ===
class ExportConfig:
    """Configuration for data export operations."""
    
    # Default output directory name
    DEFAULT_OUTPUT_DIR: str = "output_breathtable"
    
    # File naming patterns
    STANDARD_OUTPUT_PREFIX: str = "auto_breath_table_"
    DEVELOPER_OUTPUT_PREFIX: str = "dev_auto_breath_table_"
    
    # CSV export settings
    CSV_INDEX: bool = False  # Whether to include index in CSV output
    CSV_ENCODING: str = "utf-8"


# === Analysis Configuration ===
class AnalysisConfig:
    """Configuration for data analysis parameters."""
    
    # Statistical analysis
    OUTLIER_DETECTION_METHOD: str = "iqr"  # 'iqr' or 'zscore'
    OUTLIER_THRESHOLD: float = 1.5  # IQR multiplier or Z-score threshold
    
    # Smoothing parameters
    ENABLE_SMOOTHING: bool = False
    SMOOTHING_WINDOW: int = 5  # Window size for moving average
    
    # Data validation
    ENABLE_DATA_VALIDATION: bool = True
    VALIDATION_STRICTNESS: str = "medium"  # 'low', 'medium', 'high'


# === Global Configuration Class ===
class Config:
    """Main configuration class that aggregates all configuration sections."""
    
    def __init__(self):
        self.breath_detection = BreathDetectionConfig()
        self.sotair = SOTAIRConfig()
        self.qa_validation = QAValidationConfig()
        self.file_io = FileIOConfig()
        self.export = ExportConfig()
        self.analysis = AnalysisConfig()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'breath_detection': self._class_to_dict(self.breath_detection),
            'sotair': self._class_to_dict(self.sotair),
            'qa_validation': self._class_to_dict(self.qa_validation),
            'file_io': self._class_to_dict(self.file_io),
            'export': self._class_to_dict(self.export),
            'analysis': self._class_to_dict(self.analysis)
        }
    
    @staticmethod
    def _class_to_dict(config_class) -> Dict[str, Any]:
        """Convert a configuration class to dictionary."""
        return {
            key: value for key, value in config_class.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        for section, values in config_dict.items():
            if hasattr(self, section):
                section_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)


# Create default configuration instance
default_config = Config()


# === Convenience Functions ===
def get_breath_detection_config() -> BreathDetectionConfig:
    """Get breath detection configuration."""
    return default_config.breath_detection


def get_sotair_config() -> SOTAIRConfig:
    """Get SOTAIR analysis configuration."""
    return default_config.sotair


def get_qa_validation_config() -> QAValidationConfig:
    """Get QA validation configuration."""
    return default_config.qa_validation


def get_file_io_config() -> FileIOConfig:
    """Get file I/O configuration."""
    return default_config.file_io


def get_export_config() -> ExportConfig:
    """Get export configuration."""
    return default_config.export


def get_analysis_config() -> AnalysisConfig:
    """Get analysis configuration."""
    return default_config.analysis