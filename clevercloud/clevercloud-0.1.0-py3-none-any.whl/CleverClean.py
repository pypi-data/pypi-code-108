def CleverClean(text):
    """
    A preprocessor to convert all letters to lower case, and to remove all punctuations and digits from the text.  
    
    Parameters
    ----------
    text : pandas.series
        Input a pandas series of text / strings
    
    Returns
    -------
    str
        A long string containing the cleaned of version of all text
    
    Examples
    --------
    >>> sample_text = pandas.Series('Apple is MY favorite!')
    >>> CleverClean(sample_text)
    'apple is my favorite'
    
    """
    #importing string and pandas package package
    import string
    import pandas as pd
    
    #Checking if correct inputs are given 
    if not pd.api.types.is_string_dtype(text):
        raise TypeError("Input 'text' should be a panda series containing only strings")
    
    #combining strings from the panda series to one large string 
    all_strings=''
    for i in text:
        all_strings+=str(i)
        all_strings+=" "

    #coverting strings to lower case
    text_low = all_strings.lower() 

    #removing all the digits from text
    text_low_noDigits = ''.join([i for i in text_low if not i.isdigit()])

    #removing all the punctuation from text using a for loop 
    prepro_text = "" #storing the complete preprocessed text in this variable 
    for i in text_low_noDigits:
        if i not in string.punctuation:
            prepro_text+=i
    
    #returning the text 
    return prepro_text
