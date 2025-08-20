from pyecharts.charts import Line
from pyecharts import options as opts
from orapy_chart.chart.echart.base import Chart 
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
import uuid
import base64
import os

class LineChart(Chart):

    def _chart_data(self):
        new_df = (
            self.data.groupby(self.chart_model.x_axis)[self.chart_model.y_axis]
            .sum()
            .reset_index()
        )

        if (
            isinstance(self.chart_model.x_axis, str)
            or len(self.chart_model.x_axis) == 1
        ):
            x_key = (
                self.chart_model.x_axis[0]
                if isinstance(self.chart_model.x_axis, list)
                else self.chart_model.x_axis
            )
            categories = new_df[x_key].astype(str).to_list()
        else:
            categories = (
                new_df[self.chart_model.x_axis]
                .astype(str)
                .agg(" - ".join, axis=1)
                .to_list()
            )

        return new_df, categories

    def _build_line_chart(
        self, horizontal=False, for_image=False, render_path: str = None
    ) -> Line:
        line = Line(
            init_opts=opts.InitOpts(
                width="90%" if for_image else "100%",
                height=f"{self.chart_model.size.height}px",
            )
        )
        new_df, categories = self._chart_data()

        line.add_xaxis(categories)
        for column in self.chart_model.y_axis:
            line.add_yaxis(
                column,
                new_df[column].to_list(),
                is_symbol_show=False,
                label_opts=opts.LabelOpts(is_show=False),
            )

        if horizontal:
            line.reversal_axis()

        opts_dict = self.get_common_global_opts(
            include_axis=not for_image,
            include_datazoom=not for_image,
            include_toolbox=not for_image,
        )

        if for_image:
            opts_dict["datazoom_opts"] = [opts.DataZoomOpts(is_show=False)]

        line.set_global_opts(**opts_dict)
        self.extend_axes(line)

        # ✅ Nếu có đường dẫn render HTML thì render luôn ở đây
        if for_image and render_path:
            line.render(render_path)

        return line

    def render(self, horizontal=False):
        try:
            line = self._build_line_chart(horizontal=horizontal, for_image=False)
            self.html = line.render_embed()
            return self.html
        except Exception as e:
            raise RuntimeError(f"Lỗi khi render HTML: {str(e)}")

    def render_base64(self, horizontal=False):
        try:
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

            return img_base64

        except Exception as e:
            raise RuntimeError(f"Lỗi khi render base64: {str(e)}")

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

        except Exception as e:
            raise RuntimeError(f"Lỗi khi render PNG: {str(e)}")
