import pandas as pd

def n_features(df: pd.DataFrame) -> int:
    '''
    funtion that return the number of features
    '''
    return df.shape[-1]
