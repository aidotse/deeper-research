"""Aggregate screening files in /tmp/mc-expand/trav/*.tsv.

Each line: <id or null><TAB><decision><TAB><reason code or text>. Decisions: in, out, ?, pool, rej, merge, null.
Usage: proc.py counts | pending | adds | rejects   (adds/rejects print only papers not yet in the pool or rejected.md)
"""
import glob, os, re, sys
root = "/tmp/deeper-research-sim"
R = {
 "GEN": "a general machine-learning method, model, benchmark or application paper; it does not study generative models trained on model-generated data, which is the topic",
 "DET": "a machine-generated content detection or watermarking method; its contribution is detection accuracy, and it does not study recursive training or collapse",
 "ONCE": "synthetic data used once for training or analysis, with no recursive generate-and-retrain loop; matches the input's exclude theme of one-off synthetic data",
 "NC": "about neural collapse, the geometry of last-layer features; excluded by the input",
 "GAN": "mode collapse within one GAN training run, with no recursion over generations; excluded by the input",
 "SEC": "about data poisoning, backdoors or security of training; no generative model is trained on its own or another model's outputs across generations",
 "CL": "catastrophic forgetting or continual learning on real data; no model-generated training data, which is the topic",
 "MET": "a metric or evaluation method for generative models or synthetic data; it does not study recursive training on generated data",
 "DATA": "about dataset documentation, availability or governance; it does not study training on model-generated data",
 "SELF": "a self-training or self-improvement method whose contribution is task performance; it does not study degradation or its absence across generations of training on own outputs",
 "APP": "an applied systems, cloud or engineering paper; it does not study generative models trained on model-generated data",
 "SURV": "a general survey of LLM training data or synthetic data generation; model collapse is at most a passing mention, not its subject",
 "RL": "an RL or reasoning post-training method; it does not study degradation across generations of training on generated data",
 "OTH": "a paper from another field cited as background (linguistics, social science, optimisation or other); it does not study generative models trained on model-generated data",
 "PRIV": "about privacy or membership inference for synthetic data or generative models; no model is retrained on generated data across generations",
 "PERF": "performative prediction or strategic classification: the data shift comes from decisions acting on a population, not from training generative models on model-generated data",
 "EC": "about emergent communication between learning agents; it does not study generative models retrained on model-generated data across generations",
 "IL": "about iterated learning as a model of human language evolution or cognition; its subject is not generative models trained on model-generated data",
 "COL": "uses 'collapse' in another sense (model editing, representation, posterior, neural, physical or social collapse); it does not study training on model-generated data across generations",
 "BIO": "a biomedical paper on cellular autophagy, matched only by the word 'autophagy'; it is not about generative models",
 "UNREL": "about synthetic, recursive or accumulated data in an unrelated sense or application (simulation, augmentation, signal processing, feature selection); no generative model is retrained on model-generated data across generations",
 "SOC": "about AI's social, economic or cultural effects on humans; no model is retrained on model-generated data",
}
pool = set(re.findall(r'\]\(https://(?:arxiv\.org/abs/|api\.semanticscholar\.org/)([^)]+)\)', open(f"{root}/surveys/model-collapse.md").read()))
rej = set(re.findall(r'^\| \[([^\]]+)\]', open(f"{root}/graphs/model-collapse/rejected.md").read(), re.M))
mode = sys.argv[1]
files = sorted(glob.glob("/tmp/mc-expand/trav/*.tsv"), key=os.path.getmtime)
seen_add, seen_rej = set(), set()
for f in files:
    rows = [l.rstrip("\n").split("\t") for l in open(f) if l.strip()]
    name = os.path.basename(f)[:-4]
    if mode == "counts":
        from collections import Counter
        c = Counter(r[1] for r in rows)
        print(name, len(rows), dict(c))
    for r in rows:
        pid, dec = r[0], r[1]
        why = r[2] if len(r) > 2 else ""
        if mode == "pending" and dec == "?":
            print(name, pid, why)
        if mode == "adds" and dec == "in" and pid not in pool and pid not in seen_add:
            seen_add.add(pid); print(pid)
        if mode == "rejects" and dec == "out" and pid not in pool and pid not in rej and pid not in seen_rej:
            seen_rej.add(pid); print(f"{pid}\t{R.get(why, why)}")
        if mode == "check" and dec in ("pool",) and pid not in pool:
            print("NOT IN POOL but marked pool:", name, pid)
        if mode == "check" and dec == "in" and pid in rej:
            print("marked in but rejected earlier:", name, pid)
        if mode == "check" and dec == "out" and pid in pool:
            print("marked out but in pool:", name, pid)
        if mode == "check" and dec == "out" and why not in R and len(why.split()) < 6:
            print("short reason:", name, pid, why)
