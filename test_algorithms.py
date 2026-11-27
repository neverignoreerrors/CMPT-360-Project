import random
import statistics
import time


# =====================================================================
# Shared helpers
# =====================================================================

def build_coverage(oranges, cacti, sprinklers, radii):
    """Return (orangeCoverage, cactusCoverage): one set of indices per sprinkler."""
    orangeCoverage = []
    cactusCoverage = []
    for i in range(len(sprinklers)):
        orangeCoverage.append({j for j in range(len(oranges))
                               if abs(sprinklers[i] - oranges[j]) <= radii[i]})
        cactusCoverage.append({j for j in range(len(cacti))
                               if abs(sprinklers[i] - cacti[j]) <= radii[i]})
    return orangeCoverage, cactusCoverage


def eliminate_dominated(orangeCoverage, cactusCoverage):
    """Return the list of surviving sprinkler indices after dominance elimination.
    B dominates A if B covers every orange A covers and waters no cactus A doesn't.
    Among equivalent sprinklers, the smallest index survives."""
    s = len(orangeCoverage)
    eliminated = set()
    for a in range(s):
        for b in range(s):
            if a == b:
                continue
            bDominatesA = (orangeCoverage[a] <= orangeCoverage[b]
                           and cactusCoverage[b] <= cactusCoverage[a])
            if not bDominatesA:
                continue
            equivalent = (orangeCoverage[a] == orangeCoverage[b]
                          and cactusCoverage[a] == cactusCoverage[b])
            if equivalent:
                if a > b:
                    eliminated.add(a)
            else:
                eliminated.add(a)
    return [i for i in range(s) if i not in eliminated]


def find_mandatory_sprinklers(orangeCoverage, numOranges, remainingSprinklers=None):
    """Set of sprinklers that are the only (surviving) cover of some orange,
    or None if some orange has no covering sprinkler (infeasible)."""
    if remainingSprinklers is None:
        remainingSprinklers = list(range(len(orangeCoverage)))

    mandatory = set()
    for orange in range(numOranges):
        coverers = []
        for i in remainingSprinklers:
            if orange in orangeCoverage[i]:
                coverers.append(i)

        if len(coverers) == 0:
            return None
        if len(coverers) == 1:
            mandatory.add(coverers[0])
    return mandatory


# =====================================================================
# Algorithm 1: baseline
# Exhaustive search over all sprinkler subsets.
# Returns (minCost, selectedPositions), or (None, None) if infeasible.
# =====================================================================

def baseline(oranges, cacti, sprinklers, radii):
    s = len(sprinklers)
    bestCost = float("inf")
    bestMask = None

    for mask in range(1 << s):
        active = [i for i in range(s) if (mask >> i) & 1]

        valid = True
        for orange in oranges:
            covered = False
            for i in active:
                if abs(sprinklers[i] - orange) <= radii[i]:
                    covered = True
                    break
            if not covered:
                valid = False
                break

        if valid:
            cost = 0
            for cactus in cacti:
                for i in active:
                    if abs(sprinklers[i] - cactus) <= radii[i]:
                        cost += 1
                        break
            if cost < bestCost:
                bestCost = cost
                bestMask = mask

    if bestMask is None:
        return None, None
    return bestCost, [sprinklers[i] for i in range(s) if (bestMask >> i) & 1]


# =====================================================================
# Algorithm 2: fast
# Coverage preprocessing, dominance elimination, and pruning.
# Returns (minCost, selectedPositions, r), where r = surviving sprinklers.
# =====================================================================

def fast(oranges, cacti, sprinklers, radii):
    orangeCoverage, cactusCoverage = build_coverage(oranges, cacti, sprinklers, radii)
    remaining = eliminate_dominated(orangeCoverage, cactusCoverage)
    r = len(remaining)
    allOranges = set(range(len(oranges)))

    bestCost = float("inf")
    bestMask = None

    for mask in range(1 << r):
        active = []
        coveredByMask = set()
        for j in range(r):
            if (mask >> j) & 1:
                i = remaining[j]
                active.append(i)
                coveredByMask |= orangeCoverage[i]

        if coveredByMask != allOranges:
            continue                      # invalid: skip cactus work

        cactiWatered = set()
        pruned = False
        for i in active:
            cactiWatered |= cactusCoverage[i]
            if len(cactiWatered) >= bestCost:
                pruned = True
                break
        if pruned:
            continue

        if len(cactiWatered) < bestCost:
            bestCost = len(cactiWatered)
            bestMask = mask

    if bestMask is None:
        return None, None, r
    selected = [sprinklers[remaining[j]] for j in range(r) if (bestMask >> j) & 1]
    return bestCost, selected, r


