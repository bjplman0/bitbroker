import random
from name_pools import NAME_POOLS, NAME_TEMPLATES

def generate_name(category_name):
    pools = NAME_POOLS.get(category_name)
    templates = NAME_TEMPLATES.get(category_name)

    if not pools or not templates:
        return f"Unknown-{category_name}"

    template = random.choice(templates)
    return template.format(**{key:random.choice(values) for key, values in pools.items()})