import sys
from pysat.formula import CNF
from pysat.solvers import Cadical195

def read_graph(filename):
    """讀取圖文件，返回頂點數、邊數和邊列表"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    # 第一行：頂點數和邊數
    n, m = map(int, lines[0].split())
    edges = []
    for line in lines[1:]:
        u, v = map(int, line.split())
        edges.append((u, v))
    return n, edges

def generate_variables(n):
    """生成變數映射：x_{v,p} -> 變數編號"""
    var_map = {}
    var_count = 0
    for v in range(1, n + 1):  # 頂點從 1 到 n
        for p in range(1, n + 1):  # 位置從 1 到 n
            var_count += 1
            var_map[(v, p)] = var_count
    return var_map, var_count

def generate_clauses(n, edges, var_map):
    """生成 CNF 子句"""
    cnf = CNF()

    # 1. Position-Cover：每個位置至少有一個頂點
    for p in range(1, n + 1):
        clause = [var_map[(v, p)] for v in range(1, n + 1)]
        cnf.append(clause)

    # 2. Position-Uniqueness：每個位置至多一個頂點
    for p in range(1, n + 1):
        for u in range(1, n + 1):
            for v in range(u + 1, n + 1):
                cnf.append([-var_map[(u, p)], -var_map[(v, p)]])

    # 3. Vertex-Cover：每個頂點至少出現在一個位置
    for v in range(1, n + 1):
        clause = [var_map[(v, p)] for p in range(1, n + 1)]
        cnf.append(clause)

    # 4. Vertex-Uniqueness：每個頂點至多出現在一個位置
    for v in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                cnf.append([-var_map[(v, i)], -var_map[(v, j)]])

    # 5. Adjacency-Constraints：相鄰位置的頂點必須相連
    # 構建鄰接表
    adj = {v: set() for v in range(1, n + 1)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)  # 無向圖

    # 對於 p=1,...,n-1
    for p in range(1, n):
        for u in range(1, n + 1):
            for v in range(1, n + 1):
                if v not in adj[u]:  # 如果 (u,v) 不在邊集中
                    cnf.append([-var_map[(u, p)], -var_map[(v, p + 1)]])

    # 回到起點：p=n 到 p=1
    for u in range(1, n + 1):
        for v in range(1, n + 1):
            if v not in adj[u]:
                cnf.append([-var_map[(u, n)], -var_map[(v, 1)]])

    return cnf

def decode_model(n, var_map, model):
    """從 SAT 模型中提取 Hamiltonian Cycle"""
    path = [None] * n  # 位置 p 上的頂點
    for (v, p), var in var_map.items():
        if var in model:  # 如果變數為真
            path[p - 1] = v  # 位置 p 對應頂點 v
    return path

def main():
    if len(sys.argv) != 2:
        print("Usage: python reduce_hc.py graph.txt > hc.cnf")
        sys.exit(1)

    # 讀取圖
    filename = sys.argv[1]
    n, edges = read_graph(filename)

    # 生成變數
    var_map, var_count = generate_variables(n)

    # 生成子句
    cnf = generate_clauses(n, edges, var_map)

    # 將 CNF 寫入標準輸出（DIMACS 格式）
    print(f"p cnf {var_count} {len(cnf.clauses)}")
    for clause in cnf.clauses:
        print(" ".join(map(str, clause)) + " 0")

    # 使用 Cadical195 求解
    with Cadical195(bootstrap_with=cnf) as solver:
        if solver.solve():
            print("SAT")
            model = solver.get_model()
            # 解釋 Hamiltonian Cycle
            path = decode_model(n, var_map, model)
            print("Hamiltonian Cycle:", " -> ".join(map(str, path + [path[0]])))
        else:
            print("UNSAT")
            print("No Hamiltonian Cycle exists.")

if __name__ == "__main__":
    main()