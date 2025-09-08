from typing import List, Optional
from pydantic import BaseModel, Field

class ChartSize(BaseModel):
    width: int = 600
    height: int = 300

class ChartModel(BaseModel):
    id: str
    type: str 
    title: str
    x_axis: List[str]
    y_axis: List[str]
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    show_vertical: float = 0
    show_legend: bool  = True
    show_grid: bool  = False
    show_tooltip: bool = False
    show_x_axis: bool = True
    show_y_axis: bool = True
    show_x_label: bool = False
    show_y_label: bool = False
    y_axis_font_size: Optional[int] = Field(default=10, description="Font size for y-axis labels")
    y_axis_margin: Optional[int] = Field(default=8, description="Margin for y-axis labels")
    y_axis_format_large_numbers: Optional[bool] = Field(default=True, description="Format large numbers with K/M/B suffixes")

    size: Optional[ChartSize] = Field(default=ChartSize(width=600, height=300))
    