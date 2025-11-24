"""
Алгоритмы для расчета расположения узлов графа.
"""
from PyQt6.QtCore import QPointF
import math
import random
from collections import deque

class GraphLayout:
    """Базовый класс для алгоритмов расположения графов."""
    
    def __init__(self, node_distance=100):
        self.node_distance = node_distance
    
    def calculate_layout(self, nodes_map, adjacency_list):
        """
        Вычисляет позиции для узлов графа.
        nodes_map: {value: GraphNodeItem}
        adjacency_list: {node_value: list_of_neighbor_values}
        """
        raise NotImplementedError("Subclasses must implement this method")


class SpringLayout(GraphLayout):
    """Упрощенный и исправленный пружинный алгоритм."""
    
    def __init__(self, node_distance=150, iterations=100, temperature=1.0, cooling=0.95):
        super().__init__(node_distance)
        self.iterations = iterations
        self.temperature = temperature
        self.cooling = cooling

    def calculate_layout(self, nodes_map, adjacency_list):
        """Вычисляет позиции с помощью упрощенного пружинного алгоритма."""
        nodes = list(nodes_map.values())
        if not nodes:
            return

        # 1. Инициализация - используем текущие позиции или случайные
        for node in nodes:
            pos = node.pos()
            if pos.isNull() or (pos.x() == 0 and pos.y() == 0):
                # Если позиция не установлена, инициализируем случайно
                node.setPos(QPointF(
                    random.uniform(-100, 100),
                    random.uniform(-100, 100)
                ))
        
        print(f"SpringLayout: {len(nodes)} nodes, {self.iterations} iterations")
        
        # 2. Итеративное улучшение
        current_temperature = self.temperature
        
        for iteration in range(self.iterations):
            forces = {}
            
            # Инициализируем силы для всех узлов
            for node in nodes:
                forces[node] = QPointF(0, 0)
            
            # Силы отталкивания между всеми парами узлов
            for i, node1 in enumerate(nodes):
                for node2 in nodes[i+1:]:
                    pos1 = node1.pos()
                    pos2 = node2.pos()
                    
                    dx = pos1.x() - pos2.x()
                    dy = pos1.y() - pos2.y()
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 0.1:  # Избегаем деления на 0
                        dx = random.uniform(0.1, 1.0)
                        dy = random.uniform(0.1, 1.0)
                        distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Сила отталкивания (обратно пропорциональна квадрату расстояния)
                    repulsion_force = (self.node_distance * 2) ** 2 / (distance + 1)
                    
                    forces[node1] += QPointF(
                        (dx / distance) * repulsion_force,
                        (dy / distance) * repulsion_force
                    )
                    forces[node2] -= QPointF(
                        (dx / distance) * repulsion_force,
                        (dy / distance) * repulsion_force
                    )
            
            # Силы притяжения между связанными узлами
            for u_val, neighbors in adjacency_list.items():
                if u_val not in nodes_map:
                    continue
                u = nodes_map[u_val]
                
                for v_val in neighbors:
                    if v_val not in nodes_map:
                        continue
                    v = nodes_map[v_val]
                    
                    pos1 = u.pos()
                    pos2 = v.pos()
                    
                    dx = pos2.x() - pos1.x()
                    dy = pos2.y() - pos1.y()
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 0.1:
                        continue
                    
                    # Сила притяжения (пропорциональна расстоянию)
                    attraction_force = (distance - self.node_distance) * 0.1
                    
                    forces[u] += QPointF(
                        (dx / distance) * attraction_force,
                        (dy / distance) * attraction_force
                    )
                    forces[v] -= QPointF(
                        (dx / distance) * attraction_force,
                        (dy / distance) * attraction_force
                    )
            
            # Применяем силы с ограничением температуры
            max_force = current_temperature * 10
            
            for node in nodes:
                force = forces[node]
                
                # Ограничиваем максимальную силу
                force_magnitude = math.sqrt(force.x()**2 + force.y()**2)
                if force_magnitude > max_force:
                    force = QPointF(
                        force.x() / force_magnitude * max_force,
                        force.y() / force_magnitude * max_force
                    )
                
                # Обновляем позицию
                new_pos = node.pos() + force
                node.setPos(new_pos)
            
            # Охлаждение
            current_temperature *= self.cooling


