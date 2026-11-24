oranges = [2, 6]
cacti = [4, 8]
sprinklers = [3, 6, 7]
radii = [2, 1, 2]

s = len(sprinklers)

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

    print(f"Mask: {mask:0{s}b} → Valid: {valid}")