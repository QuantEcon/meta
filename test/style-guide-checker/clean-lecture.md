# Clean Test Lecture

This is a test lecture that follows the QuantEcon style guide perfectly.

## Introduction

This lecture demonstrates proper style formatting.

### Code example with proper Greek letters

```python
import numpy as np
import quantecon as qe

def utility_function(c, α=0.5, β=0.95):
    """Utility function with proper Unicode Greek letters."""
    return (c**(1-α) - 1) / (1-α) * β

# Proper timing with qe.Timer()
with qe.Timer():
    result = utility_function(1.0)
```

### Math notation

The equation is properly formatted:

$$
x_t = α x_{t-1} + ε_t
$$ (eq:dynamics)

We can reference it with {eq}`eq:dynamics`.

### Figure example

```{code-cell} ipython3
---
mystnb:
  figure:
    caption: sample data visualization
    name: fig-sample
---
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2], lw=2)
ax.set_xlabel("time")
ax.set_ylabel("value")
plt.show()
```