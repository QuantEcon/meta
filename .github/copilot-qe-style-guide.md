# QuantEcon Style Guide

This document consolidates the main style rules from the QuantEcon style guide for use in copilot reviews of lectures. It covers the essential conventions that ensure consistency and quality across QuantEcon content.

## Writing Conventions

### General Writing Principles
- Keep it clear and keep it short
- Use one sentence paragraphs only
- Keep those one sentence paragraphs short and clear
- The value of the lecture is the importance and clarity of the information divided by the number of words
- Ensure good logical flow with no jumps
- Choose the simplest option when you have reasonable alternatives
- Don't capitalize unless necessary

### Emphasis and Definitions
- Use **bold** for definitions (e.g., "A **closed set** is a set whose complement is open.")
- Use *italic* for emphasis (e.g., "All consumers have *identical* endowments.")

### Titles and Headings
- **Lecture titles**: Capitalize all words (e.g., "How it Works: Data, Variables and Names")
- **All other headings**: Capitalize only the first word and proper nouns (e.g., "Binary packages with Python frontends")

## Code Style

### General Principles
- Follow [PEP8](https://peps.python.org/pep-0008/) unless there's a good mathematical reason to do otherwise
- Use capitals for matrices when closer to mathematical notation
- Operators surrounded by spaces: `a * b`, `a + b`, but `a**b` for $a^b$

### Variable Naming
**Prefer Unicode symbols for Greek letters commonly used in economics:**
- Use `α` instead of `alpha`
- Use `β` instead of `beta`
- Use `γ` instead of `gamma`
- Use `δ` instead of `delta`
- Use `ε` instead of `epsilon`
- Use `σ` instead of `sigma`
- Use `θ` instead of `theta`
- Use `ρ` instead of `rho`

Example:
```python
# ✅ Preferred: Unicode variables
def utility_function(c, α=0.5, β=0.95):
    return (c**(1-α) - 1) / (1-α) * β

# ❌ Avoid: Spelled-out Greek letters  
def utility_function(c, alpha=0.5, beta=0.95):
    return (c**(1-alpha) - 1) / (1-alpha) * beta
```

### Package Installation
- Lectures should run in a base installation of Anaconda Python
- Install non-Anaconda packages at the top of the lecture:
```python
!pip install quantecon
!pip install --upgrade yfinance
```
- Use `tags: [hide-output]` for installation cells
- **JAX exception**: Don't install `jax` at the top; use GPU warning admonition instead

### Performance Timing
**Use modern `qe.Timer()` context manager:**
```python
# ✅ Preferred: Timer context manager
import quantecon as qe

with qe.Timer():
    result = expensive_computation()

# ❌ Avoid: Manual timing patterns
import time
start_time = time.time()
result = expensive_computation()
end_time = time.time()
```

## Math Notation

### Standard Conventions
- Use `\top` for transpose: $A^\top$
- Use `\mathbb{1}` for vectors/matrices of ones: $\mathbb{1}$
- Use square brackets for matrices: `\begin{bmatrix} ... \end{bmatrix}`
- **Do not** use bold face for matrices or vectors
- Use curly brackets for sequences: `\{ x_t \}_{t=0}^{\infty}`

### Equation Formatting
- Use `\begin{aligned} ... \end{aligned}` within math environments for alignment
- Don't use `\tag` for manual equation numbering
- Use built-in equation numbering:
```markdown
$$
x_y = 2
$$ (label)
```
- Reference equations with `{eq}` role: `{eq}`label``

## Figures

### General Rules
1. **No** embedded titles in matplotlib (no `ax.set_title`)
2. Add `title` metadata to `figure` directive or `code-cell` metadata
3. Use lowercase for captions, except first letter and proper nouns
4. Keep caption titles to about 5-6 words max
5. Set descriptive `name` for reference with `numref`
6. Axis labels should be lowercase ("time" not "Time")
7. Keep the `box` around matplotlib figures (don't remove spines)
8. Use `lw=2` for all matplotlib line charts
9. Figures should be 80-100% of text width

### Code-Generated Figures
Use `mystnb` metadata for captions:
```python
```{code-cell} ipython3
---
mystnb:
  figure:
    caption: GDP per capita vs. life expectancy
    name: fig-gdppc-le
---
# your plotting code
```

### Plotly Figures
- Include `{only} latex` directive after plotly figures with website link
- Use `{ref}` role (not `{numref}`) with title text for references

## Document Structure

### Admonitions and Exercises
- Use [gated syntax](https://ebp-sphinx-exercise.readthedocs.io/en/latest/syntax.html#alternative-gated-syntax) for exercises with executable code or nested directives
- Use `:class: dropdown` for solutions by default
- For nested directives: ensure outer directive uses more ticks than inner ones

### Linking Documents
**Same lecture series:**
```markdown
[another document](figures)
[](figures)  # Uses automatic title
```

**Different lecture series (requires intersphinx setup):**
```markdown
{doc}`this lecture on linear equations<intro:linear_equations>`
{doc}`intro:linear_equations`  # Uses automatic title
```

## References

### Citations
- Use `{cite}` role: `{cite}`StokeyLucas1989`, chapter 2`
- Add bibtex entries to `<repo>/lectures/_static/quant-econ.bib`

## JAX Conversion Guidelines

### When to Use JAX
- Replace **Numba** with **JAX** for performance-critical code
- Pure NumPy lectures that aren't computationally intensive can remain NumPy

### JAX Principles
- Use **pure functions** with **no side effects**
- Don't modify inputs; return new data
- Replace large classes with structured functional approaches
- Use `NamedTuple` instead of complex `jitclass` structures

Example migration pattern:
```python
# ❌ Avoid: Mutating input arrays
def bad_update(state, shock):
    state[0] += shock  # Modifies input
    return state

# ✅ Prefer: Pure function returning new data
def good_update(state, shock):
    return state.at[0].add(shock)  # Returns new array
```

## Repository Conventions

### Naming Schemes
- Use characters that don't require shift key (`-` not `_`)
- **Lectures**: `lecture-{name}`, `lecture-{name}.notebooks`
- **Books**: `book-{name}`, `book-{name}.public`, `quantecon-book-{name}`
- **Projects**: `project-{name}`

---

This style guide should be used to ensure QuantEcon lectures maintain consistency in writing style, code formatting, mathematical notation, figure presentation, and overall document structure.