import torch
import numpy as np
import pandas as pd

# Función para obtener suma de embeddings:
def sum_embeddings(row, model, tokenizer, column):
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # and move our model over to the selected device
    model.to(device)
    
    encoding = tokenizer(str(row[column]), return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encoding.to(device))
    return list(np.array(outputs[0][0].sum(axis=0).cpu()))

# Función para obtener promedio de embeddings:
def mean_embeddings(row, model, tokenizer, column):
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # and move our model over to the selected device
    model.to(device)
    
    encoding = tokenizer(str(row[column]), return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encoding.to(device))
    return list(np.array(outputs[0][0].mean(axis=0).cpu()))

# Función para obtener embedding CLS:
def cls_embeddings(row, model, tokenizer, column):
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # and move our model over to the selected device
    model.to(device)
    
    encoding = tokenizer(str(row[column]), return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encoding.to(device))
    return list(np.array(outputs[1][0].cpu()))

def sentence_encoder(df, model, tokenizer, column = 'text', encoding = 'mean'):
    
    if encoding == 'sum':
        # Aplicar función suma a cada frase del dataframe:
        sum_df = df.apply(sum_embeddings, model=model, tokenizer= tokenizer, column=column, axis = 1, result_type='expand')
        sum_df = sum_df.rename(columns ={col: 'SUM_{}'.format(col) for col in sum_df.columns})
        result_df = df.join(sum_df)
        return(result_df)
    
    elif encoding == 'mean':
        # Aplicar función suma a cada frase del dataframe:
        mean_df = df.apply(mean_embeddings, model=model, tokenizer= tokenizer, column=column, axis = 1, result_type='expand')
        mean_df = mean_df.rename(columns ={col: 'MEAN_{}'.format(col) for col in mean_df.columns})
        result_df = df.join(mean_df)
        return(result_df)
    
    elif encoding == 'cls':
        # Aplicar función suma a cada frase del dataframe:
        cls_df = df.apply(cls_embeddings, model=model, tokenizer= tokenizer, column=column, axis = 1, result_type='expand')
        cls_df = cls_df.rename(columns ={col: 'CLS_{}'.format(col) for col in cls_df.columns})
        result_df = df.join(cls_df)
        return(result_df)
        
    else:
        print('Encoding {} not found'.format(encoding))
        return()
    
    
    
    