# src/chart/components/bar_chart.py
# This file defines a BarChart class that extends the Chart base class.

import gc
import os
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from chart.base import BaseChart
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot


class BarChart(BaseChart):

    def render(self, horizontal=False, show_label: bool = False):
        try:
            bar = self._build_bar_chart(
                horizontal=horizontal, show_label=show_label, for_image=False
            )

            bar.add_js_funcs(
                f"""
                var chartDom = document.getElementById('{bar.chart_id}');
                var chartInstance = echarts.getInstanceByDom(chartDom);
                chartInstance.on('magictypechanged', function(params) {{
                    if (params.currentType === 'line') {{
                        const option = chartInstance.getOption();
                        if (option.series) {{
                            option.series.forEach(series => {{
                                series.showSymbol = true;      
                                series.symbolSize = 0;         
                                series.emphasis = {{
                                    focus: 'series',
                                    scale: true,
                                    symbolSize: 8        
                                }};
                            }});
                            chartInstance.setOption(option);
                        }}
                    }}
                }});
                """
            )

            self.html = bar.render_embed()

            # Release memory
            del bar
            gc.collect()

            return self.html
        except Exception as e:
            raise RuntimeError(f"BarChart renders to HTML failed.\nError: {str(e)}")

    def render_base64(self, horizontal=False, show_label: bool = False):
        import base64
        import uuid

        try:

            unique_id = uuid.uuid4().hex
            tmp_html = f"_tmp_chart_{unique_id}.html"
            tmp_png = f"_tmp_chart_{unique_id}.png"

            self._build_bar_chart(
                horizontal=horizontal,
                show_label=show_label,
                for_image=True,
                render_path=tmp_html,
            )

            make_snapshot(snapshot, tmp_html, tmp_png)

            with open(tmp_png, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            os.remove(tmp_html)
            os.remove(tmp_png)

            # Release memory
            del tmp_html, tmp_png
            gc.collect()

            # Return the base64 encoded image
            return img_base64
        except Exception as e:
            raise RuntimeError(f"BarChart renders base64 failed.\nError: {str(e)}")

    def render_png(
        self,
        output_path: str = None,
        image_name: str = "chart.png",
        horizontal=False,
        show_label: bool = False,
    ):
        try:
            output_dir = output_path or os.getcwd()
            os.makedirs(output_dir, exist_ok=True)

            image_path = os.path.join(output_dir, image_name)
            html_path = image_path.rsplit(".", 1)[0] + ".html"

            self._build_bar_chart(
                horizontal=horizontal,
                show_label=show_label,
                for_image=True,
                render_path=html_path,
            )

            make_snapshot(snapshot, html_path, image_path)
            # Don't delete HTML file for testing
            # os.remove(html_path)

            # Release memory
            # del html_path
            # gc.collect()

            return image_path

        except Exception as e:
            raise RuntimeError(f"BarChart render PNG failed.\nError: {str(e)}")

    def _prepare_chart_data(self):
        new_df = (
            self.data.groupby(self.chart_model.x_axis)[self.chart_model.y_axis]
            .sum()
            .reset_index()
        )

        if len(self.chart_model.x_axis) == 1:
            categories = new_df[self.chart_model.x_axis[0]].astype(str).to_list()
        else:
            categories = (
                new_df[self.chart_model.x_axis]
                .astype(str)
                .agg(" - ".join, axis=1)
                .to_list()
            )

        return new_df, categories


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

    def _build_bar_chart(self, horizontal=False, show_label=False, for_image=False, render_path: str = None) -> Bar:
        # Calculate width to accommodate large numbers
        chart_width = "1200px" if for_image else "100%"
        chart_height = f"{self.chart_model.size.height}px"
        
        bar = Bar(
            init_opts=opts.InitOpts(
                width=chart_width,
                height=chart_height,
            )
        )

        new_df, categories = self._prepare_chart_data()

        bar.add_xaxis(categories)

        for column in self.chart_model.y_axis:
            # Add formatter for bar labels if K/M/B formatting is enabled
            label_formatter = None
            if show_label and getattr(self.chart_model, "y_axis_format_large_numbers", True):
                label_formatter = JsCode("function(params) { var value = params.value; if (value >= 1000000000) { return (value / 1000000000).toFixed(1) + 'B'; } else if (value >= 1000000) { return (value / 1000000).toFixed(1) + 'M'; } else if (value >= 1000) { return (value / 1000).toFixed(1) + 'K'; } else { return value.toString(); } }")
            
            bar.add_yaxis(
                column,
                new_df[column].to_list(),
                label_opts=opts.LabelOpts(
                    is_show=show_label,
                    formatter=label_formatter
                ),
            )

        if horizontal:
            bar.reversal_axis()

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
                font_size=getattr(self.chart_model, "y_axis_font_size", 14),
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
            opts_dict["datazoom_opts"] = [opts.DataZoomOpts(is_show=False)]
            # Override y-axis options for better PNG rendering with K/M/B formatting
            opts_dict["yaxis_opts"] = opts.AxisOpts(
                is_show=self.chart_model.show_y_axis,
                axislabel_opts=opts.LabelOpts(
                    is_show=getattr(self.chart_model, "show_y_label", True),
                    font_size=max(getattr(self.chart_model, "y_axis_font_size", 14), 14),  # Ensure minimum 14 for PNG
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
            

            


        bar.set_global_opts(**opts_dict)
        bar.set_colors(self.colors)

        if for_image and render_path:
            bar.render(render_path)

        self.cleanup(new_df, categories, opts_dict)
        return bar
