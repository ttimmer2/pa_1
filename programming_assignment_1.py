import test_sets
import logging
from time import time

logging.basicConfig(filename='manhattan-distance-runtime.log',format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO) # this is from https://stackoverflow.com/questions/533048/how-to-log-source-file-name-and-line-number-in-python

logger = logging.getLogger(__name__)

def timer(func):
    # This function shows the execution time of 
    # the function object passed
    # this function is from https://www.geeksforgeeks.org/timing-functions-with-decorators-python/
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        logger.debug(f'Function {func.__name__!r} executed in {(t2-t1):.20f}s')
        file = "results.txt"
        with open(file, "a") as f:
            f.write(f"{t2-t1}, {len(args[0])}\n")
        return result
    return wrap_func


def sort_by_distance(tup):
    """
    Return the 0 indexed tuple (where distance will be stored).
    """
    return tup[0]

def sort_by_x(tup):
    """
    Return the 0 indexed tuple (where the x-value will be stored).
    """
    return tup[0]

#@timer
def iterative_minimum_manhattan_distance(points, m):
    """
    first, check that m is not too large, small, or not a number.
    Sort the points array.
    Then initialize an array with (distance, point1, point2) tuples wheere the distance is infinity.
    Iterate once through points, calculating the manhattan distance for each point to the point at the next index to the right.
    If this distance is smaller than the current minimum, update minimum_distance and resort the list.

    Next, make sure there aren't any minima that were missed.
    Starting with the first element, go to the right while elementN.x - element1.x < the largest minimum.
    Then run the brute force method on this.
    For each minimum returned by brute force, check if it is less than the largest minimum. If so, replace it and resort the list.

    input: list of points, integer m - number of minima to calculate
    return: list of tuples where tuple is (distance, (x,y), (x,y))
    """
    logger.debug(f"Calculating {m} minimum manhattan distances for set {points}.")
    if not isinstance(m,int):
        logger.error(f"m must be an integer.")
        raise Exception(f"m must be an integer.")        
    if m > len(points):
        logger.error(f"m of length {m} is greater than the number of points ({len(points)}.")
        raise Exception(f"m of length {m} is greater than the number of points ({len(points)}.")
    if m < 1:
        logger.error(f"m of length {m} is too small. m must be at least 1")
        raise Exception(f"m of length {m} is too small. m must be at least 1")
    if len(points) > len(list(set(points))):
        logger.error(f"Points is not a proper set.")
        raise Exception(f"Points is not a proper set.")

    points.sort(key=sort_by_x)
    logger.debug("Sorting the points array")

    # initialize a list of length m with infinite values
    minimum_distances = [(float("inf"),(0,0),(0,0)) for integer in range(0,m)]
    logger.debug("Initialized minimum_distances array.")

    # iterate through, getting distance of closest points. check each distance against last distance in min list. If lower, add replace the last value with it, and resort the list
    logger.debug("Iterating through points.")
    for index, current_point in enumerate(points): # make sure points have x and y with numberic values
        if not isinstance(current_point[0], (int,float)) or not isinstance(current_point[1], (int,float)):
            logger.error(f"points must have x and y with numeric values: {current_point} fails.")
            raise Exception(f"points must have x and y with numeric values: {current_point} fails.")

        if index < len(points) - 1:
            next_point = points[index+1]
            logger.debug(f"Calculating the manhattan distance of {current_point} and {next_point}")
            manhattan_distance = calculate_manhattan_distance(current_point, next_point) # calculate the distance between the next point in the list
            if manhattan_distance < minimum_distances[-1][0]:
                logger.debug(f"{manhattan_distance} is less than {minimum_distances[-1]}")
                minimum_distances[-1] = (manhattan_distance,current_point,next_point)
                minimum_distances.sort(key=sort_by_distance) # resort
                logger.debug(f"minimum distances updated to {minimum_distances}")

    index_iterator = 0      # we are using a non-traditional iterator because we don't want to calculate distances more than once. We also want to use the lower minimum as it is calculated.
    logger.debug(f"The largest minimum is {minimum_distances[-1][0]}. Iterating through list again.")
    while index_iterator < len(points):
        index = index_iterator
        current_point = points[index]
        if current_point == points[-1]:
            break
        index_increment = 1
        while index+index_increment < len(points) and points[index + index_increment][0] - current_point[0] < minimum_distances[-1][0]:
            index_increment += 1
        if index_increment > 1:
            minima = brute_force(points[index:index+index_increment+1], len(points))
            logger.debug(f"Calculating minima with brute force for indices {index} through {index+index_increment+1}.")
            for minimum in minima:
                logger.debug(f"Comparing minima to minima in minimum distances.")
                if minimum[0] < minimum_distances[-1][0] and minimum not in minimum_distances:
                    minimum_distances[-1] = minimum
                    minimum_distances.sort(key=sort_by_x)
        index_iterator += index_increment
    logger.debug(f"{points} has minimum distances of {minimum_distances}")
    return minimum_distances
