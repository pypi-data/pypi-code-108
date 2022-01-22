from datetime import datetime
from argparse import ArgumentParser 


MODELS = [ "Rich", "Muon", "GlobalPID", "GlobalMuonId" ]
PARTICLES = [ "Muon", "Pion", "Kaon", "Proton" ]
SAMPLES = [ "2016MagUp", "2016MagDown" ]


def argparser ( description = None, avoid_arguments = None ):   # TODO complete docstring
  """Return a parser with a set of default arguments.

  Parameters
  ----------
    description : `str`, optional
      Description for the ArgumentParser object 
      (`None`, by default).

    avoid_arguments : `list` of `str`, optional
      ...

  Returns
  -------
    parser : `argparse.ArgumentParser`
      Parser with default arguments.
  """
  if avoid_arguments is None:
    avoid_arguments = []
  if isinstance (avoid_arguments, str):
    avoid_arguments = [avoid_arguments]
  if not isinstance (avoid_arguments, list):
    raise ValueError ("Arguments to avoid should be passed as list of strings.")

  timestamp = str (datetime.now()) . split (".") [0]
  timestamp = timestamp . replace (" ","_")
  version = ""
  for time, unit in zip ( timestamp.split(":"), ["h","m","s"] ):
    version += time + unit   # YYYY-MM-DD_HHhMMmSSs

  parser = ArgumentParser ( description = description )
  if "model" not in avoid_arguments:
    parser . add_argument ( "-m" , "--model", required = True, choices = MODELS )
  if "particle" not in avoid_arguments:
    parser . add_argument ( "-p" , "--particle", required = True, choices = PARTICLES ) 
  if "sample" not in avoid_arguments:
    parser . add_argument ( "-s" , "--sample", required = True, choices = SAMPLES ) 
  if "version" not in avoid_arguments:
    parser . add_argument ( "-v" , "--version", default = timestamp )

  return parser
