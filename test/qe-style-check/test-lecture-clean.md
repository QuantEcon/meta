# Clean Test Lecture

This lecture follows the QuantEcon Style Guide correctly.

## Introduction

This is a well-structured paragraph with one sentence.

Each paragraph contains only one sentence as required by the style guide.

## Code examples

Here's properly formatted Python code:

```python
import quantecon as qe

def utility_function(c, α=0.5, β=0.95):
    """Utility function with proper Greek letters."""
    return (c**(1-α) - 1) / (1-α) * β

# Proper timing with qe.Timer
with qe.Timer():
    result = expensive_computation()
```

## Mathematical notation

Proper transpose notation:

$$A^\\top = \\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix}$$

Properly numbered equation:

$$
x = y + z
$$ (equation1)

## Figures

```python
```{code-cell} ipython3
---
mystnb:
  figure:
    caption: sine wave over time
    name: fig-sine
---
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y, lw=2)
plt.xlabel("time")
plt.ylabel("amplitude")
plt.show()
```

## Proper heading capitalization

This heading follows the correct capitalization rules.

### Another properly formatted heading

Only the first word and proper nouns like Python are capitalized.

## Proper emphasis usage

This sentence has a proper definition: A **closed set** is a set whose complement is open.

This sentence has proper emphasis: All consumers have *identical* endowments.