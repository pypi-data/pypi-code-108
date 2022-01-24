import torch
import torch.nn.functional as F


def random_sample(logits):
    """

    :param logits: shape (num_tokens,)
    :return: token probabilities, token index

    """
    p = F.softmax(logits, dim=0)

    token_idx = torch.multinomial(p.view(-1), 1)
    token_p = torch.gather(p, 0, token_idx)

    return token_p.squeeze(), token_idx.squeeze()


def select_max(logits):
    p = F.softmax(logits, dim=0)

    token_p, token_idx = torch.max(p, dim=0)

    return token_p, token_idx


def filter_top_p(logits, top_p=0.9):
    """

    :param logits: shape (num_tokens,)
    :param top_p:

    :return: kept logits, kept token indices
    """

    p = F.softmax(logits, dim=0)

    p_sorted, sorted_indices = torch.sort(p, dim=0, descending=True)
    p_cumulative = torch.cumsum(p_sorted, dim=0)

    to_keep = p_cumulative <= top_p

    # Always keep at least one, so shift to the right
    to_keep[1:] = to_keep[:-1].clone()
    to_keep[0] = True

    to_keep = sorted_indices[to_keep]

    return logits[to_keep], to_keep


def filter_top_k(logits, top_k=20):
    """

    :param logits: shape (num_tokens,)
    :param top_k:

    :return: kept logits, kept token indices
    """

    p = F.softmax(logits, dim=0)

    p_sorted, sorted_indices = torch.sort(p, dim=0, descending=True)

    to_keep = sorted_indices[:top_k]

    return logits[to_keep], to_keep
