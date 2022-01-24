from kapla.services.errors import InvalidSubjectError


def match_subject(msg_subject: str, subscription_subject: str) -> bool:
    """An approximative attempt to write a function to check if a message should be processed by a subscription"""
    if not msg_subject:
        raise InvalidSubjectError("Subject cannot be empty")
    if not subscription_subject:
        raise InvalidSubjectError("Subscription subject cannot be empty")
    # By default consider there is no match
    matches = False
    # If both subjects are equal
    if msg_subject == subscription_subject:
        return True
    # Split subjects using "." character
    msg_tokens = msg_subject.split(".")
    total_tokens = len(msg_tokens)
    subscription_tokens = subscription_subject.split(".")
    # Iterate over each token
    for idx, token in enumerate(subscription_tokens):
        # If tokens are equal, let's continue
        try:
            if token == msg_tokens[idx]:
                # Continue the iteration on next token
                continue
        except IndexError:
            # If tokens are different, then let's continue our if/else statements
            matches = False
        # If token is ">"
        if token == ">":
            # Then we can return True
            return True
        # If token is "*"
        if token == "*":
            matches = True
            # Continue the iteration on next token
            continue
        # Else it means that subject do not match
        else:
            return False
    if token == "*" and (total_tokens - idx) > 1:
        return False
    return matches
