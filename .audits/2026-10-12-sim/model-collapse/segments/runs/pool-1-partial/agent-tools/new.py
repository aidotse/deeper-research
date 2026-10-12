"""Print the IDs from argv/stdin that are neither in the survey pool nor in rejected.md."""
import re, sys
root = "/tmp/deeper-research-sim"
pool = set(re.findall(r'\]\(https://(?:arxiv\.org/abs/|api\.semanticscholar\.org/)([^)]+)\)', open(f"{root}/surveys/model-collapse.md").read()))
rej = set(re.findall(r'^\| \[([^\]]+)\]', open(f"{root}/graphs/model-collapse/rejected.md").read(), re.M))
ids = sys.argv[1:] or sys.stdin.read().split()
for i in ids:
    tag = "POOL" if i in pool else "REJ" if i in rej else "NEW"
    print(tag, i)