# @timer
def brute_force(points,m):
    """
    create an empty list.
    iterate through points.
    For each iteration, iterate through points, calculating the distances (only if index1 < index2). append the distances to the empty list
    Lastly, sort the empty list.
    Return the empty list indexed from [0:m]

    input: list of points, integer m - number of minima to calculate
    return: list of tuples where tuple is (distance, (x,y), (x,y))    
    """
    logger.debug(f"Calling brute_force on points {points} for {m} minima")
    closest_points = []
    for index_1, point_1 in enumerate(points):
        for index_2, point_2 in enumerate(points):
            if (point_1 == point_2) or index_2<index_1:
                # we don't want to compare the distance of the point to itself, since we know this is 0.
                # We can reduce our comparisons in half, and avoid returning the same points if we only compare smaller indexed values to larger indexed values
                continue
            else:
                manhattan_distance = calculate_manhattan_distance(point_1, point_2) # the points are in an (x,y) tuple. This calculates the manhattan distance
                closest_points.append((manhattan_distance,points[index_1],points[index_2])) # add the value to closest points list.
    closest_points.sort(key=sort_by_distance) # sort by manhattan distance
    return closest_points[0:m] # we will return the subarray with only the m shortest points

def calculate_manhattan_distance(point_1, point_2):
    """
    calculate the manhattan distance
    input: point1 and point2 should be tuples (x,y) where x and y are numbers
    return: int or float distance
    """
    return abs(point_1[0]-point_2[0])+abs(point_1[1]-point_2[1])



def log_function(func, *args,**kwargs):
    """
    Utility function to log runs
    """
    logger.info(f"running for {func.__name__} with list of length {len(args[0])} and m equal to {args[1]}")
    t1 = time()
    result = func(*args, **kwargs)
    t2 = time()
    logger.info(f"Found minima in {t2-t1} seconds.")

if __name__ == "__main__":

    # trace run
    trace_set = [(1, 199999), (1, 22), (1, -123981), (0, 0), (0, 1), (-11, 3), (1, 4), (91283, 12), (44, 199999)]
    log_function(iterative_minimum_manhattan_distance, trace_set, 5)

    # O of n^2
    log_function(brute_force, test_sets.test_10_random_points_set, 10)
    log_function(brute_force, test_sets.test_100_random_points_set, 10)
    log_function(brute_force,test_sets.test_1000_random_points_set, 10)
    log_function(brute_force,test_sets.test_10000_random_points_set, 10)

    # Average case
    log_function(iterative_minimum_manhattan_distance, test_sets.test_10_random_points_set, 10)
    log_function(iterative_minimum_manhattan_distance, test_sets.test_100_random_points_set, 10)
    log_function(iterative_minimum_manhattan_distance, test_sets.test_1000_random_points_set, 10)
    log_function(iterative_minimum_manhattan_distance, test_sets.test_10000_random_points_set, 10)
    log_function(iterative_minimum_manhattan_distance, test_sets.test_100000_random_points_set, 10)


    # worst case
    log_function(iterative_minimum_manhattan_distance,test_sets.test_10_worst_case, 10)
    log_function(iterative_minimum_manhattan_distance,test_sets.test_100_worst_case, 10)
    log_function(iterative_minimum_manhattan_distance,test_sets.test_1000_worst_case, 10)
    log_function(iterative_minimum_manhattan_distance,test_sets.test_10000_worst_case, 10)