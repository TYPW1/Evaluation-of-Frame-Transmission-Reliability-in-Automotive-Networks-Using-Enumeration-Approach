from itertools import chain, combinations
from decimal import *
from collections import Counter

# This function calculates the probability that a packet is successfully
# transmitted over a link, based on the bit error rate and packet size.
def get_link_success_probability(ber, packet_size):
    # Convert BER to a decimal for high precision calculation
    ber_decimal = Decimal(ber)
    # The success probability for one bit is 1 minus the bit error rate
    one_bit_success = Decimal(1) - ber_decimal
    # The success probability for the whole packet is the one bit success rate
    # to the power of the packet size
    link_success_probability = one_bit_success ** Decimal(packet_size)
    return link_success_probability

# Test the function with a BER of 10^-10 and a packet size of 3200 bits
ber_test_1 = 10**-10
packet_size_test = 3200

# Calculate the success probability for the given BER and packet size
link_success_probability_test_1 = get_link_success_probability(ber_test_1, packet_size_test)
link_success_probability_test_1

# Transmission on each link can be either succeeded or failed. Hence, there
# are many different combinations. Each combination could lead to either a
# successful or a failed source to destination transmission, which will be
# checked by the check_transmission_success() function below.
# This function will use the itertools module to generate all possible combinations
# of link failures given the route (which is a list of links in the network)
def enumerate_all_combinations(route):
    # Generate all possible combinations of the route
    # This will include the empty set (no failures) up to the full set (all failures)
    all_combinations = chain.from_iterable(combinations(route, r) for r in range(len(route)+1))
    # Convert iterator to list for easier use
    return list(all_combinations)

# Example usage:
# Let's say we have a network route that consists of 3 links for simplicity
sample_route = [("MCU-4", "SW_4"), ("SW_4", "SW_2"), ("SW_2", "SGA")]

# Now we'll enumerate all combinations of failures for this route
all_failure_combinations = enumerate_all_combinations(sample_route)
all_failure_combinations

# Given a link failure combination, it is possible to determine whether a packet
# can still be transmitted from source to destination. "route" contains all
# the possible links related to a source to destination packet transmission.
def check_transmission_success(source, destination, route, link_failure_combination):
    # Convert the link failure combination to a set for easier checking
    failed_links = set(link_failure_combination)
    
    # If there is at least one path where none of the links have failed,
    # then the transmission is successful.

    # We will assume that 'route' is a list of all possible direct links
    # from source to destination, including redundant paths.

    #a dictionary where keys are nodes and values are sets of connected nodes
    network_graph = {}
    for link in route:
        if link[0] not in network_graph:
            network_graph[link[0]] = set()
        network_graph[link[0]].add(link[1])

        # Since this is an undirected graph (for simplicity), we add the link in both directions
        if link[1] not in network_graph:
            network_graph[link[1]] = set()
        network_graph[link[1]].add(link[0])

    # Perform a Depth-First Search (DFS) to find if a path exists
    def dfs(current_node, destination, visited):
        if current_node == destination:
            return True
        visited.add(current_node)
        for neighbor in network_graph.get(current_node, []):
            if neighbor not in visited:
                # If the link is not failed, we can travel to the neighbor
                if (current_node, neighbor) not in failed_links and (neighbor, current_node) not in failed_links:
                    if dfs(neighbor, destination, visited):
                        return True
        return False
    
    # Initialize visited set and start DFS from the source node
    visited = set()
    return dfs(source, destination, visited)

# Test the check_transmission_success function
source = "MCU-4"
destination = "SGA"
# Assume the first link has failed
link_failure_combination_test = [(sample_route[0],)]

# Check if the transmission is successful given the failure combination
transmission_success = check_transmission_success(source, destination, sample_route, link_failure_combination_test)
transmission_success


# Given a packet of a certain size, the route that can be used to transmit the
# packet from source to destination, and the bit error rate on each link, this
# function calculates the probability that the packet can be transmitted
# successfully from source to destination. Besides that, it also outputs other
# information, such as packet loss rate, average time in hour between 2 successive
# packet loss, and most importantly a formula which formulates the probability
# calculation.
# Correcting the total_success_probability_calculation function to ensure that
# all floating-point operations are done using Decimal for high precision.

def total_success_probability_calculation(ber, packet_size, route, source, destination):
    # Calculate the success probability of a single link
    link_success_probability = get_link_success_probability(ber, packet_size)

    # Enumerate all possible failure combinations for the links
    all_failure_combinations = enumerate_all_combinations(route)

    # Initialize the total success probability
    total_success_probability = Decimal(0)

    # Check each failure combination
    for failure_combination in all_failure_combinations:
        # Check if the current failure combination still allows for a successful transmission
        if check_transmission_success(source, destination, route, failure_combination):
            # Calculate the probability for this successful combination
            success_combination_probability = (link_success_probability ** (Decimal(len(route)) - len(failure_combination))) * \
                                              ((Decimal(1) - link_success_probability) ** len(failure_combination))
            # Add this probability to the total success probability
            total_success_probability += success_combination_probability

    # Calculate packet loss rate
    packet_loss_rate = Decimal(1) - total_success_probability

    # Calculate the average time between two packet losses in hours, given a packet is sent every 10ms
    packets_per_second = Decimal(100)  # 100 packets are sent per second
    packets_per_hour = packets_per_second * Decimal(3600)
    average_time_between_losses = Decimal(1) / (packet_loss_rate * packets_per_hour)

    # Return the calculated probabilities and average time
    return {
        'total_success_probability': total_success_probability,
        'packet_loss_rate': packet_loss_rate,
        'average_time_between_losses_hours': average_time_between_losses
    }

