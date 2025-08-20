# Description: EChart components.

from orapy_chart.chart.echart.bar_chart import BarChart
from orapy_chart.chart.echart.line_chart import LineChart
from orapy_chart.chart.echart.pie_chart import PieChart
from orapy_chart.chart.chart_model import ChartModel

charts = {
    "ChartModel": ChartModel,
    "LineChart": LineChart,
    "BarChart": BarChart,
    "PieChart": PieChart,
}
