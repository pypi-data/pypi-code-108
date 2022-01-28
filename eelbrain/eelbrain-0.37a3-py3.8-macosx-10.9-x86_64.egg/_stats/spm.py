# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Statistical Parametric Mapping"""
from operator import mul

import numpy as np

from .. import _info, fmtxt
from .._data_obj import Dataset, Factor, Var, NDVar, Case, asmodel, asndvar, assub, combine, dataobj_repr
from .._exceptions import DimensionMismatchError
from . import stats
from .stats import lm_betas_se_1d
from .test import star
from .testnd import TTestOneSample
from functools import reduce


class LM:
    """Fixed effects linear model

    Parameters
    ----------
    y : NDVar
        Dependent variable.
    model : Model
        Model to fit.
    ds : Dataset
        Optional Dataset providing data for y/model.
    coding : 'dummy' | 'effect'
        Model parametrization (default is dummy coding). Vars are centered for
        effect coding (but not for dummy coding).
    subject : str
        Optional information used by :class:`LMGroup`.
    sub : index
        Only use part of the data.

    See Also
    --------
    LMGroup

    Examples
    --------
    See :ref:`exa-two-stage` example.
    """
    def __init__(self, y, model, ds=None, coding='dummy', subject=None, sub=None):
        sub = assub(sub, ds)
        y = asndvar(y, sub, ds)
        n_cases = len(y)
        model = asmodel(model, sub, ds, n_cases)
        p = model._parametrize(coding)
        b, se, t = stats.lm_t(y.x, p)
        # find variables to keep
        variables = {}
        if ds is not None:
            for key, item in ds.items():
                if isinstance(item, Factor):
                    if sub is not None:
                        item = item[sub]
                    if len(item.cells) == 1:
                        variables[key] = item.cells[0]
        # subject
        if subject is not None:
            if not isinstance(subject, str):
                raise TypeError(f"subject={subject!r}: needs to be string or None")
            variables['subject'] = subject
        self.coding = coding
        self._coeffs_flat = b.reshape((len(b), -1))
        self._se_flat = se.reshape((len(se), -1))
        self.model = model
        self._p = p
        self.dims = y.dims[1:]
        self.subject_variables = variables
        self._y = dataobj_repr(y)
        self._init_secondary()

    def __setstate__(self, state):
        self.coding = state['coding']
        self._coeffs_flat = state['coeffs']
        self._se_flat = state['se']
        self.model = state['model']
        self.dims = state['dims']
        self._y = state.get('y')
        if 'subject' in state:
            self.subject_variables = {'subject': state['subject']}
        else:
            self.subject_variables = state['subject_variables']
        if 'p' in state:
            self._p = state['p']
        else:
            self._p = self.model._parametrize(self.coding)
        self._init_secondary()

    def _init_secondary(self):
        self.subject = self.subject_variables.get('subject', None)
        self._shape = tuple(map(len, self.dims))
        self.column_names = self._p.column_names
        self.n_cases = self.model.df_total

    def __getstate__(self):
        return {'coding': self.coding, 'coeffs': self._coeffs_flat, 'se': self._se_flat, 'model': self.model, 'dims': self.dims, 'subject_variables': self.subject_variables, 'y': self._y}

    def __repr__(self):
        y = self._y or '<?>'
        return f"<LM: {y} ~ {self.model.name}>"

    def _coefficient(self, term):
        """Regression coefficient for a given term"""
        index = self._index(term)
        return self._coeffs_flat[index].reshape((1,) + self._shape)

    def _index(self, term):
        if term in self.column_names:
            return self.column_names.index(term)
        elif term in self._p.terms:
            index = self._p.terms[term]
            if index.stop - index.start > 1:
                raise NotImplementedError("Term has more than one column")
            return index.start
        else:
            raise KeyError(f"Unknown term: {term!r}")

    def coefficient(self, term):
        ":class:`NDVar` with regression coefficient for a given term"
        return NDVar(self._coefficient(term)[0], self.dims, name=term)

    def t(self, term):
        ":class:`NDVar` with t-values for a given term"
        index = self._index(term)
        se = self._se_flat[index]
        flat_index = se == 0.
        any_flat = np.any(flat_index)
        if any_flat:
            se = se.copy()
            se[flat_index] = 1.
        t = self._coeffs_flat[index] / se
        if any_flat:
            t[np.logical_and(flat_index, t == 0)] = 0.
            t[np.logical_and(flat_index, t != 0)] *= np.inf
        info = _info.for_stat_map('t')
        info['term'] = term
        return NDVar(t.reshape(self._shape), self.dims, info, term)

    def _n_columns(self):
        return {term: s.stop - s.start for term, s in self._p.terms.items()}


