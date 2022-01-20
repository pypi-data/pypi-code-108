from transformers import pipeline


def sentiment(sentence='We are very happy to show you the Transformers library.'):
    """ INPUT
    # single sentence
    sentence = 'When typing this command for the first time, a pretrained model and its tokenizer are downloaded and cached. We will look at both later on, but as an introduction the tokenizer’s job is to preprocess the text for the model, which is then responsible for making predictions. The pipeline groups all of that together, and post-process the predictions to make them readable. For instance:'
    
    # multiple sentences
    sentence = ['hi, my name is ailever.', 'what is your name?']
    """

    sentiment = pipeline('sentiment-analysis')
    results = sentiment(sentence)
    
    for i, result in enumerate(results):
        print(f"[{i}] label: {result['label']}, with score: {round(result['score'], 4)}")

    return results


def answer(question, context):
    """ INPUT
    question = 'What is extractive question answering?'
    context = r'Extractive Question Answering is the task of extracting an answer from a text given a question. An example of a question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune a model on a SQuAD task, you may leverage the examples/question-answering/run_squad.py script.'

    """
    answer = pipeline("question-answering")
    result = answer(question, context)
    
    print(f"Answer: '{result['answer']}', score: {round(result['score'], 4)}, start: {result['start']}, end: {result['end']}")
    return result


def summary(article):
    """ INPUT
    article = 'New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York. A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband. Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other. In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage. Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the 2010 marriage license application, according to court documents. Prosecutors said the marriages were part of an immigration scam. On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further. After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002. All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say. Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages. Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted. The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali. Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force. If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.'
    """

    summary = pipeline("summarization")
    result = summary(article, max_length=130, min_length=30, do_sample=False)

    print(result)
    return result


def generation(sentence="As far as I am concerned, I will"):
    """ INPUT
    sentence = 'As far as I am concerned, I will'
    """
    
    generation = pipeline("text-generation")
    result = generation(sentence, max_length=50, do_sample=False)

    print(result)
    return result

