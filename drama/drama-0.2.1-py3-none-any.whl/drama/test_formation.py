from drama.io import cfg
from drama.mission.timeline import FormationTimeline
import stereoid.utils.config as st_config

if __name__ == '__main__':
    paths = st_config.parse(section="Paths")
    stereoid_dir = paths["main"]
    pardir = paths["par"]

    runid = "XTI_model_support"
    parfile = pardir.joinpath("Hrmny_%s.cfg" % runid)
    conf = cfg.ConfigFile(parfile)
    form_id = conf.formation.id
    print("formation id: %s" % form_id)
    ftl = FormationTimeline(parfile, secondary=True)

