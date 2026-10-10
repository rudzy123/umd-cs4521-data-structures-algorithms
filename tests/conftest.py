"""Hypothesis settings shared by every test module."""

from hypothesis import settings

settings.register_profile("lab", max_examples=40, deadline=None, derandomize=True)
settings.load_profile("lab")
