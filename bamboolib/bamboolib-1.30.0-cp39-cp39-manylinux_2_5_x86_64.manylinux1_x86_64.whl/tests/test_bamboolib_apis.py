import bamboolib as bam
import pandas as pd


def test_all_high_level_user_apis():
    """Make sure all user exposed APIs are available and work"""

    df = pd.read_csv(bam.titanic_csv)

    # This doesn't replace a good integration check of course
    bam.show(df)
    bam.plot(df)
    bam.plot(df, "Age")
    bam.plot(df, "Age", "Sex")
    bam.predictors(df, "Survived")
    bam.patterns(df)
    bam.correlations(df)