# =====================================================================
# Algorithm 3: fast_mandatory
# Everything in fast(), plus mandatory sprinkler detection.
# Returns (minCost, selectedPositions, r, numMandatory),
# or (None, None, r, 0 or numMandatory) if infeasible.
# =====================================================================

def fast_mandatory(oranges, cacti, sprinklers, radii):
    orangeCoverage, cactusCoverage = build_coverage(oranges, cacti, sprinklers, radii)
    remaining = eliminate_dominated(orangeCoverage, cactusCoverage)
    r = len(remaining)
    allOranges = set(range(len(oranges)))

    mandatory = find_mandatory_sprinklers(orangeCoverage, len(oranges), remaining)
    if mandatory is None:
        return None, None, r, 0

    mandatoryOranges = set()
    mandatoryCacti = set()
    for i in mandatory:
        mandatoryOranges |= orangeCoverage[i]
        mandatoryCacti |= cactusCoverage[i]

    # Early termination: mandatory sprinklers already cover every orange.
    if mandatoryOranges == allOranges:
        selected = [sprinklers[i] for i in sorted(mandatory)]
        return len(mandatoryCacti), selected, r, len(mandatory)

    # Enumerate subsets of the optional sprinklers only (bit j -> optional[j],
    # whose entries are original sprinkler indices).
    optional = [i for i in remaining if i not in mandatory]
    k = len(optional)
    bestCost = float("inf")
    bestOptional = None

    for mask in range(1 << k):
        chosen = [optional[j] for j in range(k) if (mask >> j) & 1]

        covered = set(mandatoryOranges)           # fresh copy per candidate
        for i in chosen:
            covered |= orangeCoverage[i]
        if covered != allOranges:
            continue                              # invalid: skip cactus work

        watered = set(mandatoryCacti)             # mandatory cacti always count
        pruned = len(watered) >= bestCost
        if not pruned:
            for i in chosen:
                watered |= cactusCoverage[i]
                if len(watered) >= bestCost:
                    pruned = True
                    break
        if pruned:
            continue

        bestCost = len(watered)
        bestOptional = chosen

    if bestOptional is None:
        return None, None, r, len(mandatory)

    selected = [sprinklers[i] for i in sorted(mandatory | set(bestOptional))]
    return bestCost, selected, r, len(mandatory)


# =====================================================================
# Instance generators
# =====================================================================

MIN_POS, MAX_POS = 0, 20
MIN_RADIUS, MAX_RADIUS = 0, 5


def generate_case():
    """Unconstrained random instance (robustness tests; may be infeasible)."""
    numOranges = random.randint(1, 5)
    numCacti = random.randint(0, 5)
    numSprinklers = random.randint(1, 10)

    oranges = [random.randint(MIN_POS, MAX_POS) for _ in range(numOranges)]
    cacti = [random.randint(MIN_POS, MAX_POS) for _ in range(numCacti)]
    sprinklers = [random.randint(MIN_POS, MAX_POS) for _ in range(numSprinklers)]
    radii = [random.randint(MIN_RADIUS, MAX_RADIUS) for _ in range(numSprinklers)]
    return oranges, cacti, sprinklers, radii


def generate_feasible_case(numSprinklers, numOranges, numCacti):
    """Random instance where every orange is covered by at least one sprinkler."""
    sprinklers = [random.randint(MIN_POS, MAX_POS) for _ in range(numSprinklers)]
    radii = [random.randint(MIN_RADIUS, MAX_RADIUS) for _ in range(numSprinklers)]

    oranges = []
    for _ in range(numOranges):
        i = random.choice(range(numSprinklers))
        low = max(MIN_POS, sprinklers[i] - radii[i])
        high = min(MAX_POS, sprinklers[i] + radii[i])
        oranges.append(random.randint(low, high))

    cacti = [random.randint(MIN_POS, MAX_POS) for _ in range(numCacti)]
    return oranges, cacti, sprinklers, radii


