def CleverWordCloud(text, CleverStop, max_w):
  
    """
    This function generates a word cloud with customized stopwords and max words included. 
    
    Parameters
    ----------
    text : str
        Input an array of text / strings 
    
    CleverStop: set 
        Input a set of strings 

    max_w: int 
        Input an integer to indicate the maximum number of words included in the word cloud  
    
    Returns
    -------
    png image 
        Display the png image 
    
    Examples
    --------
    >>> CleverWordCloud(text, {"are", "my", "is"}, 200) 
    
    """
    from wordcloud import WordCloud
    import nltk
    if not isinstance(text, str):
        raise TypeError("Input text should be a string.")
   
    if not isinstance(CleverStop, set):
        raise TypeError("Input CleverStop should be a set.")
        
    if not isinstance(max_w, int):
        raise TypeError("Input max_w should be an integer.")
        
    for item in CleverStop:
        if not isinstance(item, str):
            raise TypeError("Each element of the CleverStop set should be a string.")
    
    wordcloud = WordCloud(stopwords=CleverStop, max_words=max_w).generate(text)
    image = wordcloud.to_image()
    image.show()  
    return image
