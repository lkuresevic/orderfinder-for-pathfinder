from vpr_io import *

from sort import *

from plot import *

from commands import *

def count_num_inv(permuted_list, ordered_list):
    # Create a dictionary to map values to their indices in the ordered list
    value_to_index = {value: idx for idx, value in enumerate(ordered_list)}
    
    # Convert permuted_list to list of ranks based on ordered_list
    ranks = [value_to_index[value] for value in permuted_list]
    
    # Count inversions using modified merge sort algorithm (O(n log n))
    def merge_sort_count(arr):
        if len(arr) <= 1:
            return arr, 0
        
        mid = len(arr) // 2
        left, inv_left = merge_sort_count(arr[:mid])
        right, inv_right = merge_sort_count(arr[mid:])
        merged, inv_merge = merge_count(left, right)
        
        total = inv_left + inv_right + inv_merge
        return merged, total
    
    def merge_count(left, right):
        result = []
        i = j = 0
        inv_count = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
                inv_count += len(left) - i
                
        result.extend(left[i:])
        result.extend(right[j:])
        return result, inv_count
    
    _, num_inversions = merge_sort_count(ranks)
    return num_inversions
