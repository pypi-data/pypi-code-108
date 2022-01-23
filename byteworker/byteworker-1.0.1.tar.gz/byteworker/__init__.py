
# Check if bytes object has double slash
def is_byte_has_double_slash(byte_obj):
  strdata = str(byte_obj)
  if "\\\\" in strdata:
    # print("yes")
    return True
  else: 
    return False

# Change double slash to single slash
def double_slash_to_sinble_slash(byte_obj):
  btstr  = byte_obj.decode("utf-8").encode()
  result = btstr.decode('unicode_escape').encode("raw_unicode_escape")
  return result

# Get perfect byes if has double slash change to single slash
# If has signle slash just return it
def get_perfect_byte(byte_obj):
  if(is_byte_has_double_slash(byte_obj)):
    return double_slash_to_sinble_slash(byte_obj)
  else:
    return byte_obj


def byte_to_word_to_decemal_array(byte_obj):
  perfect_byte_obj = get_perfect_byte(byte_obj)

  byte_obj_length = len(perfect_byte_obj)
  res_list = []

  for i in range(0, byte_obj_length+1, 2):
    data = int.from_bytes(perfect_byte_obj[i:i+2], "little")
    res_list.append(data)

    if(i+2 == byte_obj_length):
      break
  
  return res_list
