"""
Libreria per fare grafici di fit e tabelle LaTeX a partire da dati raccolti in un file Excel
TODO: graph log
"""
__docformat__="numpy"

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import pandas as pd
from pint import UnitRegistry
import re

def _tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def _converti_latex(text):
    ureg = UnitRegistry()
    um=re.search(r"\[(.+)\]",text).group(1) #ricerca unità di misura
    u=ureg.Unit(um)
    um_tex=f"{u:Lx}"
    new_text=text.replace("["+um+"]","[]") #cancellazione unità di misure
    new_text=_tex_escape(new_text) 
    new_text=new_text.replace("[]",r"\(\left["+um_tex+r"\right]\)") #inserimento siunix dopo aver fatto l'escape dei caratteri speciali per latex
    return new_text

def fit(file_name,file_result,variabile_x,variabile_y,sigma_y,f_fit,titoli_p_latex,
    split_graphs=False,
    titoli=["",""],
    xlabel=None,
    ylabel=None,
    chi=True,
    x_chi=0,
    y_chi=0,
    post_decimal_chi=0,
    log_to_file=False,
    path=".",
    xscale="linear",
    yscale="linear",
    griglia_fit={
        "which" : "both",
        "ls" : "dashed",
        "color" : "powderblue"
    },
    griglia_residui={
        "which" : "both",
        "ls" : "dashed",
        "color" : "powderblue"
    },
    style_fit={"fmt" : "."},
    fit_line_color="darkorange",
    style_residui={"fmt" : "."},
    res_line_color="navy",
    pad_percent=0.10,
    foglio="Foglio1",
    funzioni_modifica=[None, None],
    fig_dimension=(6.24136,4.4)
):
    """
    funzione che genera:

        - un pdf:

            - contenente il grafico di fit e quello dei residui

        - un file LaTeX:
        
            - contenete i parametri ottimali del fit
    
    Parameters
    -------------------------
    file_name : str
        nome file excel da elaborare

    file_result : str
        nome da dare ai pdf generati

    variable_x, variable_y, sigma_y : str
        ogni parametro contine il valore dell'header della colonna del foglio excel da cui prendere i dati
        (deve contenere l'unità di misura nel formato: "[unità di misura]")

    f_fit : func
        funzione che rappresenta la curva g(x) utilizzata nel fit.
        il primo parametro di f è x, gli altri sono tutti i parametri che definiscono g(x)

    titoli_p_latex : list
        elenco dei nomi dei parametri ottimali che vengono ricavati dal fit
        verranno usati come contenuto della cella del titolo di una tabella latex contenente i valori numerici dei parametri

    split_graphs: bool, optional
        se True la funzione genera due file separati per il grafico dei residui e il grafico di fit (default: False)

    titoli : list, optional
        lista di due elementi con i due titoli per i due grafici, il primo è il grafico di fit e il secondo è il grafico dei 
        residui (default: ["",""])
    
    xlabel, ylabel : str, optional
        stringa da utilizzare per la generazione dei label degli assi del grafico, usare notazione LaTeX. Se None allora i nomi delle colonne
        del file excel verranno utilizzati, convertendoli automaticamente in LaTeX ed interpretando um tra parentesi quadre (default: None)

    chi : bool, optional
        se True allora sul grafico viene mostrato il valore del chi quadro e il numero di gradi di libertà (default: True)

    x_chi, y_chi : int, optional
        coordinate del punto in cui scrivere il valore del chi quadro e il numero di gradi di libertà (default: 0, 0 --> primo punto del plot)

    post_decimal_chi : int, optional
        numero di cifre dopo la virgola con cui scrivere il valore del chi quadro (default: 0)

    log_to_file : bool, optional
        if True le informazioni sulla bontà del grafico sono messe in un file di testo. If False le informazioni possono essere lette in console. (default: False)

    path : str, optional
        path directory di partenza (default: ".")

    xscale, yscale : str, optional
        tipo di scala da utilizzare per l'asse corrispondente del grafico (default: 'linear')

    griglia_fit, griglia_residui : dict, optional
        dizionario contenente i parametri opzionali da passare a pyplot.grid() (default: {"which" : "both", "ls" : "dashed", "color" : "powderblue"})

    style_fit, style_residui : dict, optional
        dizionario contenente i parametri opzionali da passare a pyplot.errorbar() (default: {"fmt" : "."})

    fit_line_color, res_line_color : str, optional
        colori da applicare alla curva di fit e alla linea dello zero nel grafico dei residui (default: "darkorange", "navy")

    pad_pecent: float, optional
        dimensione percentuale dello spazio del grafico in più rispetto al minimo necessario a contenere i dati (default: 0.10)

    foglio : str, optional
        nome del foglio da cui prendere i dati (default: "Foglio1")

    funzioni_modifica : list, optional
        lista contenete due funzioni (default: [None, None]). Entrambe devono avere 6 parametri: (fig, asse, x, y, params, data). La prima funzione verrà applicata al
        grafico di fit, la seconda al grafico dei residui, i parametri che vengono passati sono:

        - fig, asse: oggetti restituiti da pyplot.subplots() relativi al grafico che si vuole modificare
            
        - x, y: vettori contenenti il set di dati di cui si sta creando il grafico
            
        - params: vettore dei parametri ottimali di fit
            
        - data: panda dataframe rappresentante il foglio Excel

    fig_dimensions : (float, float), optional
        tupla contenete le dimensioni (x,y) dell'immagine creata in inches (default: (6.24136,4.5))

    Examples
    ----------------------------
    >>> def retta(x,m,q):
            return m*x+q
        result="nome grafico"
        file="moto_rettilineo.xlsx"
        var_x="tempi [s]"
        var_y="posizioni [cm]"
        sigma_y="incertezza posizione [cm]"
        titoli=["\\hat{m} [\\si{\\centi\\metre\\per\\second}]", "\\hat{q} [\\si{\\centi\\metre}]"]
        result=fit(file,result,var_x,var_y,sigma_y,retta,titoli)
        if result:
            print(result)
    
    oppure usando la funzione del pendolo fisico che utilizza un solo parametro:
    >>> def pendolo(d, l):
            return 2.0 * np.pi * np.sqrt((l**2.0 / 12.0 + d**2.0) / (9.81 * d))
        result="nome grafico"
        file="pendolo.xlsx"
        var_x="lunghezze [m]"
        var_y="tempi_medi [s]"
        sigma_y="sigma_t [s]"
        titoli_pendolo=["\\hat{l} [\\si{\\metre}]"]
        result=fit(file,result,var_x,var_y,sigma_y,pendolo,titoli_pendolo)
        if result:
            print(result)

    oppure passando parametri opzionali:
    >>> def retta(x,m,q):
            return m*x+q
        my_path="C:\\Users\\cremo\\Documents\\Università\\Relazioni"
        res="nome grafico"
        file="moto_rettilineo.xlsx"
        x="tempi [s]"
        y="posizioni [cm]"
        s_y="incertezza posizione [cm]"
        titoli=["\\hat{m} [\\si{\\centi\\metre\\per\\second}]", "\\hat{q} [\\si{\\centi\\metre}]"]
        asse_y="log"
        style={"ls" : "dotted", "color" : "green"}
        result=fit(file,res,x,y,s_y,retta,titoli,yscale=asse_y,griglia_fit=style, path=my_path)
        if result:
            print(result)
    """

    #verifica parametri
    if "[" not in variabile_x or "]" not in variabile_x: 
        return "Manca unità di misura in x"
    if "[" not in variabile_y or "]" not in variabile_y:
        return "Manca unità di misura in y"
    if "[" not in sigma_y or "]" not in sigma_y:
        return "Manca unità di misura in dy"
    if not file_name:
        return "specificare nome file excel"
    if not file_result:
        return "specificare nome file pdf risultato (senza .pdf)"

    #lettura file
    excel = pd.read_excel(path+'\\'+file_name, sheet_name=foglio)

    t=[e for e in excel[variabile_x].tolist() if e == e] #NaN != NaN quindi il test impedisce di scrivere i valori nulli
    y=[e for e in excel[variabile_y].tolist() if e == e]
    dy=[e for e in excel[sigma_y].tolist() if e == e]

    #fit
    popt, pcov = curve_fit(f_fit,t,y,sigma=dy)
    chi=sum(np.power((y-f_fit(np.array(t),*popt)), 2)/np.power(dy,2))
    gradi_di_liberta=len(t)-len(popt)
    chi_rid=chi/gradi_di_liberta

    #valutazione grafico
    sopra_fit=0
    sotto_fit=0
    lontano_fit=0
    for element_y, element_t, element_dy in zip(y, t, dy):
        if element_y-f_fit(element_t,*popt)>0:
            sopra_fit+=1
        if element_y-f_fit(element_t,*popt)<0:
            sotto_fit+=1
        if np.absolute(element_y-f_fit(element_t,*popt))>element_dy:
            lontano_fit+=1

    frase_log=[]
    frase_log.append("Numero di punti sopra alla funzione di best fit: "+str(sopra_fit)+"\n"+"Numero di punti sotto alla funzione di best fit: "+str(sotto_fit))
    frase_log.append("(expected: " + str(len(t)/2)+")")
    frase_log.append("Numero di punti che distano dal grafico n>1 barre di errore: "+str(lontano_fit)+" (expected: "+str(0.32 *len(t))+")")
    if log_to_file:
        with open(path+"\\"+file_result+"_fit_log.txt", 'w') as fit_log:
            fit_log.write("\n".join(frase_log))
            fit_log.close()
    else:
        print(frase_log[0])
        print(frase_log[1])
        print(frase_log[2])

    #scrittura file_tabella.tex
    empty_space="&"*(len(popt)-1)+r"\\" #linee vuote per aggiungere spazio prima e dopo in ogni riga
    lines_prima=[r"\renewcommand{\arraystretch}{0.5}",r"\begin{table}[h!]",r"\centering"]
    colonne="c"*len(popt) #colonne centrate in numero variaabile a seconda di len(popt)
    lines_prima.append(r"\begin{tabular}{"+colonne+r"}")
    lines_prima.append(r"\toprule")
    lines_prima.append(empty_space)
    lines_prima.append(r" & ".join(titoli_p_latex)+r" \\")#titoli
    lines_prima.append(empty_space)
    lines_prima.append(r"\midrule")
    lines_prima.append(empty_space)
    string_popt=[str(i_opt) for i_opt in popt] #numeri convertiti in stringa
    lines_prima.append(r" & ".join(string_popt)+r" \\") #valori
    lines_prima.append(empty_space)
    lines_dopo=[r"\bottomrule",r"\end{tabular}",r"\caption{risultati del fit}",r"\end{table}",r"\renewcommand{\arraystretch}{1}"]
    lines_prima.extend(lines_dopo)    
    
    with open(path+"\\"+file_result+"_tabella.tex", 'w') as tabella_tex:
        tabella_tex.write("\n".join(lines_prima))
        tabella_tex.close()

    #disegno grafico 
    plt.rcParams["figure.figsize"] = fig_dimension #dimensioni

    pad=(max(t)-min(t))*pad_percent #aggiunta spazio
    lim_inf=min(t)-pad if min(t)-pad>0 else 0
    lim_sup=max(t)+pad

    a1 = np.linspace(lim_inf, min(t), 1001) #separazione per tratteggio
    a2 = np.linspace(min(t), max(t), 1001)
    a3 = np.linspace(max(t), lim_sup, 1001)

    plt.rcParams.update({"text.usetex" : True,   #LaTeX
        "font.family": "computer modern",
        "text.latex.preamble": "\n".join([ # plots will use this preamble
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{siunitx}",
        r"\usepackage{amsmath}",
        ])})
    
    if not xlabel:
        xlabel=_converti_latex(variabile_x)

    if not ylabel:
        ylabel=_converti_latex(variabile_y)

    if x_chi==0:
        x_chi=t[0]*1.1
    if y_chi==0:
        y_chi=y[0]*1.1

    if split_graphs:
        fig1, ax1 = plt.subplots(1, 1)
        fig2, ax2 = plt.subplots(1, 1)
    else:
        fig1, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [4, 1]}, sharex=True)

    #grafico di fit
    ##aspetto
    ax1.set_title(titoli[0])
    ax1.set_xscale(xscale)
    ax1.set_yscale(yscale)
    ax1.grid(**griglia_fit)
    ##plot
    ax1.errorbar(t, y, dy, **style_fit)
    ax1.plot(a1, f_fit(a1, *popt), linestyle="dashed", color=fit_line_color) # l'asterisco indica che popt viene espanso passando i parametri singolarmente e non come lista.
    ax1.plot(a2, f_fit(a2, *popt), color=fit_line_color)
    ax1.plot(a3, f_fit(a3, *popt), linestyle="dashed", color=fit_line_color)
    ##adjust limits
    ax1.set_xlim(min(a1),max(a3))

    #residui
    ##aspetto
    ax2.set_title(titoli[1])
    ax2.margins(0, 0.2)
    ax2.set_xscale(xscale)
    ax2.set_yscale(yscale)
    ax2.grid(**griglia_residui)
    ##plot
    y_res=y-f_fit(np.array(t), *popt)  # l'asterisco indica che popt viene espanso passando i parametri singolarmente e non come lista.
    ax2.errorbar(t, y_res, dy, **style_residui)
    ax2.plot(a1, a1-a1, color=res_line_color)
    ax2.plot(a2, a2-a2, color=res_line_color)
    ax2.plot(a3, a3-a3, color=res_line_color)
    ##adjust for x axi symmetry
    low, high = ax2.get_ylim() 
    bound = max(abs(low), abs(high)) # find the new limits
    ax2.set_ylim(-bound, bound) # set new limits
    ax2.set_xlim(min(a1),max(a3))  

    #chi^2
    if chi:
        ax1.text(x_chi,y_chi,r"$$\frac{\chi^2}{\nu}="+str(round(chi_rid,post_decimal_chi))+r"$$")

    fig1.supxlabel(xlabel, y=0.05)
    fig1.supylabel(ylabel, x=0.03)

    if funzioni_modifica[0]:
        funzioni_modifica[0](fig1, ax1,t,y,popt, excel)  

    if split_graphs:
        
        fig2.supxlabel(xlabel, y=0.05)
        fig2.supylabel(ylabel, x=0.03)

        if funzioni_modifica[1]:
            funzioni_modifica[1](fig2, ax2,t,y,popt, excel)   
        
        fig2.tight_layout()
        fig2.canvas.manager.set_window_title("Residui") 

        fig2.savefig(path+'\\'+file_result+'_residui.pdf')
    else:
        if funzioni_modifica[1]:
            funzioni_modifica[1](fig1, ax2,t,y,popt, excel)     

    fig1.tight_layout()
    fig1.canvas.manager.set_window_title("Grafico") 
    fig1.savefig(path+'\\'+file_result+'.pdf')
    plt.show()

