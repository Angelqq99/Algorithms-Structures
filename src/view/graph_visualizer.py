"""
Визуализатор графов с анимациями.
"""
from PyQt6.QtCore import QTimer, QPointF, QRectF, Qt
from PyQt6.QtGui import QColor
from view.scene_items import GraphNodeItem, GraphEdgeItem
from view.graph_layout import SpringLayout, CircularLayout, TreeLayout


class GraphVisualizer:
    """Класс для визуализации алгоритмов на графов (BFS, DFS, Dijkstra)."""
    
    def __init__(self, scene, view):
        self.scene = scene
        self.view = view
        self.nodes = {}
        self.edges = {}
        self.adjacency_list = {}
        self.node_values = {}  # Словарь для хранения значений узлов
        
        # Доступные алгоритмы компоновки с увеличенными расстояниями
        self.layout_algorithms = {
            "Spring": SpringLayout(node_distance=300),
            "Circular": CircularLayout(node_distance=350),
            "Tree": TreeLayout(node_distance=250)
        }
        self.current_layout = "Spring"
        self.layout_algorithm = self.layout_algorithms[self.current_layout]
        self.user_selected_layout = None
        
        # Направленность графа (True - ориентированный, False - неориентированный)
        self.is_directed = False  # По умолчанию неориентированный
        self.animation_duration_ms = 500

    def set_layout_algorithm(self, algorithm_name):
        """Устанавливает алгоритм компоновки."""
        if algorithm_name in self.layout_algorithms:
            self.current_layout = algorithm_name
            self.layout_algorithm = self.layout_algorithms[algorithm_name]
            
            if algorithm_name != "Auto":
                self.user_selected_layout = algorithm_name
                
            return True
        return False

    def set_directed(self, is_directed):
        """Устанавливает направленность графа."""
        self.is_directed = is_directed
        print(f"Graph direction set to: {'directed' if is_directed else 'undirected'}")

    def clear(self):
        """Очищает сцену - исправленная версия."""
        try:
            print(f"Clearing graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
            
            # Останавливаем все таймеры анимации
            for node in list(self.nodes.values()):
                if node and hasattr(node, 'color_timer') and node.color_timer.isActive():
                    node.color_timer.stop()
            
            # Удаляем ребра из сцены ПЕРЕД узлами
            for edge_key, edge_item in list(self.edges.items()):
                if edge_item:
                    try:
                        # Явно удаляем связи из узлов
                        if hasattr(edge_item, 'start_node') and edge_item.start_node:
                            edge_item.start_node.remove_connected_edge(edge_item)
                        if hasattr(edge_item, 'end_node') and edge_item.end_node:
                            edge_item.end_node.remove_connected_edge(edge_item)
                        
                        # Удаляем из сцены
                        if edge_item.scene():
                            self.scene.removeItem(edge_item)
                    except Exception as e:
                        print(f"Error removing edge: {e}")
            self.edges.clear()
            
            # Удаляем узлы из сцены
            for node_key, node_item in list(self.nodes.items()):
                if node_item:
                    try:
                        # Очищаем список связанных ребер
                        if hasattr(node_item, 'connected_edges'):
                            node_item.connected_edges.clear()
                        
                        if node_item.scene():
                            self.scene.removeItem(node_item)
                    except Exception as e:
                        print(f"Error removing node: {e}")
            self.nodes.clear()
            
            # Очищаем структуры данных
            self.adjacency_list.clear()
            
            # Принудительное обновление сцены
            self.scene.update()
            
            print("Graph cleared successfully")
            
        except Exception as e:
            print(f"Error clearing graph: {e}")
            import traceback
            traceback.print_exc()

    def _get_edge_key(self, u, v):
        """Возвращает нормализованный ключ ребра."""
        # Для неориентированных графов всегда сортируем
        if not self.is_directed:
            return tuple(sorted((u, v)))
        else:
            return (u, v)  # Для ориентированных графов порядок важен

    def _analyze_graph_structure(self, graph_data):
        """Анализирует структуру графа для выбора лучшего алгоритма компоновки."""
        # Если пользователь явно выбрал компоновку, используем ее
        if self.user_selected_layout and self.user_selected_layout in self.layout_algorithms:
            return self.user_selected_layout
        
        # Собираем все узлы
        all_nodes = set()
        edge_count = 0
        
        for node, neighbors in graph_data.items():
            all_nodes.add(node)
            if isinstance(neighbors, dict):
                all_nodes.update(neighbors.keys())
                edge_count += len(neighbors)
            elif isinstance(neighbors, list):
                for neighbor in neighbors:
                    if isinstance(neighbor, tuple):
                        all_nodes.add(neighbor[0])
                    else:
                        all_nodes.add(neighbor)
                edge_count += len(neighbors)
        
        node_count = len(all_nodes)
        
        # Считаем среднюю степень
        avg_degree = edge_count / node_count if node_count > 0 else 0
        
        # Улучшенная логика выбора
        if node_count <= 6:
            return "Circular"
        elif avg_degree <= 1.5:
            return "Tree"
        else:
            return "Spring"

    def _normalize_graph_data(self, graph_data):
        """Нормализует данные графа к единому формату."""
        normalized = {}
        
        for node, neighbors in graph_data.items():
            normalized[node] = {}
            
            if isinstance(neighbors, dict):
                # Формат уже нормализован: {сосед: вес}
                for neighbor, weight in neighbors.items():
                    normalized[node][neighbor] = weight
                    
            elif isinstance(neighbors, list):
                # Формат списка: [сосед] или [(сосед, вес)]
                for neighbor in neighbors:
                    if isinstance(neighbor, tuple):
                        neighbor_node, weight = neighbor
                        normalized[node][neighbor_node] = weight
                    else:
                        normalized[node][neighbor] = 1  # Вес по умолчанию
        
        return normalized

    def create_graph(self, graph_data, start_node_value=None, is_directed=None):
        """Создает начальное представление графа."""
        # Используем переданное значение или значение по умолчанию
        if is_directed is not None:
            self.is_directed = is_directed
        
        print(f"Creating graph with layout: {self.current_layout}")
        print(f"Graph data: {len(graph_data)} nodes, directed: {self.is_directed}")
        
        self.clear()
        self.adjacency_list = {}

        try:
            # Нормализуем данные графа
            normalized_graph = self._normalize_graph_data(graph_data)
            
            # Автоматический выбор алгоритма компоновки
            best_layout = self._analyze_graph_structure(normalized_graph)
            self.set_layout_algorithm(best_layout)
            print(f"Using {best_layout} layout algorithm")

            # 1. Создание всех узлов
            all_nodes = set()
            all_nodes.update(normalized_graph.keys())
            for neighbors in normalized_graph.values():
                all_nodes.update(neighbors.keys())

            print(f"Total unique nodes: {len(all_nodes)}")

            # Создаем узлы
            for node_val in all_nodes:
                is_start = (node_val == start_node_value) if start_node_value else False
                
                # Получаем значение для отображения
                display_value = self.node_values.get(node_val, node_val)
                
                node_item = GraphNodeItem(display_value, is_start=is_start)
                self.scene.addItem(node_item)
                self.nodes[node_val] = node_item
                self.adjacency_list[node_val] = []

            # 2. Создание ребер
            edge_count = 0
            for u_val, neighbors in normalized_graph.items():
                if u_val not in self.nodes:
                    continue
                
                for v_val, weight in neighbors.items():
                    if v_val not in self.nodes:
                        continue

                    edge_key = self._get_edge_key(u_val, v_val)

                    # Добавляем в список смежности
                    if v_val not in self.adjacency_list[u_val]:
                        self.adjacency_list[u_val].append(v_val)
                    
                    # Для неориентированного графа добавляем обратную связь
                    if not self.is_directed:
                        if v_val not in self.adjacency_list:
                            self.adjacency_list[v_val] = []
                        if u_val not in self.adjacency_list[v_val]:
                            self.adjacency_list[v_val].append(u_val)

                    # Создаем ребро только если его еще нет
                    if edge_key not in self.edges:
                        u_node = self.nodes[u_val]
                        v_node = self.nodes[v_val]
                        edge_item = GraphEdgeItem(u_node, v_node, weight, is_directed=self.is_directed)
                        self.scene.addItem(edge_item)
                        self.edges[edge_key] = edge_item
                        edge_count += 1
                        print(f"Created edge {u_val} -{'>' if self.is_directed else '-'} {v_val} with weight {weight}")

            print(f"Created {len(self.nodes)} nodes and {edge_count} edges")
            print(f"Adjacency list: {self.adjacency_list}")

            # 3. Расчет расположения выбранным алгоритмом
            if self.nodes:
                self.layout_algorithm.calculate_layout(self.nodes, self.adjacency_list)

            # 4. Центрирование и масштабирование
            self._center_and_scale_graph()
                
            return True
            
        except Exception as e:
            print(f"Error creating graph: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _center_and_scale_graph(self):
        """Центрирует и масштабирует граф для лучшего отображения."""
        if not self.nodes:
            return
            
        try:
            # Находим границы графа
            all_positions = [node.pos() for node in self.nodes.values()]
            min_x = min(pos.x() for pos in all_positions)
            max_x = max(pos.x() for pos in all_positions)
            min_y = min(pos.y() for pos in all_positions)
            max_y = max(pos.y() for pos in all_positions)
            
            width = max_x - min_x
            height = max_y - min_y
            
            # Добавляем отступы
            padding = 150
            scene_rect = QRectF(min_x - padding, min_y - padding, 
                            width + 2*padding, height + 2*padding)
            
            # Устанавливаем область сцены
            self.scene.setSceneRect(scene_rect)
            
            # Используем fit_to_content для масштабирования
            if self.view and hasattr(self.view, 'fit_to_content'):
                self.view.fit_to_content(padding)
            else:
                # Fallback для старого поведения
                self.view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
                
            print(f"Graph centered and scaled: {width:.1f}x{height:.1f}")
            
        except Exception as e:
            print(f"Error centering graph: {e}")

    def process_action(self, action):
        """Обрабатывает шаг алгоритма."""
        try:
            action_type = action.get("type")

            if action_type == "graph_init":
                graph_data = action["graph"]
                start_node = action["start_node"]
                
                # Используем настройку направленности из визуализатора
                success = self.create_graph(graph_data, start_node, is_directed=self.is_directed)
                if success:
                    self._center_and_scale_graph()
                return success

            node_val = action.get("node")
            node_item = self.nodes.get(node_val)

            if action_type == "visit" and node_item:
                node_item.highlight("#7EE081") # Зеленый
                
                if "distance" in action:
                    node_item.update_distance_text(str(action["distance"]))
                return True

            elif action_type == "discover" and node_item:
                node_item.highlight("#F9C80E") # Желтый
                
                from_node = action.get('from_node')
                if from_node and from_node in self.nodes:
                    edge_key = self._get_edge_key(from_node, node_val)
                    edge_item = self.edges.get(edge_key)
                    if edge_item:
                        edge_item.highlight("#F9C80E")
                return True

            elif action_type == "update_distance" and node_item:
                node_item.highlight("#4A90E2") # Синий
                
                if "new_distance" in action:
                    node_item.update_distance_text(str(action["new_distance"]))
                return True

            elif action_type == "complete":
                print("Completing algorithm - highlighting all nodes")
                self._highlight_all_nodes("#7EE081")
                self._center_and_scale_graph()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing action: {e}")
            return False

    def _highlight_all_nodes(self, color_hex):
        """Безопасно подсвечивает все узлы."""
        try:
            for node_val, node_item in list(self.nodes.items()):
                if node_item and hasattr(node_item, 'highlight'):
                    node_item.highlight(color_hex)
        except Exception as e:
            print(f"Error highlighting all nodes: {e}")

    def get_graph_info(self):
        """Возвращает информацию о текущем состоянии графа."""
        info = {
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "is_directed": self.is_directed,
            "current_layout": self.current_layout,
            "adjacency_list": self.adjacency_list
        }
        return info