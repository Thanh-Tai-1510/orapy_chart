# src/chart/chart.py
# This file defines a Chart class that extends the BaseChart class.

from typing import List
import pandas as pd
from chart.base import BaseChart
from chart.models.chart_model import ChartModel
from chart.components.line_chart import LineChart
from chart.components.pie_chart import PieChart
from chart.components.bar_chart import BarChart


class Chart(BaseChart):

    def __init__(self, chart_model: ChartModel, data: pd.DataFrame, 
                 colors: List[str]=  ["#009953", "#00F284", "#F2B950", "#F28444", "#F2D8CE"],
                 show_label: bool = False,
                 donut_pie: bool = True,
                 ):
        super().__init__(chart_model, data, colors)
        self.show_label = show_label
        self.donut_pie = donut_pie

    def render_html(self):
        '''Render the chart to HTML'''
        try:
            html = ''
            if self.chart_model.type == "line":
                chart = LineChart(self.chart_model, self.data)
                html = chart.render(horizontal=False,)
            elif self.chart_model.type == "bar":
                chart = BarChart(self.chart_model, self.data)
                html = chart.render(horizontal=False, show_label=self.show_label)
            elif self.chart_model.type == "pie":
                chart = PieChart(self.chart_model, self.data)
                html = chart.render(donut=self.donut_pie, show_label=self.show_label)
            else:
                raise ValueError(f"Unsupported chart type: {self.chart_model.type}")
            
            self.cleanup(chart)
            return html
        except Exception as e:
            raise RuntimeError(f"Chart render to HTML failed.\nError: {str(e)}")

    def render_base64(self):
        '''Render the chart to base64'''
        try:
            base64 = ''
            if self.chart_model.type == "line":
                chart = LineChart(self.chart_model, self.data)
                base64 = chart.render_base64(horizontal=False,)
            elif self.chart_model.type == "bar":
                chart = BarChart(self.chart_model, self.data)
                base64 = chart.render_base64(horizontal=False, show_label=self.show_label)
            elif self.chart_model.type == "pie":
                chart = PieChart(self.chart_model, self.data)
                base64 = chart.render_base64(donut=self.donut_pie, show_label=self.show_label)
            else:
                raise ValueError(f"Unsupported chart type: {self.chart_model.type}")
            self.cleanup(chart)
            return base64
        except Exception as e:
            raise RuntimeError(f"Chart render to base64 failed.\nError: {str(e)}")

    def render_png(self, output_path: str = None, image_name: str = "chart.png"):
        '''Render the chart to PNG'''
        try:
            png = ''
            if self.chart_model.type == "line":
                chart = LineChart(self.chart_model, self.data)
                png = chart.render_png(output_path=output_path, image_name=image_name, horizontal=False)
            elif self.chart_model.type == "bar":
                chart = BarChart(self.chart_model, self.data)
                png = chart.render_png(output_path=output_path, image_name=image_name, horizontal=False, show_label=self.show_label)
            elif self.chart_model.type == "pie":
                chart = PieChart(self.chart_model, self.data)
                png = chart.render_png(output_path=output_path, image_name=image_name, donut=self.donut_pie, show_label=self.show_label)
            else:
                raise ValueError(f"Unsupported chart type: {self.chart_model.type}")
            
            self.cleanup(chart)
            return png
        except Exception as e:
            raise RuntimeError(f"Chart render to PNG failed.\nError: {str(e)}")
        
    