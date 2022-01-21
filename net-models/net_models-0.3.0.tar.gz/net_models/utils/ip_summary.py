import ipaddress

from pydantic.typing import List, Tuple

from net_models.utils import get_logger

LOGGER = get_logger(name="IPSum", verbosity=5)

def to_bit_string(network: ipaddress.IPv4Network) -> Tuple[str, str]:
    octets = [f"{int(x):08b}" for x in str(network.network_address).split('.')]
    mask_octets = [f"{int(x):08b}" for x in str(network.netmask).split('.')]
    network_bits = "".join(octets)
    mask_bits = "".join(mask_octets)
    return network_bits, mask_bits

def from_bit_string(network_bits: str, prefix_length: int) -> ipaddress.IPv4Network:
    octets = [str(int(network_bits[i:i+8], 2)) for i in range(0, 32, 8)]
    network = ipaddress.IPv4Network(f"{'.'.join(octets)}/{prefix_length}")
    return network

def deduplicate_networks(networks: List[ipaddress.IPv4Network]) -> List[ipaddress.IPv4Network]:
    networks = list(set(networks))
    temp_networks = list(networks)
    for network in networks:
        LOGGER.debug(msg=f"Working on {network}")
        other_networks = [x for x in networks if x != network]
        for other_network in other_networks:
            if network.supernet_of(other_network):
                if other_network in temp_networks:
                    LOGGER.debug(msg=f"Removing '{other_network}' as it is a subnet of {network}")
                    temp_networks.remove(other_network)
            elif network.subnet_of(other_network):
                if network in temp_networks:
                    LOGGER.debug(msg=f"Removing '{network}' as it is a subnet of {other_network}")
                    temp_networks.remove(network)
    networks = temp_networks
    return networks


def summarize_networks(networks: List[ipaddress.IPv4Network]):
    networks = deduplicate_networks(networks=networks)

    networks_binary = [(to_bit_string(network=x)[0] , x.prefixlen) for x in networks]

    run = True
    counter = 0
    while run:
        LOGGER.debug(f"Run {counter}")
        run = False
        prefix_set = set([x[1] for x in networks_binary])
        for prefix in prefix_set:
            LOGGER.debug(f"Run {counter}, Prefix: {prefix}")
            network_candidates = [x for x in networks_binary if x[1] == prefix]
            if len(network_candidates) == 1:
                continue
            print(f"{prefix=} {network_candidates=}")
            max_right_common_bits = 0
            max_left_common_bits = 0
            for i in reversed(range(prefix)):
                # LOGGER.debug(msg=f"Checking Right-bit {i}")
                ith_bits = [x[0][i] for x in network_candidates]
                if len(set(ith_bits)) == 1:
                    # All network_candidates have same ith bit
                    max_right_common_bits += 1
                else:
                    break
            for i in range(prefix):
                # LOGGER.debug(msg=f"Checking Left-bit {i}")
                ith_bits = [x[0][i] for x in network_candidates]
                if len(set(ith_bits)) == 1:
                    # All network_candidates have same ith bit
                    max_left_common_bits += 1
                else:
                    break
            print(f"{max_right_common_bits=}\n{max_left_common_bits=}")
            for i in range(max_left_common_bits, prefix-max_right_common_bits):
                LOGGER.debug(f"Run {counter}, Prefix: {prefix} {i=}")
                subnet_bits = list(set([x[0][i:prefix] for x in network_candidates]))
                max_permutations = 2**(prefix-i)
                print(f"{i=} {max_permutations=} {subnet_bits=}")
                summary_network = None
                if len(subnet_bits) < max_permutations:
                    LOGGER.debug(msg=f"Less than {max_permutations=}, continue")
                    continue
                elif len(subnet_bits) == max_permutations:
                    LOGGER.debug(msg=f"Found {len(subnet_bits)=} == {max_permutations=}")
                    supernet_binary = (f"{network_candidates[0][0][:i]}{'0'*(32-i)}", i)
                    supernet = from_bit_string(*supernet_binary)
                    LOGGER.debug(msg=f"Found summary network {supernet}")
                    networks_binary.append(supernet_binary)
                    for network_binary in network_candidates:
                        LOGGER.debug(msg=f"Removing network {from_bit_string(*network_binary)} as it is subnet of summary {supernet}")
                        networks_binary.remove(network_binary)
                        network_candidates.remove(network_binary)
                    run = True
                else:
                    LOGGER.debug(msg=f"Found {len(subnet_bits)=} >= {max_permutations=}")
                    for subnet_bits_subset in set(subnet_bits):
                        print(f"{subnet_bits_subset=}")
                        supernet_candidate_bin_prefix = f"{network_candidates[0][0][:i-len(subnet_bits_subset)]}{subnet_bits_subset}"
                        supernet_candidate = (f"{supernet_candidate_bin_prefix}{'0' * (32-i-len(subnet_bits_subset))}", prefix-len(subnet_bits_subset))
                        print(f"{supernet_candidate_bin_prefix=} {supernet_candidate=}")
                        for n in network_candidates:
                            print(f"\t{n[0][:i]}, {n[0].startswith(supernet_candidate_bin_prefix)}")
                        LOGGER.debug(msg=f"Looking for subnets starting with {supernet_candidate_bin_prefix}")
                        subnet_candidates = [x for x in network_candidates if x[0].startswith(supernet_candidate_bin_prefix)]
                        print(f"\t{subnet_candidates=}")
                        if len(subnet_candidates) == max_permutations:
                            supernet_binary = supernet_candidate
                            supernet = from_bit_string(*supernet_binary)
                            LOGGER.debug(msg=f"Found summary network {supernet}")
                            networks_binary.append(supernet_binary)
                            for network_binary in subnet_candidates:
                                LOGGER.debug(msg=f"Removing network {from_bit_string(*network_binary)} as it is subnet of summary {supernet}")
                                networks_binary.remove(network_binary)
                                network_candidates.remove(network_binary)
                            run = True

    networks = [from_bit_string(*x) for x in networks_binary]
    networks = deduplicate_networks(networks=networks)
    return networks



def main():
    networks = [
        "192.168.0.0/24",
        "192.168.1.0/24",
        "192.168.2.0/24",
        "192.168.3.0/25",
        "192.168.3.128/25",
        "192.168.128.0/26",
        "192.168.128.64/26",
        "192.168.128.128/26",
        "192.168.128.192/26",

    ]
    networks = [ipaddress.IPv4Network(x) for x in networks]
    networks2 = [ipaddress.IPv4Network(f"10.3.{100+i}.0/24") for i in range(26)]
    print(summarize_networks(networks=networks2))


if __name__ == '__main__':
    main()

