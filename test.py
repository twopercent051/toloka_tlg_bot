a = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 5},
    {"a": 4, "b": 2},
    {"a": 5, "b": 2},
]

b = list(filter(lambda x: x["b"] == 2, a))

c = list(i["a"] for i in a)

print(c)
