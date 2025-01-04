with open('rodante.tsv') as fp:
    lines = fp.readlines()

for line in lines:
    try:
        _, code, descr, qty, _ = line.split('\t')
    except ValueError:
        print(line)
        break
    qty = int(qty)
    while qty:
        print(code, descr, sep='\t')
        qty -= 1