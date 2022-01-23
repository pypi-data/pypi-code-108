"""
Nozomi
Secret Module
author: hugh@blinkybeach.com
"""
import hmac
from nozomi.ancillary.immutable import Immutable
from nozomi.errors.error import NozomiError
from nozomi.security.salt import Salt
from nozomi.data.datastore import Datastore
from typing import TypeVar, Type, Optional
from nozomi.data.query import Query


try:
    import argon2
except ImportError:
    argon2 = None


T = TypeVar('T', bound='Secret')


class Secret:
    """
    A user's secret passphrase
    """
    _Q_RETRIEVE_BY_EMAIL = Query.optionally_from_file(
        'queries/secret/retrieve.sql'
    )

    def __init__(
        self,
        salt: Salt,
        hashed_passphrase: str,
        agent_id: Optional[int] = None
    ) -> None:

        assert isinstance(hashed_passphrase, str)
        assert isinstance(salt, Salt)
        if agent_id is not None:
            assert isinstance(agent_id, int)
        self._hashed_passphrase = hashed_passphrase
        self._salt = salt
        self._agent_id = agent_id

        return

    hashed_passphrase = Immutable(lambda s: s._hashed_passphrase)
    salt = Immutable(lambda s: s._salt.string)
    agent_id = Immutable(lambda s: s._agent_id)

    Q_RETRIEVE_BY_EMAIL = Immutable(lambda s: s._load_query(
        s._Q_RETRIEVE_BY_EMAIL
    ))

    @classmethod
    def _load_query(cls: Type[T], query: Optional[Query]) -> Query:
        if query is None:
            raise NotImplementedError('A required SQL query is not implemented')
        return query

    @classmethod
    def _compute_hash(cls: Type[T], raw_secret: str, salt: Salt) -> str:
        """Compute the Argon2 hash of the provided secret"""
        assert isinstance(raw_secret, str)
        assert isinstance(salt, Salt)
        if not argon2:
            raise NotImplementedError('Install argon2-cffi')
        computed_hash = argon2.low_level.hash_secret(
            raw_secret.encode('utf-8'),
            salt=salt.utf8_bytes,
            time_cost=10,
            memory_cost=64,
            parallelism=2,
            hash_len=48,
            type=argon2.Type.I
        ).decode('utf-8')
        return computed_hash

    def matches(self, plaintext_passphrase: str) -> bool:
        """Return True if the supplied passphrase matches this one"""
        supplied_secret_hash = self._compute_hash(
            plaintext_passphrase,
            self._salt
        )
        comparison = hmac.compare_digest(
            supplied_secret_hash,
            self._hashed_passphrase
        )
        assert isinstance(comparison, bool)
        if comparison is True:
            return True
        return False

    @classmethod
    def create_from_plaintext(cls: Type[T], plaintext_passphrase: str) -> T:
        """Return a Secret created based on the supplied plaintext passphrase"""
        if not isinstance(plaintext_passphrase, str):
            raise NozomiError('Passphrases must be strings', 400)
        salt = Salt.create()
        hashed_passphrase = cls._compute_hash(plaintext_passphrase, salt)
        return cls(salt, hashed_passphrase)

    @classmethod
    def retrieve_for_user_id(cls: Type[T], user_id: int) -> T:
        """Return the active Secret for a given User ID"""
        raise NotImplementedError

    @classmethod
    def retrieve_for_email(
        cls: Type[T],
        email: str,
        datastore: Datastore
    ) -> Optional[T]:
        """
        Return the active Secret for a given email, or None if no secret exists
        for said email
        """
        assert isinstance(datastore, Datastore)
        assert isinstance(email, str)

        arguments = {'email_address': email.lower()}
        query = cls._load_query(cls._Q_RETRIEVE_BY_EMAIL)
        result = query.execute(datastore, arguments)
        if result is None:
            return None

        return cls(
            salt=Salt(salt_b64_string=result['salt']),
            hashed_passphrase=result['secret_hash'],
            agent_id=result['agent']
        )

    def __str__(self) -> str:
        return self.hashed_passphrase
