# Test Markdown with Only Non-Python Code

This file contains no Python code blocks to test that nothing is processed.

## Julia Code

```{code-cell} julia
function calculate_fibonacci(n)
    if n <= 1
        return n
    else
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
    end
end

result = calculate_fibonacci(10)
println("Fibonacci(10) = $result")
```

## JavaScript Code

```javascript
function calculateSum(arr) {
    return arr.reduce((sum, num) => sum + num, 0);
}

const numbers = [1, 2, 3, 4, 5];
const total = calculateSum(numbers);
console.log(`Total: ${total}`);
```

## R Code

```r
# Calculate mean and standard deviation
data <- c(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
mean_value <- mean(data)
sd_value <- sd(data)

print(paste("Mean:", mean_value))
print(paste("Standard Deviation:", sd_value))
```

## Plain Text

```
This is just plain text in a code block.
No language is specified.
Should be ignored by the formatter.
```

## YAML

```yaml
name: Example YAML
description: This is a YAML code block
config:
  setting1: value1
  setting2: value2
  numbers:
    - 1
    - 2
    - 3
```