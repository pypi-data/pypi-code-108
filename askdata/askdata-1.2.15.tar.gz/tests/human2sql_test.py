from pandas import DataFrame
from askdata.human2sql import ask_dataframe

if __name__ == "__main__":
    df = DataFrame({
        "player": ["Ciro Ronaldo", "Ciro Immobile", "Ciro Immobile", "Ciro Immobile", "Ciro Immobile",
                   "Sergej Milinkovic-Savic", "Andreas Pereira"],
        "plate": ["FK224MB", "SL490BN", "WE580PW", "DO392BC", "DO392BC", "DO392BC", "BN489AS"],
        "cellular": ["3315602894", "3343284552", "3385694126", "3481369874", "3481369874", "3481369874", "3337123698"],
        "address": ["Via degli Alagno 150", "Piazza di Spagna 1", "Viale Marconi 384", "Viale Marconi 384",
                    "Viale Marconi 384", "Largo Argentina 42", "Via Lanfranco Maroi 64"],
        "revenue": [1000, 70, 1, 1238494, 402920, 8422, 23894],
        "goals": [23, 10, 20, 30, 40, 10, 15],
        "date": ["2020/10/1", "2020/11/12", "2020/10/03", "2020/10/04", "2021/11/05", "2021/11/06", "2021/10/06"]
    })
    query = "please give me revenue for player of October 2020"
    response_df = ask_dataframe(df, query)
    print(response_df[0])
