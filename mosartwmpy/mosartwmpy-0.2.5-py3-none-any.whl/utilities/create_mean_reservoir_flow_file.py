import click
import xarray as xr
import pandas as pd


# @click.command()
# @click.option(
#     '--flow-path',
#     type=click.Path(
#         file_okay=False,
#         dir_okay=True,
#         writable=False,
#         resolve_path=True,
#     ),
#     prompt='What is the path to a folder containing mosartwmpy output for which to find the monthly average flow?',
#     help="""Path to the directory containing mosartwmpy output for finding monthly average flow."""
# )
# @click.option(
#     '--reservoir-parameter-path',
#     default='./input/reservoirs/grand_reservoir_parameters.nc',
#     type=click.Path(
#         file_okay=True,
#         dir_okay=False,
#         writable=False,
#         resolve_path=True,
#     ),
#     prompt='What is the path to the reservoir parameter file used for the mean flow simulation?',
#     help="""Path to the reservoir parameter file."""
# )
def create_mean_reservoir_flow_file(
    flow_path,
    reservoir_parameter_path,
    output_path='average_monthly_flow.parquet',
    flow_key='channel_inflow',
    flow_time_key='time',
    grand_id_key='GRAND_ID',
    grid_cell_index_key='GRID_CELL_INDEX',
):

    flow = xr.open_mfdataset(f"{flow_path}/*.nc")[[flow_key]].load()
    mean_monthly_flow = flow[flow_key].groupby(f'{flow_time_key}.month').mean()
    flow.close()
    del flow

    reservoir_params = xr.open_dataset(reservoir_parameter_path).load()
    grand_id = reservoir_params[grand_id_key].values.flatten()
    grid_cell_index = reservoir_params[grid_cell_index_key].values.flatten()
    reservoir_params.close()
    del reservoir_params

    # find the monthly average flow at dam locations
    columns = mean_monthly_flow.shape[-1]
    flow_rows = []
    for i in range(grand_id.size):
        for m, mean_flow in enumerate(
            mean_monthly_flow.values[:, grid_cell_index[i] // columns, grid_cell_index[i] % columns]
        ):
            flow_rows.append({
                'GRAND_ID': grand_id[i],
                'MONTH_INDEX': m,
                'MEAN_FLOW': mean_flow,
            })
    flow = pd.DataFrame(flow_rows).sort_values(['GRAND_ID', 'MONTH_INDEX'])

    flow.to_parquet(output_path)

    return flow
