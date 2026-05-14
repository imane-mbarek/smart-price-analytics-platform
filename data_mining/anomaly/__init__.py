"""Detection d'anomalies prix."""

from .isolation_forest import detect_isolation_forest
from .lof_model import detect_lof, detect_anomalies

__all__ = ["detect_isolation_forest", "detect_lof", "detect_anomalies"]
