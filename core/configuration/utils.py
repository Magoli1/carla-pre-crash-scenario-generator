def get_pipeline_step_names(pipeline_config):
    step_names = []
    for step in pipeline_config:
        if isinstance(step, dict):
            step_names.append(list(step.keys())[0])
        elif isinstance(step, str):
            step_names.append(step)
        else:
            raise Exception("Pipeline config not valid")
    return step_names
