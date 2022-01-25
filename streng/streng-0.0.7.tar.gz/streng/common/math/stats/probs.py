import numpy as np
# from scipy.stats import lognorm, norm, mode
import matplotlib.pyplot as plt
from scipy import stats
from dataclasses import dataclass, field
from ....common.io.output import OutputTable


@dataclass
class ProbDist:
    X: np.array = field(init=False)
    μX: float = field(init=False)
    σX: float = field(init=False)
    modeX: float = field(init=False)
    μlnX: float = field(init=False)
    σlnX: float = field(init=False)
    θ: float = field(init=False)
    ν: float = field(init=False)

    title: str = field(init=False, default="Probability Distribution Example")

    @classmethod
    def from_sample(cls, sample):
        cls.X = sample
        cls.μX = np.mean(sample)
        cls.σX = np.std(sample)
        cls.μlnX = np.mean(np.log(sample))
        cls.θ = np.median(sample)
        cls.σlnX = np.std(np.log(sample))
        cls.modeX = cls.get_lognorm_mode(cls.μlnX, cls.σlnX)
        return cls

    @classmethod
    def from_θβ(cls, θ, β):
        cls.X = []
        ν = np.sqrt(np.exp(β ** 2) - 1.0)
        cls.μX = θ * np.sqrt(1.0 + ν ** 2)
        cls.σΧ = ν * cls.μX
        cls.θ = θ
        cls.σlnX = β
        cls.modeX = cls.get_lognorm_mode(cls.μlnX, cls.σlnX)
        return cls

    @classmethod
    def from_μXσX(cls, μX, σX):
        cls.X = []
        ν = σX/μX
        β = np.sqrt(np.log(1.0 + ν**2))
        θ = μX / np.sqrt(1+ν**2)
        cls.μX = μX
        cls.σΧ = σX
        cls.θ = θ
        cls.μlnX = np.log(θ)
        cls.σlnX = β
        cls.modeX = cls.get_lognorm_mode(cls.μlnX, cls.σlnX)
        return cls

    @staticmethod
    def get_lognorm_mode(μlnX, σlnX):
        return np.exp(μlnX-σlnX**2)

    @staticmethod
    def get_lognorm_mean(μlnX, σlnX):
        return np.exp(μlnX+0.5*σlnX**2)

    def __str__(self):
        out = OutputTable()
        out.data.append({'quantity': 'mean value of X', 'value': self.μX})
        out.data.append({'quantity': 'standard deviation of X', 'value': self.σX})
        out.data.append({'quantity': 'mode value of X', 'value': self.modeX})
        out.data.append({'quantity': 'mean value of lnX', 'value': self.μlnX})
        out.data.append({'quantity': 'standard deviation of lnX = β', 'value': self.σlnX})
        out.data.append({'quantity': 'θ = median value of lnX', 'value': self.θ})
        return out.to_markdown

    def plot(self):
        f, ax = plt.subplots(figsize=(12, 8))

        if len(self.X) > 0:
            count, bins = np.histogram(self.X, 100)
            x = np.linspace(min(bins), max(bins), 10000)
            # Σχεδίαδη του ιστογράμματος του δείγματος
            ax.hist(self.X, 80, density=True, align='mid', color='#395280')
        else:
            x = np.linspace(0.0, 8*self.θ, 10000)

        # Συναρτήσεις pdf και cdf
        # Προσοχή, πρέπει να βάλω np.exp(μ) στο scale, όχι όμως και στο σ. Έλεγχος με τη σχέση από τα βιβλία
        # pdf = (np.exp(-(np.log(x) - μ)**2 / (2 * σ**2)) / (x * σ * np.sqrt(2 * np.pi)))
        pdf = stats.lognorm(s=self.σlnX, scale=np.exp(self.μlnX)).pdf(x)
        cdf = stats.lognorm(s=self.σlnX, scale=np.exp(self.μlnX)).cdf(x)


        # Σχεδίαση της pdf συνάρτησης
        ax.plot(x, pdf, linewidth=3, color='r')

        ax.plot(x, cdf, linewidth=2, color='#fbaea6')

        ymax = 1.1 * max(pdf)

        ax.plot([self.θ, self.θ], [0., ymax], linewidth=2, color='g', label=f'median = {self.θ:.3f}')
        ax.plot([self.μX, self.μX], [0., ymax], linewidth=2, color='c', label=f'mean = {self.μX:.3f}')
        ax.plot([self.modeX, self.modeX], [0., ymax], linewidth=2, color='#5b5ea6', label=f'mode = {self.modeX:.3f}')
        ax.legend()
        # ax.set_xlim(0.,max(x))

        # ax.set_ylabel(r'$T\ [^oC]$')
        ax.set_xlabel(r'$PGA$')

        ax.set_ylim(0., ymax)

        return f, ax
