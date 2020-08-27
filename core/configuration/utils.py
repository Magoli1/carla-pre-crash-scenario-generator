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


def get_duplicates(sequence):
    seen = set()
    seen_add = seen.add
    seen_twice = set(x for x in sequence if x in seen or seen_add(x))
    return list(seen_twice)
