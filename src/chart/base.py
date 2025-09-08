# src/chart/components/base.py
# This file defines a base Chart class that provides common functionality for chart components.

from chart.models.chart_model import ChartModel
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from typing import List
import pandas as pd
import gc


class BaseChart:

    def __init__(self, chart_model: ChartModel, data: pd.DataFrame, 
                 colors: List[str]=  ["#009953", "#00F284", "#F2B950", "#F28444", "#F2D8CE"]):
        self.chart_model = chart_model
        self.data = data
        self.html = None

        # Allow overriding colors from chart_model if provided
        self.colors = colors

    def set_colors(self, colors: List[str]):
        self.colors = colors

    def set_default_axis(self):
        try:
            df = self.data.copy()
            if not self.chart_model.x_axis:
                datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()
                if datetime_cols:
                    self.chart_model.x_axis = datetime_cols
                else:
                    self.chart_model.x_axis = df.select_dtypes(exclude="number").columns.tolist()

            if not self.chart_model.y_axis:
                self.chart_model.y_axis = df.select_dtypes(include="number").columns.tolist()

            del df
            gc.collect()

        except Exception as e:
            raise ValueError(f"Failed to set default axis.\nError: {str(e)}")


    def get_tooltip_opts(self) -> opts.TooltipOpts:
        """Get tooltip options
            Tooltip default for all charts (can be overridden in subclass)"""
        tooltip_type = getattr(self.chart_model, "tooltip_type", "cross")
        
        # Add formatter for K/M/B formatting in tooltip
        formatter = None
        if getattr(self.chart_model, "y_axis_format_large_numbers", True):
            formatter = JsCode("function(params) { var result = params[0].name + '<br/>'; params.forEach(function(param) { var value = param.value; if (value >= 1000000000) { value = (value / 1000000000).toFixed(1) + 'B'; } else if (value >= 1000000) { value = (value / 1000000).toFixed(1) + 'M'; } else if (value >= 1000) { value = (value / 1000).toFixed(1) + 'K'; } else { value = value.toString(); } result += param.marker + ' ' + param.seriesName + ': ' + value + '<br/>'; }); return result; }")
        
        return opts.TooltipOpts(
            is_show=self.chart_model.show_tooltip,
            trigger="axis",
            axis_pointer_type=tooltip_type,
            formatter=formatter,
        )

    def get_common_global_opts(self, include_axis: bool = True, include_toolbox: bool = True, include_datazoom: bool = True):
        """Create global options for all charts"""
        opts_dict = {
            "title_opts": opts.TitleOpts(
                title=(
                    self.chart_model.title.upper()
                    if getattr(self.chart_model, "show_title", True)
                    else ""
                )
            ),
            "legend_opts": opts.LegendOpts(
                is_show=self.chart_model.show_legend, pos_top="20px"
            ),
            "tooltip_opts": self.get_tooltip_opts(),
        }

        if include_axis:
            opts_dict.update(
                {
                    "xaxis_opts": opts.AxisOpts(
                        is_show=self.chart_model.show_x_axis,
                        axislabel_opts=opts.LabelOpts(
                            is_show=getattr(self.chart_model, "show_x_label", True)
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=getattr(self.chart_model, "show_grid", False)
                        ),
                    ),
                    "yaxis_opts": opts.AxisOpts(
                        is_show=self.chart_model.show_y_axis,
                        axislabel_opts=opts.LabelOpts(
                            is_show=getattr(self.chart_model, "show_y_label", True),
                            font_size=getattr(self.chart_model, "y_axis_font_size", 10),
                            margin=getattr(self.chart_model, "y_axis_margin", 8),
                            formatter=JsCode("function(value){return value>=1000000000?(value/1000000000).toFixed(1)+'B':value>=1000000?(value/1000000).toFixed(1)+'M':value>=1000?(value/1000).toFixed(1)+'K':value}") if getattr(self.chart_model, "y_axis_format_large_numbers", True) else None,
                        ),
                        splitline_opts=opts.SplitLineOpts(
                            is_show=getattr(self.chart_model, "show_grid", False)
                        ),
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(width=1)
                        ),
                        axistick_opts=opts.AxisTickOpts(
                            is_align_with_label=True
                        ),
                    ),
                }
            )

        if include_toolbox:
            opts_dict["toolbox_opts"] = opts.ToolboxOpts(
                is_show=True,
                feature={
                    "magicType": {
                        "show": True,
                        "type": ["line", "bar", "stack"],
                    },
                    "saveAsImage": {"show": True},
                },
            )

        if include_datazoom:
            range_start, range_end = getattr(self.chart_model, "datazoom_range", (10, 70))
            opts_dict["datazoom_opts"] = [
                opts.DataZoomOpts(
                    type_="slider",
                    orient="horizontal",
                    range_start=range_start,
                    range_end=range_end,
                    pos_bottom="5%",
                    pos_top="88%",
                    pos_left="10%",
                    pos_right="10%",
                ),
                opts.DataZoomOpts(type_="inside"),
            ]

        return opts_dict

    def extend_opts(self, opts_dict: dict, extra_opts: dict) -> dict:
        """Merge additional options into opts_dict (subclass can override)"""
        opts_dict.update(extra_opts)
        return opts_dict

    def cleanup(self, *objs):
        """Cleanup memory for dataframe/temporary variables"""
        for obj in objs:
            try:
                del obj
            except:
                pass
        gc.collect()

    def render(self):
        raise NotImplementedError("Need implement this method in subclass")
