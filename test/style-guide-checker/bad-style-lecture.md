# Test Lecture With Style Issues

This lecture has multiple style guide violations that should be detected.

## Bad code example with spelled-out Greek letters

```python
import time
import numpy as np

def utility_function(c, alpha=0.5, beta=0.95):
    """Bad example using spelled-out Greek letters."""
    return (c**(1-alpha) - 1) / (1-alpha) * beta

# Bad timing pattern
start_time = time.time()
result = utility_function(1.0)
end_time = time.time()
print(f"Execution time: {end_time - start_time:.4f} seconds")
```

## Heading Capitalization Issues

### this heading should be capitalized properly

This is another example of poor heading style.

### Another Bad Example OF Capitalization

This heading has inconsistent capitalization.

## More Issues

This section has various other style problems:

- Using "alpha" instead of α
- Manual timing instead of qe.Timer()
- Improper heading capitalization
- Missing proper math notation

The variable gamma should be γ, and delta should be δ.

### Math Issues

Bad equation formatting:

$x_t = alpha * x_{t-1} + epsilon_t$

Should use proper Unicode and equation numbering.

```python
# More bad Greek letter usage
def another_function(x, sigma=1.0, theta=0.5, rho=0.9):
    return x * sigma + theta * rho
```