class LMGroup:
    """Group level analysis for linear model :class:`LM` objects
    
    Parameters
    ----------
    lms : sequence of LM
        A separate :class:`LM` object for each subject.

    Attributes
    ----------
    column_names : [str]
        Names of the linear model columns.
    column_keys : [str]
        Corresponding dataset keys (with invalid characters replaced).
    tests : None | {str: TTestRelated}
        Tests computed with :meth:`compute_column_ttests`.
    samples : None | int
        Number of samples used to compute tests in :attr:`tests`.

    See Also
    --------
    LM

    Examples
    --------
    See :ref:`exa-two-stage` example.
    """
    def __init__(self, lms):
        # check lms
        lm0 = lms[0]
        n_columns_by_term = lm0._n_columns()
        for lm in lms[1:]:
            if lm.dims != lm0.dims:
                raise DimensionMismatchError("LMs have incompatible dimensions")
            elif lm._n_columns() != n_columns_by_term:
                raise ValueError(f"Model for {lm0.subject} and {lm.subject} don't match")
            elif lm.coding != lm0.coding:
                raise ValueError("Models have incompatible coding")

        # make sure to have a unique subject label for each lm
        name_i = 0
        subjects = [lm.subject for lm in lms]
        str_names = tuple(filter(None, subjects))
        if len(set(str_names)) < len(str_names):
            raise ValueError(f"Duplicate subject names: {', '.join(map(repr, str_names))}")
        new_name = 'S000'
        for i in range(len(subjects)):
            if not subjects[i]:
                while new_name in subjects:
                    name_i += 1
                    new_name = 'S%03i' % name_i
                subjects[i] = new_name

        self._lms = lms
        self._subjects = tuple(subjects)
        self.tests = None
        self._init_secondary()

    def __setstate__(self, state):
        self._lms = state['lms']
        self._subjects = state['subjects']
        self.tests = state.get('tests')
        self._init_secondary()

    def _init_secondary(self):
        lm = self._lms[0]
        self.dims = lm.dims
        self.coding = lm.coding
        self.column_names = lm.column_names
        if self.tests is None:
            self.samples = None
        else:
            self.samples = self.tests[self.column_names[0]].samples
        # subject variables
        self.subject_variables = Dataset()
        self.subject_variables['subject'] = Factor(self._subjects, random=True)
        keys = set().union(*(lm.subject_variables for lm in self._lms))
        for key in keys:
            values = [lm.subject_variables.get(key, '') for lm in self._lms]
            self.subject_variables[key] = Factor(values)
        self.column_keys = [Dataset.as_key(name) for name in self.column_names]

    def __getstate__(self):
        return {'lms': self._lms, 'tests': self.tests, 'subjects': self._subjects}

    def __repr__(self):
        lm = self._lms[0]
        y = lm._y or '<?>'
        return f"<LMGroup: {y} ~ {lm.model.name}, n={len(self._lms)}>"

    def coefficients(self, term):
        "Coefficients for one term as :class:`NDVar`"
        x = np.concatenate([lm._coefficient(term) for lm in self._lms])
        return NDVar(x, (Case,) + self.dims, name=term)

    def coefficients_dataset(self, terms=None, long=False):
        """Regression coefficients in a :class:`Dataset`

        By default, each regression coefficient is assigned as separate column.
        With ``long=True``, a long form table is produced, in which the
        coefficients for different terms are stacked vertically and the ``term``
        :class:`Factor` specifies which term the coefficients correspond to.

        Parameters
        ----------
        terms : str | sequence of str
            Terms for which to retrieve coefficients (default is all terms).
        long : bool
            Produce a table in long form.

        Returns
        -------
        ds : Dataset
            If the dataset is in the wide form (default), each model coefficient
            is assigned as :class:`NDVar` with a key corresponding to the
            ``.column_keys`` attribute.
            If the dataset is in the long form (with ``long=True``), it has the
            following entries:

             - ``coeff``: the coefficients in an :class:`NDVar`
             - ``term``: a :class:`Factor` with the name of the term

            In addition, all available subject-variables are assigned.
        """
        if isinstance(terms, str):
            terms = (terms,)
        elif terms is None:
            terms = self.column_names

        if long:
            ds = Dataset({
                'coeff': combine([self.coefficients(term) for term in terms]),
                'term': Factor(terms, repeat=len(self._lms)),
                **self.subject_variables.tile(len(terms)),
            })
        else:
            ds = Dataset({Dataset.as_key(name): self.coefficients(name) for name in terms})
            ds.update(self.subject_variables)
        return ds

    def column_ttest(self, term, return_data=False, popmean=0, *args, **kwargs):
        """One-sample t-test on a single model column

        Parameters
        ----------
        term : str
            Name of the term to test.
        return_data : bool
            Return the individual subjects' coefficients along with test
            results.
        popmean : scalar
            Value to compare y against (default is 0).
        tail : 0 | 1 | -1
            Which tail of the t-distribution to consider:
            0: both (two-tailed);
            1: upper tail (one-tailed);
            -1: lower tail (one-tailed).
        samples : None | int
            Number of samples for permutation cluster test. For None, no
            clusters are formed. Use 0 to compute clusters without performing
            any permutations.
        pmin : None | scalar (0 < pmin < 1)
            Threshold for forming clusters:  use a t-value equivalent to an
            uncorrected p-value.
        tmin : None | scalar
            Threshold for forming clusters.
        tfce : bool
            Use threshold-free cluster enhancement (Smith & Nichols, 2009).
            Default is False.
        tstart, tstop : scalar
            Restrict time window for permutation cluster test.
        mintime : scalar
            Minimum duration for clusters (in seconds).
        minsource : int
            Minimum number of sources per cluster.

        Returns
        -------
        result : TTestOneSample
            T-test result.
        data : Dataset (only with ``return_data=True``)
            Dataset with subjects' coefficients.

        Notes
        -----
        Performs a one-sample t-test on coefficient estimates from all subjects
        to test the hypothesis that the coefficient is different from popmean
        in the population.
        """
        coeff = self.coefficients(term)
        res = TTestOneSample(coeff, popmean, None, None, None, *args, **kwargs)
        if return_data:
            ds = Dataset({'coeff': coeff})
            ds.update(self.subject_variables)
            ds['n'] = Var([lm.n_cases for lm in self._lms])
            return res, ds
        else:
            return res

    def design(self, subject=None):
        "Table with the design matrix"
        if subject is None:
            lm = self._lms[0]
            subject = self._subjects[0]
        else:
            for lm, lm_subject in zip(self._lms, self._subjects):
                if lm_subject == subject:
                    break
            else:
                raise ValueError(f"subject={subject!r}")

        table = lm.model.as_table(lm.coding)
        table.caption(f"Design matrix for {subject}")
        return table

    def compute_column_ttests(self, *args, **kwargs):
        """Compute all tests and store them in :attr:`self.tests`

        Parameters like :meth:`.column_ttest`, starting with ``popmean``.
        """
        self.tests = {}
        for term in self.column_names:
            self.tests[term] = self.column_ttest(term, False, *args, **kwargs)
        self.samples = self.tests[self.column_names[0]].samples

    def info_list(self):
        l = fmtxt.List("LMGroup info")
        for effect in self.column_names:
            res = self.tests[effect]
            l.add_sublist(effect, [res.info_list()])
        return l

    def table(self, title=None, caption=None):
        """Table listing all terms and corresponding smallest p-values

        Parameters
        ----------
        title : text
            Title for the table.
        caption : text
            Caption for the table.

        Returns
        -------
        table : eelbrain.fmtxt.Table
            ANOVA table.
        """
        if not self.tests:
            raise RuntimeError("Need to precompute tests with .compute_column_ttests()")
        table = fmtxt.Table('lrrl', title=title, caption=caption)
        table.cells('Term', 't_max', 'p', 'sig')
        table.midrule()
        for term, res in self.tests.items():
            table.cell(term)
            table.cell(fmtxt.stat(res.t.extrema()))
            pmin = res.p.min()
            table.cell(fmtxt.p(pmin))
            table.cell(star(pmin))
        return table


# for backwards compatibility
RandomLM = LMGroup
