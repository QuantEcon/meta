# Test Markdown with Unformatted Python Code

This file contains Python code that needs formatting to test the code style checker.

## MyST Code Cells

```{code-cell} python
import numpy as np
def   badly_formatted_function(  x,y  ):
    result=x+y
    return result

x=5;y=10
print(f"Result is {badly_formatted_function(x,y)}")
```

```{code-cell} python3
class BadlyFormattedClass:
 def __init__(self,value):
  self.value=value
 def get_value( self ):
        return self.value

obj=BadlyFormattedClass(42)
print( obj.get_value() )
```

## Standard Markdown Code Blocks

```python
import matplotlib.pyplot as plt

def plot_data(x,y,title="Default Title"):
   fig,ax=plt.subplots()
   ax.plot(x,y)
   ax.set_title(title)
   return fig

data_x=[1,2,3,4,5]
data_y=[2,4,6,8,10]
plot_data(data_x,data_y,"My Plot")
```

```ipython
# This is an ipython code block
import pandas as pd

df=pd.DataFrame({"A":[1,2,3],"B":[4,5,6]})
print(df.head())

# Badly formatted lambda
process_data=lambda x: x*2+1
result=process_data(5)
print(f"Result: {result}")
```

## Non-Python Code Blocks (Should be skipped)

```julia
# This Julia code should not be formatted
function badly_formatted_julia(x,y)
    return x+y
end

result=badly_formatted_julia(1,2)
println("Result: $result")
```

```javascript
// This JavaScript code should not be formatted
function badlyFormattedJS(x,y){
return x+y;
}

let result=badlyFormattedJS(1,2);
console.log("Result: "+result);
```

## Mixed Code Blocks

```{code-cell} ipython3
# This should be formatted
import numpy as np

def calculate_mean(  arr  ):
    return np.mean(arr)

data=np.array([1,2,3,4,5])
mean_value=calculate_mean(data)
print(f"Mean: {mean_value}")
```

```{code-cell} julia
# This Julia code should be skipped
function calculate_sum(x, y)
    return x + y
end

result = calculate_sum(10, 20)
println("Sum: $result")
```