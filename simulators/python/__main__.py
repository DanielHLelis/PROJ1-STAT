if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Args: {trial_count} {n} {p0} {s0} {tr} [beta] [seed]")
        exit(1)

    trial_count = int(sys.argv[1])

    n = int(sys.argv[2])
    p0 = float(sys.argv[3])
    s0 = int(sys.argv[4])

    tr = INF if sys.argv[5].strip().lower().startswith(
        'inf') else int(sys.argv[5])

    beta = 0 if len(sys.argv) < 7 else float(sys.argv[6])
    seed = int(time.time() * 1000) if len(sys.argv) < 8 else int(sys.argv[7])

    data = multiple_trials(trial_count, n, p0, s0, tr, beta, seed)

    def escape(x): return str(x).replace('.', '_')

    try:
        os.mkdir('results')
    except Exception as _:
        pass

    file_name = f'results/{trial_count}-{n}-{escape(p0)}-{s0}-{tr}-{escape(beta)}-{seed}.json'

    with open(file_name, 'w') as f:
        json.dump(data, f)
