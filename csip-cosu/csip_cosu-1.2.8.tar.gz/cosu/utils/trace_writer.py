from typing import Dict, List, Set, Tuple

TraceList = List[Tuple[Dict[str, float], float]]


def write_run_trace(file: str, run_trace: TraceList, num_steps: int = 0, num_runs_per_step: int = 0) -> None:
    if num_steps <= 0 or num_runs_per_step <= 0:
        write_raw_run_trace(file, run_trace)
        return

    variable_list: List[str] = create_variable_list(run_trace)
    split_trace_list: List[List[TraceList]] = split_trace(
        run_trace, num_steps, num_runs_per_step)
    try:
        with open(file, "w") as writer:
            writer.write("@T,trace\n")
            writer.write("@H,cost,round,step,{}\n".format(",".join(variable_list)))
            round: int = 1
            for round_list in split_trace_list:
                step: int = 1
                for step_list in round_list:
                    for param, cost in step_list:
                        record = ",{},{},{}".format(cost, round, step)
                        for name in variable_list:
                            if name in param:
                                record += ",{}".format(param[name])
                            else:
                                record += ","
                        writer.write(record + "\n")
                    step = step + 1
                round = round + 1
    except IOError:
        print("Failed to write to file {}".format(file))


def write_raw_run_trace(file: str, run_trace: TraceList) -> None:
    variable_list: List[str] = create_variable_list(run_trace)
    try:
        with open(file, "w") as writer:
            writer.write("@T,trace\n")
            writer.write("@H,cost,{}\n".format(",".join(variable_list)))
            for param, cost in run_trace:
                record = ",{}".format(cost)
                for name in variable_list:
                    if name in param:
                        record += ",{}".format(param[name])
                    else:
                        record += ","
                writer.write(record + "\n")
    except IOError:
        print("Failed to write to file {}".format(file))


def create_variable_list(run_trace: TraceList) -> List[str]:
    variable_set: Set[str] = set()
    for param, cost in run_trace:
        for name in param.keys():
            variable_set.add(name)
    return list(variable_set)


def split_trace(run_trace: TraceList, num_steps: int, num_runs_per_step: int) -> List[List[TraceList]]:
    step = 1
    i = 0
    split_trace_list: List[List[TraceList]] = list()
    step_list: List[TraceList]
    while i < len(run_trace):
        if step == 1:
            step_list = list()
            split_trace_list.append(step_list)

        endpoint = i + num_runs_per_step
        if endpoint > len(run_trace):
            endpoint = len(run_trace)

        step_list.append(run_trace[i:endpoint])
        i = endpoint
        step = step + 1
        if step > num_steps:
            step = 1

    return split_trace_list