class CircularLayout(GraphLayout):
    """Расположение узлов по кругу - ИСПРАВЛЕННАЯ версия."""
    
    def __init__(self, node_distance=200):  # Оптимальное расстояние
        super().__init__(node_distance)
    
    def calculate_layout(self, nodes_map, adjacency_list):
        """Вычисляет позиции для круговой компоновки."""
        nodes = list(nodes_map.values())
        if not nodes:
            return
            
        n = len(nodes)
        
        # Автоматический расчет радиуса на основе количества узлов
        base_radius = self.node_distance * 0.8
        radius = base_radius * math.sqrt(n)  # Более плавное увеличение
        
        # Для очень маленьких графов делаем круг более компактным
        if n <= 4:
            radius = base_radius * 1.2
        elif n <= 8:
            radius = base_radius * 1.8
        else:
            radius = base_radius * (1 + math.log(n + 2))
        
        print(f"CircularLayout: {n} nodes, radius: {radius:.1f}")
        
        # Рассчитываем центр сцены на основе текущих позиций
        if nodes:
            # Находим текущий центр масс
            center_x = sum(node.pos().x() for node in nodes) / n
            center_y = sum(node.pos().y() for node in nodes) / n
        else:
            center_x, center_y = 0, 0
        
        # Располагаем узлы по кругу
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node.setPos(QPointF(x, y))


class TreeLayout(GraphLayout):
    """Иерархическое расположение в виде дерева - УЛУЧШЕННАЯ версия."""
    
    def __init__(self, node_distance=250):  # Увеличенное расстояние
        super().__init__(node_distance)
    
    def _find_root(self, adjacency_list):
        """Находит корень дерева (узел с минимальной степенью входа)."""
        in_degree = {}
        
        # Считаем входящие степени
        for node in adjacency_list:
            if node not in in_degree:
                in_degree[node] = 0
            for neighbor in adjacency_list[node]:
                if neighbor not in in_degree:
                    in_degree[neighbor] = 0
                in_degree[neighbor] += 1
        
        # Ищем узел с минимальной входящей степенью (вероятный корень)
        if in_degree:
            return min(in_degree.items(), key=lambda x: x[1])[0]
        return None

    def _build_tree_structure(self, adjacency_list, root_value):
        """Строит древовидную структуру из списка смежности."""
        visited = set()
        tree_structure = {}
        
        def dfs(node):
            if node in visited:
                return None
            visited.add(node)
            
            node_data = {
                'value': node,
                'children': []
            }
            
            # Добавляем соседей, которые еще не посещены (для построения дерева)
            for neighbor in adjacency_list.get(node, []):
                if neighbor not in visited:
                    child_data = dfs(neighbor)
                    if child_data:
                        node_data['children'].append(child_data)
            
            return node_data
        
        root_data = dfs(root_value)
        return root_data

    def _calculate_tree_layout(self, node_data, nodes_map, x=0, y=0, level=0):
        """Рекурсивно вычисляет позиции для древовидной структуры."""
        if not node_data:
            return x
            
        node_value = node_data['value']
        children = node_data['children']
        
        # Устанавливаем позицию текущего узла
        if node_value in nodes_map:
            node = nodes_map[node_value]
            node.setPos(QPointF(x, y))
        
        # Если нет детей, возвращаем текущую позицию
        if not children:
            return x
            
        # Вычисляем общую ширину поддерева
        total_width = 0
        child_positions = []
        
        for child in children:
            child_width = self._calculate_subtree_width(child)
            total_width += child_width
        
        # Располагаем детей
        current_x = x - total_width * self.node_distance / 2
        
        for child in children:
            child_width = self._calculate_subtree_width(child)
            child_center = current_x + child_width * self.node_distance / 2
            self._calculate_tree_layout(child, nodes_map, child_center, y + self.node_distance * 2, level + 1)
            current_x += child_width * self.node_distance
        
        return x

    def _calculate_subtree_width(self, node_data):
        """Вычисляет ширину поддерева."""
        if not node_data:
            return 0
            
        children = node_data.get('children', [])
        if not children:
            return 1
            
        total_width = 0
        for child in children:
            total_width += self._calculate_subtree_width(child)
            
        return max(1, total_width)

    def calculate_layout(self, nodes_map, adjacency_list):
        if not nodes_map:
            return
            
        nodes = list(nodes_map.values())
        
        # Находим корень дерева
        root_value = self._find_root(adjacency_list)
        if not root_value or root_value not in nodes_map:
            # Если не нашли корень, берем первый узел
            root_value = list(nodes_map.keys())[0]
        
        # Строим древовидную структуру
        tree_structure = self._build_tree_structure(adjacency_list, root_value)
        
        if tree_structure:
            # Вычисляем позиции используя древовидный алгоритм
            self._calculate_tree_layout(tree_structure, nodes_map, 0, 0)
            print(f"TreeLayout: {len(nodes)} nodes, root: {root_value}")
        else:
            # Fallback: используем компактное расположение по уровням
            self._fallback_layout(nodes_map, adjacency_list, root_value)

    def _fallback_layout(self, nodes_map, adjacency_list, root_value):
        """Резервный алгоритм для случаев, когда нельзя построить дерево."""
        visited = set()
        queue = deque([(root_value, 0, 0)])  # (node, level, position_in_level)
        level_nodes = {}
        
        # BFS для определения уровней и позиций
        while queue:
            node_val, level, pos_in_level = queue.popleft()
            if node_val in visited:
                continue
                
            visited.add(node_val)
            
            # Сохраняем узел для уровня
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append((node_val, pos_in_level))
            
            # Добавляем соседей в порядке их степени (для лучшего баланса)
            neighbors = adjacency_list.get(node_val, [])
            # Сортируем соседей по степени (меньшая степень сначала)
            neighbors_sorted = sorted(neighbors, 
                                   key=lambda n: len(adjacency_list.get(n, [])))
            
            for i, neighbor_val in enumerate(neighbors_sorted):
                if neighbor_val not in visited and neighbor_val in nodes_map:
                    queue.append((neighbor_val, level + 1, i))
        
        # Располагаем узлы по уровням
        max_level = max(level_nodes.keys()) if level_nodes else 0
        
        print(f"TreeLayout (fallback): {len(nodes_map)} nodes, {max_level + 1} levels")
        
        for level, nodes_in_level in level_nodes.items():
            # Увеличенные расстояния между узлами на уровне
            level_width = len(nodes_in_level) * self.node_distance * 3
            start_x = -level_width / 2
            
            for i, (node_val, _) in enumerate(nodes_in_level):
                if node_val in nodes_map:
                    x = start_x + i * self.node_distance * 3
                    y = level * self.node_distance * 2  # Увеличенное расстояние между уровнями
                    nodes_map[node_val].setPos(QPointF(x, y))


