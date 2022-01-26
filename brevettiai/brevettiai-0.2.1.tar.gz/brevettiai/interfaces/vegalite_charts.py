import altair as alt
import pandas as pd
import numpy as np


def make_selector_chart(df, x_name, y_name, chart_text, selector, color="red", size=10, scale_type="linear"):
    chart_line = alt.Chart(df).mark_line(color='green').encode(
        x=alt.X(x_name, scale=alt.Scale(type=scale_type)),
        y=alt.Y(y_name, scale=alt.Scale(type=scale_type)))

    chart_text = alt.Chart(df).mark_text(align='left',baseline='middle', dx=7, fontSize=20).encode(
        x=alt.X(x_name, scale=alt.Scale(type=scale_type)),
        y=alt.Y(y_name, scale=alt.Scale(type=scale_type)),
        text=chart_text,
        color=alt.condition(selector, alt.value(color), 'security_threshold')).add_selection(selector)
    chart_layered = alt.layer(chart_line, chart_text)
    return chart_layered


def make_security_selection(devel_pred_output, classes):
    step = 1
    rng = np.arange(0.0, 100+step, step)

    security_charts = []

    for cl in classes:
        sec_level = '{}_security_level'.format(cl)
        select_security = alt.selection_single(on='mouseover', nearest=True, empty='none')
        scores_accept = devel_pred_output[devel_pred_output.category.apply(lambda x: cl in x)]["prob_" + cl].values
        scores_reject = devel_pred_output[devel_pred_output.category.apply(lambda x: cl not in x)]["prob_" + cl].values

        FRR = [0.0 if len(scores_accept)==0 else (scores_accept < thr/100).sum()/len(scores_accept ) for thr in rng]
        TRR = [0.0 if len(scores_reject)==0 else (scores_reject < thr/100).sum()/len(scores_reject) for thr in rng]

        ROC_df = pd.DataFrame({'FRR': FRR, 'TRR': TRR+1e-5*rng, sec_level: rng,
                               'security_threshold': ['security_level']*len(rng)})

        ROC_comb_alt = make_selector_chart(df=ROC_df, x_name='TRR', y_name='FRR', chart_text=sec_level,
                                           selector=select_security)\
            .properties(title=sec_level)\
            .configure_title(fontSize=24, anchor='start', color='green').interactive().to_json()

        security_charts.append(ROC_comb_alt)
    return security_charts


def dataset_summary(samples):
    if isinstance(samples, pd.DataFrame):
        samples = samples.copy()
    else:
        samples = pd.DataFrame(list(samples) if isinstance(samples, np.ndarray) else samples)

    samples["category"] = samples["category"].apply(lambda x: x if isinstance(x, str) else "/".join(x))

    samples = samples.groupby(["dataset", "category"]) \
        .size().reset_index(name="samples")

    chart = alt.Chart(samples) \
        .mark_bar() \
        .encode(x='samples',
                y='dataset',
                color='category',
                order=alt.Order(
                    'category',
                    sort='ascending'
                ),
                tooltip = ['samples', 'dataset', 'category']) \
        .configure_axis(labelLimit=30)

    return chart.to_json()