# Example usage:
# Let's calculate the total success probability for the sample network with a BER of 10^-10
ber_example = 10**-10  # Bit Error Rate
packet_size_example = 3200  # Packet Size
source_example = "MCU-4"  # Source node
destination_example = "SGA"  # Destination node
sample_route_example = [("MCU-4", "SW_4"), ("SW_4", "SW_2"), ("SW_2", "SGA")]  # Example route

# Calculate the total success probability for the example network
result_example = total_success_probability_calculation(ber_example, packet_size_example, sample_route_example, source_example, destination_example)
result_example

def total_success_probability_calculation_with_formula(ber, packet_size, route, source, destination):
    # Calculate the success probability of a single link
    link_success_probability = get_link_success_probability(ber, packet_size)

    # Enumerate all possible failure combinations for the links
    all_failure_combinations = enumerate_all_combinations(route)

    # Initialize the total success probability
    total_success_probability = Decimal(0)

    # Start constructing the success formula
    success_formula = ""

    # Check each failure combination
    for failure_combination in all_failure_combinations:
        # Check if the current failure combination still allows for a successful transmission
        if check_transmission_success(source, destination, route, failure_combination):
            # Calculate the probability for this successful combination
            success_combination_probability = (link_success_probability ** (Decimal(len(route)) - len(failure_combination))) * \
                                              ((Decimal(1) - link_success_probability) ** len(failure_combination))
            # Add this probability to the total success probability
            total_success_probability += success_combination_probability

            # Construct the success formula part for this combination
            if success_formula:  # Add "+" if it's not the first term
                success_formula += " + "
            success_combination_probability_str = f"({success_combination_probability.normalize()})"
            success_formula += f"{success_combination_probability_str} * p^{len(route) - len(failure_combination)} * (1-p)^{len(failure_combination)}"

    # Calculate packet loss rate
    packet_loss_rate = Decimal(1) - total_success_probability

    # Calculate the average time between two packet losses in hours, given a packet is sent every 10ms
    packets_per_second = Decimal(100)  # 100 packets are sent per second
    packets_per_hour = packets_per_second * Decimal(3600)
    average_time_between_losses = Decimal(1) / (packet_loss_rate * packets_per_hour)

    # Return the calculated probabilities, average time, and the success formula
    return {
        'total_success_probability': total_success_probability,
        'packet_loss_rate': packet_loss_rate,
        'average_time_between_losses_hours': average_time_between_losses,
        'success_formula': success_formula
    }

if __name__ == '__main__':
    # Each network architecture is represented by all the links that can be used
    # for packet transmission from source to destination.
    network1_route = [("MCU-4", "SW_4"), ("MCU-4", "SW_A"), ("SW_4", "SW_A"), ("SW_4", "SW_2"), ("SW_A", "SW_B"),
                      ("SW_2", "SW_B"), ("SW_2", "SGA"), ("SW_B", "SGA")]
    network2_route = [("MCU-4", "SW_4"), ("SW_4", "SW_A"), ("SW_4", "SW_2"), ("SW_A", "SW_B"), ("SW_2", "SW_B"),
                      ("SW_B", "SGA")]
    network3_route = [("MCU-4", "SW_4"), ("SW_4", "SW_2"), ("SW_2", "SW_B"), ("SW_B", "SGA")]

    # Add your code here, which calculates the success probability for frame transmission
    # from source to destination for different bit error rates, and different network architectures.
    
    # Bit Error Rates to consider

    bers = [10**-10, 10**-12]

    # Packet size is constant
    packet_size = 3200

    # Source and destination are assumed to be the same for all architectures
    source = "MCU-4"
    destination = "SGA"

    # Store the routes in a dictionary for easy access
    network_routes = {
        'Baseline': network1_route,
        'CB-aware': network2_route,
        'CB-aware with multi-homing': network3_route
    }

    # Results dictionary to store the results for each architecture and BER
    results = {}

    # Perform calculations for each network architecture and BER
    for architecture_name, route in network_routes.items():
        for ber in bers:
            key = f"{architecture_name} - BER: {ber}"
            results[key] = total_success_probability_calculation(ber, packet_size, route, source, destination)

    results

    # Using the same network architecture routes and BERs as defined earlier
    network_routes = {
        'Baseline': network1_route,
        'CB-aware': network2_route,
        'CB-aware with multi-homing': network3_route
    }

    # Dictionary to hold all the results
    all_results_with_formula = {}

    # Calculate the results for each architecture and BER
    for architecture_name, route in network_routes.items():
        for ber in bers:
            # Construct the key for the results dictionary
            key = f"{architecture_name} - BER: {ber}"
            # Calculate the success probability and other metrics including the success formula
            all_results_with_formula[key] = total_success_probability_calculation_with_formula(ber, packet_size, route, source, destination)

    # Output the results for each case
    for result_key, result_values in all_results_with_formula.items():
        print(f"Results for {result_key}:")
        print(f" Total Success Probability: {result_values['total_success_probability']}")
        print(f" Packet Loss Rate: {result_values['packet_loss_rate']}")
        print(f" Average Time Between Losses (hours): {result_values['average_time_between_losses_hours']}")
        print(f" Success Formula: {result_values['success_formula']}\n")