class ForceAtlasLayout(GraphLayout):
    """Упрощенная версия ForceAtlas2 алгоритма - УЛУЧШЕННАЯ."""
    
    def __init__(self, node_distance=280, iterations=350):  # Увеличенное расстояние
        super().__init__(node_distance)
        self.iterations = iterations
        
    def _initialize_random_layout(self, nodes, width=1600, height=1200):  # Увеличенная область
        """Инициализация случайным образом."""
        for node in nodes:
            x = random.uniform(-width/2, width/2)
            y = random.uniform(-height/2, height/2)
            node.setPos(QPointF(x, y))
        
    def calculate_layout(self, nodes_map, adjacency_list):
        nodes = list(nodes_map.values())
        if not nodes:
            return

        # Инициализация СЛУЧАЙНАЯ, а не круговая!
        self._initialize_random_layout(nodes, 1800, 1400)  # Увеличенная область
        
        print(f"ForceAtlasLayout: {len(nodes)} nodes, {self.iterations} iterations, distance: {self.node_distance}")

        # Оптимизация
        for iteration in range(self.iterations):
            forces = {node.value: QPointF(0, 0) for node in nodes}
            
            # Отталкивание (сильно усиленное)
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes[i+1:], i+1):
                    pos1 = node1.pos()
                    pos2 = node2.pos()
                    
                    dx = pos1.x() - pos2.x()
                    dy = pos1.y() - pos2.y()
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    if distance > 0:
                        # Сила отталкивания (сильно усиленная)
                        force = 30000 / (distance * distance + 20)  # Усиленное отталкивание
                        forces[node1.value] += QPointF(
                            dx / distance * force,
                            dy / distance * force
                        )
                        forces[node2.value] -= QPointF(
                            dx / distance * force,
                            dy / distance * force
                        )
            
            # Притяжение (ослабленное для большего расстояния)
            for u_val, neighbors in adjacency_list.items():
                if u_val not in nodes_map:
                    continue
                u = nodes_map[u_val]
                
                for v_val in neighbors:
                    if v_val not in nodes_map:
                        continue
                    v = nodes_map[v_val]
                    
                    pos1 = u.pos()
                    pos2 = v.pos()
                    
                    dx = pos2.x() - pos1.x()
                    dy = pos2.y() - pos1.y()
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    if distance > 0:
                        # Сила притяжения (ослабленная для большего расстояния)
                        target_distance = self.node_distance * 1.3  # Увеличенное целевое расстояние
                        if distance < target_distance:
                            force = (distance - target_distance) * 0.025  # Отталкивание если слишком близко
                        else:
                            force = (distance - target_distance) * 0.015  # Притяжение если слишком далеко
                            
                        forces[u.value] += QPointF(
                            dx / distance * force,
                            dy / distance * force
                        )
                        forces[v.value] -= QPointF(
                            dx / distance * force,
                            dy / distance * force
                        )
            
            # Применение сил с замедлением
            speed = 12.0 / (1.0 + iteration / 6.0)  # Более высокая начальная скорость
            
            for node in nodes:
                force = forces[node.value]
                new_pos = node.pos() + force * speed
                
                # Увеличенные границы области
                max_bound = 800  # Увеличенная граница
                new_pos.setX(max(-max_bound, min(max_bound, new_pos.x())))
                new_pos.setY(max(-max_bound, min(max_bound, new_pos.y())))
                
                node.setPos(new_pos)