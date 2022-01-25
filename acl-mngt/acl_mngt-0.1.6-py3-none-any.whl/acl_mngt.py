#!/usr/local/bin/python3

import re
import socket
from ipaddress import IPv4Address


class AclEntry:
    txt_regex = r'^(allow|deny)\s+(ingress|egress)\s+''' + \
                r'(\d+\.\d+\.\d+\.\d+)' + \
                r'(\/(1$|2$|3$|4$|5$|6$|7$|8$|9$|10$|11$|12$|13$|14$|15$|16$' + \
                r'|17$|18$|19$|20$|21$|22$|23$|24$|25$|26$|27$|28$|29$|30$|31$|32$))?$'
    allow = direction = priority = src_subnet = src_prefix_length = dst_subnet = dst_prefix_length = None

    def __init__(self, txt: str = None, allow: bool = None, direction: str = None, priority: int = None,
                 src_subnet: str = None,
                 src_prefix_length: int = 32, dst_subnet: str = None, dst_prefix_length: int = 32):
        self.allow = allow if allow else self.allow
        self.direction = direction if direction else self.direction
        self.priority = priority if priority else self.priority
        self.src_prefix_length = src_prefix_length if src_prefix_length else self.src_prefix_length
        self.dst_prefix_length = dst_prefix_length if dst_prefix_length else self.dst_prefix_length
        if src_subnet:
            if '/' in src_subnet:
                self.src_subnet = src_subnet.split('/')[0]
                self.src_prefix_length = int(src_subnet.split('/')[1])
            else:
                self.src_subnet = src_subnet
        if dst_subnet:
            if '/' in dst_subnet:
                self.dst_subnet = dst_subnet.split('/')[0]
                self.dst_prefix_length = int(dst_subnet.split('/')[1])
            else:
                self.dst_subnet = dst_subnet
        if txt:
            txt = txt.strip()
            character = self.validate_txt_input(txt)
            if type(character) is int:
                raise ValueError(f"Not a valid ACL:\n'{txt}'\n{' ' * (character + 1)}^ error at character {character}")
            if match := re.search(self.txt_regex, txt):
                self.allow = match.group(1) == 'allow'
                self.direction = match.group(2)
                self.dst_subnet = match.group(3)
                self.dst_prefix_length = int(match.group(5)) if match.group(5) else 32
            else:
                raise Exception(f"Raise condition, not a valid ACL:\n'{txt}'")

    def validate_txt_input(self, txt):
        """
        Validate raw txt input
        """
        # Setup
        unpack_txt = txt.strip()
        character = len(txt) - len(unpack_txt)

        # Validate allow/deny
        if unpack_txt[:5] == 'allow':
            unpack_txt = unpack_txt[5:]
        elif unpack_txt[:4] == 'deny':
            unpack_txt = unpack_txt[4:]
        else:
            return character
        unpack_txt = unpack_txt.strip()
        character = len(txt) - len(unpack_txt)

        # Validate ingress/egress
        if unpack_txt[:7] == 'ingress':
            unpack_txt = unpack_txt[7:]
        elif unpack_txt[:6] == 'egress':
            unpack_txt = unpack_txt[6:]
        else:
            return character
        unpack_txt = unpack_txt.strip()
        character = len(txt) - len(unpack_txt)

        # Validate IPv4 address
        ipv4 = unpack_txt.split('/')[0]
        if not self.is_valid_ipv4_address(ipv4):
            return character

        unpack_txt = unpack_txt[len(ipv4):]
        character = len(txt) - len(unpack_txt)

        # Validate optional prefix length/cidr notation
        if len(unpack_txt.strip()) == 0:
            return True

        if unpack_txt[0] != '/':
            return character
        unpack_txt = unpack_txt[1:]
        character = len(txt) - len(unpack_txt)

        if not unpack_txt.strip().isdigit():
            return character
        if int(unpack_txt.strip()) not in list(range(1, 33)):
            return character
        return True

    def validate(self, raise_error=False):
        """
        Validate object
        """
        if not isinstance(self.allow, bool):
            if raise_error:
                raise ValueError("ValueError: Boolean 'allow' not set")
            return False
        if not isinstance(self.direction, str) or self.direction not in ['ingress', 'egress']:
            if raise_error:
                raise ValueError(f"ValueError: Str direction None or not in ['ingress', 'egress']: '{self.direction}'")
        if not isinstance(self.priority, int) or self.priority not in list(range(10, 101)):
            if raise_error:
                raise ValueError(f"ValueError: Int priority None or not in range(10,101): '{self.priority}'")
        if not isinstance(self.src_subnet, str) or not self.is_valid_ipv4_address(self.src_subnet):
            if raise_error:
                raise ValueError(f"ValueError: Str src_subnet None or invalid: '{self.src_subnet}'")
            return False
        if not isinstance(self.src_prefix_length, int) or self.src_prefix_length not in list(range(1, 33)):
            if raise_error:
                raise ValueError(f"ValueError: Int src_prefix_length None or invalid: '{self.src_prefix_length}'")
            return False
        if not isinstance(self.dst_subnet, str) or not self.is_valid_ipv4_address(self.dst_subnet):
            if raise_error:
                raise ValueError(f"ValueError: Str dst_subnet None or invalid: '{self.dst_subnet}'")
            return False
        if not isinstance(self.dst_prefix_length, int) or self.dst_prefix_length not in list(range(1, 33)):
            if raise_error:
                raise ValueError(f"ValueError: Int dst_prefix_length None or invalid: '{self.dst_prefix_length}'")
            return False
        return True

    @staticmethod
    def is_valid_ipv4_address(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False
        return True

    @staticmethod
    def wildcard_mask(prefix_length: int):
        # str(IPv4Address(int(IPv4Address._make_netmask('24')[0])^(2**32-1)))
        # output: 0.0.0.255
        # pylint: disable
        return str(IPv4Address(int(IPv4Address._make_netmask(prefix_length)[0]) ^ (2 ** 32 - 1)))

    def format_str(self, vendor: str):
        self.validate(raise_error=True)
        a_subnet = self.src_subnet if self.direction == 'egress' else self.dst_subnet
        a_prefix_length = self.src_prefix_length if self.direction == 'egress' else self.dst_prefix_length
        b_subnet = self.dst_subnet if self.direction == 'egress' else self.src_subnet
        b_prefix_length = self.dst_prefix_length if self.direction == 'egress' else self.src_prefix_length
        if vendor == 'cisco':
            s = f"ip:inacl#{self.priority}={'allow' if self.allow else 'deny'} ip " \
                f"{'host' if a_prefix_length == 32 else ''} {a_subnet} " \
                f"{self.wildcard_mask(a_prefix_length) if a_prefix_length != 32 else ''} " \
                f"{'host' if b_prefix_length == 32 else ''} {b_subnet} " \
                f"{self.wildcard_mask(b_prefix_length) if b_prefix_length != 32 else ''}"
            # Remove consequtive spaces and trailing spaces
            s = re.sub(r"\s+$", "", s, flags=re.M)
            s = re.sub(r"\s+", " ", s)
            return s
        raise ValueError(f"Invalid format type: '{format}'")

    def __str__(self):
        self.validate(raise_error=True)
        return f"{'allow' if self.allow else 'deny'} {self.src_subnet}/{self.src_prefix_length}"

    def __repr__(self):
        if self.validate():
            return f"{'allow' if self.allow else 'deny'} {self.src_subnet}/{self.src_prefix_length} " \
                   f"-> {self.dst_subnet}/{self.dst_prefix_length}"
        return f"Invalid: {'allow' if self.allow else 'deny'} {self.src_subnet}/{self.src_prefix_length} " \
            f"-> {self.dst_subnet}/{self.dst_prefix_length}"


class AclFactory:
    def __init__(self, accesslist: str, src_subnet: str, src_routed_subnets_list: list = None):
        self.aclEntryList = []
        self.priority = 10
        acl_text_entry_list = accesslist.split('\n')
        line = 1
        for acl_text_entry in acl_text_entry_list:
            acl_text_entry = acl_text_entry.strip()
            if acl_text_entry == '' or acl_text_entry[0] == '#':
                line += 1
                continue
            try:
                self.aclEntryList.append(AclEntry(acl_text_entry, priority=self.priority, src_subnet=src_subnet))
            except ValueError as e:
                raise ValueError(str(e) + f" on line {line}.") from None
            line += 1
            self.priority += 1
        if src_routed_subnets_list:
            for rsubnet in src_routed_subnets_list:
                line = 1
                for acl_text_entry in acl_text_entry_list:
                    acl_text_entry = acl_text_entry.strip()
                    if acl_text_entry == '' or acl_text_entry[0] == '#':
                        line += 1
                        continue
                    self.aclEntryList.append(AclEntry(acl_text_entry, priority=self.priority, src_subnet=rsubnet))
                    self.priority += 1

    def render(self, vendor: str):
        ret = ""
        for i in self.aclEntryList:
            ret += i.format_str(vendor) + "\n"
        ret += f"ip:inacl#{self.priority}=deny ip any any"
        return ret
