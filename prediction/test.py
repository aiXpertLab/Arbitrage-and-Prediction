import numpy as np
from sklearn.datasets import load_iris
import pandas as pd
 
# Loading irirs dataset
data = load_iris()
df = pd.DataFrame(data.data,
                  columns = data.feature_names)
print(df.head(10))