oranges = [2, 6]
cacti = [4, 8]
sprinklers = [3, 6, 7]
radii = [2, 1, 2]

s = len(sprinklers)

bestCost = float("inf")
bestMask = None

for mask in range(1 << s):
    active = []
    for i in range(s):
        if (mask >> i) & 1:
            active.append(i)

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
            watered = False
            for i in active:
                if abs(sprinklers[i] - cactus) <= radii[i]:
                    watered = True
                    break
            if watered:
                cost += 1

        if cost < bestCost:
            bestCost = cost
            bestMask = mask

        print(f"Mask: {mask:0{s}b} → Valid: {valid}, Cost: {cost}")
    else:
        print(f"Mask: {mask:0{s}b} → Valid: {valid}")

if bestMask is None:
    print("No valid selection found")
else:
    selected = []
    for i in range(s):
        if (bestMask >> i) & 1:
            selected.append(sprinklers[i])

    print()
    print(f"Best Mask: {bestMask:0{s}b}")
    print(f"Selected Sprinklers: {selected}")
    print(f"Minimum Cacti Watered: {bestCost}")