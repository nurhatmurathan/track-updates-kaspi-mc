from enum import Enum


class LoggingLevelsEnum(Enum):
    CRITICAL = "CRITICAL"  # 50
    ERROR = "ERROR"  # 40
    WARNING = "WARNING"  # 30
    INFO = "INFO"  # 20
    DEBUG = "DEBUG"  # 10
    NOTSET = "NOTSET"  # 0


class CampaignStateEnum(Enum):
    ENABLED = "Enabled"
    PAUSED = "Paused"
    ENDED = "Ended"
    ARCHIVED = "Archived"
