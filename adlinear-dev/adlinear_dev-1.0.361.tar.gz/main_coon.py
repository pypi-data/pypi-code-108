# import itertools
# import os
import argparse
from transparentpath import Path
import numpy as np
import pandas as pd
from adlinear import nmfmodel as nmf
from randomgenerators import randomgenerators as rng
import dotenv

Path.set_global_fs("gcs", bucket="nmf_experiments_dev", token="cred_gcs.json")
dotenv.load_dotenv()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Creates the yaml file to launch several iterations of a program on GCP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-o", "--output", type=str, default="wfold_scree_plots.csv", help="Output file path")
    parser.add_argument("-r", "--runs", type=int, default=1, help="Number of iterations per node")
    parser.add_argument("-w", "--writefreq", type=int, default=1, help="Write frequency")
    parser.add_argument("-e", "--epsilon", type=float, default=0.10, help="Epsilon")
    parser.add_argument("-m", "--ncmin", type=int, default=2, help="Minimum number of components")
    parser.add_argument("-M", "--ncmax", type=int, default=45, help="Maximum number of components")
    parser.add_argument("-W", "--w_avg", type=int, default=2, help="Average size of W clusters")
    parser.add_argument("-H", "--h_avg", type=int, default=10, help="Average size of H clusters")
    # parser.add_argument("-a", "--wclust_f", type=float, default=1.0, help="#W clusters to #H clusters maximum ratio")
    parser.add_argument("-i", "--icorrmin", type=float, default=0.5, help="Minimum intra-cluster correlation")
    parser.add_argument("-I", "--icorrmax", type=float, default=0.95, help="Maximum intra-cluster correlation")
    parser.add_argument("-x", "--xcorrmin", type=float, default=0.0, help="Minimum extra-cluster correlation")
    parser.add_argument("-X", "--xcorrmax", type=float, default=0.5, help="Maximum extra-cluster correlation")
    parser.add_argument("-p", "--do_entropy", type=bool, default=False, help="Optional entropy calculation")
    args = parser.parse_args()
    outputpath = Path(args.output)
    epsilon = args.epsilon
    ncmin = args.ncmin
    ncmax = args.ncmax
    nruns = args.runs
    # wclust_f = args.wclust_f
    w_avg = args.w_avg
    h_avg = args.h_avg
    do_ent = args.do_entropy
    icorrmin = args.icorrmin
    icorrmax = args.icorrmax
    xcorrmin = args.xcorrmin
    xcorrmax = args.xcorrmax
    writefreq = args.writefreq

    print(f"Will execute {nruns} run(s), will write output(s) in {outputpath} every {writefreq} iteration(s)")

    rand_norms = True
    df_mini_scree_plots = pd.DataFrame(index=[], columns=[])
    for itrial in range(nruns):
        nb_clusters = np.random.randint(low=ncmin, high=ncmax)
        intra_corr = np.random.uniform(low=icorrmin, high=icorrmax)
        xtra_corr = np.random.uniform(low=xcorrmin, high=xcorrmax)
        h_size = h_avg * nb_clusters
        # w_size = np.random.randint(low=max(nb_clusters, int(h_size / 5.0)), high=5*h_size)
        w_size = np.random.randint(low=max(nb_clusters, int(h_size / 5.0)), high=5 * h_size)
        eps = np.random.uniform(low=0.0, high=epsilon)
        # TODO: lift the constraint that W and H have same number of clusters
        # w_avg = h_avg
        # nb_w_clusters = max(int(w_size / w_avg), 1)
        nb_w_clusters = nb_clusters
        w_avg = int(w_size / nb_w_clusters)
        # wclust_factor = np.random.uniform(0.0, wclust_f)

        generated_M, _, _, _ = rng.generate_nmf_reconstruction(n_comp=nb_clusters, n_feat=h_size, n_obs=w_size,
                                                               h_icorr_min=icorrmin, h_icorr_max=xcorrmax,
                                                               w_icorr_min=xcorrmin, w_icorr_max=icorrmax,
                                                               random_norms=rand_norms, epsilon=eps,
                                                               avg_h_clust=h_avg,
                                                               avg_w_clust=w_avg)
        rnstr = "RandNorms" if rand_norms else "ConstNorms"

        df_scree_plot = nmf.generate_scree_plot(generated_M, ncmin=ncmin, ncmax=ncmax, known_ncomp=nb_clusters,
                                                do_entropies=do_ent)
        df_mini_scree_plots = nmf.collect_windows_from_scree_plot(df_collected_windows=df_mini_scree_plots,
                                                                  df_scree_plot=df_scree_plot, known_ncomp=nb_clusters,
                                                                  ncomp_margin=5)

        if itrial % writefreq == 0 or itrial == nruns-1:
            print(f"Saving iteration {itrial} in {outputpath}")
            # assert not df_mini_scree_plots.empty
            outputpath.write(df_mini_scree_plots)
            # df_scree_plot.to_csv(args.output.split(".csv")[0]+f"_scp{itrial}_nc{nb_clusters}.csv")
            assert outputpath.isfile()
            assert not outputpath.read().empty
