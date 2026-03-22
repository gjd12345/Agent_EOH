import numpy as np
import types
import warnings
import sys
import importlib
import os
import traceback
from prompts import GetPrompts

class Evaluation():
    def __init__(self):
        self.n_instance = 5
        self.n_customers = 50
        self.capacity = 100
        self.depot = 0
        self.instance_data = self.generate_instances()
        self.prompts = GetPrompts()
        self._last_error = None
        self._last_traceback = None

    def generate_instances(self):
        # CVRPLIB instances
        import os
        
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        files = [f for f in os.listdir(data_dir) if f.endswith(".vrp")]
        
        instances = []
        for file in files:
            path = os.path.join(data_dir, file)
            instance = self.read_vrplib_instance(path)
            # Add giant tour placeholder
            dist_matrix = instance['dist_matrix']
            instance['giant_tour'] = self.generate_giant_tour(dist_matrix)
            instances.append(instance)
            
        return instances

    def read_vrplib_instance(self, file_path):
        """Parse CVRPLIB .vrp file"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        instance = {}
        coord_section = False
        demand_section = False
        coords = []
        demands = []
        
        for line in lines:
            if "CAPACITY" in line:
                instance['capacity'] = int(line.split()[-1])
            elif "NODE_COORD_SECTION" in line:
                coord_section = True
                continue
            elif "DEMAND_SECTION" in line:
                coord_section = False
                demand_section = True
                continue
            elif "DEPOT_SECTION" in line:
                break
                
            if coord_section:
                parts = line.split()
                # CVRPLIB uses 1-based indexing, we keep it but coords[0] will be depot
                try:
                    coords.append([float(parts[1]), float(parts[2])])
                except: pass
            elif demand_section:
                try:
                    demands.append(int(line.split()[1]))
                except: pass
                
        instance['coords'] = np.array(coords)
        instance['demands'] = np.array(demands)
        instance['n_customers'] = len(coords) - 1
        
        # Calculate distance matrix
        dist_matrix = np.sqrt(np.sum((instance['coords'][:, np.newaxis, :] - instance['coords'][np.newaxis, :, :]) ** 2, axis=-1))
        instance['dist_matrix'] = dist_matrix
        instance['name'] = os.path.basename(file_path)
        
        return instance

    def generate_giant_tour(self, dist_matrix):
        """Standard Nearest Neighbor Giant Tour generation."""
        n = len(dist_matrix)
        unvisited = list(range(1, n))
        current = self.depot
        tour = []
        while unvisited:
            next_node = min(unvisited, key=lambda x: dist_matrix[current, x])
            tour.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        return np.array(tour)

    def optimal_split(self, giant_tour, demands, dist_matrix, capacity):
        """
            输入:
                gaint tour :返回的是llm生成的客户排序
                demands :每个客户的货物需求量
                dist_matrix ：所有节点（包括仓库 0 和客户）之间的距离矩阵
                capacity ：单辆卡车的最大载重
            输出:
                routes:路线:第i辆车去对应的客户那边
        """
        n = len(giant_tour)
        # dp[i] 存储的是 切分前 i 个客户所需的最小总距离
        # 状态转移矩阵:dp[i] = min_{1 ≤ j ≤ i, 且 sum_{k=j}^{i} 满足[giant_tour[k-1]] ≤ capacity} ( dp[j-1] + cost(j, i) )
        dp = np.full(n + 1, np.inf)
        dp[0] = 0 
        
        # 还要输出一个具体的最优路线,用pred来记录切分点
        pred = np.zeros(n + 1, dtype=int)
        
        for i in range(1, n + 1):
            load = 0
            # 内层循环 j：倒序尝试将第 j 到第 i 个客户分配给同一辆新卡车
            for j in range(i, 0, -1):
                load += demands[giant_tour[j-1]]
                
                if load > capacity: break
                
                # 计算这辆新卡车跑这一趟的物理距离：从仓库出发 -> 客户 j -> ... -> 客户 i -> 回到仓库
                cost = dist_matrix[0, giant_tour[j-1]] 
                for k in range(j, i):
                    cost += dist_matrix[giant_tour[k-1], giant_tour[k]] 
                cost += dist_matrix[giant_tour[i-1], 0] 
                
                # DP 状态转移：
                if dp[j-1] + cost < dp[i]:
                    dp[i] = dp[j-1] + cost
                    pred[i] = j-1 # 记录：为了达到最优的 dp[i]，最后一刀应该切在 j-1 这个位置
            
        # 从后往前推导出具体的车辆派送路线
        routes = []
        curr = n
        while curr > 0:
            prev = pred[curr]
            # 截取 giant_tour 中从 prev 到 curr 的这一段，这就是一辆卡车的完整服务名单
            routes.append(giant_tour[prev:curr].tolist())
            curr = prev
            
        # 因为我们是从最后一个客户往前推的，所以得到的路线列表是倒序的，这里将其翻转回正常顺序
        routes.reverse()
        return routes

    def check_constraints(self, routes, demands, capacity):
        visited = set()
        for route in routes:
            route_demand = 0
            for node in route:
                if node in visited:
                    return False # Duplicate visit
                visited.add(node)
                route_demand += demands[node]
            if route_demand > capacity:
                return False
        
        # Check if all customers visited
        if len(visited) != len(demands) - 1: # -1 for depot
            return False
            
        return True

    def calculate_total_distance(self, routes, dist_matrix):
        total_dist = 0
        for route in routes:
            if not route: continue
            total_dist += dist_matrix[self.depot, route[0]]
            for i in range(len(route) - 1):
                total_dist += dist_matrix[route[i], route[i+1]]
            total_dist += dist_matrix[route[-1], self.depot]
        return total_dist

    def run_local_search(self, routes, dist_matrix, demands, capacity):
        """
        用局部搜索算子来实现路线的微调:
            1.2-opt:调整两个客户的访问顺序,看看会不会更好
            2.relocate:在满足负载的条件下,讲某个客户从一个路线换到另一个路线上
        """
        best_routes = [list(r) for r in routes]
        
        def calculate_route_cost(route):
            if not route: return 0
            c = dist_matrix[self.depot, route[0]]
            for k in range(len(route)-1):
                c += dist_matrix[route[k], route[k+1]]
            c += dist_matrix[route[-1], self.depot]
            return c

        def two_opt_intra(r_idx):
            route = best_routes[r_idx]
            n_nodes = len(route)
            if n_nodes < 2: 
                return False
            best_imp = 0
            move = None
            
            # Simple 2-opt: reverse segment i..j
            for i in range(n_nodes - 1):
                for j in range(i + 1, n_nodes):
                    # Cost delta calculation
                    n_i_prev = self.depot if i == 0 else route[i-1]
                    n_i = route[i]
                    n_j = route[j]
                    n_j_next = self.depot if j == n_nodes - 1 else route[j+1]
                    
                    current_cost = dist_matrix[n_i_prev, n_i] + dist_matrix[n_j, n_j_next]
                    new_cost = dist_matrix[n_i_prev, n_j] + dist_matrix[n_i, n_j_next]
                    
                    diff = new_cost - current_cost
                    if diff < best_imp - 1e-6:
                        best_imp = diff
                        move = (i, j)
            
            if move:
                i, j = move
                route[i:j+1] = reversed(route[i:j+1])
                return True
            return False

        def relocate_inter():
            nonlocal best_routes
            has_imp = False
            for r1_idx in range(len(best_routes)):
                for r2_idx in range(len(best_routes)):
                    if r1_idx == r2_idx: continue
                    r1 = best_routes[r1_idx]
                    r2 = best_routes[r2_idx]
                    if not r1: continue
                    
                    r2_load = sum(demands[n] for n in r2)
                    
                    for i, cust in enumerate(r1):
                        if r2_load + demands[cust] > capacity: continue
                        
                        # Try insert at all positions in r2
                        base_cost = calculate_route_cost(r1) + calculate_route_cost(r2)
                        
                        # Remove from r1
                        r1_new = r1[:i] + r1[i+1:]
                        
                        best_pos = -1
                        min_delta = 0
                        
                        # Calc r1 reduction
                        # ... simplified for speed: just recalculate
                        
                        # Try inserting into r2
                        for j in range(len(r2) + 1):
                            r2_new = r2[:j] + [cust] + r2[j:]
                            new_total = calculate_route_cost(r1_new) + calculate_route_cost(r2_new)
                            if new_total < base_cost - 1e-6:
                                min_delta = new_total - base_cost
                                best_pos = j
                                # Greedy first improvement
                                best_routes[r1_idx] = r1_new
                                best_routes[r2_idx] = r2[:best_pos] + [cust] + r2[best_pos:]
                                return True
            return False

        # Main LS Loop
        max_iter = 5 
        for _ in range(max_iter):
            iter_improved = False
            # 1. Intra-route optimization (2-opt)
            for i in range(len(best_routes)):
                if two_opt_intra(i): iter_improved = True
            
            # 2. Inter-route optimization (Relocate)
            # Only run if 2-opt didn't do much, or periodically
            if not iter_improved:
                if relocate_inter(): iter_improved = True
            
            if not iter_improved: break
            
        return best_routes

    def evaluate(self, code_string):
        self._last_error = None
        self._last_traceback = None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # 1. Execute LLM Heuristic
                heuristic_module = types.ModuleType("heuristic_module")
                try:
                    exec(code_string, heuristic_module.__dict__)
                except Exception as e:
                    self._last_error = f"Exec error: {str(e)}"
                    self._last_traceback = traceback.format_exc()
                    return None
                
                if 'generate_giant_tour' not in heuristic_module.__dict__:
                    self._last_error = "Missing 'generate_giant_tour' function"
                    return None
                
                total_fitness = 0
                
                for instance in self.instance_data:
                    # 2. Run Heuristic
                    try:
                        tour = heuristic_module.generate_giant_tour(
                            instance['coords'], 
                            instance['demands'], 
                            instance['dist_matrix']
                        )
                    except Exception as e:
                        # Log the error for the Agent to fix
                        self._last_error = f"Runtime error: {str(e)}"
                        self._last_traceback = traceback.format_exc()
                        return None
                    
                    # Basic Validation
                    if not isinstance(tour, (list, np.ndarray)):
                        self._last_error = f"Invalid return type: expected list or ndarray, got {type(tour)}"
                        return None
                    
                    tour_arr = np.array(tour).flatten()
                    if len(tour_arr) != instance['n_customers']:
                        self._last_error = f"Invalid tour length: got {len(tour_arr)}, expected {instance['n_customers']}. Hint: tour should contain only customer indices (1 to n), excluding depot 0."
                        return None
                    
                    # Check for duplicates or out-of-bounds
                    if len(set(tour_arr)) != len(tour_arr):
                        self._last_error = "Tour contains duplicate customer indices."
                        return None
                    
                    if np.any((tour_arr < 1) | (tour_arr > instance['n_customers'])):
                        self._last_error = f"Tour contains invalid indices (must be between 1 and {instance['n_customers']})."
                        return None
                    
                    tour = tour_arr
                        
                    # 2. Optimal Split
                    try:
                        routes = self.optimal_split(
                            tour, 
                            instance['demands'], 
                            instance['dist_matrix'], 
                            instance['capacity']
                        )
                    except Exception as e:
                        self._last_error = f"Split error: {str(e)}"
                        self._last_traceback = traceback.format_exc()
                        return None
                    
                    # 3. Calculate Cost
                    dist = self.calculate_total_distance(routes, instance['dist_matrix'])
                    
                    # --- Process Reward (PRM) Placeholder ---
                    # [INJECTED BY AGENT]
                    polar_angles = np.arctan2(np.diff(instance['coords'][tour, 1]), np.diff(instance['coords'][tour, 0]))
                    polar_diff = np.abs(np.diff(polar_angles))
                    load_balance = np.std([sum(instance['demands'][tour[i:i+5]]) for i in range(0, len(tour), 5)])
                    process_reward = (np.sum(polar_diff) * 10) + (load_balance * 50)
                    # Composite Fitness: Distance + Agent-designed Penalties
                    fitness = dist + process_reward
                    
                    total_fitness += fitness
                
                return total_fitness / len(self.instance_data)
                
        except Exception as e:
            self._last_error = f"General error: {str(e)}"
            self._last_traceback = traceback.format_exc()
            return None

    def generate_giant_tour(self, dist_matrix):
        """Standard Nearest Neighbor Giant Tour generation."""
        n = len(dist_matrix)
        unvisited = list(range(1, n))
        current = self.depot
        tour = []
        while unvisited:
            next_node = min(unvisited, key=lambda x: dist_matrix[current, x])
            tour.append(next_node)
            unvisited.remove(next_node)
            current = next_node
        return np.array(tour)
