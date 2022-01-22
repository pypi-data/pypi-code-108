"""
Create a dataset in json file format from PGN files.
"""

import os
import chess.pgn
import pandas as pd
import argparse

def readPgn(path):
    train_df = pd.DataFrame(columns=["text", "labels"])
    for file in os.listdir(path):
        if file.endswith(".pgn"):
            file_path = os.path.join(path, file)
            train_df = train_df.append(importPgn(file_path), ignore_index=True)
    train_df.to_json(os.path.join(path, "fen.json"))

def importPgn(pgn_file):
    pgn = open(pgn_file)
    train_df = pd.DataFrame(columns=["text", "labels"])

    # Python>=3.8
    # while game := chess.pgn.read_game(pgn):
    while True:
        try:
            game = chess.pgn.read_game(pgn)
            result = game.headers["Result"]
            if result == "1-0":
                result_label = 2
            elif result == "0-1":
                result_label = 1
            else:
                result_label = 0

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                train_df = train_df.append({"text": board.fen(), "labels": result_label}, ignore_index=True)
        except:
            break
    return train_df

    def create_json_for_train_and_eval(self, train_pgn="train-pgn", eval_pgn="eval-pgn"):
        # Preparing train data
        readPgn(train_pgn)

        # Preparing eval data
        readPgn(eval_pgn)


def console_script():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--path", dest='path', default="train-pgn", type=str, help="Directory from which you want to read.  Default is train-pgn.")
    args = parser.parse_args()

    readPgn(args.path)

if __name__ == "__main__":
    console_script()
