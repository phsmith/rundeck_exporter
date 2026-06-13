import sys

# Strip pytest's own CLI args (file paths, flags) so that rundeck_exporter.args
# can use parse_args() without hitting unknown-argument errors at import time.
sys.argv = sys.argv[:1]
