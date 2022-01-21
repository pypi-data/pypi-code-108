class DataPlotter(object):
    def plot_data(self, x, y, y_pred, current_epoch: int, global_step: int):
        raise NotImplementedError("plot_data method must be implemented.")
