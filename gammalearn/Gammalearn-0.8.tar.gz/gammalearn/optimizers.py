import torch.optim as optim
import torch


def load_sgd(net, parameters):
    """
    Load the SGD optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'learning_rate' in parameters.keys(), 'Missing learning rate for the optimizer !'
    assert 'weight_decay' in parameters.keys(), 'Missing weight decay for the optimizer !'
    assert 'nesterov' in parameters.keys(), 'Missing nesterov for the optimizer !'
    assert 'momentum' in parameters.keys(), 'Missing momentum for the optimizer !'
    return optim.SGD(net.parameters(),
                     lr=parameters['learning_rate'],
                     weight_decay=parameters['weight_decay'],
                     nesterov=parameters['nesterov'],
                     momentum=parameters['momentum'])


def load_adam(net, parameters):
    """
    Load the Adam optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'learning_rate' in parameters.keys(), 'Missing learning rate for the optimizer !'
    kwargs = {'lr': parameters['learning_rate']}
    if 'weight_decay' in parameters.keys():
        kwargs['weight_decay'] = parameters['weight_decay']
    if 'amsgrad' in parameters.keys():
        kwargs['amsgrad'] = parameters['amsgrad']

    return optim.Adam(net.parameters(), **kwargs)


def load_rmsprop(net, parameters):
    """
    Load the RMSprop optimizer
    Parameters
    ----------
    net (nn.Module): the network of the experiment
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    assert 'learning_rate' in parameters.keys(), 'Missing learning rate for the optimizer !'
    kwargs = {'lr': parameters['learning_rate']}
    if 'weight_decay' in parameters.keys():
        kwargs['weight_decay'] = parameters['weight_decay']
    if 'alpha' in parameters.keys():
        kwargs['alpha'] = parameters['alpha']

    return optim.RMSprop(net.parameters(), **kwargs)


def freeze(net, parameters):
    """
    Freeze the network parameters
    Parameters
    ----------
    net (nn.Module): the network or the subnetwork (e.g. feature)
    parameters (dict): a dictionary describing the parameters of the optimizer

    Returns
    -------
    the optimizer
    """
    for p in net.parameters():
        p.requires_grad = False

    return None


#############################
# Regularization strategies #
#############################


def l1(net):
    """
    Simple L1 penalty.
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for param in net.parameters():
        penalty += torch.norm(param, 1)

    return penalty


def l2(net):
    """
    Simple L2 penalty.
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for param in net.parameters():
        penalty += torch.norm(param, 2)**2

    return penalty / 2


def elastic(net):
    """
    Elastic penalty (L1 + L2).
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """

    return l1(net) + l2(net)


def srip(net):
    """
    Spectral Restricted Isometry Property (SRIP) regularization penalty. See https://arxiv.org/abs/1810.09102
    Parameters
    ----------
    net (nn.Module): the network.

    Returns
    -------
    the penalty
    """
    penalty = 0
    for n, W in net.named_parameters():
        if W.ndimension() >= 2:
            # print('{} : {}'.format(n, W.ndimension()))
            cols = W[0].numel()
            rows = W.shape[0]
            w1 = W.view(-1, cols)
            wt = torch.transpose(w1, 0, 1)
            if rows > cols:
                m = torch.matmul(wt, w1)
                ident = torch.eye(cols, cols, device=W.device)
            else:
                m = torch.matmul(w1, wt)
                ident = torch.eye(rows, rows, device=W.device)

            w_tmp = m - ident
            b_k = torch.rand(w_tmp.shape[1], 1, device=W.device)

            v1 = torch.matmul(w_tmp, b_k)
            norm1 = torch.norm(v1, 2)
            v2 = torch.div(v1, norm1)
            v3 = torch.matmul(w_tmp, v2)

            penalty += (torch.norm(v3, 2))**2
    return penalty
