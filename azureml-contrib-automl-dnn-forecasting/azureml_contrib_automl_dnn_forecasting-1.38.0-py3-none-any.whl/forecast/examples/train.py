import argparse
import datetime
import enum
import functools
import json
import math
import os
from typing import Optional, Sequence

import numpy as np
import torch
from torch.utils.data import DataLoader

import forecast.callbacks as cbs
from forecast.data import FUTURE_DEP_KEY_UTF
from forecast.data.sources import ElectricityDataSource, GEFCom14DataSource, GithubDataSource, M5DataSource
from forecast.forecaster import Forecaster
from forecast.losses import QuantileLoss
import forecast.metrics
from forecast.models.backbone import MultilevelType
from forecast.models.canned import create_tcn_quantile_forecaster
from forecast.models.premix import EmbeddingConfig


def create_model(dset_channels: int, horizon: int, args, embeddings: Optional[Sequence[EmbeddingConfig]]):
    return create_tcn_quantile_forecaster(
        input_channels=dset_channels,
        num_cells_per_block=args.num_cells,
        multilevel=MultilevelType[args.multilevel.upper()].name,
        horizon=horizon,
        num_quantiles=len(args.quantiles),
        num_channels=args.num_channels,
        num_blocks=args.depth,
        dropout_rate=args.dropout,
        init_dilation=args.init_dilation,
        embeddings=embeddings,
    )


DSET_MAP = {
    "github": GithubDataSource,
    "gefcom14": GEFCom14DataSource,
    "electricity": ElectricityDataSource,
    "m5": M5DataSource,
}


class EmbedMode(enum.Enum):
    NONE = "none"
    ONE_HOT = "one-hot"
    SQUARE_ROOT = "square-root"
    THIRD_ROOT = "third-root"
    FOURTH_ROOT = "fourth-root"

    def channel_count(self, num_vals: int) -> int:
        if self in (EmbedMode.NONE, EmbedMode.SQUARE_ROOT, EmbedMode.THIRD_ROOT, EmbedMode.FOURTH_ROOT):
            return 1
        elif self is EmbedMode.ONE_HOT:
            return num_vals
        else:
            raise RuntimeError

    def embed_dim(self, num_vals: int) -> Optional[int]:
        if self in (EmbedMode.NONE, EmbedMode.ONE_HOT):
            return None
        elif self is EmbedMode.SQUARE_ROOT:
            return math.ceil(num_vals**(1.0/2.0))
        elif self is EmbedMode.THIRD_ROOT:
            return math.ceil(num_vals**(1.0/3.0))
        elif self is EmbedMode.FOURTH_ROOT:
            return math.ceil(num_vals**(1.0/4.0))

    @property
    def is_embedded(self) -> bool:
        return self in (EmbedMode.SQUARE_ROOT, EmbedMode.THIRD_ROOT, EmbedMode.FOURTH_ROOT)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dataset", choices=DSET_MAP.keys(), required=True)

    parser.add_argument("--num-cells", type=int, required=True)
    parser.add_argument("--depth", type=int, required=True)
    parser.add_argument("--dropout", type=float, required=True)
    parser.add_argument("--init-dilation", type=int, default=2)
    parser.add_argument("--log-num-channels", type=int)
    parser.add_argument("--num-channels", type=int)
    parser.add_argument("--quantiles", type=float, nargs="+", default=[0.1, 0.25, 0.5, 0.75, 0.9])
    parser.add_argument("--multilevel", type=str, default="cell")
    parser.add_argument("--embedding", choices=[e.value for e in EmbedMode], default=EmbedMode.ONE_HOT.value)

    parser.add_argument("--log-lr", type=float)
    parser.add_argument("--lr", type=float)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-epochs", type=int, default=2000)

    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--reduction-factor", type=float, default=0.5)
    parser.add_argument("--min-improvement", type=float, default=0.001)

    parser.add_argument("--out-dir", type=str, required=True)
    parser.add_argument("--out-dir-pattern", type=str)
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--train-workers", type=int, default=4)
    parser.add_argument("--val-workers", type=int, default=4)

    args = parser.parse_args()
    if not args.lr:
        args.lr = 10 ** args.log_lr
    if not args.num_channels:
        args.num_channels = 2 ** args.log_num_channels
    if args.out_dir_pattern:
        formatted_pattern = args.out_dir_pattern.format(**{k.replace("_", "-"): v for k, v in vars(args).items()})
        args.out_dir = os.path.join(args.out_dir, formatted_pattern)
        os.makedirs(args.out_dir)

    med_index = args.quantiles.index(0.5)

    source = DSET_MAP[args.dataset](eager=True)
    dc = source.get_config()

    embed_mode = EmbedMode(args.embedding)
    n_channels = (
        dc.feature_channels +
        dc.forecast_channels +
        sum(embed_mode.channel_count(enc.num_vals) for enc in dc.encodings) -
        len(dc.encodings)
    )
    embeddings = []
    for enc in dc.encodings:
        if embed_mode.is_embedded and enc.num_vals > 2:
            # embedding indices work on NN feature index -- cat(past_regressand, past_regressor)
            # encoding indices work on past_regressor feature index
            # all of the datasets currently only have 1 target (hence the 1+)
            # TODO: fixme once num_targets is added to the dataset class
            embeddings.append(EmbeddingConfig(1 + enc.feature_index, enc.num_vals, embed_mode.embed_dim(enc.num_vals)))
    if not embeddings:
        embeddings = None

    # create the model
    model = create_model(n_channels, source.DEFAULT_FORECAST_HORIZON, args, embeddings)
    model.to(args.device)

    # get the datasets
    batch_tf = source.batch_transform
    train_ds, val_ds = source.get_dataset(window_size=model.receptive_field, one_hot=embed_mode is EmbedMode.ONE_HOT)

    while True:
        try:
            train_dl = DataLoader(
                train_ds,
                args.batch_size,
                shuffle=True,
                pin_memory=True,
                num_workers=args.train_workers,
            )
            val_dl = DataLoader(
                val_ds,
                args.batch_size,
                shuffle=False,
                pin_memory=True,
                num_workers=args.val_workers,
            )

            opt = torch.optim.Adam(model.parameters(), lr=args.lr)
            lr_sched = torch.optim.lr_scheduler.ReduceLROnPlateau(
                opt,
                patience=int(args.patience / 2),
                factor=args.reduction_factor
            )
            loss = QuantileLoss(args.quantiles)
            metrics = [
                forecast.metrics.LearningRate(opt),
                forecast.metrics.SMAPE(med_index, forecast.metrics.MetricMode.TRAIN_VAL),
            ]
            callbacks = [
                cbs.TensorboardCallback(args.out_dir, report_every=10),
                cbs.NotFiniteTrainingLossCallback(5),
                cbs.CheckpointCallback(1, args.out_dir, args=vars(args)),
                cbs.ReduceLROnPlateauCallback(lr_sched, "loss"),
                cbs.EarlyStoppingCallback(args.patience, args.min_improvement, metric=None)  # TODO: NRMSE
            ]

            forecaster = Forecaster(model, args.device, metrics, callbacks, batch_tf)
            forecaster.fit(train_dl, loss, opt, args.num_epochs, val_dl)
            break
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"OOM at batch size {args.batch_size}. Halving batch size and learning rate.")
                args.batch_size //= 2
                args.lr /= 2
            else:
                raise

    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    to_save = {
        "hyperparameters": vars(args),
        "model": model.state_dict(),
    }
    torch.save(
        to_save,
        os.path.join(args.out_dir, f"checkpoint-{args.dataset}-{now}.pt")
    )

    compute_metrics(forecaster, val_dl, args.quantiles, args.out_dir)


