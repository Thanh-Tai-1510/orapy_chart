
from orapy_chart.chart.chart_model import ChartModel
from pyecharts import options as opts
from typing import Any
import pandas as pd


class Chart:
    
    def __init__(self, chart_model: ChartModel, data: pd.DataFrame):
        self.chart_model = chart_model
        self.data = data
        self.html = None

    def render(self):
        raise NotImplementedError("Need implement this method in subclass")

    def get_common_global_opts(self, include_axis: bool = True, include_toolbox: bool = True, include_datazoom: bool = True):
        """Tạo global_opts chung cho tất cả biểu đồ"""

        opts_dict = {
            "title_opts": opts.TitleOpts(title=self.chart_model.title.upper() if getattr(self.chart_model, "show_title", True) else ""),
            "legend_opts": opts.LegendOpts(is_show=self.chart_model.show_legend,pos_top="20px"),
            "tooltip_opts": opts.TooltipOpts(is_show=self.chart_model.show_tooltip)
        }

        if include_axis:
            opts_dict.update({
                "xaxis_opts": opts.AxisOpts(
                    is_show=self.chart_model.show_x_axis,
                    axislabel_opts=opts.LabelOpts(is_show=getattr(self.chart_model, "show_x_label", True)),
                    splitline_opts=opts.SplitLineOpts(is_show=getattr(self.chart_model, "show_grid", False))
                ),
                "yaxis_opts": opts.AxisOpts(
                    is_show=self.chart_model.show_y_axis,
                    axislabel_opts=opts.LabelOpts(is_show=getattr(self.chart_model, "show_y_label", True)),
                    splitline_opts=opts.SplitLineOpts(is_show=getattr(self.chart_model, "show_grid", False))
                )
            })

        if include_toolbox:
            opts_dict["toolbox_opts"] = opts.ToolboxOpts(
                is_show=True,
                feature={
                    "magicType": {
                        "show": True,
                        "title": ["Biểu đồ đường", "Biểu đồ cột", "Xếp chồng"],
                        "type": ["line", "bar", "stack"]
                    },
                    "saveAsImage": {"show": True, "title": "Tải xuống biểu đồ"}
                }
            )

        if include_datazoom:
            opts_dict["datazoom_opts"] = [opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]

        return opts_dict


    def extend_axes(self, chart: Any, extend_x: bool = True, extend_y: bool = True):
            """Gắn thêm các trục mở rộng vào biểu đồ nếu cần"""
            if extend_y:
                chart.extend_axis(
                    yaxis=opts.AxisOpts(
                        name="label Y",
                        type_="value",
                        offset=80,
                        position="right",
                        axislabel_opts=opts.LabelOpts(formatter="{value} ml")
                    )
                )
            if extend_x:
                chart.extend_axis(
                    xaxis=opts.AxisOpts(
                        name="label X",
                        type_="value",
                        position="bottom"
                    )
                )