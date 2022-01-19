#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe RocAnalyser permettant de calculer, mettre en forme simplement des 
courbes ROC.

Created on Tue Nov 24 12:50:56 2020

@author: Cyrile Delestre
"""

from dataclasses import dataclass, field
from typing import List, Optional
from itertools import product, chain
from collections import OrderedDict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score
from joblib import Parallel, delayed
from tqdm import tqdm

from .statistique import cdf_normal, cdf_rayleigh, kolmogorov_smirnov_test
from dstk.utils import weighted_avg_and_std, chunker

@dataclass
class ROCAnalyzer:
    r"""
    Classe d'analyse d'un modèle de classification multi-classe utilisant les 
    propriétés de la courbe ROC (Receiver Operating Characteristic). La 
    classe comporte également un gestionnaire des plots pour faciliter 
    l'affichage des figures.
    
    Parameters
    ----------
    y_true : np.ndarray
        ndarray de dimension (n_samples,) où chaque classe est représentée par 
        un int. L'entier doit correspondre à l'argument de la classe (0 pour 
        la première classe, 1 pour la seconde, etc.). Si ce n'est pas le cas 
        faire :
            np.argmax(y_true)
    y_score : np.ndarray
        ndarray de dimension (n_samples, n_classes) contenant les probabilités 
        d'appartenance de chaque classe. C'est typiquement la sortie de type 
        Scikit-Learn model.predict_propba(X_eval). Attention le cas bi-classe 
        y_score doit être de dimension (n_samples, 2).
    labels : Optional[List[str]]
        nom des labels du modèle. Doit suivre l'ordre de l'indexation de 
        y_true. Si non-renseigné (None) utilise l'indexation de y_true pour 
        identifier les classes.
    sample_weight : Optional[np.ndarray]
        poids sur les samples.
    drop_intermediate : bool
        (paramètre de sklearn.metrics.roc_curve), drop un threshold 
        sous-optimal (qui n'apparait pas sur la courbe car trop rapproché 
        d'un autre). Permet d'alléger la représentation.
    densities : List[str]
        liste des densités théoriques à tester pour l'estimation de courbe 
        ROC théorique. Attention certaines peuvent demander le package SciPy. 
        Le choix pour déterminer la meilleure loi adaptée pour la 
        représentation de la densité du score sera la loi ayant l'écart 
        minimum de la différence de Kolmogorov-Smirnov. Par défaut seule la 
        loi Normale est utilisée, on appelle cette estimation de la courbe ROC 
        la courbe ROC Binormale. Liste possible implanté pour le moment :
            'normal', 'rayleigh'
    roc_multi_class : str
        type de courbe ROC dans le cadre d'une modélisation multi-classe. 
        Soit 'one-vs-rest' (par défaut) et chaques classes seront 
        repsésentées. Dans ce cas l'AUC sera la probabilité que le score de 
        la classe i soit supérieur au score de la classe non i. Sinon 
        'one-vs-one' où on test la classe i sachant qu'on est dans la classe 
        j. Dans ce cas  l'AUC sera la probabilité que le score de la classe i 
        soit supérieur à classe réelle j.

    Notes
    -----
    La partie estimation de la courbe ROC théorique est encore en cours de 
    réflexion...

    Les attributs liés à l'analyse ne sont pas générés tant que l'analyse 
    en question n'a pas tourné. Par exemple on a pas les moyennes des classes 
    tant que 
    :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.process_roc_theo` 
    ne s'est pas exécuté. Voir dans la doc de chacunes des méthodes 
    (généralement commençant par ``process_``) les attributs d'analyse qui y 
    sont générés.
    
    Examples
    --------
    >>> import pandas as pd
    >>> from sklearn.datasets import make_moons
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.model_selection import train_test_split
    >>> from dstk.visualization import ROCAnalyser
    >>> 
    >>> # Exemple de données d'une classification binaire généré
    >>> # procéduralement
    >>> data_moons, target_moons = make_moons(
    >>>     n_samples = 1000,
    >>>     shuffle = True,
    >>>     noise = 0.5,
    >>>     random_state = 42
    >>> )
    >>> 
    >>> (X_train_moons, X_eval_moons, y_train_moons,
    >>> y_eval_moons) = train_test_split(
    >>>     data_moons,
    >>>     target_moons,
    >>>     train_size = 800,
    >>>     random_state = 42
    >>> )
    >>> 
    >>> rf = RandomForestClassifier(random_state = 42)
    >>> rf.fit(X_train_moons, y_train_moons)
    >>> 
    >>> y_score_moons = rf.predict_proba(X_eval_moons)
    >>> 
    >>> ana_moons = ROCAnalyser(
    >>>     y_eval_moons,
    >>>     y_score_moons,
    >>>     densities = ['normal', 'rayleigh']
    >>> )
    >>> ana_moons.plot_roc_bootstrap().plot_roc_theo().plot_roc()
    
    Affiche la courbe ROC de ce cas bi-classe et affiche également 
    l'estimation de la courbe théorique de ce modèle ainsi la précision de 
    la courbe ROC via une approche de bootstraping.
    
    >>> analyse = ana_moons.get_annalyse()
    >>> pd.DataFrame(analyse)
           best_tresh  roc_auc  best_tresh_theo ... 1_ks_normal  1_ks_rayleigh
        0         0.4  0.88055           0.4987 ...    0.148793       0.909485
    
    Voici un autre exemple d'un modèle 3 classes sur un dataset généré.
    
    >>> from sklearn.datasets import make_multilabel_classification
    >>> from sklearn.linear_model import LogisticRegression
    >>> from dstk.visualization import ROCAnalyser
    >>> 
    >>> data_wine, target_wine = make_multilabel_classification(
    >>>     n_samples = 1000,
    >>>     n_features = 5,
    >>>     n_classes = 3,
    >>>     random_state = 42
    >>> )
    >>> 
    >>> (X_train_wine, X_eval_wine, y_train_wine,
    >>> y_eval_wine) = train_test_split(
    >>>     data_wine,
    >>>     np.argmax(target_wine, axis = 1),
    >>>     train_size = 25,
    >>>     random_state = 42
    >>> )
    >>> 
    >>> lr = LogisticRegression(max_iter = 1e3, random_state = 42)
    >>> lr.fit(X_train_wine, y_train_wine)
    >>> 
    >>> y_score_wine = lr.predict_proba(X_eval_wine)
    >>> ana_wine = ROCAnalyser(
    >>>     y_eval_wine,
    >>>     y_score_wine,
    >>>     labels = ['Champagne', 'Bordeau', 'Beaujolais'],
    >>>     densities = ['normal', 'rayleigh']
    >>> )
    >>> ana_wine.plot_roc_manager(3).plot_roc().plot_roc_theo()
    
    Affiche les courbes ROC associées à chaques classes ainsi que les
    estimations des courbes théoriques de ce modèle.
    
    >>> ana_wine.process_performance_matrix()
                    Champagne   Bordeau  Beaujolais
        Champagne    0.954217  0.207498    0.233000
        Bordeau      0.190446  0.916519    0.577172
        Beaujolais   0.052897  0.334532    0.981586
    """
    y_true: np.ndarray
    y_score: np.ndarray
    labels: Optional[List[str]]=None
    sample_weight: Optional[np.ndarray]=None
    drop_intermediate: bool=True
    densities: List[str]=field(default_factory = lambda: ['normal'])
    roc_multi_class: str='one-vs-one'
    
    def __post_init__(self):
        self.nb_class = self.y_score.shape[1]
        if self.nb_class == 1:
            raise AttributeError(
                "Il n'y a qu'une seule classe, y_score doit être de "
                "dimension : (n_samples, n_classes)."
            )
        if not self.labels is None and len(self.labels) != self.nb_class:
            raise AttributeError(
                "Il n'y a pas le bon nombre d'éléments dans labels. Le "
                f"nombre d'éléments attendu est {self.nb_class} alors que "
                f"labels a une taille de {len(self.labels)}. Pour rappel "
                "labels peut être None."
            )
        if not self.roc_multi_class in ['one-vs-one', 'one-vs-rest']:
            raise AttributeError(
                "L'argument roc_multi_class doit être soit : 'one-vs-one' "
                f"ou 'one-vs-rest' et non '{self.roc_multi_class}'."
            )
        self.analyse = OrderedDict()
        fn_density = dict(
            normal = cdf_normal,
            rayleigh = cdf_rayleigh
        )
        self.list_density = [
            (name, fn_density[name]) for name in self.densities
        ]

    def _roc(self, ratio):
        r"""
        Méthode privée calculant la courbe ROC, l'AUC et d'autres attributs.
        """
        (fpr, tpr, thresh, best_thresh, best_fpr, best_tpr, 
         roc_auc, nb_obs, idx_sel) = [], [], [], [], [], [], [], [], []
        size  = len(self.y_true)
        idx = np.sort(
            np.random.choice(
                range(size),
                size = int(ratio*size),
                replace = False
            )
        )
        if self.nb_class == 2:
            fpr_, tpr_, thresh_ = roc_curve(
                y_true = self.y_true[idx],
                y_score = self.y_score[idx, 1],
                sample_weight = self.sample_weight,
                drop_intermediate = self.drop_intermediate
            )
            idx_best = np.argmax(tpr_ - fpr_)
            fpr.append(fpr_)
            tpr.append(tpr_)
            thresh.append(thresh_)
            best_thresh.append(thresh_[idx_best])
            best_fpr.append(fpr_[idx_best])
            best_tpr.append(tpr_[idx_best])
            roc_auc.append(auc(fpr_, tpr_))
            nb_obs.append(np.sum(self.y_true[idx] == 2))
            idx_sel.append(idx)
        else:
            for ii in range(self.nb_class):
                if self.roc_multi_class == 'one-vs-rest':
                    y_score = self.y_score[idx, ii]
                elif self.roc_multi_class == 'one-vs-one':
                    filt_not_class = ~(self.y_true[idx]==ii).ravel()
                    y_score = self.y_score[idx, ii]
                    y_score[filt_not_class] = (
                        (1-self.y_score[idx, self.y_true[idx].ravel()])
                        [filt_not_class]
                    )
                else:
                    raise AttributeError(
                        "L'argument roc_multi_class doit être soit : "
                        "'one-vs-one' ou 'one-vs-rest' et non "
                        f"'{self.roc_multi_class}'."
                    )
                fpr_, tpr_, thresh_ = roc_curve(
                    y_true = (self.y_true[idx] == ii).astype(int),
                    y_score = y_score,
                    sample_weight = self.sample_weight,
                    drop_intermediate = self.drop_intermediate
                )
                idx_best = np.argmax(tpr_ - fpr_)
                fpr.append(fpr_)
                tpr.append(tpr_)
                thresh.append(thresh_)
                best_thresh.append(thresh_[idx_best])
                best_fpr.append(fpr_[idx_best])
                best_tpr.append(tpr_[idx_best])
                roc_auc.append(auc(fpr_, tpr_))
                nb_obs.append(np.sum(self.y_true[idx] == ii))
                idx_sel.append(idx)
        return list(
            zip(fpr, tpr, thresh, best_thresh, best_fpr,
                best_tpr, roc_auc, nb_obs, idx_sel)
        )

    def process_roc(self):
        r"""
        Méthode de calcul de la courbe ROC pour chacune des classes. Cette 
        méthode ne peut être appliquée qu'une seule fois car son résultat est 
        stocké dans l'attribut 'data_roc'.
        
        Notes
        -----
        Dans le cadre de l'attribut 'analyse' certains de ses éléments sont 
        calculés ici :
        
        'best_tresh' :
            correspondant au seuil optimal de modèle au sens de la courbe ROC.
        'roc_auc' :
            AUC associé à la classe.
        'nb_obs' :
            Nombre d'observation par classe.
        
        See also
        --------
        process_roc_theo, process_roc_bootstrap, process_performance_matrix
        """
        self.data_roc = self._roc(ratio=1)
        data_roc = list(zip(*self.data_roc))
        self.analyse['best_thresh'] = data_roc[3]
        self.analyse['roc_auc'] = data_roc[6]
        self.analyse['nb_obs'] = data_roc[7]
        return self

    def process_roc_bootstrap(self,
                              monte_carlo: int=100,
                              ratio: float=0.8,
                              n_jobs: int=1,
                              verbose: bool=False):
        r"""
        Méthode d'estimation de la courbe ROC et de ses statistiques par 
        bootstrap. Permet d'apprécier la volatilité de l'estimateur et de 
        donner un AUC ou un seuillage optimal plus robuste.
        
        Parameters
        ----------
        :monte_carlo: nombre de courbe ROC estimées (par défaut 100).
        :ratio: ratio d'observation conservé pour une estimation de la courbe 
            ROC (par défaut 0.8).
        :n_jobs: permet de paralléliser les calculs des courbes ROC et des 
            AUC.
        :verbose: permet d'afficher une barre d'avancement.
        
        Notes
        -----
        Dans le cadre de l'attribut 'analyse' certains de ses éléments sont 
        calculés ici :
        
        'best_thresh_bootstrap_mean' :
            correspondant au seuil moyen optimal du modèle au sens de la 
            courbe ROC estimée.
        'best_thresh_bootstrap_med' :
            correspondant au seuil median optimal du modèle au sens de la 
            courbe ROC estimée.
        'best_thresh_bootstrap_std' :
            correspondant à l'écart-type du seuil optimal du modèle au sens 
            de la courbe ROC estimée.
        'roc_auc_booststrap_mean' :
            AUC moyen associé à la classe déterminée sur l'estimation de la 
            courbe ROC.
        'roc_auc_booststrap_med' :
            AUC meidan associé à la classe déterminée sur l'estimation de la 
            courbe ROC.
        'roc_auc_booststrap_std' :
            écart-type de l'AUC associé à la classe déterminée sur 
            l'estimation de la courbe ROC.
        'nb_obs_booststrap' :
            nombre d'observation pour l'estimation de la courbe ROC.
        
        See also
        --------
        process_roc, process_roc_theo, process_performance_matrix
        """
        iterator = range(monte_carlo)
        if verbose:
            iterator = tqdm(
                iterator,
                desc = f'{self.process_roc_bootstrap.__name__}'
            )
        with Parallel(n_jobs=n_jobs) as par:
            self.data_roc_bootstrap = par(
                delayed(self._roc)(ratio) for ii in iterator
            )
        data_roc_bootstrap = list(zip(*self.data_roc_bootstrap))
        best_tresh = list(
            map(lambda x: list(map(lambda y: y[3], x)), data_roc_bootstrap)
        )
        roc_auc = list(
            map(lambda x: list(map(lambda y: y[6], x)), data_roc_bootstrap)
        )
        self.analyse['best_thresh_bootstrap_mean'] = (
            np.mean(best_tresh, axis=1).tolist()
        )
        self.analyse['best_threch_bootstrap_med'] = (
            np.median(best_tresh, axis=1).tolist()
        )
        self.analyse['best_thresh_bootstrap_std'] = (
            np.std(best_tresh, axis=1).tolist()
        )
        self.analyse['roc_auc_bootstrap_mean'] = (
            np.mean(roc_auc, axis=1).tolist()
        )
        self.analyse['roc_auc_bootstrap_med'] = (
            np.median(roc_auc, axis=1).tolist()
        )
        self.analyse['roc_auc_bootstrap_std'] = (
            np.std(roc_auc, axis=1).tolist()
        )
        self.analyse['nb_obs_bootstrap'] = list(
            map(lambda x: list(map(lambda y: y[7], x))[0], data_roc_bootstrap)
        )
        return self

    def process_roc_theo(self):
        r"""
        Méthode déterminant la densité théorique la plus proche de la 
        densité du score et calculant la courbe ROC théorique associée aux 
        densités théoriques. La liste de choix des lois théoriques est 
        initiée à l'instanciation de la classe ROCAnalyser dans l'attribut 
        'densities'.
        
        Notes
        -----
        La courbe ROC étant par définition dans
        Scikite-Learn par :
            fpr, tpr, thresh = ROC(y_true, y_socre)
        
        Si on détermine la loi de répartition des faux positifs et des vrais 
        positifs alors :
            fpr, tpr, thresh = CDF(law_fp, thresh), CDF(law_tp, thresh), thresh
        
        D'autres approches sont possibles mais nécessitent obligatoirement 
        SciPy (ce qu'on ne souhaite pas) car il faut pouvoir calculer CDP^-1.
        
        Seules les lois Normale, Rayleigh ne nécessitent pas le package SciPy.
        
        Dans le cadre de l'attribut 'analyse' certains de ses éléments sont 
        calculés ici :
        
        'best_thresh_theo' :
            correspondant au seuil optimal de modèle au sens de la courbe ROC 
            théorique.
        'roc_auc_theo' :
            AUC associé à la classe déterminée sur la courbe ROC théorique.
        mean_{classe_i} :
            moyennes des classes (vrai positive et fausses positives) pour 
            chaque hypothèse d'appartenance.
        std_{classe_i} :
            écart-types des classes (vrai positive et fausses positives) pour 
            chaque hypothèse d'appartenance.
        {classe_i}_ks_{densité_j} :
            écart de Kolmogorov-Smirnov de la classe i pour la densité j pour 
            chaque hypothèse.
        
        See also
        --------
        process_roc, process_roc_bootstrap, process_performance_matrix
        """
        thresh_theo_ = np.linspace(-6, 7, 5000)
        bins = [-6, -4, -1]+np.arange(0,1.1,0.1).tolist()+[1, 2, 5, 7]
        (fpr_theo, tpr_theo, thresh_theo, best_thresh_theo, best_fpr_theo, 
         best_tpr_theo, roc_auc_theo) = [], [], [], [], [], [], []
        mean_over_classes, std_over_classes, ks_over_classes = [], [], []
        for ii in range(self.nb_class):
            if self.nb_class == 2:
                ii = 1
            y_ = [
                self.y_score[self.y_true == cc, ii]
                for cc in range(self.nb_class)
            ]
            mean, std = list(
                zip(
                    *[weighted_avg_and_std(
                        x = yy,
                        sample_weight = self.sample_weight,
                        axis = 0
                    ) for yy in y_]
                )
            )
            mean, std = np.array(mean).ravel(), np.array(std).ravel()
            dens_select = []
            ks_ov = []
            for qq in range(self.nb_class):
                ks = []
                for name, cdf in self.list_density:
                    ks_ = kolmogorov_smirnov_test(
                        x = y_[qq],
                        cdf = cdf,
                        mean = mean[qq],
                        std = std[qq],
                        bins = bins
                    )
                    ks.append((cdf, ks_))
                ks_sort = sorted(ks, key=lambda x: x[1], reverse=False)
                dens_select.append(ks_sort[0][0])
                ks_ov.append([kk for _, kk  in ks])
            tpr_ = 1-dens_select[ii](
                thresh_theo_,
                mean = mean[ii],
                std = std[ii]
            )
            dens_select_other = dens_select
            dens_select_other.pop(ii)
            mean_other = np.delete(mean, ii)
            std_other = np.delete(std, ii)
            fpr_ = np.zeros_like(thresh_theo_)
            for qq, cdf in enumerate(dens_select_other):
                fpr_ += 1-cdf(
                    thresh_theo_,
                    mean = mean_other[qq],
                    std = std_other[qq]
                )
            fpr_ /= len(dens_select_other)
            mean_over_classes.append(mean)
            std_over_classes.append(std)
            ks_over_classes.append(ks_ov)
            idx = np.argmax(tpr_ - fpr_)
            fpr_theo.append(fpr_)
            tpr_theo.append(tpr_)
            thresh_theo.append(thresh_theo_)
            best_thresh_theo.append(thresh_theo_[idx])
            best_fpr_theo.append(fpr_[idx])
            best_tpr_theo.append(tpr_[idx])
            roc_auc_theo.append(auc(fpr_, tpr_))
            if self.nb_class == 2:
                break
        self.data_roc_theo = list(
            zip(
                fpr_theo,
                tpr_theo,
                thresh_theo,
                best_thresh_theo,
                best_fpr_theo,
                best_tpr_theo,
                roc_auc_theo
            )
        )
        self.analyse['best_thresh_theo'] = best_thresh_theo
        self.analyse['roc_auc_theo'] = roc_auc_theo
        mean_unzip = list(zip(*mean_over_classes))
        sdt_unzip = list(zip(*std_over_classes))
        ks_unzip_ = list(zip(*ks_over_classes))
        for ii in range(self.nb_class):
            self.analyse[
                f'mean_{ii if self.labels is None else self.labels[ii]}'
            ] = mean_unzip[ii]
            self.analyse[
                f'std_{ii if self.labels is None else self.labels[ii]}'
            ] = sdt_unzip[ii]
            ks_unzip = list(zip(*ks_unzip_[ii]))
            for qq, nn in enumerate(self.list_density):
                mm, _ = nn
                self.analyse[
                    f'{ii if self.labels is None else self.labels[ii]}_ks_{mm}'
                ] = ks_unzip[qq]
        return self

    def _auc_par(self, lot):
        r"""
        Méthode interne permettant de calculer en parallèle des AUC.
        """
        auc_res = []
        for class_a, class_b in lot:
            auc_res.append(
                roc_auc_score(
                    (self.y_true == class_a).astype(int),
                    self.y_score[:, class_b],
                    sample_weight = self.sample_weight
                )
            )
        return auc_res

    def process_performance_matrix(self,
                                   size: int=10,
                                   n_jobs: int=1,
                                   verbose: bool=False):
        r"""
        Méthode de calcul de la matrice de performance au sens du score 
        d'un modèle de classification.
        
        Parameters
        ----------
        size : int
            taille des tronçons où les combinaisons des classes seront mises. 
            Surtout utile si n_jobs > 1.
        n_jobs : int
            permet de paralléliser le calcul des AUC sur toutes les 
            combinaisons des classes (nombre de calcul d'AUC == nb_class**2).
            Pas très utile si le nombre de classe est faible.
        verbose : bool
            permet d'afficher une barre d'avancement des calculs des AUC au 
            travers des différents tronçons.
        
        Returns
        -------
        DataFrame contenant la matrice de performance où les noms des colonnes 
        et indices font référence aux noms des classes. Le résultat est 
        stocké dans l'attribut 'performance_matrix' (pas besoin de calculer 
        tout le temps cette matrice).
        
        Notes
        -----
        Si on note S(X_i) un score de la classe i et H_i l'hypothèse qu'on 
        est dans la classe i, alors la matrice de performance peut être 
        définie comme suit :
        
        >>> performance_matrix à n classes
        P(S(X_0)>S(not X_0)|H_0) P(S(X_0)>S(X_1)|H_0)     P(S(X_0)>S(X_2)|H_0)     ...
        P(S(X_1)>S(X_0)|H_1)     P(S(X_1)>S(not X_1)|H_1) P(S(X_1)>S(X_2)|H_1)     ...
        P(S(X_2)>S(X_0)|H_2)     P(S(X_2)>S(X_1)|H_2)     P(S(X_2)>S(not X_2)|H_2) ...
        ...
        
        Cas particulier, complémentarité des classes d'une classification 
        binaire (si on est pas dans l'hypothèse H_0 c'est qu'on est 
        obligatoirement dans l'hypothèse H_1) :
        
        >>> performance_matrix d'une classe binaire
        P(S(X_0)>S(X_1)|H_0)     P(S(X_0)>S(X_1)|H_0)
        P(S(X_1)>S(X_0)|H_1)     P(S(X_1)>S(X_0)|H_1)
        
        avec :
        
        >>> 
        P(S(X_0)>S(X_1)|H_0) = P(S(X_1)>S(X_0)|H_1)
        P(S(X_1)>S(X_0)|H_1) = P(S(X_0)>S(X_1)|H_0)
        P(S(X_0)>S(X_1)|H_0) + P(S(X_0)>S(X_1)|H_1) = 1
        P(S(X_0)>S(X_1)|H_0) + P(S(X_1)>S(X_0)|H_0) = 1
        
        Donc dans le cas binaire la matrice complète ne sert à rien car on 
        peut déduire l'ensemble des performances qu'avec un élément de la 
        matrice. Habituellement c'est P(S(X_1)>S(X_0)|H_1) qui est donné. 
        Il est important de noter que ceci n'est plus vrai pour une 
        classification supérieure à 2 classes car on ne peut plus exploiter 
        la complémentarité des hypothèses.
        
        See also
        --------
        process_roc, process_roc_theo
        """
        prod = list(product(range(self.nb_class), repeat=2))
        prod = chunker(prod, size)
        len_prod = int(np.ceil(self.nb_class**2/size))
        if verbose:
            prod = tqdm(
                prod,
                desc = f'{self.process_performance_matrix.__name__}',
                total = len_prod
            )
        with Parallel(n_jobs = n_jobs) as par:
            res = par(
                delayed(self._auc_par)(lot)
                for lot in prod
            )
        self.performance_matrix = pd.DataFrame(
            data = np.array(
                list(chain.from_iterable(res))
            ).reshape(self.nb_class, self.nb_class),
            columns = self.labels,
            index = self.labels
        )
        return self.performance_matrix

    def get_performance_matrix(self, **kargs):
        r"""
        Méthode de renvoit de l'attribut 'performance_matrix' si ce dernier 
        a été calculé.
        
        Parameters
        ----------
        **kargs :
            arguments de process_performance_matrix.
        
        Returns
        -------
        performance_matrix : pd.DataFrame
            DataFrame contenant la matrice de performance où 
            les noms des colonnes et indices font référence aux noms des 
            classes.
        
        See also
        --------
        process_performance_matrix
        """
        if not hasattr(self, 'performance_matrix'):
            return self.process_performance_matrix(**kargs)
        return self.performance_matrix

    def get_annalyse(self):
        r"""
        Méthode de renvoit de l'attribut 'analyse'.
        
        Returns
        -------
        analyse : Dict[str, Union[float, str]]
            pour lire facilement le contenu utilisé Pandas :
                pd.DataFrame(analyse)
        
        Notes
        -----
        Le contenu de 'analyse' varie en fonction des méthodes qui ont été 
        calculées.
        
        See also
        --------
        process_roc, process_roc_theo
        """
        return self.analyse

    def get_data_roc(self):
        r"""
        Méthode de récupération des calculs des courbes ROC. Si non calculés 
        exécute la méthode process_roc.
        
        Returns
        -------
        data_roc : List[List[float]]
            liste de calculs de chaque courbe ROC (si classification binaire 
            alors qu'une seule courbe ROC). Le format est :
                [[fpr, tpr, thresh, best_thresh, best_fpr, best_tpr, roc_auc, 
                nb_obs, idx_sel]]
        
        See also
        --------
        get_data_roc_theo, get_data_roc_bootstrap, process_roc
        """
        if not hasattr(self, 'data_roc'):
            self.process_roc()
        return self.data_roc

    def get_data_roc_bootstrap(self):
        r"""
        Méthode de récupération des calculs des courbes ROC Bootstrap. Si 
        non calculés exécute la méthode process_roc_bootstrap avec ces 
        valeurs par défaut.
        
        Returns
        -------
        data_roc_bootstrap: List[List[float]]
            liste de calculs de chaque courbe ROC par Monte-Calo. Le format 
            est :
                [[fpr, tpr, thresh, best_thresh, best_fpr, best_tpr, roc_auc, 
                nb_obs, idx_sel]]
        
        Notes
        -----
        Afin de récupérer tous les Monte-carlo par classe il suffit de faire :
        >>> data_roc_bootstrap = list(zip(*analyser.get_data_roc_bootstrap()))
        
        See also
        --------
        get_data_roc_theo, get_data_roc, process_roc_bootstrap
        """
        if not hasattr(self, 'data_roc_bootstrap'):
            self.process_roc_bootstrap()
        return self.data_roc_bootstrap

    def get_data_roc_theo(self):
        r"""
        Méthode de récupération des calculs des courbes ROC théoriques. Si non 
        calculés exécute la méthode process_roc_theo.
        
        Returns
        -------
        data_roc_theo : List[List[float]]
            liste de calculs de chaque courbe ROC (si classification binaire 
            alors qu'une seule courbe ROC). Le format est :
                [[fpr_theo, tpr_theo, thresh_theo, best_thresh_theo, 
                best_fpr_theo, best_tpr_theo, roc_auc_theo]]
        
        See also
        --------
        get_data_roc, get_data_roc_bootstrap, process_roc_theo
        """
        if not hasattr(self, 'data_roc_theo'):
            self.process_roc_theo()
        return self.data_roc_theo

    def _trim_axis(self, axis, length):
        r"""
        Méthode interne permettant de flatten les figures ainsi que de 
        supprimer les figures inutiles.
        """
        axs = axis.flat
        for ax in axs[length:]:
            ax.remove()
        return axs[:length]

    def _legend_manager(self):
        r"""
        Méthode interne permettant de rafraichir les légendes des figures.
        """
        if self.nb_class == 2:
            self.axis_roc[0].legend(loc = 4)
        else:
            for ii in range(self.nb_class):
                self.axis_roc[ii].legend(loc = 4, prop={'size': 8})

    def get_plot_roc(self):
        r"""
        Méthode de récupération des figures de la classe pour une 
        manipulation externe.
        
        Returns
        -------
        fig_roc : figure
        axis_roc : axes
        """
        return self.fig_roc, self.axis_roc

    def plot_roc_manager(self, number_columns: int=3):
        r"""
        Méthode d'initialisation des figures.
        
        Parameters
        ----------
        number_columns : int
            dans le cas d'un multi-plot permet de déterminer le nombre de 
            colonnes souhaité (le nombre de lignes sera calculé en fonction).
        
        Notes
        -----
        L'éxécution de cette méthode fait un RAZ des figures exitantes dans 
        la classe.
        """
        if number_columns > 0:
            if self.nb_class == 2:
                self.fig_roc, axis = plt.subplots(1, 1)
                self.axis_roc = np.array([axis])
                
            else:
                self.fig_roc, self.axis_roc = plt.subplots(
                    int(np.ceil(self.nb_class/number_columns)),
                    number_columns
                )
            if self.nb_class > 2:
                self.axis_roc = self._trim_axis(self.axis_roc, self.nb_class)
            for ii in range(self.nb_class) if self.nb_class > 2 else [0]:
                self.axis_roc[ii].set_aspect('equal', 'box')
                self.axis_roc[ii].grid()
        self.fig_roc.text(0.5, 0.04, 'Ratio faux positif', ha='center')
        self.fig_roc.text(
            0.04,
            0.5,
            'Ratio vrai positif',
            va='center',
            rotation='vertical'
        )
        return self

    def plot_roc(self, seuil_opti: bool=True, seuil_opti_values: bool=True):
        r"""
        Méthode d'affichage des courbes ROC dans un contexte bi-classe et 
        multi-classe.
        
        Parameters
        ----------
        seuil_opti : bool
            permet d'afficher le seuil optimal de la classe au sens de la 
            courbe ROC.
        seuil_opti_values : bool
            affiche sur la courbe la valeur du ratio de vrai positif et faux 
            positif pour le seuil optimal (utilisé seulement si 
            seuil_opti = True).
        
        Notes
        -----
        Si la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.process_roc` 
        est non éxécutée, exécution de cette dernière, idem pour la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.plot_roc_manager`.
        
        See also
        --------
        plot_roc_theo, plot_roc_bootstrap
        """
        if not hasattr(self, 'data_roc'):
            data_roc = self.process_roc().get_data_roc()
        else:
            data_roc = self.data_roc
        if not hasattr(self, 'axis_roc'):
            self.plot_roc_manager()
        for ii, mesure in enumerate(data_roc):
            if self.nb_class == 2:
                if not hasattr(self, 'data_roc_bootstrap'):
                    label = (
                        f'$P(X_1 > X_0)$ = {mesure[6]:.2}'
                        f'\nGini = {2*mesure[6]-1:.2}'
                    ) if self.labels is None else (
                        f'P($X_{self.labels[1]} > X_{self.labels[0]}$) = '
                        f'{mesure[6]:.2}'
                        f"\nGini = {2*mesure[6]-1:.2}"
                    )
                else:
                    label = (
                        f'$P(X_1>X_0)$={mesure[6]:.2f}$\pm$'
                        f"{self.analyse['roc_auc_bootstrap_std'][0]:.2f}"
                        f'\nGini={2*mesure[6]-1:.2f}$\pm$'
                        f"{2*self.analyse['roc_auc_bootstrap_std'][0]:.2f}"
                    ) if self.labels is None else (
                        f'P($X_{self.labels[1]}>X_{self.labels[0]}$)='
                        f'{mesure[6]:.2f}$\pm$'
                        f"{self.analyse['roc_auc_bootstrap_std'][0]:.2f}"
                        f'\nGini={2*mesure[6]-1:.2f}$\pm$'
                        f"{2*self.analyse['roc_auc_bootstrap_std'][0]:.2f}"
                    )
            else:
                if not hasattr(self, 'data_roc_bootstrap'):
                    label = f'AUC={mesure[6]:.2f}\nGini={2*mesure[6]-1:.2f}'
                else:
                    label = (
                        f'AUC={mesure[6]:.2f}$\pm$'
                        f"{self.analyse['roc_auc_bootstrap_std'][ii]:.2f}"
                        f'\nGini={2*mesure[6]-1:.2f}$\pm$'
                        f"{2*self.analyse['roc_auc_bootstrap_std'][ii]:.2f}"
                    )
            self.axis_roc[ii].plot(mesure[0], mesure[1], label = label)
            self.axis_roc[ii].plot([0, 1], [0, 1], 'r--', label = 'aléatoire')
            if seuil_opti:
                self.axis_roc[ii].plot(
                    [mesure[4], mesure[4]],
                    [0, mesure[5]],
                    color = '#A9A9AD',
                    linestyle = '--',
                    label = (
                        f'seuil opti {mesure[3]:.2}$\pm$'
                        f"{self.analyse['best_thresh_bootstrap_std'][ii]:.2f}"
                    ) if hasattr(self, 'data_roc_bootstrap') else (
                        f'seuil opti {mesure[3]:.2}'
                    )
                )
                self.axis_roc[ii].plot(
                    [0, mesure[4]],
                    [mesure[5], mesure[5]],
                    linestyle = '--',
                    color = '#A9A9AD'
                )
                if seuil_opti_values:
                    self.axis_roc[ii].text(
                        mesure[4],
                        0.07,
                        f"{mesure[4]:.2}",
                        rotation = -90,
                        verticalalignment = 'bottom',
                        color = '#A9A9AD',
                        fontsize = 8,
                        fontweight = 'bold'
                    )
                    self.axis_roc[ii].text(
                        0.07,
                        mesure[5],
                        f"{mesure[5]:.2}",
                        verticalalignment = 'bottom',
                        color = '#A9A9AD',
                        fontsize = 8,
                        fontweight = 'bold'
                    )
            if self.nb_class == 2:
                self.axis_roc[0].set_title(
                    "ROC curve Classe "
                    f"{'1' if self.labels is None else self.labels[1]}"
                )
            else:
                self.axis_roc[ii].set_title(
                    "ROC curve Classe "
                    f"{f'{ii}' if self.labels is None else self.labels[ii]}",
                    fontsize=10
                )
        self._legend_manager()
        return self

    def plot_roc_bootstrap(self):
        r"""
        Méthode d'affichage des courbes ROC boostrap dans un contexte 
        bi-classe et multi-classe.
        
        Notes
        -----
        Si la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.process_roc_bootstrap` 
        est non éxécutée, exécution de cette dernière, idem pour la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.plot_roc_manager`.
        
        See also
        --------
        plot_roc_theo, plot_roc
        """
        if not hasattr(self, 'data_roc_bootstrap'):
            data_roc_bootstrap = (
                self.process_roc_bootstrap().get_data_roc_bootstrap()
            )
        else:
            data_roc_bootstrap = self.data_roc_bootstrap
        if not hasattr(self, 'axis_roc'):
            self.plot_roc_manager()
        for data_roc in data_roc_bootstrap:
            for ii, mesure in enumerate(data_roc):
                self.axis_roc[ii].plot(
                    mesure[0],
                    mesure[1],
                    color = '#B5BDC4',
                    alpha = 0.5,
                    linewidth = 0.5
                )
        return self

    def plot_roc_theo(self,
                      seuil_opti: bool=True,
                      seuil_opti_values: bool=True):
        r"""
        Méthode d'affichage des estimations des courbes ROC théoriques dans un 
        contexte bi-classe et multi-classe.
        
        Parameters
        ----------
        seuil_opti : bool
            permet d'afficher le seuil optimal de la classe au sens de la 
            courbe ROC.
        seuil_opti_values : bool
            affiche sur la courbe la valeur du ratio de vrai positif et faux 
            positif pour le seuil optimal (utilisé seulement si 
            seuil_opti = True).
        
        Notes
        -----
        Si la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.process_roc_theo` 
        est non éxécutée, exécution de cette dernière, idem pour la méthode 
        :func:`~dstk.visualization._roc_analyser.ROCAnalyzer.plot_roc_manager`.
        
        See also
        --------
        plot_roc, plot_roc_bootstrap
        """
        if not hasattr(self, "data_roc_theo"):
            data_roc_theo = self.process_roc_theo().get_data_roc_theo()
        else:
            data_roc_theo = self.data_roc_theo
        if not hasattr(self, 'axis_roc'):
            self.plot_roc_manager()

        for ii, mesure in enumerate(data_roc_theo):
            if self.nb_class == 2:
                label = (
                    fr"ROC théo $P(X_1>X_0)$={mesure[6]:.2f}"
                    f"\nGini={2*mesure[6]-1:.2}"
                ) if self.labels is None else (
                    fr"ROC théo $P(X_{self.labels[1]}>X_{self.labels[0]})$="
                    f"{mesure[6]:.2f}\n"
                    f"Gini={2*mesure[6]-1:.2f}"
                )
            else:
                label = (
                    f"ROC théo AUC={mesure[6]:.2f}\n"
                    f"Gini={2*mesure[6]-1:.2f}"
                )
            self.axis_roc[ii].plot(
                mesure[0],
                mesure[1],
                label = label,
                linestyle = '--',
                color = '#83BF56'
            )
            if seuil_opti:
                self.axis_roc[ii].plot(
                    [mesure[4], mesure[4]],
                    [0, mesure[5]],
                    color = '#C9DABC',
                    linestyle = '--',
                    label = f'seuil opti théo {mesure[3]:.2}'
                )
                self.axis_roc[ii].plot(
                    [0, mesure[4]],
                    [mesure[5], mesure[5]],
                    linestyle = '--',
                    color = '#C9DABC'
                )
                if seuil_opti_values:
                    self.axis_roc[ii].text(
                        mesure[4],
                        0,
                        f"{mesure[4]:.2}",
                        rotation = -90,
                        verticalalignment = 'bottom',
                        color = '#C9DABC',
                        fontsize = 8,
                        fontweight = 'bold'
                    )
                    self.axis_roc[ii].text(
                        0,
                        mesure[5],
                        f"{mesure[5]:.2}",
                        verticalalignment = 'bottom',
                        color = '#C9DABC',
                        fontsize = 8,
                        fontweight = 'bold'
                    )
        self._legend_manager()
        return self

    def plot_roc_show(self):
        r"""
        Méthode permettant d'afficher les figures (pas besoin de relancer 
        tous les calculs si la fenêtre a été fermée).
        
        See also
        --------
        plot_roc, plot_roc_theo
        """
        self.fig_roc.show()
