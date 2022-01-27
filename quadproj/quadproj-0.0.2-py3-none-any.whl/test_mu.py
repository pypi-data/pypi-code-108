from quadrics import Quadric
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase
from matplotlib.collections import LineCollection

fontP = FontProperties()
fontP.set_size('xx-small')
mm = 3


def colored_line(x, y, s, e, cmap, ax, n_points, m=mm):
    lx = len(x)
    if m == 0:
        xx = x
        yy = y
        cc = np.arange(s, e)
    else:
        xx = x[m-1:lx-m+1]
        yy = y[m-1:lx-m+1]
        cc = np.arange(s+m-1, e-m+1)

    points = np.array([xx, yy]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0, n_points-1)
    if m == 0:
        lc = LineCollection(segments, cmap=cmap, norm=norm, linestyle='dotted')
    else:
        lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(cc)
    line = ax.add_collection(lc)
    if m != 0:
        colored_line(x[:m], y[:m], s, s+m, cmap, ax, n_points, 0)
        colored_line(x[lx-m:], y[lx-m:], e-m, e, cmap, ax, n_points, 0)
    return line


def test_mu_ellipse():
    text_params = {'ha': 'center', 'va': 'center', 'family': 'sans-serif',
                   'fontsize': 12}
    param = {}
    param['A'] = np.array([[-2, 0], [0, 1.2]])  # 2 and 1 or 2 and 1/2
    param['b'] = np.array([0, 0])
    param['c'] = -1
    param['projection_type'] = 'exact'
    Q = Quadric(param)
    fig, axs = plt.subplots(2, 2, figsize=(10, 7))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]
    ax1.axis('equal')
    Q.plot(ax1, fig)

    R = np.sort(-1/Q.eig)
    I = np.argsort(-1/Q.eig)
    X0 = np.array([0.1, 0.4])  # 0.3, 0.2  (0.3,0)
    x0 = X0  # Or transpose ? TBD
    x0_std = Q.to_standardized(X0)
    mu_min, x_min, _ = Q._get_lambda_dichotomy(x0, return_xd=True)
    mu_max, x_max, xd = Q._get_lambda_dichotomy(x0, flag_max=True, flag_all=True, return_xd=True)
    print('xd', xd)
    E = np.ones(Q.dim)
    L_diag = np.diag(Q.L)
    inv_I_lA = lambda l: np.dot(np.dot(Q.U, np.diag(1/(E+l*L_diag))), Q.U.T)
    n_points = 600  # 600
    points = [0, n_points//3, 2*n_points//3, n_points]
    colormap = cm.get_cmap('autumn', n_points)
    colormap = cm.get_cmap('RdYlBu_r', n_points)

    def x(mu):
        return inv_I_lA(mu) @ (x0 - 0.5*mu*Q.b)

    def fun(mu):
        _xx = x(mu)
        return _xx.T @ Q.A @ _xx + Q.b.T @ _xx + Q.c

    def d_fun(mu):
        _inv_I_lA = inv_I_lA(mu)
        out = (2*Q.A @ x(mu)+Q.b).T @ (-_inv_I_lA @ Q.A @ _inv_I_lA @ (x0 - 0.5*mu*Q.b)
                                       - 0.5 * _inv_I_lA @ Q.b)
        return out

    def norm(mu):
        return np.linalg.norm(x(mu)-x0)

    eps = 0.1  # 0.1
    mu_mid = (R[1]+R[0])/2
    mu_L = mu_mid-3
    mu_R = mu_mid+3
    mu1 = np.linspace(mu_L, R[0]-eps, n_points//3, endpoint=True)
    mu2 = np.linspace(R[0]+eps, R[1]-eps, n_points//3, endpoint=True)
    mu3 = np.linspace(R[1]+eps, mu_R, n_points//3, endpoint=True)
    mu = np.hstack((mu1, mu2, mu3))
    mu_ax1 = mu
    if X0[I[0]] == 0:
        mu_ax1 = np.hstack((np.linspace(mu_L, R[1]-eps, 2*(n_points//3), endpoint=True), mu3))
    elif X0[I[1]] == 0:
        mu_ax1 = np.hstack((mu1, np.linspace(R[0]+eps, mu_R, 2*(n_points//3), endpoint=True)))
    mu_ax1 = mu
    x_mu = []
    f_mu = []
    df_mu = []
    norm_mu = []
    print('Test', x(R[0]+0.00000001))
    flag_degenerate = False
    if np.any(x0 == 0):
        flag_degenerate = True

    for i, m in enumerate(mu):
        _x = x(mu_ax1[i])
        x_mu.append(_x)
        f_mu.append(fun(m))
        df_mu.append(d_fun(m))
        norm_mu.append(np.linalg.norm(x(m)-x0))

        if m > 0:
            color = 'purple'
        else:
            color = 'orange'
        color = colormap(i)
        if i in [-1]:
            color = 'red'
            _s = '%0.2f' % m
            ax1.text(x_mu[-1][0], x_mu[-1][1], _s, color=color)
        if not flag_degenerate:
            if i == 0:
                _s = r'$\mu \to -\infty$'
            #    ax1.text(x_mu[-1][0], x_mu[-1][1], _s)
            if i == n_points//3-1:
                _s = r'$\mu \to \frac{-1}{\lambda_2}$'
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == n_points//3:
                _s = r'$\mu \to \frac{-1}{\lambda_2}$'
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == 2*n_points//3-1:
                _s = r'$\mu \to \frac{-1}{\lambda_1}$'
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == 2*n_points//3:
                _s = r'$\mu \to \frac{-1}{\lambda_1}$'
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == n_points-1:
                _s = r'$\mu \to \infty$'
            #    ax1.text(x_mu[-1][0], x_mu[-1][1], _s)

        ax1.scatter(x_mu[-1][0], x_mu[-1][1], color=color, s=4)
        # ax2.scatter(m, fun(m), color=color)
    min_style = {'color': 'purple', 'marker': 'v', 'zorder': 2, 's': 12}
    max_style = {'color': 'purple', 'marker': 's', 'zorder': 2, 's': 12}
    min_style_2 = {'markeredgecolor': min_style['color'],
                   'markerfacecolor': min_style['color'], 'marker': min_style['marker'],
                   'zorder': min_style['zorder'], 'markersize': 6, 'color': 'w'}
    max_style_2 = {'markeredgecolor': max_style['color'],
                   'markerfacecolor': max_style['color'],
                   'marker': max_style['marker'],
                   'zorder': max_style['zorder'],
                   'markersize': 6, 'color': 'w'}
    legend_elements = [Line2D([0], [0], color='b', lw=2, label=r'$\mathcal{Q}(\Psi)$'),
                       Line2D([0], [0], label=r'$\mathbf{x}(\mu^*)$', **min_style_2),
                       Line2D([0], [0], label=r'$\mathbf{x}(\mu^{**})$', **max_style_2),
                       Line2D([0], [0], marker='x', color='w',
                              label=r'$\mathbf{x}^0 = \mathbf{x}(0)$',
                              markeredgecolor='red', markersize=8, zorder=2)]
    if flag_degenerate:
        legend_elements.append(
                       Line2D([0], [0], color='w', label=r'$\mathbf{x}^\mathrm{d}$',
                              marker='o', markerfacecolor='green', markersize=8, zorder=2)
        )
    fig.tight_layout(pad=2.1)

#    ax1.text(0.4, -0.2, r'$\mu \to \pm \infty$', **text_params)
    ax1.set_xlabel(r'$x_1$')
    ax1.set_ylabel(r'$x_2$')
    xlim1 = [-2, 2]
    ax1.axis('equal')
    ax1.set_xlim(xlim1)
    ax1.set_ylim(xlim1)
    
    ax1.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1, 0), prop=fontP)

    fig2, ax5 = plt.subplots()
    hexbins = ax5.hexbin([], [],
                         bins=20, gridsize=50, cmap=colormap)
    cb = fig.colorbar(hexbins, ax=ax1)
    cb.set_ticks([-0.1, 0.1])  # it's in percent so 10/100 = 0.1
    # vertically oriented colorbar
    cb.ax.set_yticklabels([r'$\mu \to -\infty$', r'$\mu \to \infty$'])
    color = 'tab:blue'
    print(x0, X0)
    print(Q.eig)
    if np.all(x0 != 0):
        colored_line(mu1, f_mu[points[0]:points[1]], points[0],
                     points[1], colormap, ax2, n_points, m=2)
        colored_line(mu2, f_mu[points[1]:points[2]], points[1],
                     points[2], colormap, ax2, n_points, m=5)
        colored_line(mu3, f_mu[points[2]:points[3]], points[2],
                     points[3], colormap, ax2, n_points, m=2)
    print(x0, I)
    print(x0[I[0]])
    if X0[I[0]] == 0:
        colored_line(np.hstack((mu1, mu2)), f_mu[points[0]:points[2]],
                     points[0], points[2], colormap, ax2, n_points, m=1)
        colored_line(mu3, f_mu[points[2]:points[3]], points[2], points[3],
                     colormap, ax2, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, f_mu[points[0]:points[1]], points[0], points[1],
                     colormap, ax2, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), f_mu[points[1]:points[3]],
                     points[1], points[3], colormap, ax2, n_points, m=1)


    # ax2.set_ylim([-1, 4])
    # xlim = [-4, 4]  # -2, 2
    labels = [r'$\mu \to -\infty$', r'$\frac{-1}{\lambda_2}$',
              r'$\frac{-1}{\lambda_1}$', r'$0$', r'$\mu \to \infty$']

    asymptot_linestyle = {'linestyle': 'dashed', 'color': 'grey'}
    for j in range(Q.dim):
        if X0[I[j]] != 0:
            ax2.plot([R[j], R[j]], [min(f_mu), max(f_mu)], **asymptot_linestyle)
            ax3.plot([R[j], R[j]], [min(norm_mu), max(norm_mu)], **asymptot_linestyle)
            ax4.plot([R[j], R[j]], [min(df_mu), max(df_mu)], **asymptot_linestyle)
    xlim = ax2.get_xlim()
    ax2.plot([xlim[0], xlim[1]], [0, 0], color='red', alpha=0.5, zorder=1)
    ticks = [xlim[0], R[I[1]], R[I[0]], 0, xlim[1]]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(labels)
    ax3.set_xticks(ticks)
    ax3.set_xticklabels(labels)
    ax4.set_xticks(ticks)
    ax4.set_xticklabels(labels)
    ax2.set_xlabel(r'$\mu$')
    ax2.set_ylabel(r'$f(\mu)$')
    ax2.set_xlim(xlim)
    ax2.yaxis.set_ticks_position('right')
    # ax2.set_xlim(xlim)
    if np.all(x0 != 0):
        colored_line(mu1, norm_mu[points[0]:points[1]], points[0], points[1],
                     colormap, ax3, n_points, m=2)
        colored_line(mu2, norm_mu[points[1]:points[2]], points[1], points[2],
                     colormap, ax3, n_points, m=6)
        colored_line(mu3, norm_mu[points[2]:points[3]], points[2], points[3],
                     colormap, ax3, n_points, m=2)
    if X0[I[0]] == 0:
        colored_line(np.hstack((mu1, mu2)), norm_mu[points[0]:points[2]], points[0],
                     points[2], colormap, ax3, n_points, m=1)
        colored_line(mu3, norm_mu[points[2]:points[3]], points[2], points[3],
                     colormap, ax3, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, norm_mu[points[0]:points[1]], points[0], points[1],
                     colormap, ax3, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), norm_mu[points[1]:points[3]],
                     points[1], points[3], colormap, ax3, n_points, m=1)

    ax3.set_xlabel(r'$\mu$')
    ax3.set_ylabel(r'$||\mathbf{x}^0 - \mathbf{x}(\mu)||_2$')
    ax3.set_xlim(xlim)
    # ax3.set_ylim([0, 1.95])
    if np.all(x0 != 0):
        colored_line(mu1, df_mu[points[0]:points[1]], points[0],
                     points[1], colormap, ax4, n_points, m=2)
        colored_line(mu2, df_mu[points[1]:points[2]], points[1],
                     points[2], colormap, ax4, n_points, m=50)
        colored_line(mu3, df_mu[points[2]:points[3]], points[2],
                     points[3], colormap, ax4, n_points, m=2)
    print('\n\n DF \n\n')
    print(mu3)
    if X0[I[0]] == 0:
        colored_line(mu3, df_mu[points[2]:points[3]], points[2],
                     points[3], colormap, ax4, n_points, m=1)
        colored_line(np.hstack((mu1, mu2)), df_mu[points[0]:points[2]],
                     points[0], points[2], colormap, ax4, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, df_mu[points[0]:points[1]], points[0],
                     points[1], colormap, ax4, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), df_mu[points[1]:points[3]],
                     points[1], points[3], colormap, ax4, n_points, m=1)

    # # Asymptot
    print(x0, x0)
    a0 = Q._get_asymptot_value(fun, x0_std, j=1, i=0)
    a1 = Q._get_asymptot_value(fun, x0_std, j=0, i=1)
    if np.any(Q.V != np.eye(Q.dim)) and True:
        a0_old = a0
        a0 = a1
        a1 = a0_old
    print('a0', a0)
    print('a1', a1)
    if not flag_degenerate:
        ax1.plot([a0, a0], [xlim1[0]-1, xlim1[1]+1], linestyle='dotted', color='grey')
        ax1.plot([xlim[0], xlim[1]], [a1, a1], linestyle='dotted', color='grey')
    flag_d = False
    print(xd)
    for _xd in xd:
        ax1.scatter(_xd[0], _xd[1], color='green', zorder=2)
        _norm = np.linalg.norm(_xd - x0)
        ax3.plot([xlim[0], xlim[1]], [_norm+0.1, _norm+0.1], color='green')
        x_text = xlim[1] + (R[1] - xlim[1])/3*2
        ax3.text(x_text, _norm+0.2,
                 r'$||\mathbf{x}^0 - \mathbf{x}^\mathrm{d}||_2$', color='green')
        if x0[0] == 0:
            ax1.plot([0, _xd[0]], [_xd[1], _xd[1]], color='grey', zorder=0)
        else:
            ax1.plot([_xd[0], _xd[0]], [0, _xd[1]], color='grey', zorder=0)
    if len(xd) == 0 and flag_degenerate:
        if x0[0] == 0:
            _s = x0[1]/(1+Q.eig[1]/Q.eig[0])
            ax1.plot([-1, 1], [_s, _s], color='grey', zorder=0)
        else:
            _s = x0[0]/(1+Q.eig[0]/Q.eig[1])
            ax1.plot([_s, _s], [-1, 1], color='grey', zorder=0)

    if False:
        for i in range(Q.dim):
            if x0[i] == 0:
                if i == 1:
                    # j1 = 0
                    # j2 = 1
                    # ax1.plot([0, 0], [xlim[0]+2, xlim[1]-2], color='grey', zorder=0)
                    # ax1.scatter([0, 0], [-np.sqrt(abs((1-0**2*Q.eig[j1])/Q.eig[j2])),
                    # np.sqrt(abs((1-0**2*Q.eig[j1])/Q.eig[j2]))], color='green')
                    mu = -1/Q.eig[1]
                    _x = x0[0] / (1+mu*Q.eig[0])
                    print('eig', Q.eig, x0, _x)
                    ylim1 = ax1.get_ylim()
                    ylim1 = [ylim1[0], ylim1[1]]
                    _y = ylim1[1]
                    flag_d = False
                    if (1-Q.eig[0]*_x**2)/Q.eig[1] > 0:
                        flag_d = True
                        _y = np.sqrt((1-Q.eig[0]*_x**2)/Q.eig[1])
                        ax1.scatter([_x, _x], [-_y, _y], color='green', zorder=2)
                        _d_1 = np.array([_x, _y])
                        _d_2 = np.array([_x, _y])
                        _norm = [np.linalg.norm(_d_1 - x0), np.linalg.norm(_d_2 - x0)]
                        ax3.plot([xlim[0], xlim[1]], [_norm[0]+0.1, _norm[0]+0.1],
                                 color='green')
                    ax1.text(_x+0.1, _y/2, '$d$')
                    x_text = xlim[1] + (R[1] - xlim[1])/3*2
                    if not flag_d:
                        _y = ylim1[1]
                    ax1.plot([_x, _x], [-_y, _y], color='grey', zorder=0)
                else:
                    # j1 = 1
                    # j2 = 0
                    # ax1.plot([xlim1[0], xlim1[1]], [0, 0], color='grey', zorder=0)
                    # ax1.scatter([-np.sqrt((1-0**2*Q.eig[j1])/Q.eig[j2]), np.sqrt((1-0**2*Q.eig[j1])/Q.eig[j2])], [0, 0], color='green')
                    mu = -1/Q.eig[0]
                    _x = x0[1] / (1+mu*Q.eig[1])
                    _y = xlim1[1]
                    flag_d = False
                    print(x0, x0[1])
                    if (1-Q.eig[1]*_x**2)/Q.eig[0] > 0:
                        flag_d = True
                        _y = np.sqrt((1-Q.eig[1]*_x**2)/Q.eig[0])
                        ax1.scatter([-_y, _y], [_x, _x], color='green', zorder=2)
                        ax1.text(-_y-0.5, _x, '$d$')
                    ax1.plot([xlim1[0], xlim1[1]], [_x, _x], color='grey', zorder=0)
                    _d_1 = np.array([-_y, _x])
                    _d_2 = np.array([_y, _x])
                    _norm = [np.linalg.norm(_d_1 - x0), np.linalg.norm(_d_2 - x0)]
                    x_text = xlim[0] + (R[0] - xlim[0])/2
                    ax3.plot([xlim[0], xlim[1]], [_norm[0], _norm[0]], color='green')
                if flag_d:
                    ax3.text(x_text, _norm[0]+0.2,
                             r'$||\mathbf{x}^0 - \mathbf{x}^\mathrm{d}||_2$',
                             color='green')

    ax4.set_xlabel(r'$\mu$')
    ax4.set_ylabel(r'$f^\prime(\mu)$')
    ax4.yaxis.set_ticks_position('right')
    ax4.set_xlim(xlim)
    # ax4.set_ylim([-50, 50])
    ax1.scatter(x0[0], x0[1], color='red', marker='x')
    if x_min is not None:
        ax1.scatter(x_min[0], x_min[1], **min_style)
        ax2.scatter(mu_min, fun(mu_min), **min_style)
        ax3.scatter(mu_min, norm(mu_min), **min_style)
        ax4.scatter(mu_min, d_fun(mu_min), **min_style)
        ax1.scatter(x_max[0], x_max[1], **max_style)
        ax2.scatter(mu_max, fun(mu_max), **max_style)
        ax3.scatter(mu_max, norm(mu_max), **max_style)
        ax4.scatter(mu_max, d_fun(mu_max), **max_style)
    plt.close(fig2)
    fig.savefig('tmp/changes_mu/x_trajectories_mu.png')
    fig.savefig('tmp/changes_mu/x_trajectories_mu.pdf')
    plt.show()

