# orapy_chart/__init__.py

__version__ = "0.1.0"
__author__ = "Thanh Tai"

# Import main components
from .echart import charts
from .chart.chart_model import ChartModel

# Make charts easily accessible
__all__ = ["charts", "ChartModel"]