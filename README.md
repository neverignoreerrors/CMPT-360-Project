# CMPT-360-Project

# Sprinkler Selection (Brute Force)

Finds the subset of sprinklers that waters every orange tree while watering as few cacti as possible. The program checks every possible subset, so the answer is guaranteed to be optimal.

## Input

The input is defined as four lists at the top of the script, all positions on a number line:

| Variable     | Meaning                                                  |
|--------------|----------------------------------------------------------|
| `oranges`    | Positions of the orange trees (must be watered)          |
| `cacti`      | Positions of the cacti (should be watered as little as possible) |
| `sprinklers` | Positions of the sprinklers                              |
| `radii`      | `radii[i]` is the reach of the sprinkler at `sprinklers[i]` |

`sprinklers` and `radii` must have the same length. A sprinkler at position `p` with radius `r` waters any plant at position `x` where `abs(p - x) <= r` (the boundary is inclusive).

Example:

```python
oranges = [2, 6]
cacti = [4, 8]
sprinklers = [3, 6, 7]
radii = [2, 1, 2]
```

## Output

**Per-mask debug lines.** Each subset is written as a binary mask, where bit `i` (counting from the right) means sprinkler `i` is on. Valid subsets also show their cost, the number of distinct cacti watered:

```
Mask: 011 → Valid: True, Cost: 1
Mask: 100 → Valid: False
```

A subset is **valid** if every orange is watered by at least one active sprinkler. Costs are only computed for valid subsets.

**Final summary.** After all subsets are checked:

```
Best Mask: 011
Selected Sprinklers: [3, 6]
Minimum Cacti Watered: 1
```

If no subset covers every orange, the program prints `No valid selection found` instead.

If several valid subsets tie for the lowest cost, the first one found (the lowest mask number) is reported.

## How to run

Requires Python 3.6 or newer (for f-strings). No extra packages are needed.

1. Save the code as `sprinklers.py`.
2. Edit the four input lists at the top if you want to try a different case.
3. Run it from a terminal:

```
python sprinklers.py
```

(Use `python3` if that is how Python is invoked on your system.)

## How it works

1. With `s` sprinklers there are `1 << s` (that is, 2^s) subsets. The program loops over every number from `0` to `(1 << s) - 1`.
2. For each number, the bits that are set give the active sprinklers, stored as indices.
3. The subset is valid if every orange is covered by at least one active sprinkler.
4. For valid subsets, the cost is the number of cacti covered by at least one active sprinkler. Each cactus counts once, however many sprinklers reach it.
5. `bestCost` and `bestMask` are updated whenever a valid subset has a strictly lower cost.

## Complexity

The runtime is O(2^s · s · (o + c)), where `s`, `o`, and `c` are the numbers of sprinklers, oranges, and cacti. The exponential factor means this approach is practical only for small `s` (roughly 20 or fewer).

## Test case

```python
oranges = [2]
cacti = [4]
sprinklers = [3, 5]
radii = [2, 1]
```

Expected result:

```
Best Mask: 01
Selected Sprinklers: [3]
Minimum Cacti Watered: 1
```

This case checks that validity is enforced before cost, that each cactus is counted once, that ties keep the first (smaller) selection, and that the radius boundary is inclusive.