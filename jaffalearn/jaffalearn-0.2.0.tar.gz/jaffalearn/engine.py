from collections import defaultdict

from tqdm import tqdm

import torch


class Engine:
    def __init__(self, system, device=None):
        self.system = system
        self.device = device
        self.callbacks = []
        self.epoch = 0

    def fit(self,
            loader_train,
            loader_val=None,
            n_epochs=1,
            relative=False,
            show_progress=False,
            ):
        if relative:
            n_epochs = self.epoch + n_epochs

        # Ensure training is done on the specified device
        if loader_val is None:
            self.to_device(loader_train)
        else:
            self.to_device(loader_train, loader_val)

        for self.epoch in range(self.epoch, n_epochs):
            # Display a progress bar during training if requested
            if show_progress:
                loader = tqdm(loader_train)
                loader.set_description(f'Epoch {self.epoch}')
            else:
                loader = loader_train

            self.training_loop(loader)
            if loader_val is not None:
                self.validation_loop(loader_val)

            if self.system.scheduler is not None:
                self.system.scheduler.step()

            for callback in self.callbacks:
                callback()

    def test(self, loader, show_progress=False):
        self.to_device(loader)

        # Display a progress bar during the test loop if requested
        if show_progress:
            loader = tqdm(loader)

        self.test_loop(loader)
        for callback in self.callbacks:
            callback()

    def predict(self, loader, show_progress=False):
        self.to_device(loader)

        # Display a progress bar during prediction if requested
        if show_progress:
            loader = tqdm(loader)

        return self.inference_loop(loader)

    def training_loop(self, loader):
        self.system.train()

        outputs = defaultdict(list)
        for batch in loader:
            self.system.zero_grad(set_to_none=True)

            # Forward pass
            output = self.system.training_step(batch)
            if output is None:
                continue

            # Backward pass
            if isinstance(output, torch.Tensor):
                output.backward()
            elif isinstance(output, dict):
                output.pop('loss').backward()
                _accumulate(outputs, output)
            else:
                name = f'{type(self.system).__name__}.training_step'
                raise RuntimeError(f'Invalid return type for {name}')

            # Update weights using optimizer
            self.system.optimizer.step()

        self.system.training_epoch_end(**outputs)

    def validation_loop(self, loader):
        self.inference_loop(loader, self.system.validation_step,
                            self.system.validation_epoch_end)

    def test_loop(self, loader):
        self.inference_loop(loader, self.system.test_step,
                            self.system.test_epoch_end)

    def inference_loop(self, loader, step_fn=None, end_fn=None):
        if step_fn is None:
            step_fn = self.system
        if end_fn is None:
            end_fn = self.system.collate

        self.system.eval()

        outputs = defaultdict(list)
        with torch.no_grad():
            for batch in loader:
                output = step_fn(batch)
                if output is None:
                    continue

                if isinstance(output, torch.Tensor):
                    outputs['y_pred'].append(output)
                elif isinstance(output, dict):
                    _accumulate(outputs, output)
                else:
                    raise RuntimeError('Invalid return type for `step_fn`')

        return end_fn(**outputs)

    def serialize(self):
        checkpoint = {
            'epoch': self.epoch,
            'rng_state': torch.get_rng_state(),
        }
        if torch.cuda.is_available():
            checkpoint['cuda_rng_state'] = torch.cuda.get_rng_state()

        checkpoint.update(self.system.serialize())

        return checkpoint

    def restore_state(self, checkpoint):
        self.epoch = checkpoint['epoch'] + 1

        torch.set_rng_state(checkpoint['rng_state'].cpu())
        if checkpoint.get('cuda_rng_state') is not None \
                and torch.cuda.is_available():
            torch.cuda.set_rng_state(checkpoint['cuda_rng_state'].cpu())

        self.system.restore_state(checkpoint)

    def to_device(self, *others):
        device = self.device
        if device is not None:
            self.system.to(device)
            for other in others:
                other.to(device)


def _accumulate(accumulation, new_dict):
    for k, v in new_dict.items():
        accumulation[k].append(v)
    return accumulation
