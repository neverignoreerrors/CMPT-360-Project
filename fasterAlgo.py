oranges = [2, 10]
cacti = [4]
sprinklers = [3]
radii = [2]

s = len(sprinklers)

orangeCoverage = []
cactusCoverage = []

for i in range(s):
    coveredOranges = set()
    for j in range(len(oranges)):
        if abs(sprinklers[i] - oranges[j]) <= radii[i]:
            coveredOranges.add(j)
    orangeCoverage.append(coveredOranges)

    coveredCacti = set()
    for j in range(len(cacti)):
        if abs(sprinklers[i] - cacti[j]) <= radii[i]:
            coveredCacti.add(j)
    cactusCoverage.append(coveredCacti)

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

remainingSprinklers = []
for i in range(s):
    if i not in eliminated:
        remainingSprinklers.append(i)

# Reduced search with pruning
r = len(remainingSprinklers)
allOranges = set(range(len(oranges)))

bestCost = float("inf")
bestMask = None

for mask in range(1 << r):
    active = []
    coveredByMask = set()
    for j in range(r):
        if (mask >> j) & 1:
            i = remainingSprinklers[j]
            active.append(i)
            coveredByMask |= orangeCoverage[i]

    # Invalid selections skip cactus evaluation entirely
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

    cost = len(cactiWatered)
    if cost < bestCost:
        bestCost = cost
        bestMask = mask

if bestMask is None:
    print("No valid selection found")
else:
    selected = []
    for j in range(r):
        if (bestMask >> j) & 1:
            selected.append(sprinklers[remainingSprinklers[j]])

    print(f"Best Reduced Mask: {bestMask:0{r}b}")
    print(f"Selected Sprinklers: {selected}")
    print(f"Minimum Cacti Watered: {bestCost}")