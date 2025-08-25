# Test Lecture with Style Issues

This lecture contains various style issues for testing the QuantEcon Style Guide Checker.

## Writing Style Issues

This paragraph contains multiple sentences in one paragraph which violates the style guide. This should be split into separate one-sentence paragraphs. This is another sentence that makes the paragraph too long.

## Code Style Issues

Here's some Python code with style issues:

```python
# Greek letter issues
def utility_function(c, alpha=0.5, beta=0.95, gamma=0.1):
    return (c**(1-alpha) - 1) / (1-alpha) * beta + gamma

# Timing issues
import time
start_time = time.time()
result = expensive_computation()
end_time = time.time()
print(f"Computation took {end_time - start_time:.2f} seconds")
```

## Math Notation Issues

Here are some mathematical expressions with style issues:

$$A^T = \begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}$$

And an equation with manual numbering:

$$x = y + z \tag{1}$$

## Figure Issues

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)  # Missing line width
plt.title("Sine Wave")  # Should not use title
plt.xlabel("Time")  # Should be lowercase
plt.ylabel("Amplitude")  # Should be lowercase
plt.show()
```

## Heading Capitalization Issues

### This Is An Improperly Capitalized Heading With Too Many Capital Letters

The heading above violates the style guide by capitalizing all words instead of just the first word and proper nouns.

### Another Example Of Bad Capitalization Pattern

This is also incorrectly capitalized.

## Emphasis Issues

This sentence has a definition that should be bolded: A closed set is a set whose complement is open.

This sentence needs emphasis on a word: All consumers have identical endowments.