def compute_metrics(forecaster, dataloader, quantiles, out_dir):
    from forecast.metrics.functional import smape

    preds = forecaster.predict(dataloader)
    act = np.concatenate([b[FUTURE_DEP_KEY_UTF].to('cpu').numpy() for b in dataloader], axis=0)
    med_ind = quantiles.index(0.5)

    def medify(f):
        @functools.wraps(f)
        def wrapper(p, a):
            return float(f(p[med_ind], a))
        return wrapper

    metrics = {
        "smape": medify(smape),
        "nrmse": medify(nrmse),
        "deepar_nrmse": medify(deepar_nrmse),
        "nmae": medify(nmae),
        "mape": medify(mape),
        "medape": medify(medape),
        "eva": medify(eva),
    }
    for q in [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]:
        # handle late binding with bound_q
        metrics[f"quantile_{q}"] = lambda p, a, bound_q=q: float(qloss(p[med_ind], a, bound_q))

    out = {n: m(preds, act) for n, m in metrics.items()}

    with open(os.path.join(out_dir, "metrics.json"), "w") as f:
        json.dump(out, f)

    with open(os.path.join(out_dir, "predictions.json"), "w") as f:
        to_save = {f"quantile_{q}": p.tolist() for q, p in zip(quantiles, preds)}
        to_save["actual"] = act.tolist()
        json.dump(to_save, f)


def nrmse(pred, act):
    p = pred.reshape(-1)
    a = act.reshape(-1)
    return np.sqrt(np.mean(((p - a) / a)**2))


def deepar_nrmse(preds, act):
    return np.sqrt(((preds.squeeze() - act.squeeze())**2).mean()) / np.abs(act).mean()


def nmae(preds, act):
    return np.abs(preds.squeeze() - act.squeeze()).mean() / np.abs(act).mean()


def mape(preds, act):
    return 100 * np.abs((preds.squeeze() - act.squeeze()) / act.squeeze()).mean()


def medape(preds, act):
    return 100 * np.median(np.abs((preds.squeeze() - act.squeeze()) / act.squeeze()))


def eva(preds, act):
    return 1 - np.var(preds.squeeze() - act.squeeze()) / np.var(act.squeeze())


def qloss(preds, act, q):
    p = preds.reshape(-1)
    a = act.reshape(-1)
    num = np.sum(q * (a - p) * (a > p) + (1-q) * (p - a) * (p > a))
    denom = np.abs(a).sum()
    return 2 * num / denom


if __name__ == "__main__":
    main()
