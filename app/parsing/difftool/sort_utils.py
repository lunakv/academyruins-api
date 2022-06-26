import re


def is_after(left, right):
    """Determine if a rule number should be sorted after another.

    The CR numbering doesn't conform to a standard lexographical
    ordering -- it doesn't fit either purely alphabetical or, near
    as I can tell, any of the 'version' sorting utils out there.
    This function provides proper comparison between rules numbers
    for accurate sorting.

    Keyword arguments:
    left -- rule to compare from
    right -- rule to compare to
    """
    split_left = re.match(r"^([0-9]{3,})(?:\.([0-9]+)([a-z]*))\.?$", left)
    split_right = re.match(r"^([0-9]{3,})(?:\.([0-9]+)([a-z]*))\.?$", right)

    # e.g. 100.1a splits into 100, 1, and a
    # First two are ints, so treat them as such
    l_rule = int(split_left.group(1))
    l_sub = int(split_left.group(2))
    l_letter = split_left.group(3)

    r_rule = int(split_right.group(1))
    r_sub = int(split_right.group(2))
    r_letter = split_right.group(3)

    if l_rule > r_rule:
        return True
    elif l_rule == r_rule:
        if len(str(l_sub)) > len(str(r_sub)):
            return True
        if l_sub > r_sub:
            return True
        elif (l_rule == r_rule) and (l_sub == r_sub):
            return l_letter > r_letter


def insertion_sort(input_List):
    """Generic insertion sort.

    Keyword arguments:
    input_list -- the list to sort
    """
    for i in range(1, len(input_List)):
        cur = input_List[i]
        pos = i

        while pos > 0 and is_after(input_List[pos - 1][0], cur[0]):
            input_List[pos] = input_List[pos - 1]
            pos = pos - 1
        input_List[pos] = cur
