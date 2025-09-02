# Test Document with Style Issues

This document contains various style issues that should be detected by the QuantEcon style guide checker.

## Code Issues

Here's some Python code with style problems:

```python
# Greek letters spelled out instead of Unicode
def utility_function(c, alpha=0.5, beta=0.95):
    return (c**(1-alpha) - 1) / (1-alpha) * beta

# More Greek letters
gamma = 0.02
delta = 0.1
sigma = 2.0
theta = 0.8
rho = 0.9
epsilon = 1e-6
```

## Writing Issues

This is a **definition** but should use bold formatting.

This text has *emphasis* correctly formatted.

Some more text with emphasis but using _underscores_ instead of asterisks.

## Heading Issues

### This Heading Has Too Many Capital Letters And Should Be Fixed

### another heading with wrong capitalization

## Math Issues

Some inline math: $A^T$ should be $A^\top$.

Matrix notation:
$$
\begin{pmatrix}
1 & 2 \\
3 & 4
\end{pmatrix}
$$

Should use square brackets instead.

## Figure Issues

Some text describing a figure that should have proper captions and naming.