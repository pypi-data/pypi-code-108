from askdata import nlg
import pandas as pd

if __name__ == "__main__":
    df = pd.DataFrame()
    df = df.append({'player': 'Cristiano Ronaldo', 'goals': 10, 'team': 'Juventus'}, ignore_index=True)
    df = df.append({'player': 'Roberto Baggio', 'goals': 2, 'team': 'Milan'}, ignore_index=True)
    examples = [["player=Cristiano Ronaldo, goals=3, team=Juventus", "Cristiano Ronaldo scored 3 goals for Juventus"]]
    res = nlg.text_from_data(df=df, examples=examples, fit_items=False, max_tokens=64)
    print(res)
