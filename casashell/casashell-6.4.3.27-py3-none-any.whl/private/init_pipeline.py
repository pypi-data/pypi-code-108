
# eventually the warnings here should be errors, causing casa --pipeline to exit

pipelineOK = True

try:
    import pipeline
except:
    print("WARN: could not import pipeline")
    pipelineOK = False
    config.startup_log.append(("could not import pipeline","WARN"))

if  pipelineOK:
    try:
        pipeline.initcli()
    except:
        print("WARN: pipeline.initcli() failed")
        config.start_log.append(("pipeline.initcli() failed","WARN"))
