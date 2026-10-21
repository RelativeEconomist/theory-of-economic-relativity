"""
Reusable executable TER scenarios.

Numbered tests in research/tests remain the source of truth for each
economic question and its hypotheses. A scenario moves here only when a
real second consumer, such as a research.adapters adapter, needs it; the
numbered test then imports it. Adapters import scenarios and contain no
economic mechanisms. A scenario and its adapter share a filename where
practical.
"""
