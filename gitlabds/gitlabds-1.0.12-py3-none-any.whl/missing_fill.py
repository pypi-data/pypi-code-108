def missing_fill(df=None, columns="all", method="zero", inplace=False, verbose=True):

    """
    Fill missing values using a range of different options.
    
    See https://pypi.org/project/gitlabds/ for more information and example calls.
    """

    import pandas as pd

    if inplace == True:
        df2 = df

    else:
        df2 = df.copy(deep=True)

    # Get all columns with missing values
    missing_cols = set(df.columns[df.isnull().any()].tolist())

    if columns == "all":
        # Pull all numeric columns to miss fill
        all_numeric = set(df.select_dtypes(include=["number"]).columns.tolist())
        # print(all_numeric)

        # Remove columns that have no missing values
        var_list = list(all_numeric & missing_cols)

    else:
        var_list = columns

    print("\nMissing Fill")
    print(f"Columns selected for {method} filling: {columns}\n")
    print(f"Actual columns with missing values that will be {method} filled: {var_list}\n")

    for v in var_list:

        if method == "zero":
            fill_value = 0
            df[var_list] = df[var_list].fillna(0)

        elif method == "mean":
            fill_value = df[v].mean()

        elif method == "median":
            fill_value = df[v].median()

        if verbose == True:
            print(f"Field: {v}; Fill Value: {fill_value}")

        df[v] = df[v].fillna(fill_value)

    if method == "drop_row":
        print("drop row...nothing will happen. This is future functionality.")

    if method == "drop_column":
        print("drop column...nothing will happen. This is future functionality")

    return df2
