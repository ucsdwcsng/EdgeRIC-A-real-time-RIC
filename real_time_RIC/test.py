f_params = open("param_edgeric.txt")
line_algo = 0
lines = f_params.readlines()
idx_algos_str = lines[line_algo].split()
idx_algos = [eval(i) for i in idx_algos_str]
print(idx_algos_str)
print(idx_algos)