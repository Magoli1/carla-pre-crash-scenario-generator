def get_pipeline_step_names(step_config):
    step_names = []
    for step in step_config:
        if isinstance(step, dict):
            step_names.append(list(step.keys())[0])
        elif isinstance(step, str):
            step_names.append(step)
        else:
            raise Exception("Pipeline config not valid")
    return step_names

def extract_pipeline_name(pipeline):
    return list(pipeline.keys())[0]

def extract_pipeline_config(pipeline):
    return list(pipeline.values())[0]
