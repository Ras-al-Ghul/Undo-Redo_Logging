#!/usr/bin/python
import sys

def open_log_files(quanta):
	name = "./../log/" + str(quanta + 1)
	name += ".txt"
	f1 = open(name + "_undo", "wa")
	f2 = open(name + "_redo", "wa")
	return f1, f2

def operate(p1, p2, op):
	if op == 1:
		return p1 + p2
	if op == 2:
		return p1 * p2
	if op == 3:
		return p1 - p2

def log_transaction(ttype, var, mvar = None, varname = None, t = None, fp = None, tnumber = None):
	if ttype == "start":
		values = ""
		for key, value in sorted(var.items()):
			values += " " + key + " " + str(value)
		values += "\n"
		tnumber = tnumber + 1
		return "<START T" + str(tnumber) + ">" + values

	elif ttype == "modify":
		values = ""
		for key, value in sorted(var.items()):
			values += " " + key + " " + str(value)
		values += "\n"
		tnumber = tnumber + 1
		tempvalue = mvar[varname]
		if tempvalue == -1:
			tempvalue = var[varname]
		t += "<T" + str(tnumber) + "," + varname + "," + str(tempvalue) + ">" + values
		return t

	elif ttype == "commit":
		values = ""
		for key, value in sorted(var.items()):
			values += " " + key + " " + str(value)
		values += "\n"
		tnumber = tnumber + 1
		t += "<COMMIT T" + str(tnumber) + ">" + values
		return t

	elif ttype == "flushlog":
		fp.write(t)
		t = ""
		return t

def read_transactions():
	try:
		with open("./T1", 'r') as file1:
			T1 = file1.readlines()
			T1 = [T1[i].strip("\n") for i in range(len(T1))]
		with open("./T2", 'r') as file2:
			T2 = file2.readlines()
			T2 = [T2[i].strip("\n") for i in range(len(T2))]
		with open("./T3", 'r') as file3:
			T3 = file3.readlines()
			T3 = [T3[i].strip("\n") for i in range(len(T3))]
		file1.close()
		file2.close()
		file3.close()
		return T1, T2, T3
	except:
		print "[Error] Transaction files T1, T2 or T3 not found in directory. Aborting"
		sys.exit(0)

def main():
	T1, T2, T3 = read_transactions()
	for quantum in range(max(len(T1), len(T2), len(T3))):
		file_pointer_undo, file_pointer_redo = open_log_files(quantum)
		variables = {"A": 8, "B": 8, "C": 5, "D": 10}
		mvariables = {"A": -1, "B": -1, "C": -1, "D": -1}
		fp1, fp2, fp3 = 0, 0, 0
		t_undo = []
		t_redo = []
		var = [[], [], []]
		varval = [[], [], []]
		flag = [0] * 3
		readflag = [0] * 3
		while(1):
			command1 = []
			command2 = []
			command3 = []
			for i in range(quantum + 1):
				try:
					command1.append(T1[fp1 + i])
				except:
					pass
				try:
					command2.append(T2[fp2 + i])
				except:
					pass
				try:
					command3.append(T3[fp3 + i])
				except:
					pass
			fp1 += quantum + 1
			fp2 += quantum + 1
			fp3 += quantum + 1
			command = [command1, command2, command3]

			for it in range(3):
				if command[it] is []:
					continue
				if flag[it] == 0:
					t_undo.append(log_transaction("start", variables, tnumber = it))
					t_redo.append(log_transaction("start", variables, tnumber = it))
				for i in command[it]:
					if 'READ' in i:
						i = i.replace('READ(', "")
						tempval = mvariables[i[0]]
						if tempval == -1:
							tempval = variables[i[0]]
						tempvar = i[i.index(",")+1: -1].lstrip()
						if tempvar not in var[it]:
							var[it].append(tempvar)
							varval[it].append(tempval)
						else:
							varval[it][var[it].index(tempvar)] = tempval
					
					elif 'WRITE' in i:
						i = i.replace('WRITE(', "")
						tempvar_update = i[0]
						tempvar_write = i[i.index(",")+1: -1].lstrip()
						t_undo[it] = log_transaction("modify", variables, mvar = mvariables, t = t_undo[it], varname = tempvar_update, tnumber = it)
						mvariables[tempvar_update] = varval[it][var[it].index(tempvar_write)]
						t_redo[it] = log_transaction("modify", variables, mvar = mvariables, t = t_redo[it], varname = tempvar_update, tnumber = it)
						# print t_undo[it]

					elif 'OUTPUT' in i:
						if flag[it] == 0:
							t_undo[it] = log_transaction("flushlog", variables, t = t_undo[it], fp = file_pointer_undo)
							t_redo[it] = log_transaction("commit", variables, t = t_redo[it], tnumber = it)
							t_redo[it] = log_transaction("flushlog", variables, t = t_redo[it], fp = file_pointer_redo)
						i = i.replace('OUTPUT(', "")
						tempvar_update_database = i[-2]
						variables[tempvar_update_database] = mvariables[tempvar_update_database]
						flag[it] += 1
						if flag[it] == 2:
							t_undo[it] = log_transaction("commit", variables, t = t_undo[it], tnumber = it)
							t_undo[it] = log_transaction("flushlog", variables, t = t_undo[it], fp = file_pointer_undo)

					elif '=' in i:
						try:
							tempvar_update = i[:i.index(":")].rstrip()
						except:
							tempvar_update = i[:i.index("=")].rstrip()
						i = i[i.index("=") + 1:].lstrip()
						if '+' in i:
							tempvar1 = i[:i.index("+")].rstrip()
							tempvar2 = i[i.index("+")+1:].rstrip()
							op = 1
						elif '*' in i:
							tempvar1 = i[:i.index("*")].rstrip()
							tempvar2 = i[i.index("*")+1:].rstrip()
							op = 2
						elif '-' in i:
							tempvar1 = i[:i.index("-")].rstrip()
							tempvar2 = i[i.index("-")+1:].rstrip()
							op = 3
						try:
							tempvar2 = int(tempvar2)
							updatevalue = operate(varval[it][var[it].index(tempvar1)], tempvar2, op)
						except:
							try:
								tempvar1 = int(tempvar1)
								updatevalue = operate(varval[it][var[it].index(tempvar2)], tempvar1, op)
							except:
								updatevalue = operate(varval[it][var[it].index(tempvar1)], varval[it][var[it].index(tempvar2)], op)
						varval[it][var[it].index(tempvar_update)] = updatevalue

			if fp1 >= len(T1) and fp2 >= len(T2) and fp3 >= len(T3):
				break
		tempdict = {"A": 16, "B": 16, "C": 16, "D": 17}
		if variables == tempdict:
			file_pointer_undo.write(str(quantum + 1))
			file_pointer_redo.write(str(quantum + 1))
		file_pointer_undo.close()
		file_pointer_redo.close()

if __name__ == '__main__':
	main()