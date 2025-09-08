# src/chart/components/line_chart.py
# This file defines a LineChart class that extends the Chart base class.

import os
import gc
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from chart.base import BaseChart
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
import pandas as pd

class LineChart(BaseChart):

    def render(self, horizontal=False):
        try:
            line = self._build_line_chart(horizontal=horizontal, for_image=False)
            self.html = line.render_embed()

            del line
            gc.collect()

            return self.html

        except Exception as e:
            raise RuntimeError(f"LineChart renders to HTML failed.\nError: {str(e)}")

    def render_base64(self, horizontal=False):
        try:
            import uuid
            import base64

            unique_id = uuid.uuid4().hex
            tmp_html = f"_tmp_chart_{unique_id}.html"
            tmp_png = f"_tmp_chart_{unique_id}.png"

            # Gọi _build_line_chart có render ra HTML nếu cần
            self._build_line_chart(
                horizontal=horizontal, for_image=True, render_path=tmp_html
            )
            make_snapshot(snapshot, tmp_html, tmp_png)
            with open(tmp_png, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            # Xóa file tạm (chỉ khi không lỗi)
            os.remove(tmp_html)
            os.remove(tmp_png)

            del tmp_html, tmp_png
            gc.collect()

            return img_base64
        except Exception as e:
            raise RuntimeError(f"LineChart renders base64 failed.\nErorr: {str(e)}")

    def render_png(
        self, output_path: str = None, image_name: str = "chart.png", horizontal=False
    ):
        try:
            output_dir = output_path or os.getcwd()
            os.makedirs(output_dir, exist_ok=True)
            image_path = os.path.join(output_dir, image_name)
            html_path = image_path.rsplit(".", 1)[0] + ".html"
            self._build_line_chart(
                horizontal=horizontal, for_image=True, render_path=html_path
            )
            make_snapshot(snapshot, html_path, image_path)

            os.remove(html_path)
            del html_path
            gc.collect()

            return image_path
        except Exception as e:
            raise RuntimeError(f"LineChart renders PNG failed.\nError: {str(e)}")

    def _prepare_chart_data(self):
        try:
            self.set_default_axis()
            new_df = (
                self.data.groupby(self.chart_model.x_axis)[self.chart_model.y_axis]
                .sum()
                .reset_index()
            )

            if (isinstance(self.chart_model.x_axis, str) or len(self.chart_model.x_axis) == 1 ):
                x_key = (self.chart_model.x_axis[0] if isinstance(self.chart_model.x_axis, list) else self.chart_model.x_axis )
                categories = new_df[x_key].astype(str).to_list()
            else:
                categories = (
                    new_df[self.chart_model.x_axis]
                    .astype(str)
                    .agg(" - ".join, axis=1)
                    .to_list()
                )
            

            
            return new_df, categories
        except Exception as e:
            return pd.DataFrame(), []
    


    def _format_large_numbers(self, value):
        """Format large numbers with K/M/B suffixes"""
        if value >= 1000000000:
            return f"{(value / 1000000000):.1f}B"
        elif value >= 1000000:
            return f"{(value / 1000000):.1f}M"
        elif value >= 1000:
            return f"{(value / 1000):.1f}K"
        else:
            return str(value)

    def _format_data_for_display(self, df):
        """Format data values for display if K/M/B formatting is enabled"""
        if getattr(self.chart_model, "y_axis_format_large_numbers", True):
            # Create a copy of the data to avoid modifying the original
            formatted_df = df.copy()
            
            # Format y-axis columns
            for col in self.chart_model.y_axis:
                if col in formatted_df.columns:
                    formatted_df[col] = formatted_df[col].apply(self._format_large_numbers)
            
            return formatted_df
        return df

    def _build_line_chart(self, horizontal=False, for_image=False, render_path: str = None) -> Line:
        # Calculate width to accommodate large numbers
        chart_width = "1200px" if for_image else "100%"
        chart_height = f"{self.chart_model.size.height}px"
        
        line = Line(
            init_opts=opts.InitOpts(
                width=chart_width,
                height=chart_height,
                animation_opts=opts.AnimationOpts(animation=False) if for_image else opts.AnimationOpts(),
            )
        )
        new_df, categories = self._prepare_chart_data()
        
        line.add_xaxis(categories)
        for column in self.chart_model.y_axis:
                line.add_yaxis(
                    column,
                    new_df[column].to_list(),
                    is_symbol_show=False,
                    symbol_size=8,
                    is_hover_animation=True,
                    label_opts=opts.LabelOpts(is_show=False),
                    emphasis_opts=opts.EmphasisOpts(
                        is_disabled=False,
                        focus="series",
                        linestyle_opts=opts.LineStyleOpts(width=3, opacity=1),
                    ),
                )

        if horizontal:
            line.reversal_axis()

        # dùng helper từ class cha
        opts_dict = self.get_common_global_opts(
            include_axis=False,  # Don't include axis from base to avoid formatter override
            include_datazoom=not for_image,
            include_toolbox=not for_image,
        )

        # Add axis options manually to ensure our formatter is used
        opts_dict["xaxis_opts"] = opts.AxisOpts(
            is_show=self.chart_model.show_x_axis,
            axislabel_opts=opts.LabelOpts(
                is_show=getattr(self.chart_model, "show_x_label", True)
            ),
            splitline_opts=opts.SplitLineOpts(
                is_show=getattr(self.chart_model, "show_grid", False)
            ),
        )
        
        # Add y-axis with our custom formatter
        opts_dict["yaxis_opts"] = opts.AxisOpts(
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
            min_=0,  # Set minimum to 0
            max_=None,  # Let ECharts auto-calculate max based on data
        )

        if for_image:
            opts_dict["datazoom_opts"] = [
                opts.DataZoomOpts(type_="inside", range_start=0, range_end=100, is_show=False)
            ]
            # Override y-axis options for better PNG rendering with K/M/B formatting
            opts_dict["yaxis_opts"] = opts.AxisOpts(
                is_show=self.chart_model.show_y_axis,
                axislabel_opts=opts.LabelOpts(
                    is_show=getattr(self.chart_model, "show_y_label", True),
                    font_size=max(getattr(self.chart_model, "y_axis_font_size", 10), 14),  # Ensure minimum 14 for PNG
                    margin=max(getattr(self.chart_model, "y_axis_margin", 8), 25),  # Ensure minimum 25 for PNG
                    rotate=0,  # No rotation to prevent truncation
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
                min_=0,  # Set minimum to 0
                max_=None,  # Let ECharts auto-calculate max based on data
            )
            

            


        line.set_global_opts(**opts_dict)
        line.set_colors(self.colors)

        if for_image and render_path:
            line.render(render_path)

        self.cleanup(new_df, categories, opts_dict)
        return line