e1 = Element(parameters={"p1": 0.1}, states={"S": 10.0})

u1 = Unit([e1])
u2 = Unit([e1])

e1.set_parameters({"e1_p1": 0.2})
u1.set_parameters({"u1_e1_p1": 0.3})
u2.set_parameters({"u2_e1_p1": 0.4})
