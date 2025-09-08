# ora-chart
Chart component uses in orapy

## Features

- Line charts, bar charts, and pie charts
- Support for large numbers with proper y-axis formatting
- PNG, HTML, and base64 rendering
- Customizable chart appearance and behavior

## Y-Axis Formatting for Large Numbers

The library now includes improved y-axis formatting to handle large numbers properly. When rendering charts with large values, the y-axis labels will have adequate spacing and larger chart dimensions to prevent truncation.

### K/M/B Number Formatting

For better readability of large numbers, the library automatically formats y-axis labels using:
- **K** for thousands (e.g., 1,500 → 1.5K)
- **M** for millions (e.g., 2,500,000 → 2.5M)  
- **B** for billions (e.g., 2,500,000,000 → 2.5B)

### Configuration Options

You can customize y-axis formatting using the following ChartModel properties:

- `y_axis_font_size`: Font size for y-axis labels (default: `10`)
- `y_axis_margin`: Margin for y-axis labels (default: `8`)
- `y_axis_format_large_numbers`: Enable K/M/B formatting (default: `True`)

### Automatic Improvements for PNG Rendering

When rendering to PNG, the library automatically:
- Increases chart width to 1200px to accommodate large numbers
- Sets minimum font size to 14px for better readability
- Sets minimum margin to 25px to prevent label truncation
- Disables animations for cleaner PNG output
- Applies K/M/B formatting to y-axis labels (if enabled)

### Example Usage

```python
from chart.models.chart_model import ChartModel, ChartSize

chart_model = ChartModel(
    id="my_chart",
    type="line",
    title="Chart with Large Numbers",
    x_axis=["category"],
    y_axis=["value"],
    y_axis_font_size=14,           # Larger font
    y_axis_margin=30,             # More margin
    y_axis_format_large_numbers=True  # Enable K/M/B formatting
    size=ChartSize(width=800, height=400)
)

# Disable K/M/B formatting
chart_model_disabled = ChartModel(
    id="example_disabled",
    type="line",
    title="Example Chart (No K/M/B)",
    x_axis=["category"],
    y_axis=["value"],
    y_axis_format_large_numbers=False  # Disable K/M/B formatting
)
```

## Installation

```bash
pip install -e .
```

## Usage

```python
import pandas as pd
from chart.chart import Chart
from chart.models.chart_model import ChartModel, ChartSize

# Create your data
data = {
    'category': ['A', 'B', 'C'],
    'value': [1000000, 2000000, 1500000]
}
df = pd.DataFrame(data)

# Create chart model
chart_model = ChartModel(
    id="example",
    type="line",
    title="Example Chart",
    x_axis=["category"],
    y_axis=["value"]
)

# Create and render chart
chart = Chart(chart_model, df)
png_path = chart.render_png()  # Renders to PNG
html = chart.render_html()      # Renders to HTML
base64 = chart.render_base64()  # Renders to base64
```
