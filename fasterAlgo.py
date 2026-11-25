oranges = [2, 6]
cacti = [4, 8]
sprinklers = [3, 6, 7]
radii = [2, 1, 2]

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

        # B dominates A: B covers every orange A covers,
        # and B waters no cactus that A doesn't already water.
        bDominatesA = (orangeCoverage[a] <= orangeCoverage[b]
                       and cactusCoverage[b] <= cactusCoverage[a])

        if not bDominatesA:
            continue

        # Equivalent sprinklers: keep only the smaller index.
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

print(f"Original sprinklers: {list(range(s))}")
print(f"Remaining sprinklers: {remainingSprinklers}")
print(f"Eliminated sprinklers: {sorted(eliminated)}")