import sympy
from poisson_approval.utils.computation_engine import computation_engine
from poisson_approval.utils.Util import isnan, isneginf


# noinspection NonAsciiCharacters
class Asymptotic:
    r"""An asymptotic development of the form :math:`\exp(\mu n + \nu \log n + \xi + o(1))`.

    Parameters
    ----------
    mu : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Coefficient of the term in `n` (called "magnitude").
    nu : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Coefficient of the term in `log n`.
    xi : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Constant coefficient.
    symbolic : bool
        Whether the computations are symbolic or numeric.

    Attributes
    ----------
    μ : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Alias for `mu`.
    ν : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Alias for `nu`.
    ξ : Number, ``sp.nan``, ``np.nan``, ``- sp.oo`` or ``- np.inf``
        Alias for `xi`.

    Notes
    -----
    If a coefficient is ``sp.nan`` or ``np.nan``, it means that it is not known. In contrast, a coefficient 0 means
    that there is no corresponding term in the asymptotic development.

    If (and only if) the event is impossible, then ``mu = nu = xi = - inf``. It is possible to use either ``- sp.oo``
    or ``- np.inf``.

    Examples
    --------

        >>> import math
        >>> asymptotic = Asymptotic(mu=-1 / 9, nu=-1 / 2, xi=-1 / 2 * math.log(8 * math.pi / 9))
        >>> print(asymptotic)
        exp(- 0.111111 n - 0.5 log n - 0.513473 + o(1))
        >>> asymptotic.mu
        -0.1111111111111111
        >>> asymptotic.nu
        -0.5
        >>> asymptotic.xi
        -0.5134734250965083
    """

    def __init__(self, mu, nu, xi, symbolic=False):
        self.symbolic = symbolic
        self.ce = computation_engine(symbolic)
        self.mu = self.μ = mu
        self.nu = self.ν = nu
        self.xi = self.ξ = xi

    def __repr__(self):
        """Repr.

        Returns
        -------
        str

        Examples
        --------
            >>> import numpy as np
            >>> from fractions import Fraction
            >>> Asymptotic(mu=- Fraction(1, 10), nu=np.nan, xi=3)
            Asymptotic(mu=Fraction(-1, 10), nu=nan, xi=3)
        """
        return 'Asymptotic(mu=%r, nu=%r, xi=%r)' % (self.mu, self.nu, self.xi)

    def __str__(self):
        """Str.

        Returns
        -------
        str

        Examples
        --------
            >>> import numpy as np
            >>> from fractions import Fraction
            >>> print(Asymptotic(mu=- Fraction(1, 10), nu=np.nan, xi=3))
            exp(- 0.1 n + ? log n + 3 + o(1))
            >>> print(Asymptotic(mu=-np.inf, nu=-np.inf, xi=-np.inf))
            exp(- inf)
        """
        if self.symbolic:
            return self._str_symbolic()
        else:
            return self._str_approximate()

    def _str_symbolic(self):
        """Auxiliary function for __str__
        """
        if isneginf(self.mu) and isneginf(self.nu) and isneginf(self.xi):
            return "exp(- inf)"

        def nice(x, suffix):
            # x : coefficient, suffix : `sympy` expression
            if isnan(x):
                return ' + ?' if suffix == 1 else ' + ? %s' % suffix
            if x == 0:
                return ''
            a = sympy.symbols('a')
            result = str(a + x * suffix)
            assert result[0:2] == 'a '
            return result[1:]

        n = sympy.symbols('n')
        s = nice(self.mu, n) + nice(self.nu, sympy.log(n)) + nice(self.xi, 1)
        s += ' + o(1)'
        if s[1] == "+":
            s = s[3:]
        else:
            s = s[1:]
        s = "exp(%s)" % s
        return s

    def _str_approximate(self):
        """Auxiliary function for __str__
        """
        if isneginf(self.mu) and isneginf(self.nu) and isneginf(self.xi):
            return "exp(- inf)"

        def nice(x, suffix):
            if isnan(x):
                return ' + ? ' + suffix if suffix else ' + ?'
            if x == 1 and suffix:
                return ' + ' + suffix
            if x == -1 and suffix:
                return ' - ' + suffix
            if x == 0:
                return ''
            result = ' + ' if x > 0 else ' - '
            result += "{:.6g}".format(float(abs(x)))
            result += ' ' + suffix if suffix else ''
            return result

        s = nice(self.mu, 'n') + nice(self.nu, 'log n') + nice(self.xi, '')
        s += ' + o(1)'
        if s[1] == "+":
            s = s[3:]
        else:
            s = s[1:]
        s = "exp(%s)" % s
        return s

    def _repr_pretty_(self, p, cycle):  # pragma: no cover - Only for notebooks
        # https://stackoverflow.com/questions/41453624/tell-ipython-to-use-an-objects-str-instead-of-repr-for-output
        p.text(str(self) if not cycle else '...')

    @property
    def limit(self):
        """Number, nan or infinity : Limit when `n` tends to infinity.

        Examples
        --------
            >>> import numpy as np
            >>> Asymptotic(mu=-1, nu=0, xi=0).limit
            0
            >>> Asymptotic(mu=1, nu=0, xi=0).limit
            inf
            >>> Asymptotic(mu=-1, nu=np.nan, xi=np.nan).limit
            0
            >>> Asymptotic(mu=0, nu=-1, xi=np.nan).limit
            0

        `nan` means that the limit is unknown:

            >>> Asymptotic(mu=0, nu=0, xi=np.nan).limit
            nan
        """
        if isnan(self.mu):
            return self.ce.nan
        elif self.mu > 0:
            return self.ce.inf
        elif self.mu < 0:
            return 0
        else:  # self.mu == 0
            if isnan(self.nu):
                return self.ce.nan
            elif self.nu > 0:
                return self.ce.inf
            elif self.nu < 0:
                return 0
            else:  # self.nu == 0:
                if isnan(self.xi):
                    return self.ce.nan
                else:
                    return self.ce.simplify(self.ce.exp(self.xi))

    def __mul__(self, other):
        """Multiplication of two asymptotic developments.

        Parameters
        ----------
        other: `Asymptotic` or Number.

        Returns
        -------
        product : Asymptotic
            The product of this asymptotic development and `other`.

        Examples
        --------
            >>> import numpy as np
            >>> print(Asymptotic(mu=42, nu=51, xi=69) * Asymptotic(mu=1, nu=2, xi=3))
            exp(43 n + 53 log n + 72 + o(1))
            >>> print(Asymptotic(mu=42, nu=51, xi=69) * Asymptotic(mu=1, nu=np.nan, xi=np.nan))
            exp(43 n + ? log n + ? + o(1))
        """
        if not isinstance(other, Asymptotic):
            other = Asymptotic(0, 0, self.ce.log(other), symbolic=self.symbolic)

        def my_addition(x, y):
            return 0 if self.ce.look_equal(x, -y) else self.ce.simplify(x + y)

        return Asymptotic(my_addition(self.mu, other.mu),
                          my_addition(self.nu, other.nu),
                          my_addition(self.xi, other.xi),
                          symbolic=self.symbolic)

    def __rmul__(self, other):
        """
        Examples
        --------
            >>> print(3 * Asymptotic(mu=42, nu=51, xi=69))
            exp(42 n + 51 log n + 70.0986 + o(1))
        """
        return self * other

    def __truediv__(self, other):
        """Division of two asymptotic developments.

        Parameters
        ----------
        other: `Asymptotic` or Number.

        Returns
        -------
        ratio : Asymptotic
            The division of this asymptotic development by `other`.

        Examples
        --------
            >>> import numpy as np
            >>> print(Asymptotic(mu=42, nu=51, xi=69) / Asymptotic(mu=1, nu=2, xi=3))
            exp(41 n + 49 log n + 66 + o(1))
            >>> print(Asymptotic(mu=42, nu=51, xi=69) / Asymptotic(mu=1, nu=np.nan, xi=np.nan))
            exp(41 n + ? log n + ? + o(1))
            >>> print(1 / Asymptotic(mu=42, nu=51, xi=69))
            exp(- 42 n - 51 log n - 69 + o(1))
            >>> print(Asymptotic(mu=42, nu=51, xi=69) / 2)
            exp(42 n + 51 log n + 68.3069 + o(1))
        """
        if not isinstance(other, Asymptotic):
            other = Asymptotic(0, 0, self.ce.log(other), symbolic=self.symbolic)
        return self * Asymptotic(- other.mu, - other.nu, - other.xi, symbolic=self.symbolic)

    def __rtruediv__(self, other):
        if not isinstance(other, Asymptotic):
            other = Asymptotic(0, 0, self.ce.log(other), symbolic=self.symbolic)
        return other / self

    # noinspection PyTypeChecker
    def __add__(self, other):
        """Addition of two asymptotic developments.

        Parameters
        ----------
        other: `Asymptotic` or Number.

        Returns
        -------
        sum : Asymptotic
            The sum of this asymptotic development and `other`.

        Examples
        --------
            >>> print(Asymptotic(mu=42, nu=2, xi=69) + Asymptotic(mu=1, nu=51, xi=3))
            exp(42 n + 2 log n + 69 + o(1))
            >>> print(Asymptotic(mu=42, nu=2, xi=69) + Asymptotic(mu=42, nu=51, xi=3))
            exp(42 n + 51 log n + 3 + o(1))
            >>> print(Asymptotic(mu=42, nu=2, xi=4) + Asymptotic(mu=42, nu=2, xi=3))
            exp(42 n + 2 log n + 4.31326 + o(1))
            >>> print(Asymptotic(mu=42, nu=2, xi=4) + 1)
            exp(42 n + 2 log n + 4 + o(1))
            >>> print(1 + Asymptotic(mu=42, nu=2, xi=4))
            exp(42 n + 2 log n + 4 + o(1))
            >>> print(Asymptotic(mu=42, nu=2, xi=69) + Asymptotic(mu=41.99999999, nu=51, xi=3))
            exp(42 n + 51 log n + 3 + o(1))
        """
        if not isinstance(other, Asymptotic):
            other = Asymptotic(0, 0, self.ce.log(other), symbolic=self.symbolic)
        if isnan(self.mu) or isnan(other.mu):
            return Asymptotic(self.ce.nan, self.ce.nan, self.ce.nan, symbolic=self.symbolic)
        elif self.ce.look_equal(self.mu, other.mu):
            mu = max(self.mu, other.mu)
            if isnan(self.nu) or isnan(other.nu):
                return Asymptotic(mu, self.ce.nan, self.ce.nan, symbolic=self.symbolic)
            elif self.ce.look_equal(self.nu, other.nu):
                nu = max(self.nu, other.nu)
                xi = self.ce.simplify(self.ce.log(self.ce.exp(self.xi) + self.ce.exp(other.xi)))
                return Asymptotic(mu, nu, xi, symbolic=self.symbolic)
            elif self.nu > other.nu:
                return Asymptotic(mu, self.nu, self.xi, symbolic=self.symbolic)
            else:
                return Asymptotic(mu, other.nu, other.xi, symbolic=self.symbolic)
        elif self.mu > other.mu:
            return Asymptotic(self.mu, self.nu, self.xi, symbolic=self.symbolic)
        else:
            return Asymptotic(other.mu, other.nu, other.xi, symbolic=self.symbolic)

    def __radd__(self, other):
        return self + other

    def look_equal(self, other, *args, **kwargs):
        """Test if two asymptotic developments can reasonably be considered as equal.

        Parameters
        ----------
        other : Asymptotic
        *args
            Cf. ``math.isclose``.
        **kwargs
            Cf. ``math.isclose``.

        Returns
        -------
        bool
            True if this asymptotic development can reasonably be considered equal to `other`. Cf.
            :meth:`ComputationEngine.look_equal`.

        Examples
        --------
            >>> Asymptotic(mu=1, nu=2, xi=3).look_equal(
            ...     Asymptotic(mu=0.999999999999, nu=2.00000000001, xi=3))
            True
        """
        if not isinstance(other, Asymptotic):
            return False
        some_coefficients_are_nan = (isnan(self.mu) or isnan(self.nu) or isnan(self.xi)
                                     or isnan(other.mu) or isnan(other.nu) or isnan(other.xi))
        if some_coefficients_are_nan:
            raise ValueError('Can assert look_equal only when all coefficients are known.')
        return (self.ce.look_equal(self.mu, other.mu, *args, **kwargs)
                and self.ce.look_equal(self.nu, other.nu, * args, ** kwargs)
                and self.ce.look_equal(self.xi, other.xi, *args, **kwargs))

    @classmethod
    def poisson_value(cls, tau, k, symbolic=False):
        """Asymptotic development of ``P(X = k)``, where ``X ~ Poison(tau * n)``.

        Parameters
        ----------
        tau : Number
            The parameter of the Poisson distribution is ``tau * n``, where `n` tends to infinity.
        k : int
            The desired value in ``P(X = k)``.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X = k)``, where ``X ~ Poison(tau * n)``.

        Examples
        --------
            >>> print(Asymptotic.poisson_value(tau=0, k=0))
            exp(o(1))
            >>> print(Asymptotic.poisson_value(tau=0, k=1))
            exp(- inf)
            >>> print(Asymptotic.poisson_value(tau=1, k=1))
            exp(- n + log n + o(1))
            >>> from math import log
            >>> Asymptotic.poisson_value(tau=2, k=3).look_equal(
            ...     Asymptotic(mu=-2, nu=3, xi=3 * log(2) - log(6)))
            True
        """
        ce = computation_engine(symbolic)
        if tau == 0:
            if k == 0:
                return cls(mu=0, nu=0, xi=0, symbolic=symbolic)
            else:
                return cls(mu=-ce.inf, nu=-ce.inf, xi=-ce.inf, symbolic=symbolic)
        return cls(mu=- tau, nu=k, xi=ce.simplify(k * ce.log(tau) - ce.log(ce.factorial(k))), symbolic=symbolic)

    @classmethod
    def poisson_x1_eq_x2_plus_k(cls, tau_1, tau_2, k, symbolic=False):
        """Asymptotic development of ``P(X_1 = X_2 + k)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        k : int
            The desired value in ``P(X_1 = X_2 + k)``.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 = X_2 + k)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import log, pi, sqrt
            >>> print(Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=0, tau_2=1, k=0))
            exp(- n + o(1))
            >>> print(Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=0, tau_2=1, k=1))
            exp(- inf)
            >>> print(Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=1, tau_2=0, k=1))
            exp(- n + log n + o(1))
            >>> Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=2, tau_2=0, k=3).look_equal(
            ...     Asymptotic(mu=-2, nu=3, xi=3 * log(2) - log(6)))
            True
            >>> Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=1, tau_2=1, k=0).look_equal(
            ...     Asymptotic(mu=0, nu=- 1 / 2, xi=- 1 / 2 * log(4 * pi)))
            True
            >>> Asymptotic.poisson_x1_eq_x2_plus_k(tau_1=1, tau_2=2, k=3).look_equal(
            ...     Asymptotic(mu=- (1 - sqrt(2)) ** 2, nu=- 1 / 2, xi=- 1 / 2 * log(32 * pi * sqrt(2))))
            True
        """
        ce = computation_engine(symbolic)
        if tau_1 == 0:
            if k == 0:
                return cls(mu=- tau_2, nu=0, xi=0, symbolic=symbolic)
            else:
                return cls(mu=-ce.inf, nu=-ce.inf, xi=-ce.inf, symbolic=symbolic)
        elif tau_2 == 0:
            return cls(mu=- tau_1, nu=k, xi=ce.simplify(k * ce.log(tau_1) - ce.log(ce.factorial(k))), symbolic=symbolic)
        else:
            return cls(
                mu=ce.simplify(- (ce.sqrt(tau_1) - ce.sqrt(tau_2)) ** 2),
                nu=- ce.S(1) / 2,
                xi=ce.simplify(- ce.S(1) / 2
                               * ce.log(4 * ce.pi * ce.sqrt(tau_1 * tau_2) * ce.S(tau_2**k) / tau_1**k)),
                symbolic=symbolic
            )

    @classmethod
    def poisson_eq(cls, tau_1, tau_2, symbolic=False):
        """Asymptotic development of ``P(X_1 = X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 = X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import pi, log
            >>> print(Asymptotic.poisson_eq(tau_1=0, tau_2=0))
            exp(o(1))
            >>> print(Asymptotic.poisson_eq(tau_1=1/10, tau_2=0))
            exp(- 0.1 n + o(1))
            >>> Asymptotic.poisson_eq(tau_1=1/10, tau_2=9/10).look_equal(
            ...     Asymptotic(mu=-.4, nu=-.5, xi=-.5 * log(1.2 * pi)))
            True
        """
        return cls.poisson_x1_eq_x2_plus_k(tau_1, tau_2, 0, symbolic=symbolic)

    @classmethod
    def poisson_one_more(cls, tau_1, tau_2, symbolic=False):
        """Asymptotic development of ``P(X_1 = X_2 + 1)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 = X_2 + 1)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import pi, log
            >>> print(Asymptotic.poisson_one_more(tau_1=0, tau_2=1/10))
            exp(- inf)
            >>> print(Asymptotic.poisson_one_more(tau_1=1/10, tau_2=0))
            exp(- 0.1 n + log n - 2.30259 + o(1))
        """
        return cls.poisson_x1_eq_x2_plus_k(tau_1, tau_2, 1, symbolic=symbolic)

    @classmethod
    def poisson_x1_ge_x2_plus_k(cls, tau_1, tau_2, k, symbolic=False):
        """Asymptotic development of ``P(X_1 >= X_2 + k)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        k : int
            The desired value in ``P(X_1 >= X_2 + k)``.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 >= X_2 + k)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import log, sqrt, pi
            >>> print(Asymptotic.poisson_x1_ge_x2_plus_k(tau_1=0, tau_2=1, k=0))
            exp(- n + o(1))
            >>> print(Asymptotic.poisson_x1_ge_x2_plus_k(tau_1=0, tau_2=1, k=1))
            exp(- inf)
            >>> print(Asymptotic.poisson_x1_ge_x2_plus_k(tau_1=1, tau_2=0, k=0))
            exp(o(1))
            >>> Asymptotic.poisson_x1_ge_x2_plus_k(tau_1=1, tau_2=1, k=0).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=- log(2)))
            True
            >>> Asymptotic.poisson_x1_ge_x2_plus_k(tau_1=1, tau_2=2, k=3).look_equal(Asymptotic(
            ...     mu=- (1 - sqrt(2)) ** 2, nu=- 1 / 2,
            ...     xi=(- 1 / 2 * log(32 * pi * sqrt(2)) - log(1 - sqrt(1 / 2)))))
            True
        """
        ce = computation_engine(symbolic)
        if tau_1 == 0:
            if k == 0:
                return cls(mu=- tau_2, nu=0, xi=0, symbolic=symbolic)
            else:
                return cls(mu=-ce.inf, nu=-ce.inf, xi=-ce.inf, symbolic=symbolic)
        elif tau_1 > tau_2:
            # Probability 1 => the log tends to 0.
            return cls(mu=0, nu=0, xi=0, symbolic=symbolic)
        elif tau_1 == tau_2:
            # Probability 1/2 => the log tends to - log(2).
            return cls(mu=0, nu=0, xi=- ce.log(2), symbolic=symbolic)
        else:
            # Use the offset theorem with event X_1 = X_2, then infinite sum.
            return cls(
                mu=ce.simplify(- (ce.sqrt(tau_1) - ce.sqrt(tau_2)) ** 2),
                nu=- ce.S(1) / 2,
                xi=ce.simplify(
                    - ce.S(1) / 2 * ce.log(4 * ce.pi * ce.sqrt(tau_1 * tau_2) * ce.S(tau_2**k) / tau_1**k)
                    - ce.log(1 - ce.sqrt(ce.S(tau_1) / tau_2))
                ),
                symbolic=symbolic
            )

    @classmethod
    def poisson_ge(cls, tau_1, tau_2, symbolic=False):
        """Asymptotic development of ``P(X_1 >= X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 >= X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import log
            >>> print(Asymptotic.poisson_ge(tau_1=0, tau_2=0))
            exp(o(1))
            >>> print(Asymptotic.poisson_ge(tau_1=0, tau_2=1/10))
            exp(- 0.1 n + o(1))
            >>> print(Asymptotic.poisson_ge(tau_1=1/10, tau_2=0))
            exp(o(1))
            >>> Asymptotic.poisson_ge(tau_1=9/10, tau_2=1/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=0))
            True
            >>> Asymptotic.poisson_ge(tau_1=3/10, tau_2=3/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=-log(2)))
            True
            >>> asymptotic = Asymptotic.poisson_ge(tau_1=1/10, tau_2=9/10)
            >>> asymptotic_eq = Asymptotic.poisson_eq(tau_1=1/10, tau_2=9/10)
            >>> asymptotic.look_equal(
            ...     Asymptotic(mu=asymptotic_eq.mu, nu=asymptotic_eq.nu, xi=asymptotic_eq.xi + log(3/2)))
            True
        """
        return cls.poisson_x1_ge_x2_plus_k(tau_1, tau_2, 0, symbolic=symbolic)

    @classmethod
    def poisson_gt(cls, tau_1, tau_2, symbolic=False):
        """Asymptotic development of ``P(X_1 > X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 > X_2)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import log
            >>> print(Asymptotic.poisson_gt(tau_1=0, tau_2=0))
            exp(- inf)
            >>> print(Asymptotic.poisson_gt(tau_1=0, tau_2=1/10))
            exp(- inf)
            >>> print(Asymptotic.poisson_gt(tau_1=1/10, tau_2=0))
            exp(o(1))
            >>> Asymptotic.poisson_gt(tau_1=9/10, tau_2=1/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=0))
            True
            >>> Asymptotic.poisson_gt(tau_1=3/10, tau_2=3/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=-log(2)))
            True
            >>> asymptotic = Asymptotic.poisson_gt(tau_1=1/10, tau_2=9/10)
            >>> asymptotic_eq = Asymptotic.poisson_eq(tau_1=1/10, tau_2=9/10)
            >>> asymptotic.look_equal(
            ...     Asymptotic(mu=asymptotic_eq.mu, nu=asymptotic_eq.nu, xi=asymptotic_eq.xi - log(2)))
            True
        """
        return cls.poisson_x1_ge_x2_plus_k(tau_1, tau_2, 1, symbolic=symbolic)

    @classmethod
    def poisson_gt_one_more(cls, tau_1, tau_2, symbolic=False):
        """Asymptotic development of ``P(X_1 > X_2 + 1)``, where ``X_i ~ Poison(tau_i * n)``.

        Parameters
        ----------
        tau_1,tau_2 : Number
            The parameter of the Poisson distribution of ``X_i`` is ``tau_i * n``, where `n` tends to infinity.
        symbolic : bool
            Whether the computations are symbolic or numeric.

        Returns
        -------
        Asymptotic
            The asymptotic development of ``P(X_1 > X_2 + 1)``, where ``X_i ~ Poison(tau_i * n)``.

        Examples
        --------
            >>> from math import log
            >>> print(Asymptotic.poisson_gt_one_more(tau_1=0, tau_2=0))
            exp(- inf)
            >>> print(Asymptotic.poisson_gt_one_more(tau_1=0, tau_2=1/10))
            exp(- inf)
            >>> print(Asymptotic.poisson_gt_one_more(tau_1=1/10, tau_2=0))
            exp(o(1))
            >>> Asymptotic.poisson_gt_one_more(tau_1=9/10, tau_2=1/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=0))
            True
            >>> Asymptotic.poisson_gt_one_more(tau_1=3/10, tau_2=3/10).look_equal(
            ...     Asymptotic(mu=0, nu=0, xi=-log(2)))
            True
            >>> asymptotic = Asymptotic.poisson_gt_one_more(tau_1=1/10, tau_2=9/10)
            >>> asymptotic_eq = Asymptotic.poisson_eq(tau_1=1/10, tau_2=9/10)
            >>> asymptotic.look_equal(
            ...     Asymptotic(mu=asymptotic_eq.mu, nu=asymptotic_eq.nu, xi=asymptotic_eq.xi - log(6)))
            True
        """
        return cls.poisson_x1_ge_x2_plus_k(tau_1, tau_2, 2, symbolic=symbolic)
