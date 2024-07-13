"""
Effects for agents are specified in .yml files; in order to
provide the data classes access to functions from effects files
without circular references, get_effects functions are specified
in effects files and then injected into data classes at initialization
"""