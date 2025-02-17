import os
import math
import random
from qubots.base_problem import BaseProblem

class BinPackingWithConflictsProblem(BaseProblem):
    """
    Bin Packing with Conflicts Problem:

    Given a set of items with known weights and conflict relations, assign each item to a bin
    (with uniform capacity) such that:
      - The total weight in each bin does not exceed the bin capacity.
      - Conflicting items are not placed in the same bin.

    The objective is to minimize the number of bins used.

    Candidate solution representation:
      A list of integers of length equal to the number of items, where each integer represents the
      0-indexed bin assignment for the corresponding item.
    """
    
    def __init__(self, instance_file=None, nb_items=None, bin_capacity=None, weights_data=None, forbidden_items=None):
        if instance_file is not None:
            self._load_instance_from_file(instance_file)
        else:
            if nb_items is None or bin_capacity is None or weights_data is None or forbidden_items is None:
                raise ValueError("Either 'instance_file' or all parameters must be provided.")
            self.nb_items = nb_items
            self.bin_capacity = bin_capacity
            self.weights_data = weights_data
            self.forbidden_items = forbidden_items
            self._compute_bins()
    
    def _compute_bins(self):
        total_weight = sum(self.weights_data)
        self.nb_min_bins = int(math.ceil(total_weight / float(self.bin_capacity)))
        self.nb_max_bins = min(self.nb_items, 2 * self.nb_min_bins)
    
    def _load_instance_from_file(self, filename):
        # Resolve relative paths with respect to this module's directory.
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, filename)
        count = 0
        weights_data = []
        forbidden_items = []
        with open(filename) as f:
            for line in f:
                tokens = line.split()
                if count == 0:
                    self.nb_items = int(tokens[0])
                    self.bin_capacity = int(tokens[1])
                else:
                    # tokens[0] is the item identifier (can be ignored)
                    # tokens[1] is the weight for the item
                    weights_data.append(int(tokens[1]))
                    # The remaining tokens (if any) list the conflicting items.
                    # Convert them to integers and to 0-indexed.
                    conflicts = []
                    for token in tokens[2:]:
                        conflicts.append(int(token) - 1)
                    forbidden_items.append(conflicts)
                count += 1
        self.weights_data = weights_data
        self.forbidden_items = forbidden_items
        self._compute_bins()
    
    def evaluate_solution(self, solution) -> float:
        """
        Evaluate a candidate solution.

        The candidate solution should be a list of integers of length nb_items where each integer is the
        bin index (0-indexed) to which the corresponding item is assigned.

        Feasibility constraints:
          - For each bin, the total weight of items must not exceed bin_capacity.
          - For each item i, none of its forbidden (conflicting) items is assigned to the same bin.

        If any constraint is violated, a large penalty is returned.
        Otherwise, the objective is the number of bins used (i.e., the count of unique bin indices).
        """
        PENALTY = 1e9
        if not isinstance(solution, (list, tuple)) or len(solution) != self.nb_items:
            return PENALTY
        for b in solution:
            if not isinstance(b, int) or b < 0 or b >= self.nb_max_bins:
                return PENALTY
        
        # Check bin weight constraints.
        bin_weights = {}
        for i, b in enumerate(solution):
            bin_weights[b] = bin_weights.get(b, 0) + self.weights_data[i]
        for weight in bin_weights.values():
            if weight > self.bin_capacity:
                return PENALTY
        
        # Check conflict constraints.
        for i in range(self.nb_items):
            for j in self.forbidden_items[i]:
                # If j is not a valid item index, skip.
                if j < 0 or j >= self.nb_items:
                    continue
                if solution[i] == solution[j]:
                    return PENALTY
        
        # Feasible solution: objective = number of used bins.
        used_bins = len(bin_weights)
        return used_bins
    
    def random_solution(self):
        """
        Generate a random candidate solution.

        Each item is assigned a random bin index between 0 and (nb_max_bins - 1).
        """
        return [random.randint(0, self.nb_max_bins - 1) for _ in range(self.nb_items)]
