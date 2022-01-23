import matplotlib

gui_env = [i for i in matplotlib.rcsetup.interactive_bk]
non_gui_backends = matplotlib.rcsetup.non_interactive_bk
print("Non Gui backends are:", non_gui_backends)
print("Gui backends are: ", gui_env)
for gui in gui_env + non_gui_backends:  # ['agg', 'tkAgg']:
    try:
        matplotlib.use(gui, force=True)
        from matplotlib import pyplot as plt

        plt.plot([1.5, 2.0, 2.5])
        fig = plt.gcf()
        fig.suptitle(gui)
        # plt.show()
        print(f"OK     {gui.rjust(10)} :" + matplotlib.get_backend())
    except Exception as _excp:
        print(f"FAILED {gui.rjust(10)} : {_excp}")
