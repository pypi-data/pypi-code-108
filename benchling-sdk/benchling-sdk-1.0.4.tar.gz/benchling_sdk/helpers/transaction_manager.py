from contextlib import AbstractContextManager
from typing import Any, Iterable, List

from typing_extensions import Protocol


class CreateTransactionCall(Protocol):
    """Provide an interface for creating a new transaction."""

    def __call__(self) -> str:
        """Create a transaction and return a string handle (i.e., id)."""
        ...


class CommitTransactionCall(Protocol):
    """Provide an interface for committing a transaction."""

    def __call__(self, transaction_id: str) -> str:
        """Commit an existing transaction in progress."""
        ...


class AbortTransactionCall(Protocol):
    """Provide an interface for aborting an uncommitted transaction."""

    def __call__(self, transaction_id: str) -> str:
        """Abort an existing transaction which has not been committed."""
        ...


class AppendRowsCall(Protocol):
    """Provide an interface for appending rows to an existing transaction."""

    def __call__(self, transaction_id: str, rows: Iterable[Any]) -> List[str]:
        """Append rows to an existing transaction and return the updated full list."""
        ...


class TransactionManager(AbstractContextManager):
    """
    Manage transactions in Benchling in a generic way across various implementations.

    Implements a Python context manager, managing state for a Benchling transaction. Upon
    exit, the transaction manager will automatically attempt to commit the transaction. If
    an error is encountered, it will instead abort the transaction.
    """

    _transaction_id: str
    _create_transaction_call: CreateTransactionCall
    _commit_transaction_call: CommitTransactionCall
    _abort_transaction_call: AbortTransactionCall
    _append_row_call: AppendRowsCall

    def __init__(
        self,
        create_transaction_call: CreateTransactionCall,
        commit_transaction_call: CommitTransactionCall,
        abort_transaction_call: AbortTransactionCall,
        append_row_call: AppendRowsCall,
    ):
        """
        Initialize TransactionManager.

        :param create_transaction_call: A function for creating a transaction
        :param commit_transaction_call: A function for committing a transaction
        :param abort_transaction_call: A function for aborting a transaction
        :param append_row_call: A function for appending a row to an existing transaction
        """
        self._create_transaction_call = create_transaction_call
        self._commit_transaction_call = commit_transaction_call
        self._abort_transaction_call = abort_transaction_call
        self._append_row_call = append_row_call

    def __enter__(self) -> "TransactionManager":
        self._transaction_id = self._create_transaction_call()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        if exc_type:
            self.abort()
        else:
            self.commit()
        return True

    def append(self, row: Any) -> List[str]:
        """Append a single row to an existing transaction and return the full list of pending rows."""
        return self.extend([row])

    def extend(self, rows: Iterable[Any]) -> List[str]:
        """Append multiple rows to an existing transaction and return the full list of pending rows."""
        return self._append_row_call(transaction_id=self._transaction_id, rows=rows)

    def commit(self) -> str:
        """Commit the transaction in progress."""
        return self._commit_transaction_call(self._transaction_id)

    def abort(self) -> str:
        """Abort the transaction in progress."""
        return self._abort_transaction_call(self._transaction_id)
