import random
import statistics
import time


def build_coverage(oranges, cacti, sprinklers, radii):
    orangeCoverage = []
    cactusCoverage = []
    for i in range(len(sprinklers)):
        orangeCoverage.append({j for j in range(len(oranges))
                               if abs(sprinklers[i] - oranges[j]) <= radii[i]})
        cactusCoverage.append({j for j in range(len(cacti))
                               if abs(sprinklers[i] - cacti[j]) <= radii[i]})
    return orangeCoverage, cactusCoverage


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


def fast_core(oranges, cacti, sprinklers, radii):
    """The faster algorithm. Returns (minCost, selectedPositions, r),
    where r is the number of surviving sprinklers."""
    s = len(sprinklers)
    orangeCoverage, cactusCoverage = build_coverage(oranges, cacti, sprinklers, radii)

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

    remaining = [i for i in range(s) if i not in eliminated]
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
            continue

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


def fast(oranges, cacti, sprinklers, radii):
    """Same interface as baseline; used by the correctness tests."""
    cost, selected, _ = fast_core(oranges, cacti, sprinklers, radii)
    return cost, selected


# ---------- Generators ----------

MIN_POS, MAX_POS = 0, 20
MIN_RADIUS, MAX_RADIUS = 0, 5


def generate_case():
    """Unconstrained generator (robustness tests; may be infeasible)."""
    numOranges = random.randint(1, 5)
    numCacti = random.randint(0, 5)
    numSprinklers = random.randint(1, 10)

    oranges = [random.randint(MIN_POS, MAX_POS) for _ in range(numOranges)]
    cacti = [random.randint(MIN_POS, MAX_POS) for _ in range(numCacti)]
    sprinklers = [random.randint(MIN_POS, MAX_POS) for _ in range(numSprinklers)]
    radii = [random.randint(MIN_RADIUS, MAX_RADIUS) for _ in range(numSprinklers)]
    return oranges, cacti, sprinklers, radii

def generate_hard_case(numSprinklers, numCacti):
    # 1. Sprinklers at a fixed distance from each other.
    sprinklers = [i * 6 for i in range(numSprinklers)]

    # 2. Every sprinkler gets the same small radius.
    radii = [2 for _ in range(numSprinklers)]

    # 3. One orange at each sprinkler's position.
    oranges = [position for position in sprinklers]

    # 4. Cacti are random, within the span of the sprinklers.
    maxPosition = (numSprinklers - 1) * 6
    cacti = [random.randint(0, maxPosition) for _ in range(numCacti)]

    # 5. Return the instance.
    return oranges, cacti, sprinklers, radii

def find_mandatory_sprinklers(orangeCoverage, numOranges, remainingSprinklers=None):
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

def fast_mandatory(oranges, cacti, sprinklers, radii):
    """Returns (minCost, selectedPositions, r, numMandatory),
    or (None, None, r, 0) if some orange cannot be watered."""
    s = len(sprinklers)

    orangeCoverage, cactusCoverage = build_coverage(oranges, cacti, sprinklers, radii)
    eliminated = set()
    for a in range(s):
        for b in range(s):
            if a == b:
                continue
            if not (orangeCoverage[a] <= orangeCoverage[b]
                    and cactusCoverage[b] <= cactusCoverage[a]):
                continue
            if (orangeCoverage[a] == orangeCoverage[b]
                    and cactusCoverage[a] == cactusCoverage[b]):
                if a > b:
                    eliminated.add(a)
            else:
                eliminated.add(a)
    remaining = [i for i in range(s) if i not in eliminated]
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

    if mandatoryOranges == allOranges:
        selected = [sprinklers[i] for i in sorted(mandatory)]
        return len(mandatoryCacti), selected, r, len(mandatory)

    optional = [i for i in remaining if i not in mandatory]
    k = len(optional)
    bestCost = float("inf")
    bestOptional = None

    for mask in range(1 << k):
        chosen = [optional[j] for j in range(k) if (mask >> j) & 1]

        covered = set(mandatoryOranges)
        for i in chosen:
            covered |= orangeCoverage[i]
        if covered != allOranges:
            continue                      # invalid: skip cactus work

        watered = set(mandatoryCacti)
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

