# OraePy Chart

Chart utilities for Oracle AWR/ASH visualization using PyEcharts.

## Features

- **Multiple Chart Types**: Bar, Line, and Pie charts
- **Flexible Output**: HTML embed, PNG images, or Base64 encoded images
- **Oracle Database Integration**: Designed for AWR/ASH data visualization
- **Customizable**: Configurable chart options and styling

## Installation

```bash
pip install orapy_chart
```

## Dependencies

- pandas >= 1.3.0
- flask >= 2.0.0
- pydantic >= 1.8.0
- pyecharts >= 1.9.0
- snapshot-selenium >= 1.0.0

## Quick Start

```python
import pandas as pd
from orapy_chart import charts, ChartModel

# Sample data
data = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'],
    'value': [10, 25, 15, 30]
})

# Create chart model
chart_model = ChartModel(
    id="sample_chart",
    type="bar",
    title="Sample Chart",
    x_axis=['category'],
    y_axis=['value']
)

# Create and render chart
bar_chart = charts['BarChart'](chart_model, data)
html_output = bar_chart.render()
```

## Chart Types

### Bar Chart
```python
bar_chart = charts['BarChart'](chart_model, data)
html_output = bar_chart.render(horizontal=False, show_label=False)
```

### Line Chart
```python
line_chart = charts['LineChart'](chart_model, data)
html_output = line_chart.render(horizontal=False)
```

### Pie Chart
```python
pie_chart = charts['PieChart'](chart_model, data)
html_output = pie_chart.render(threshold=0.05, donut=False, show_label=False)
```

## Output Formats

All chart types support multiple output formats:

- **HTML Embed**: `chart.render()`
- **PNG Image**: `chart.render_png(output_path='./images/', image_name='chart.png')`
- **Base64 Image**: `chart.render_base64()`

## Chart Configuration

Use the `ChartModel` class to configure your charts:

```python
from orapy_chart.chart.chart_model import ChartModel, ChartSize

chart_model = ChartModel(
    id="my_chart",
    type="bar",
    title="My Chart Title",
    x_axis=['column1'],
    y_axis=['column2'],
    x_label="X Axis Label",
    y_label="Y Axis Label",
    show_legend=True,
    show_grid=False,
    show_tooltip=True,
    size=ChartSize(width=800, height=400)
)
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Thanh Tai - thanhtai.dev@gmail.com

## Repository

https://github.com/Thanh-Tai-1510/orapy_chart