def generate_hard_case(numSprinklers, numCacti):
    """Evenly spaced, non-overlapping sprinklers with one orange on each.
    Nothing is dominated, and every sprinkler is mandatory."""
    sprinklers = [i * 6 for i in range(numSprinklers)]
    radii = [2 for _ in range(numSprinklers)]
    oranges = [position for position in sprinklers]
    maxPosition = (numSprinklers - 1) * 6
    cacti = [random.randint(0, maxPosition) for _ in range(numCacti)]
    return oranges, cacti, sprinklers, radii


def is_feasible(oranges, sprinklers, radii):
    for orange in oranges:
        if not any(abs(sprinklers[i] - orange) <= radii[i]
                   for i in range(len(sprinklers))):
            return False
    return True


# =====================================================================
# Correctness tests
# Compare the minimum cost of all three algorithms.
# =====================================================================

def run_comparison_tests(numTests=100):
    passed = failed = 0

    cases = []
    for test in range(numTests):
        if test % 5 == 0:
            cases.append(generate_case())             # may be infeasible
        else:
            cases.append(generate_feasible_case(random.randint(1, 10),
                                                random.randint(1, 5),
                                                random.randint(0, 5)))
    for s in range(1, 11):                            # structured hard cases
        cases.append(generate_hard_case(s, random.randint(0, 5)))

    for oranges, cacti, sprinklers, radii in cases:
        baseCost = baseline(oranges, cacti, sprinklers, radii)[0]
        fastCost = fast(oranges, cacti, sprinklers, radii)[0]
        mandCost = fast_mandatory(oranges, cacti, sprinklers, radii)[0]

        if baseCost == fastCost == mandCost:
            passed += 1
        else:
            failed += 1
            print(f"MISMATCH: oranges={oranges}, cacti={cacti}, "
                  f"sprinklers={sprinklers}, radii={radii}, "
                  f"baseline={baseCost}, fast={fastCost}, fast_mandatory={mandCost}")

    print(f"Comparison tests: {passed} passed, {failed} failed")


# =====================================================================
# Benchmarking
# Instance is generated outside the timed region; all three algorithms
# receive the exact same arrays. Times are the median of repeated runs.
# =====================================================================

def median_time_ms(func, args, repeats=5):
    times = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        times.append(time.perf_counter() - start)
    return statistics.median(times) * 1000, result


def benchmark_instance(instance, repeats=5):
    baseMs, baseResult = median_time_ms(baseline, instance, repeats)
    fastMs, fastResult = median_time_ms(fast, instance, repeats)
    mandMs, mandResult = median_time_ms(fast_mandatory, instance, repeats)

    baseCost, fastCost, mandCost = baseResult[0], fastResult[0], mandResult[0]
    assert baseCost == fastCost == mandCost, (
        f"Cost mismatch: instance={instance}, "
        f"baseline={baseCost}, fast={fastCost}, fast_mandatory={mandCost}")

    return {"surviving": mandResult[2], "mandatory": mandResult[3], "cost": baseCost,
            "baselineMs": baseMs, "fastMs": fastMs, "mandMs": mandMs}


def run_benchmark_table(title, make_instance, sizes=(5, 8, 10, 12, 14, 16), repeats=5):
    print(title)
    print(f"{'Sprk':>4} {'Surv':>4} {'Mand':>4} {'Cost':>4} {'Baseline (ms)':>14} "
          f"{'Fast (ms)':>10} {'FastMand (ms)':>14} {'vs Base':>9} {'vs Fast':>9}")
    for s in sizes:
        row = benchmark_instance(make_instance(s), repeats)
        vsBase = row["baselineMs"] / row["mandMs"] if row["mandMs"] > 0 else float("inf")
        vsFast = row["fastMs"] / row["mandMs"] if row["mandMs"] > 0 else float("inf")
        print(f"{s:>4} {row['surviving']:>4} {row['mandatory']:>4} {row['cost']:>4} "
              f"{row['baselineMs']:>14.3f} {row['fastMs']:>10.3f} "
              f"{row['mandMs']:>14.3f} {vsBase:>8.1f}x {vsFast:>8.1f}x")
    print()


# =====================================================================
# Main
# =====================================================================

def main():
    random.seed(12345)

    run_comparison_tests(100)
    print()

    run_benchmark_table("Random feasible instances (5 oranges, 5 cacti)",
                        lambda s: generate_feasible_case(s, 5, 5))
    run_benchmark_table("Hard instances (one orange per sprinkler, 5 cacti)",
                        lambda s: generate_hard_case(s, 5))


if __name__ == "__main__":
    main()