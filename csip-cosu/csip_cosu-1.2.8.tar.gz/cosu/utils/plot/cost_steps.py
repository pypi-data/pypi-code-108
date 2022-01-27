import matplotlib.pyplot as plt
import numpy as np


def rs_key(round, step):
    return "r{}s{}".format(round, step)


def get_values(name, s, steps):
    nrounds = steps['rounds']
    vals = []
    for r in range(1, nrounds + 1):
        info = steps[rs_key(r, s)]
        params = info[s - 1]['param']
        for i, p in enumerate(params):
            if name == p['name']:
                vals.append(p['value'])
    return vals


col = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']


def plot_cost_steps(optimizer, step_trace):
    nsteps = step_trace['steps']
    nrounds = step_trace['rounds']
    iter = step_trace['iters']
    particles = step_trace['particles']
    time = step_trace['time']

    total_iter = iter * nrounds

    x = np.arange(1, total_iter + 1)
    f = plt.figure(figsize=(15, 15))

    # top plot
    plt.subplot(nsteps + 1, 1, 1)

    for i in range(nsteps):
        plt.plot(x, optimizer[i].cost_history, label='step ' + str(i + 1), color=col[i + 2])

    mini = optimizer[0].cost_history
    for i in range(1, nsteps):
        mini = np.maximum(mini, optimizer[i].cost_history)

    for i, it in enumerate(range(iter, total_iter + 1, iter)):
        plt.axvline(x=it, color='lightgray', linestyle='--')
        plt.text(it, mini[0], ' R' + str(i + 1), color='lightgray')

    plt.xlim(0, iter * nrounds)
    plt.title('cost function\n (rounds:{} iter:{} particles:{} time:{})'.format(nrounds, iter, particles, time))
    plt.legend()

    px = np.arange(iter, (nrounds + 1) * iter, iter)
    for s in range(1, nsteps + 1):

        a = plt.subplot(nsteps + 1, 1, s + 1)

        plt.subplots_adjust(hspace=0.3)
        plt.xlim(0, iter * nrounds)
        if s == nsteps:
            plt.xlabel('Iterations')

        # rounds marks
        for i, it in enumerate(range(iter, total_iter + 1, iter)):
            plt.axvline(x=it, color='lightgray', linestyle='--')

        info = step_trace[rs_key(1, s)][s - 1]
        # print(info['param'])
        i = 0
        params = info['param']

        p = params[i]
        # print('ax   ', plt)
        vals = get_values(p['name'], s, step_trace)
        title = "{}:{:.5f}".format(p['name'], vals[-1])
        a.plot(px, vals, 'v', label=p['name'], color=col[i])
        a.axhline(p['bounds'][0], linestyle='--', color='lightgray')
        a.axhline(p['bounds'][1], linestyle='--', color='lightgray')
        a.set_ylabel(p['name'], color=col[i])
        a.tick_params(axis='y', labelcolor=col[i])
        for x, y in zip(px, vals):
            label = "{:.5f}".format(y)
            a.annotate(label, (x, y), textcoords="offset points", xytext=(0, 10),
                       color="gray", ha='center')
        a.legend(loc="center left")

        if (len(params) > 1):
            sp = a.twinx()
            i = i + 1
            p = params[i]
            vals = get_values(p['name'], s, step_trace)
            title = "{} {}:{:.5f}".format(title, p['name'], vals[-1])
            # title = title + ', ' + p['name'] + ':' + str(vals[-1])
            sp.plot(px, vals, 'v', label=p['name'], color=col[i])
            sp.axhline(p['bounds'][0], linestyle='--', color='lightgray')
            sp.axhline(p['bounds'][1], linestyle='--', color='lightgray')
            sp.set_ylabel(p['name'], color=col[i])
            sp.tick_params(axis='y', labelcolor=col[i])
            for x, y in zip(px, vals):
                label = "{:.5f}".format(y)
                sp.annotate(label, (x, y), textcoords="offset points", xytext=(0, 10),
                            color="gray", ha='center')
            sp.legend(loc="right")

        # print(s, params)
        plt.legend()
        plt.title("step {}  ({})".format(s, title))

    plt.xlabel('Iterations')
    plt.show()