def generate_feasible_case(numSprinklers, numOranges, numCacti):
    """Every orange is guaranteed to be covered by at least one sprinkler."""
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


def is_feasible(oranges, sprinklers, radii):
    for orange in oranges:
        if not any(abs(sprinklers[i] - orange) <= radii[i]
                   for i in range(len(sprinklers))):
            return False
    return True


# ---------- Benchmark ----------

def benchmark_size(numSprinklers, numOranges, numCacti, repeats=5):
    # 1. Generate one feasible instance, outside any timed code.
    oranges, cacti, sprinklers, radii = generate_feasible_case(
        numSprinklers, numOranges, numCacti)
    assert is_feasible(oranges, sprinklers, radii), "Generator produced an infeasible case"

    baselineTimes = []
    fasterTimes = []

    # 2 and 3. Run each algorithm five times on the same instance and store each time.
    # Both receive the exact same arrays; neither function modifies them.
    for _ in range(repeats):
        start = time.perf_counter()
        baseCost, _ = baseline(oranges, cacti, sprinklers, radii)
        baselineTimes.append(time.perf_counter() - start)

    for _ in range(repeats):
        start = time.perf_counter()
        fastCost, _, r = fast_core(oranges, cacti, sprinklers, radii)
        fasterTimes.append(time.perf_counter() - start)

    # Checked after timing, so it doesn't affect the measurements.
    assert baseCost == fastCost, (
        f"Cost mismatch: oranges={oranges}, cacti={cacti}, "
        f"sprinklers={sprinklers}, radii={radii}, "
        f"baseline={baseCost}, fast={fastCost}")

    # 4. Medians
    baselineMedian = statistics.median(baselineTimes)
    fasterMedian = statistics.median(fasterTimes)

    # 5. Speedup from the two medians
    speedup = baselineMedian / fasterMedian if fasterMedian > 0 else float("inf")

    return {"s": numSprinklers, "r": r,
            "baselineMs": baselineMedian * 1000,
            "fasterMs": fasterMedian * 1000,
            "speedup": speedup}


def run_benchmark_table(sizes=(5, 8, 10, 12, 14, 16), numOranges=5, numCacti=5):
    rows = [benchmark_size(s, numOranges, numCacti) for s in sizes]

    print(f"{'Sprinklers':>10} {'Surviving':>10} {'Baseline (ms)':>14} "
          f"{'Faster (ms)':>12} {'Speedup':>9}")
    for row in rows:
        print(f"{row['s']:>10} {row['r']:>10} {row['baselineMs']:>14.3f} "
              f"{row['fasterMs']:>12.3f} {row['speedup']:>8.2f}x")
    return rows


# ---------- Correctness tests ----------

def run_comparison_tests(numTests=100):
    passed = failed = 0
    for test in range(numTests):
        if test % 5 == 0:
            case = generate_case()
        else:
            case = generate_feasible_case(random.randint(1, 10),
                                          random.randint(1, 5),
                                          random.randint(0, 5))
        oranges, cacti, sprinklers, radii = case

        baseCost, _ = baseline(oranges, cacti, sprinklers, radii)
        fastCost, _ = fast(oranges, cacti, sprinklers, radii)

        if baseCost == fastCost:
            passed += 1
        else:
            failed += 1
            print(f"MISMATCH: oranges={oranges}, cacti={cacti}, "
                  f"sprinklers={sprinklers}, radii={radii}, "
                  f"baseline={baseCost}, fast={fastCost}")

    print(f"Comparison tests: {passed} passed, {failed} failed")

def main():
    random.seed(12345)
    run_comparison_tests(100)
    print()
    run_benchmark_table()


if __name__ == "__main__":
    main()