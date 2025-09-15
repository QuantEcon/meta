# Test Markdown with Already Formatted Code

This file contains properly formatted Python code to test that no changes are made.

## MyST Code Cells

```{code-cell} python
import numpy as np


def well_formatted_function(x, y):
    result = x + y
    return result


x = 5
y = 10
print(f"Result is {well_formatted_function(x, y)}")
```

```{code-cell} python3
class WellFormattedClass:
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


obj = WellFormattedClass(42)
print(obj.get_value())
```

## Standard Markdown Code Blocks

```python
import matplotlib.pyplot as plt


def plot_data(x, y, title="Default Title"):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    return fig


data_x = [1, 2, 3, 4, 5]
data_y = [2, 4, 6, 8, 10]
plot_data(data_x, data_y, "My Plot")
```

```ipython
# This is an ipython code block
import pandas as pd

df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
print(df.head())

# Well formatted lambda
process_data = lambda x: x * 2 + 1
result = process_data(5)
print(f"Result: {result}")
```

## Mixed Code Blocks

```{code-cell} ipython3
# This is already formatted
import numpy as np


def calculate_mean(arr):
    return np.mean(arr)


data = np.array([1, 2, 3, 4, 5])
mean_value = calculate_mean(data)
print(f"Mean: {mean_value}")
```