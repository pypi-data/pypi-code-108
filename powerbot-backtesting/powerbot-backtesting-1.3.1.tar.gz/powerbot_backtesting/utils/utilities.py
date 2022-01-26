import pandas as pd

from powerbot_backtesting.utils.helpers_general import _find_cache


def generate_input_file(orderbooks: dict[str, pd.DataFrame]):
    """
    Generates a csv file to put positions and signals into to use with the BacktestingAlgo

    Args:
        orderbooks (dict{key: DataFrame}): Dictionary of order books

    Returns:
        csv file
    """
    # File creation
    input_file = pd.DataFrame({"contract_id": [*orderbooks]})
    input_file["position"] = ""
    input_file.set_index("contract_id", inplace=True)

    # Caching
    cache_path = _find_cache().joinpath("analysis_input")
    cache_path.mkdir(parents=True, exist_ok=True)

    # File name
    f_count = 1
    while cache_path.joinpath(f"backtesting_input_{f_count}.csv").exists():
        f_count += 1
    input_file.to_csv(cache_path.joinpath(f"backtesting_input_{f_count}.csv"), sep=";")
