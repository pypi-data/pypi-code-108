"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""
import mypythontools

# mypythontools imports mylogging, so tests can fail. Turn off and run manually...
if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    mypythontools.utils.push_pipeline(test=True, deploy=True)
