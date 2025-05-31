from ctypes import *

# name = create_string_buffer(b"test12", 10)
# print(name, "-> name")
# print(name.raw, "-> name")
# print(name.value, "-> name")


# name.value = b"doghaha"
# print(name, "-> name")
# print(name.raw, "-> name")
# print(name.value, "-> name")


# name2 = c_char_p(b"test12")
# print(name2, "-> name2")
# print(name2.value, "-> name2")


# name2.value = b"doghaha"
# print(name2, "-> name2")
# print(name2.value, "-> name2")

# STRING WITH POINTER (c_char_p)

# str_ptr = c_char_p(b"cat")
# print("Before:", str_ptr.value, "-> points to", hex(cast(str_ptr, c_void_p).value))

# str_ptr.value = b"dog"
# print("After :", str_ptr.value, "-> points to", hex(cast(str_ptr, c_void_p).value))


# num = c_int(1233333344443)
# print("Using cast():     ", hex(cast(pointer(num), c_void_p).value), f"the value is {num.value}")
# num.value = 456
# print("Using cast():     ", hex(cast(pointer(num), c_void_p).value), f"the value is {num.value}")
# print("Integer address remains constant.")

# n1 = c_int(12)
# n2 = pointer(n1)
# print(n1)
# print(n2)
# print(n2.contents)
# n2.contents.value = 15
# print("-------")
# print(hex(addressof(n1)))
# print(n2)
# print(n2.contents)



# letter = create_string_buffer(5)
# let1 = byref(letter)

# letter.value = b"a"
# print(cast(let1, POINTER(c_int)).contents, "--> a")
# letter.value = b"b"
# print(cast(let1, POINTER(c_int)).contents, "--> b")
# letter.value = b"c"
# print(cast(let1, POINTER(c_int)).contents, "--> c")


class person(Structure):
    _fields_ = [("name", c_char_p),("age", c_int)]

bob = person(b"bob", 32)

print(bob.name, bob.age)


list_array = person * 3
the_array = list_array()

the_array[0] = person(b"james", 41)
the_array[1] = person(b"pames", 45)
the_array[2] = person(b"lames", 12)

for person in the_array:
    print(person.name, " ", person.age)
