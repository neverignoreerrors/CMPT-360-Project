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

for i in range(s):
    print(f"Sprinkler {i}:")
    print(f"  Orange indices: {orangeCoverage[i]}")
    print(f"  Cactus indices: {cactusCoverage[i]}")
    print()