import torch


# TODO fix gradnorm for lightning
# see manual optimization in lightning doc
# def training_step_gradnorm(module, batch):
#     """
#     The training operations for one batch for vanilla mt learning
#     Parameters
#     ----------
#     module: LightningModule
#     batch
#
#     Returns
#     -------
#
#     """
#     # Load data
#     images = batch['image']
#     labels = batch['label']
#
#     output = module.net(images)
#
#     # Compute loss
#     losses, loss_data = module.experiment.compute_loss(output, labels)
#     losses = torch.stack(losses)
#     weighted_losses = losses * module.experiment.compute_loss.weights
#     loss = torch.sum(weighted_losses)
#
#     # Compute gradients w.r.t. the parameters of the network
#     loss.backward(retain_graph=True)
#
#     module.experiment.compute_loss.zero_grad()
#
#     # Compute the inverse training rate
#     loss_ratio = losses / module.experiment.compute_loss.initial_losses.to(module.experiment.device)
#     average_loss_ratio = loss_ratio.mean()
#     inverse_training_rate = loss_ratio / average_loss_ratio
#
#     # Compute the gradient norm of each task and the mean gradient norm
#     gw_norms = []
#     if hasattr(module.net, 'feature'):
#         common_layer = getattr(module.net.feature, module.experiment.compute_loss.last_common_layer)
#     else:
#         common_layer = getattr(module.net, module.experiment.compute_loss.last_common_layer)
#     for i, loss in enumerate(losses):
#         gw = torch.autograd.grad(loss,
#                                  common_layer.parameters(),
#                                  retain_graph=True)[0]
#         gw_norms.append(torch.norm(gw * module.experiment.compute_loss.weights[i]))
#     gw_mean = torch.stack(gw_norms).mean().to(module.experiment.device)
#
#     # Gradient target (considered as a constant term)
#     grad_target = gw_mean * (inverse_training_rate**module.experiment.compute_loss.alpha)
#     grad_target = grad_target.clone().detach().requires_grad_(False)
#     # Gradnorm loss
#     gradnorm_loss = torch.sum(torch.abs(torch.stack(gw_norms).to(module.experiment.device) - grad_target))
#
#     module.experiment.compute_loss.weights.grad = torch.autograd.grad(gradnorm_loss,
#                                                                       module.experiment.compute_loss.weights)[0]
#
#     for _, optim in experiment.optimizers.items():
#         if optim is not None:
#             optim.step()
#
#     # Normalize gradient weights
#     module.experiment.compute_loss.weights.data = module.experiment.compute_loss.weights * (module.experiment.compute_loss.task_number /
#                                                                               module.experiment.compute_loss.weights.sum())
#
#     return output, labels, loss_data


def training_step_mt(module, batch):
    """
    The training operations for one batch for vanilla mt learning
    Parameters
    ----------
    module: LightningModule
    batch

    Returns
    -------

    """
    # Load data
    images = batch['image']
    labels = batch['label']

    output = module.net(images)

    # Compute loss
    loss, loss_data = module.experiment.compute_loss(output, labels)
    loss = torch.stack(loss).sum()
    if module.experiment.regularization is not None:
        loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

    return output, labels, loss_data, loss


def training_step_ae(module, batch):
    """
    The training operations for one batch for autoencoder
    Parameters
    ----------
    module: LightningModule
    batch

    Returns
    -------

    """
    # Load data
    images = batch['image']

    output = module.net(images)

    # Compute loss
    loss = module.experiment.compute_loss(output, images)

    if module.experiment.regularization is not None:
        loss += module.experiment.regularization['function'](module.net) * module.experiment.regularization['weight']

    loss = loss.mean()

    return None, None, {'autoencoder': loss.detach().item()}, loss


def training_step_mt_gradient_penalty(module, batch):
    """
    The training operations for one batch for vanilla mt learning with gradient penalty
    Parameters
    ----------
    module: LightningModule
    batch
        Returns
        -------

        """

        # Load data
    images = batch['image']
    labels = batch['label']

    images.requires_grad = True

    output = module.net(images)

    # Compute loss
    loss, loss_data = module.experiment.compute_loss(output, labels)
    loss = torch.stack(loss).sum()
    if module.experiment.regularization is not None:
        gradient_x = torch.autograd.grad(loss, images, retain_graph=True)[0]
        penalty = torch.mean((torch.norm(gradient_x.view(gradient_x.shape[0], -1), 2, dim=1) - 1) ** 2)
        loss += penalty * module.experiment.regularization['weight']

    return output, labels, loss_data, loss


def eval_step_mt(module, batch):
    """
    The validating operations for one batch
    Parameters
    ----------
    module
    batch

    Returns
    -------

    """
    images = batch['image']
    labels = batch['label']

    output = module.net(images)
    # Compute loss and quality measures
    loss, loss_data = module.experiment.compute_loss(output, labels)
    loss = torch.stack(loss).sum()

    return output, labels, loss_data, loss


def eval_step_ae(module, batch):
    """
    The training operations for one batch for autoencoder
    Parameters
    ----------
    module: LightningModule
    batch

    Returns
    -------

    """
    # Load data
    images = batch['image']

    output = module.net(images)

    # Compute loss
    loss = module.experiment.compute_loss(output, images)
    loss = loss.mean()

    return None, None, {'autoencoder': loss.detach().item()}, loss


def test_step_mt(module, batch):
    """
    The validating operations for one batch
    Parameters
    ----------
    module
    batch

    Returns
    -------

    """
    images = batch['image']

    output = module.net(images)

    return output, batch['dl1_params']


def test_step_ae(module, batch):
    """
    The validating operations for one batch
    Parameters
    ----------
    module
    batch

    Returns
    -------

    """
    images = batch['image']

    output = module.net(images)

    # Compute loss
    loss = module.experiment.compute_loss(output, images)
    # We reduce the loss per image
    loss = torch.mean(loss, dim=tuple(torch.arange(loss.dim())[1:]))

    return {'ae_error': loss.detach()}, batch['dl1_params']
