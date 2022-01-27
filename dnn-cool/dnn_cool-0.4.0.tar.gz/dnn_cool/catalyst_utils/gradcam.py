import numpy as np
import torch
from catalyst.contrib.tools.tensorboard import SummaryWriter


class GuidedGradCamPublisher:

    def __init__(self, model, layer, forward_pass_preprocess):
        from captum.attr import GuidedGradCam
        self.model = model
        self.grad_cam = GuidedGradCam(model=model, layer=layer)
        self.forward_pass_preprocess = forward_pass_preprocess

    def __call__(self, writer: SummaryWriter, tag, sample, idx):
        if not isinstance(sample, torch.Tensor):
            sample = torch.tensor(sample)
        if sample.shape[-1] == 3:  # H, W, C
            sample = sample.permute(2, 0, 1)
        X = self.forward_pass_preprocess(sample).unsqueeze(0)
        device = next(self.model.parameters()).device
        X = X.to(device)
        logits = self.model(X)
        res = self.grad_cam.attribute(X, logits.argmax())
        res = res.squeeze().detach().cpu().numpy()
        res = (res - res.min())
        res /= res.max()
        res = (res * 255).astype(np.uint8)
        writer.add_image(f"{tag}_gradcam", res, global_step=idx)


