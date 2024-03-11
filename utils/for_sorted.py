def merge_sorted_unique(lst1: list, lst2: list) -> list:
    assert lst1 == sorted(lst1)
    assert is_all_unique_in_sorted(lst1)

    assert lst2 == sorted(lst2)
    assert is_all_unique_in_sorted(lst2)

    result = []
    i, j = 0, 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] == lst2[j]:
            result.append(lst1[i])
            i += 1
            j += 1
        elif lst1[i] < lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    while i < len(lst1):
        result.append(lst1[i])
        i += 1
    while j < len(lst2):
        result.append(lst2[j])
        j += 1
    return result


def merge_sorted_unique_many(lists: list[list]) -> list:
    merged = []
    index = [0] * len(lists)
    while True:
        i_min = -1
        for i, lst in enumerate(lists):
            if (
                    index[i] < len(lst) and
                    (i_min == -1 or lst[index[i]] < lists[i_min][index[i_min]])
            ):
                i_min = i
        if i_min == -1:
            break
        min_elem = lists[i_min][index[i_min]]
        if not merged or merged[-1] != min_elem:
            merged.append(min_elem)
        index[i_min] += 1
    return merged


def intersect_sorted_unique(lst1: list, lst2: list) -> list:
    assert lst1 == sorted(lst1)
    assert is_all_unique_in_sorted(lst1)

    assert lst2 == sorted(lst2)
    assert is_all_unique_in_sorted(lst2)

    """
    intersect two sorted arrays
    """
    result = []
    i, j = 0, 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] == lst2[j]:
            result.append(lst1[i])
            i += 1
            j += 1
        elif lst1[i] < lst2[j]:
            i += 1
        else:
            j += 1
    return result


def is_all_unique_in_sorted(lst: list) -> bool:
    for i in range(len(lst) - 1):
        if lst[i] == lst[i + 1]:
            return False
    return True
