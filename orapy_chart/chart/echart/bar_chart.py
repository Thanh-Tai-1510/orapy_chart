from pyecharts.charts import Bar
from pyecharts import options as opts
from orapy_chart.chart.echart.base import Chart
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
import base64
import uuid
import os


class BarChart(Chart):

    def _prepare_chart_data(self):
        new_df = self.data.groupby(self.chart_model.x_axis)[self.chart_model.y_axis].sum().reset_index()

        if len(self.chart_model.x_axis) == 1:
            categories = new_df[self.chart_model.x_axis[0]].astype(str).to_list()
        else:
            categories = new_df[self.chart_model.x_axis].astype(str).agg(" - ".join, axis=1).to_list()

        return new_df, categories

    def _build_bar_chart(self, horizontal=False, show_label=False, for_image=False, render_path: str = None) -> Bar:
        bar = Bar(init_opts=opts.InitOpts(
            width="90%" if for_image else "100%",
            height=f"{self.chart_model.size.height}px"
        ))

        new_df, categories = self._prepare_chart_data()

        bar.add_xaxis(categories)
        for column in self.chart_model.y_axis:
            bar.add_yaxis(column, new_df[column].to_list(), label_opts=opts.LabelOpts(is_show=show_label))

        if horizontal:
            bar.reversal_axis()

        opts_dict = self.get_common_global_opts(
            include_axis=not for_image,
            include_datazoom=not for_image,
            include_toolbox=not for_image
        )

        if for_image:
            opts_dict["datazoom_opts"] = [opts.DataZoomOpts(is_show=False)]

        bar.set_global_opts(**opts_dict)
        bar.set_colors(['#009953', '#00F284', '#F2B950', '#F28444', '#F2D8CE'])

        self.extend_axes(bar)

        if for_image and render_path:
            bar.render(render_path)

        return bar


    def render(self, horizontal=False, show_label: bool = False):
        try:
            bar = self._build_bar_chart(horizontal=horizontal, show_label=show_label, for_image=False)

            bar.add_js_funcs(
                f"""
                var chartDom = document.getElementById('{bar.chart_id}');
                var chartInstance = echarts.getInstanceByDom(chartDom);
                chartInstance.on('magictypechanged', function(params) {{
                    if (params.currentType === 'line') {{
                        const option = chartInstance.getOption();
                        if (option.series) {{
                            option.series.forEach(series => {{
                                series.symbol = 'none';
                            }});
                            chartInstance.setOption(option);
                        }}
                    }}
                }});
                """
            )

            self.html = bar.render_embed()
            return self.html
        except Exception as e:
            raise RuntimeError(f"Lỗi render HTML (BarChart): {str(e)}")

    def render_base64(self, horizontal=False, show_label: bool = False):
        try:
            unique_id = uuid.uuid4().hex
            tmp_html = f"_tmp_chart_{unique_id}.html"
            tmp_png = f"_tmp_chart_{unique_id}.png"

            self._build_bar_chart(horizontal=horizontal, show_label=show_label, for_image=True, render_path=tmp_html)

            make_snapshot(snapshot, tmp_html, tmp_png)

            with open(tmp_png, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            os.remove(tmp_html)
            os.remove(tmp_png)

            return img_base64
        except Exception as e:
            raise RuntimeError(f"Lỗi render base64 (BarChart): {str(e)}")


    def render_png(self, output_path: str = None, image_name: str = 'chart.png', horizontal=False, show_label: bool = False):
        try:
            output_dir = output_path or os.getcwd()
            os.makedirs(output_dir, exist_ok=True)

            image_path = os.path.join(output_dir, image_name)
            html_path = image_path.rsplit('.', 1)[0] + '.html'

            self._build_bar_chart(horizontal=horizontal, show_label=show_label, for_image=True, render_path=html_path)

            make_snapshot(snapshot, html_path, image_path)
            os.remove(html_path)

        except Exception as e:
            raise RuntimeError(f"Lỗi render PNG (BarChart): {str(e)}")

