import gc
import os
from typing import List
import pandas as pd
from pyecharts.charts import Pie
from pyecharts import options as opts
from chart.base import BaseChart
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot

from chart.models.chart_model import ChartModel


class PieChart(BaseChart):

    def __init__(self, chart_model: ChartModel, data: pd.DataFrame, 
                 colors: List[str]=  ['#BF9924', '#F2CC0F', '#F2A30F', '#D97D0D', '#733F12', '#7F6A51', '#FFB156', '#FFD4A2', '#7F582B', '#CCAA82']
                 ):
        super().__init__(chart_model, data, colors)

    def render(self, threshold: float = 0.05, donut: bool = False,
                group_other_name: str = "Others", show_label: bool = False):
        try:
            data_present = self._prepare_chart_data(threshold, group_other_name)
            pie = self._build_pie_chart(data_present, donut=donut, show_label=show_label, for_image=False)

            self.html = pie.render_embed()
            
            del data_present, pie  
            gc.collect()

            return self.html

        except Exception as e:
            self.html = ""
            raise RuntimeError(f"PieChart render to HTML failed.\nError: {str(e)}")
        finally:
            return self.html

    def render_base64(self, threshold: float = 0.05, donut: bool = False,
                    group_other_name: str = "Others", show_label: bool = False):
        import base64
        import uuid
        try:
            data_present = self._prepare_chart_data(threshold, group_other_name)

            unique_id = uuid.uuid4().hex
            tmp_html = f"_tmp_chart_{unique_id}.html"
            tmp_png = f"_tmp_chart_{unique_id}.png"

            self._build_pie_chart(data_present, donut=donut, show_label=show_label,
                                for_image=True, render_path=tmp_html)

            make_snapshot(snapshot, tmp_html, tmp_png)

            with open(tmp_png, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            os.remove(tmp_html)
            os.remove(tmp_png)
            
            del data_present, tmp_html, tmp_png 
            gc.collect() 
            
            return img_base64
        except Exception as e:
            raise RuntimeError(f"PieChart renders base64 failed.\nError: {str(e)}")

    def render_png(self, output_path: str = None, image_name: str = 'chart.png',
                threshold: float = 0.05, donut: bool = False,
                group_other_name: str = "Others", show_label: bool = False):
        try:
            data_present = self._prepare_chart_data(threshold, group_other_name)

            output_dir = output_path or os.getcwd()
            os.makedirs(output_dir, exist_ok=True)

            image_path = os.path.join(output_dir, image_name)
            html_path = image_path.rsplit('.', 1)[0] + '.html'

            self._build_pie_chart(data_present, donut=donut, show_label=show_label,
                                for_image=True, render_path=html_path)

            make_snapshot(snapshot, html_path, image_path)
        
            os.remove(html_path)
            del data_present, html_path
            gc.collect()
        
            return image_path
        
        except Exception as e:
            raise RuntimeError(f"PieChart renders PNG failed.\nError: {str(e)}")
        
    

    def _prepare_chart_data(self, threshold: float = 0.05, group_other_name: str = "Others"):
        if len(self.chart_model.y_axis) != 1:
            raise ValueError("Pie chart requires exactly one y_axis (value).")

        value_col = self.chart_model.y_axis[0]
        working_df = self.data.copy()

        if len(self.chart_model.x_axis) == 1:
            category_col = self.chart_model.x_axis[0]
            grouped_df = working_df.groupby(category_col)[value_col].sum().reset_index()
        else:
            category_col = "_combined_key"
            working_df[category_col] = working_df[self.chart_model.x_axis].astype(str).agg(" - ".join, axis=1)
            grouped_df = working_df.groupby(category_col)[value_col].sum().reset_index()

        total = grouped_df[value_col].sum()
        grouped_df["_percentage"] = grouped_df[value_col] / total

        mask = grouped_df["_percentage"] < threshold
        others_value = grouped_df.loc[mask, value_col].sum()
        if others_value > 0:
            grouped_df = grouped_df.loc[~mask]
            others_df = pd.DataFrame({
                category_col: [group_other_name],
                value_col: [others_value]
            })
            grouped_df = pd.concat([grouped_df, others_df], ignore_index=True)

        data_present = grouped_df[[category_col, value_col]].values.tolist()
        
        # Release memory
        del working_df, grouped_df, total, mask, others_value, others_df
        gc.collect()

        return data_present

    def _build_pie_chart(self, data_present, donut=False, show_label=False, for_image=False, render_path: str = None) -> Pie:
        pie = Pie(init_opts=opts.InitOpts(
            width="80%" if for_image else "100%",
            height=f"{self.chart_model.size.height}px"
        ))

        pie.add(
            series_name="",
            data_pair=data_present,
            radius=["40%", "75%"] if donut else "55%",
            label_opts=opts.LabelOpts(
                is_show=show_label,
                formatter="{b}: {d}%"
            )
        )

        pie.set_colors(self.colors)

        opts_dict = self.get_common_global_opts(
            include_axis=False,
            include_datazoom=False,
            include_toolbox=False
        )

        opts_dict["legend_opts"] = opts.LegendOpts(
            is_show=self.chart_model.show_legend,
            type_="scroll",
            pos_left="80%",
            orient="vertical"
        )

        pie.set_global_opts(**opts_dict)

        if for_image and render_path:
            pie.render(render_path)

        return pie