def tabella(file_name,file_result,
    path=".",
    colonne=None,
    foglio="Foglio1",
    index_on=False,
    formatter=None,
    column_align=None,
    table_caption="Tabella di dati"
):
    """
    funzione che crea una tabella in LaTeX a partire da dati in un file Excel.

    le unità di misura devono essere riportaate per ogni colonna tra parentesi quadre.

    Parameters
    -------------------------
    file_name : str
        nome file excel da elaborare

    file_result : str
        nome da dare alle tabelle generate

    path : str, optional
        path directory di partenza (default: ".")

    colonne : list, optional
        lista contenete i valori degli header delle colonne del foglio excel da cui prendere i dati
        (default: None, che corrisponde a selezionare tutte le colonne)

    foglio: str, optional
        indica il nome del foglio da cui prendere i dati (default: "Foglio1")

    index_on: bool, optional
        decide se mostrare l'indice di riga (default: False)

    formatter: dict, optional
        dizionario contenente laa funzione per formattare i valori della tabella. I valori del dizionario usano come chiave il nome
        della colonna e come volore la funzione che formatta(default: None)

    column_align: str, optional
        stringa contenete il formato delle colonne, il formato stringa deve essere stile LaTeX, ad esempio "||l|c|r||" (default: None)

    table_caption: str, optional
        label da posizionare sotto alla tabella generata (default: "Tabella di dati")

    Examples
    ----------------------------
    >>> my_path="C:\\Users\\cremo\\Documents\\Università\\Relazioni\\pendolo_json"
        file_result="nome_grafico"
        file_tabella="nome_tabella"
        file_name="prova_json.xlsx"
        formati={
            "tempi_medi [s]": "{:.4f}".format,
            "sigma_t [s]": "{:.9f}".format,
            "lunghezze [m]": "{:.3f}".format
        }
        result=js.tabella(file_name,file_tabella, formatter=formati, path=my_path)
        if result:
            print(result)
    """
    #lettura file
    excel = pd.read_excel(path+'\\'+file_name, sheet_name=foglio, usecols=colonne)
    #scrittura file
    ##creazione header in stile LaTeX
    my_header=[]
    for col in excel.columns:
        new_col=_converti_latex(col)
        my_header.append(new_col)

    latex = excel.to_latex(
        buf=path+"\\"+file_result+".tex",
        index=index_on,
        formatters=formatter,
        column_format=column_align,
        decimal=",", #separatore decimale
        longtable=True, #tipo di tabella
        caption=table_caption,
        na_rep="", #carattere da mettere nei posti NaN
        header=my_header,
        escape=False #impedisce escape latex special char
    )


