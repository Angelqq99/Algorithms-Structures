"""Визуализатор деревьев с анимациями."""
import faulthandler
faulthandler.enable()  # Включаем обработчик ошибок памяти

from PyQt6.QtCore import QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve, QRectF, Qt, QPointF
from PyQt6.QtGui import QColor, QLinearGradient, QFont, QPen, QBrush
from view.scene_items import TreeNodeItem, TreeConnectionItem, BTreeNodeItem
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout


class TreeVisualizer:
    """Класс для визуализации деревьев с анимациями."""
    
    def __init__(self, scene):
        self.scene = scene
        self.nodes = []
        self.connections = []
        # Увеличены расстояния для больших узлов
        self.layout_algorithm = CenteredTreeLayout(x_spacing=850, y_spacing=850)
        self.value_to_node = {}  # Словарь для сопоставления значений и узлов
        self.current_tree_type = "BST"  # Тип текущего дерева
        self._auto_fit_view()
    
    def clear(self):
        """Очищает сцену от всех элементов дерева безопасно."""
        print(f"TreeVisualizer.clear(): {len(self.nodes)} nodes, {len(self.connections)} connections")
        
        # Останавливаем все анимации и таймеры
        self._stop_all_animations()
        
        # Безопасно удаляем все элементы
        items_to_remove = []
        
        # Собираем все элементы для удаления с проверкой валидности
        for item in self.nodes + self.connections:
            try:
                # Проверяем, что объект еще существует
                if item is None:
                    continue
                    
                # Проверяем, что объект Qt еще не был удален
                try:
                    # Проверяем, есть ли у объекта метод scene и что он находится в нашей сцене
                    if hasattr(item, 'scene'):
                        scene = item.scene()
                        if scene is not None and scene == self.scene:
                            items_to_remove.append(item)
                except RuntimeError:
                    continue
                except AttributeError:
                    continue
                    
            except Exception as e:
                print(f"Error checking item: {e}")
                continue
        
        # Удаляем элементы одним проходом
        removed_count = 0
        for item in items_to_remove:
            try:
                # Подготавливаем к удалению
                if hasattr(item, 'prepareForRemoval'):
                    try:
                        item.prepareForRemoval()
                    except RuntimeError:
                        pass  # Объект уже удален
                
                # Удаляем из сцены
                self.scene.removeItem(item)
                removed_count += 1
            except RuntimeError as e:
                if "wrapped C/C++ object" not in str(e):
                    print(f"Error removing item: {e}")
            except Exception as e:
                print(f"Error removing item: {e}")
        
        print(f"Removed {removed_count} items from scene")
        
        # Очищаем списки
        self.nodes.clear()
        self.connections.clear()
        self.value_to_node.clear()
        
        print("TreeVisualizer cleared successfully")
    
    def _stop_all_animations(self):
        """Останавливает все активные анимации."""
        # Останавливаем анимации узлов
        for node in self.nodes:
            try:
                if node is None:
                    continue
                    
                # Проверяем, что объект еще существует
                if not hasattr(node, '_is_valid'):
                    continue
                    
                # Останавливаем анимации входа
                if hasattr(node, '_entry_anims'):
                    for anim in node._entry_anims:
                        try:
                            if anim and hasattr(anim, 'stop'):
                                anim.stop()
                        except RuntimeError:
                            pass
                    node._entry_anims = []
                
                # Останавливаем анимацию fade (BTree)
                if hasattr(node, '_fade_anim'):
                    try:
                        node._fade_anim.stop()
                    except:
                        pass
                    
            except RuntimeError:
                pass
            except Exception:
                pass
        
        # Останавливаем анимации соединений
        for connection in self.connections:
            try:
                if connection is None:
                    continue
                    
                if hasattr(connection, '_fade_anims'):
                    for anim in connection._fade_anims:
                        try:
                            if anim and hasattr(anim, 'stop'):
                                anim.stop()
                        except RuntimeError:
                            pass
                    connection._fade_anims = []
            except RuntimeError:
                pass
            except Exception:
                pass
    
    def set_tree_type(self, tree_type):
        """Устанавливает тип дерева для цветового кодирования."""
        self.current_tree_type = tree_type
    
    def create_tree_from_structure(self, tree_structure, animate=True):
        """Создает дерево из структуры данных."""
        print(f"Creating tree from structure, animate={animate}")
        
        # Очищаем старое дерево
        self.clear()
        
        if not tree_structure:
            return None
        
        try:
            # Проверяем тип дерева
            if isinstance(tree_structure, list) and tree_structure and 'keys' in tree_structure[0]:
                # Это B-дерево (список узлов)
                print(f"Detected B-tree with {len(tree_structure)} nodes")
                return self._create_btree_from_list_simple(tree_structure, animate)
            else:
                # Обычное дерево (корень + дети)
                print("Detected regular tree")
                return self._create_regular_tree(tree_structure, animate)
                
        except Exception as e:
            print(f"Ошибка при создании дерева: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_regular_tree(self, tree_structure, animate=True):
        """Создает обычное дерево из структуры данных."""
        # Создаем корневой узел
        root = self._create_node_from_data(tree_structure, 0, 0)
        if not root:
            return None
            
        self.nodes.append(root)
        
        # Сохраняем узел в словарь
        if 'keys' in tree_structure:
            self.value_to_node[str(tree_structure['keys'])] = root
        elif 'value' in tree_structure:
            self.value_to_node[tree_structure['value']] = root
        
        # Рекурсивно создаем остальные узлы
        self._build_tree_recursive(root, tree_structure)
        
        # Вычисляем расположение
        self.layout_algorithm.calculate_layout(root)
        
        # Добавляем соединения
        self._create_connections(root)
        
        # Анимируем построение
        if animate:
            self.animate_tree_construction(root)
        else:
            self._add_all_to_scene()
        
        return root
    
    def _create_btree_from_list_simple(self, btree_nodes, animate=True):
        """ПРОСТАЯ версия: Создает B-дерево из списка узлов без сложных анимаций."""
        try:
            if not btree_nodes:
                print("B-tree data is empty")
                return None
            
            print(f"Creating B-tree (simple) with {len(btree_nodes)} nodes")
            
            # Сначала очищаем сцену
            self.clear()
            
            # 1. Создаем все узлы и сохраняем в мапу
            node_map = {}
            
            for node_data in btree_nodes:
                try:
                    if 'keys' not in node_data:
                        continue
                        
                    keys = node_data.get('keys', [])
                    if not isinstance(keys, list):
                        continue
                        
                    is_leaf = node_data.get('is_leaf', False)
                    key_count = node_data.get('key_count', len(keys))
                    node_id = node_data.get('id', len(node_map))
                    
                    # Создаем узел
                    node = BTreeNodeItem(0, 0, keys, is_leaf, key_count)
                    if not node:
                        continue
                    
                    # Устанавливаем цвет типа дерева
                    node.set_tree_type_color("BTree")
                    
                    # Сохраняем узел
                    self.nodes.append(node)
                    node_map[node_id] = node
                    
                    print(f"Created B-tree node {node_id} with keys {keys}")
                    
                except Exception as e:
                    print(f"Error creating node: {e}")
                    continue
            
            print(f"Successfully created {len(self.nodes)} B-tree nodes")
            
            if not self.nodes:
                print("No nodes were created")
                return None
            
            # 2. Создаем связи между узлами
            for node_data in btree_nodes:
                try:
                    node_id = node_data.get('id', -1)
                    if node_id not in node_map:
                        continue
                    
                    node = node_map[node_id]
                    children_ids = node_data.get('children', [])
                    
                    for child_id in children_ids:
                        if child_id in node_map:
                            child = node_map[child_id]
                            node.add_child(child)
                            
                            # Создаем соединение
                            try:
                                connection = TreeConnectionItem(node, child)
                                if connection:
                                    self.connections.append(connection)
                            except Exception as e:
                                print(f"Error creating connection: {e}")
                                
                except Exception as e:
                    print(f"Error creating connections: {e}")
            
            print(f"Created {len(self.connections)} connections")
            
            # 3. Находим корень
            root = None
            
            # Собираем всех детей
            all_children = set()
            for node in self.nodes:
                if node and hasattr(node, 'children'):
                    for child in node.children:
                        if child in self.nodes:
                            all_children.add(child)
            
            # Корень - это узел, который не является чьим-то ребенком
            for node in self.nodes:
                if node and node not in all_children:
                    root = node
                    break
            
            # Если корень не найден, берем первый узел
            if not root and self.nodes:
                root = self.nodes[0]
                print("Using first node as root")
            
            if root:
                print(f"Root node found with {len(root.keys)} keys")
                
                # 4. Вычисляем позиции (простейший алгоритм)
                self._calculate_b_tree_positions_simple(root)
                
                # 5. Добавляем все на сцену сразу
                self._add_all_to_scene()
                
                # 6. Простая анимация или принудительный показ
                if animate:
                    self._animate_btree_simple()
                else:
                    # Если анимация выключена, убеждаемся что всё видно
                    for node in self.nodes:
                        if hasattr(node, 'setOpacity'): node.setOpacity(1.0)
                    for conn in self.connections:
                        if hasattr(conn, 'setOpacity'): conn.setOpacity(1.0)
                
                return root
            else:
                print("No root node found")
                return None
                
        except Exception as e:
            print(f"Ошибка при создании B-дерева: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_b_tree_positions_simple(self, root):
        """Простейший расчет позиций для B-дерева - без рекурсии."""
        if not root:
            return
        
        # Очищаем старые позиции
        for node in self.nodes:
            node.setPos(0, 0)
        
        # Обход в ширину
        from collections import deque
        
        # Используем большие отступы, так как B-Tree узлы широкие
        X_SPACING = 220  
        Y_SPACING = 180
        
        queue = deque([(root, 0, 0)])  # (node, x, y)
        visited = set()
        level_nodes = {}  # y -> list of (x, node)
        
        while queue:
            node, x, y = queue.popleft()
            
            if node in visited:
                continue
            
            visited.add(node)
            
            # Группируем по уровням для последующего центрирования
            if y not in level_nodes:
                level_nodes[y] = []
            level_nodes[y].append(node)
            
            # Добавляем детей
            if hasattr(node, 'children') and node.children:
                # Располагаем детей центрированно под родителем
                num_children = len(node.children)
                # Ширина всех детей
                total_width = num_children * X_SPACING
                start_x = x - total_width / 2 + X_SPACING / 2
                
                for i, child in enumerate(node.children):
                    if child not in visited:
                        child_x = start_x + i * X_SPACING
                        queue.append((child, child_x, y + 1))
        
        # Устанавливаем позиции с учетом отступов
        for y, nodes in level_nodes.items():
            for node in nodes:
                # В queue мы считали относительные координаты, теперь масштабируем
                # Но так как мы уже считали start_x относительно родителя, 
                # то координаты уже "почти" правильные, но могут накладываться.
                # Для B-дерева лучше использовать простой алгоритм уровней:
                pass 
                
        # --- Альтернативный подход: Reingold-Tilford упрощенный ---
        # Для надежности используем простую сетку уровней
        self._layout_btree_levels(level_nodes, Y_SPACING, X_SPACING)

    def _layout_btree_levels(self, level_nodes, y_spacing, x_spacing):
        """Раскладывает уровни, центрируя их."""
        max_y = max(level_nodes.keys()) if level_nodes else 0
        
        # Для каждого уровня
        for y in range(max_y + 1):
            if y not in level_nodes:
                continue
                
            nodes = level_nodes[y]
            # Сортируем узлы по их текущему X (чтобы сохранить порядок детей)
            # В данном случае, просто полагаемся на порядок добавления
            
            # Вычисляем общую ширину уровня
            level_width = len(nodes) * (x_spacing + 50) # +50 запас
            start_x = -level_width / 2
            
            current_x = start_x
            for node in nodes:
                # Проверяем ширину самого узла
                node_width = getattr(node, 'node_width', 160)
                # Позиционируем
                node.setPos(current_x + node_width/2, y * y_spacing)
                
                # Сдвигаем x для следующего узла
                current_x += max(node_width + 20, x_spacing)

    def _animate_btree_simple(self):
        """Простая анимация для B-дерева - плавное появление."""
        # Сначала скрываем все элементы
        for node in self.nodes:
            if hasattr(node, 'setOpacity'):
                node.setOpacity(0.0)
                node.setScale(0.8)
        
        for connection in self.connections:
            if hasattr(connection, 'setOpacity'):
                connection.setOpacity(0.0)
        
        # Постепенно показываем элементы с задержкой
        for i, node in enumerate(self.nodes):
            if hasattr(node, 'setOpacity'):
                QTimer.singleShot(i * 100, lambda n=node: self._fade_in_node(n))
        
        # Показываем соединения после узлов
        connection_delay = len(self.nodes) * 100 + 200
        for i, connection in enumerate(self.connections):
            if hasattr(connection, 'setOpacity'):
                QTimer.singleShot(connection_delay + i * 50, 
                                lambda c=connection: self._fade_in_connection(c))
    
    def _fade_in_node(self, node):
        """Плавное появление узла. ИСПРАВЛЕНА ОШИБКА GC."""
        try:
            if not hasattr(node, '_is_valid') or not node._is_valid:
                return
            
            # Анимация прозрачности
            if hasattr(node, 'setOpacity'):
                # ВАЖНО: передаем node как родителя анимации, чтобы Python не удалил объект
                anim = QPropertyAnimation(node, b"opacity", node)
                anim.setDuration(500)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # Сохраняем ссылку, чтобы наверняка
                node._fade_anim = anim 
                anim.start()
            
            # Анимация масштаба
            if hasattr(node, 'setScale'):
                node.setScale(0.8)
                anim_scale = QPropertyAnimation(node, b"scale", node)
                anim_scale.setDuration(500)
                anim_scale.setStartValue(0.8)
                anim_scale.setEndValue(1.0)
                anim_scale.setEasingCurve(QEasingCurve.Type.OutBack)
                
                node._scale_anim = anim_scale
                anim_scale.start()
                
        except Exception as e:
            print(f"Error in fade_in_node: {e}")
            # Fallback: если анимация упала, просто показываем
            node.setOpacity(1.0)
            node.setScale(1.0)
    
    def _fade_in_connection(self, connection):
        """Плавное появление соединения. ИСПРАВЛЕНА ОШИБКА GC."""
        try:
            if (not hasattr(connection, '_is_valid') or not connection._is_valid or
                not hasattr(connection, 'setOpacity')):
                return
            
            # ВАЖНО: передаем connection как родителя
            anim = QPropertyAnimation(connection, b"opacity", connection)
            anim.setDuration(400)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            connection._fade_anim = anim
            anim.start()
            
        except Exception as e:
            print(f"Error in fade_in_connection: {e}")
            connection.setOpacity(1.0)
    
    def _create_node_from_data(self, node_data, x, y):
        """Создает TreeNodeItem из данных узла."""
        try:
            # Проверяем, является ли это узлом B-дерева
            visual_type = node_data.get('visual_type', '')
            
            if visual_type == 'btree_node' or 'keys' in node_data:
                # Создаем специальный узел для B-дерева
                keys = node_data.get('keys', [])
                key_count = node_data.get('key_count', len(keys))
                is_leaf = node_data.get('is_leaf', False)
                
                # Используем специальный класс для B-дерева
                node = BTreeNodeItem(x, y, keys, is_leaf, key_count)
                node.set_tree_type_color("BTree")
                
                # Сохраняем узел в словарь по ключам
                key_str = str(keys)
                self.value_to_node[key_str] = node
                return node
            
            # Для обычных деревьев
            value = node_data.get('value', '?')
            
            # Определяем цвет в зависимости от типа дерева и данных узла
            tree_type = self.current_tree_type
            if "(" in str(value) and ")" in str(value):
                # Для узлов с дополнительной информацией (AVL, RBT и т.д.)
                if "R)" in str(value) or "(R" in str(value):
                    tree_type = "RedBlackTree_RED"
                elif "B)" in str(value) or "(B" in str(value):
                    tree_type = "RedBlackTree_BLACK"
                elif "h:" in str(value):
                    tree_type = "AVL"
                elif "p:" in str(value):
                    tree_type = "Treap"
            
            # Создаем узел с увеличенным радиусом
            node = TreeNodeItem(x, y, value, radius=95)
            
            # Устанавливаем цвет в зависимости от типа дерева
            node.set_tree_type_color(tree_type)
            
            # Сохраняем узел в словарь по значению
            self.value_to_node[value] = node
            return node
        except Exception as e:
            print(f"Ошибка при создании узла: {e}")
            return None
    
    def _build_tree_recursive(self, parent_node, parent_data):
        """Рекурсивно строит дерево из данных."""
        if not parent_node:
            return
            
        children_data = parent_data.get('children', [])
        
        for child_data in children_data:
            child_node = self._create_node_from_data(child_data, 0, 0)
            if child_node:
                # Для совместимости со старым кодом
                if hasattr(parent_node, 'add_child'):
                    parent_node.add_child(child_node)
                elif hasattr(parent_node, 'children'):
                    parent_node.children.append(child_node)
                    
                self.nodes.append(child_node)
                
                # Сохраняем связь для визуализации B-дерева
                if 'keys' in child_data:
                    self.value_to_node[str(child_data['keys'])] = child_node
                elif 'value' in child_data:
                    self.value_to_node[child_data['value']] = child_node
                
                # Рекурсивно строим поддерево
                self._build_tree_recursive(child_node, child_data)
    
    def _create_connections(self, node):
        """Рекурсивно создает соединения между узлами."""
        if not node:
            return
            
        # Проверяем, есть ли у узла атрибут children
        if not hasattr(node, 'children'):
            return
            
        for child in node.children:
            if child and hasattr(child, 'scenePos') and hasattr(child, '_is_valid') and child._is_valid:
                try:
                    connection = TreeConnectionItem(node, child)
                    # начинаем с нулевой непрозрачности
                    connection.setOpacity(0.0)
                    self.connections.append(connection)
                    self._create_connections(child)
                except Exception as e:
                    print(f"Ошибка при создании соединения: {e}")
    
    def _add_all_to_scene(self):
        """Добавляет все узлы и соединения на сцену."""
        # Сначала добавляем все узлы
        for node in self.nodes:
            try:
                if node is None:
                    continue
                    
                # Проверяем, что объект еще валиден
                if hasattr(node, '_is_valid') and not node._is_valid:
                    continue
                    
                # Проверяем, не находится ли уже на сцене
                try:
                    current_scene = node.scene() if hasattr(node, 'scene') else None
                    if current_scene != self.scene:
                        self.scene.addItem(node)
                        if hasattr(node, 'setVisible'):
                            node.setVisible(True)
                except RuntimeError:
                    # Объект уже удален
                    continue
                    
            except Exception as e:
                print(f"Error adding node to scene: {e}")
        
        # Затем добавляем соединения
        for connection in self.connections:
            try:
                if connection is None:
                    continue
                    
                # Проверяем, что объект еще валиден
                if hasattr(connection, '_is_valid') and not connection._is_valid:
                    continue
                    
                # Проверяем, не находится ли уже на сцене
                try:
                    current_scene = connection.scene() if hasattr(connection, 'scene') else None
                    if current_scene != self.scene:
                        self.scene.addItem(connection)
                        if hasattr(connection, 'setVisible'):
                            connection.setVisible(True)
                        if hasattr(connection, 'setOpacity'):
                            connection.setOpacity(1.0)
                except RuntimeError:
                    # Объект уже удален
                    continue
                    
            except Exception as e:
                print(f"Error adding connection to scene: {e}")
    
    def animate_tree_construction(self, root, delay=360):
        """Анимирует построение дерева."""
        if not root or not hasattr(root, 'setVisible'):
            return
            
        print(f"Animating tree construction with {len(self.nodes)} nodes")
        
        # Сначала добавляем все элементы на сцену невидимыми
        for node in self.nodes:
            try:
                if node is None:
                    continue
                    
                # Проверяем валидность
                if hasattr(node, '_is_valid') and not node._is_valid:
                    continue
                    
                if hasattr(node, 'setVisible'):
                    node.setVisible(False)
                    try:
                        if node.scene() != self.scene:
                            self.scene.addItem(node)
                    except RuntimeError:
                        # Объект уже удален
                        continue
            except Exception as e:
                print(f"Error preparing node for animation: {e}")
        
        for connection in self.connections:
            try:
                if connection is None:
                    continue
                    
                # Проверяем валидность
                if hasattr(connection, '_is_valid') and not connection._is_valid:
                    continue
                    
                if hasattr(connection, 'setVisible'):
                    connection.setVisible(False)
                    try:
                        if connection.scene() != self.scene:
                            self.scene.addItem(connection)
                    except RuntimeError:
                        # Объект уже удален
                        continue
            except Exception as e:
                print(f"Error preparing connection for animation: {e}")
        
        # Анимируем появление узлов и соединений
        self._animate_nodes_appearance(root, delay)
    
    def _animate_nodes_appearance(self, node, delay, current_delay=0):
        """Рекурсивно анимирует появление узлов."""
        if not node or not hasattr(node, 'setVisible'):
            return
        
        # Анимация появления узла
        QTimer.singleShot(current_delay, lambda n=node: self._safe_animate_node_appearance(n))
        
        # Анимация соединений с детьми
        # Проверяем, есть ли у узла атрибут children
        if hasattr(node, 'children'):
            for child in node.children:
                if child and hasattr(child, 'scenePos'):  # Проверяем, что child валиден
                    connection_delay = current_delay + int(delay * 0.5)
                    QTimer.singleShot(connection_delay, 
                                    lambda n=node, c=child: self._safe_animate_connection_appearance(n, c))
                    
                    # Рекурсивно анимируем детей
                    self._animate_nodes_appearance(child, delay, current_delay + delay)
    
    def _safe_animate_node_appearance(self, node):
        """Безопасная анимация появления узла."""
        try:
            self._animate_node_appearance(node)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: узел был удален до анимации")
                return
            raise e
    
    def _animate_node_appearance(self, node):
        """Анимирует появление узла."""
        if not node:
            return
            
        try:
            # Проверяем, что объект еще существует и валиден
            if hasattr(node, '_is_valid') and not node._is_valid:
                return
                
            node.setVisible(True)
            
            # Для обычных узлов
            node.setScale(0.1)
            node.setOpacity(0.0)
            
            scale_anim = QPropertyAnimation(node, b"scale", node)
            scale_anim.setDuration(700)
            scale_anim.setStartValue(0.1)
            scale_anim.setEndValue(1.0)
            scale_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            opacity_anim = QPropertyAnimation(node, b"opacity", node)
            opacity_anim.setDuration(700)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            if not hasattr(node, "_entry_anims"):
                node._entry_anims = []
            node._entry_anims.extend([scale_anim, opacity_anim])
            
            scale_anim.start()
            opacity_anim.start()
                
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: попытка анимировать удаленный объект")
                return
            raise e
        except Exception as e:
            print(f"Ошибка при анимации узла: {e}")
    
    def _safe_animate_connection_appearance(self, parent, child):
        """Безопасная анимация появления соединения."""
        try:
            self._animate_connection_appearance(parent, child)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: соединение было удалено до анимации")
                return
            raise e
    
    def _animate_connection_appearance(self, parent, child):
        """Анимирует появление соединения (fade-in)."""
        if not parent or not child or not hasattr(parent, 'scenePos') or not hasattr(child, 'scenePos'):
            return
            
        # Находим соединение между родителем и ребенком
        connection = None
        for conn in self.connections:
            if (conn and conn.start_node == parent and conn.end_node == child and
                hasattr(conn, 'setVisible')):
                connection = conn
                break
        
        if connection:
            try:
                connection.setVisible(True)
                # плавный fade-in
                anim = QPropertyAnimation(connection, b"opacity", connection)
                anim.setDuration(520)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                # сохраняем в объекте connection, чтобы анимация не уничтожилась
                if not hasattr(connection, "_fade_anims"):
                    connection._fade_anims = []
                connection._fade_anims.append(anim)
                anim.start()
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    print("Предупреждение: соединение удалено")
                    return
                raise e
            except Exception as e:
                print(f"Ошибка при показе соединения: {e}")
    
    def highlight_traversal(self, node_values, delay=900):
        """Подсвечивает последовательность узлов по их значениям."""
        for i, value in enumerate(node_values):
            QTimer.singleShot(i * delay, lambda v=value: self._safe_highlight_node_by_value(v))
    
    def _safe_highlight_node_by_value(self, value):
        """Безопасная подсветка узла по значению."""
        try:
            self._highlight_node_by_value(value)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                print("Предупреждение: узел удален до подсветки")
                return
            raise e
    
    def _highlight_node_by_value(self, value):
        """Подсвечивает узел по значению."""
        try:
            # Пробуем найти узел по значению (для обычных деревьев)
            node = self.value_to_node.get(value)
            
            # Если не нашли, пробуем найти как строку (для B-дерева)
            if not node:
                # Для B-дерева значение может быть списком, пробуем найти как строку ключей
                for key, node_item in self.value_to_node.items():
                    if isinstance(key, str) and str(value) in key:
                        node = node_item
                        break
            
            if node and hasattr(node, 'scene') and node.scene() and hasattr(node, '_is_valid') and node._is_valid:
                if isinstance(node, BTreeNodeItem):
                    # Для B-дерева подсвечиваем весь узел
                    original_bg_color = node.bg_color
                    node.bg_color = QColor("#FFD700")
                    node.update()
                    
                    # Возвращаем исходный цвет через некоторое время
                    QTimer.singleShot(600, lambda: self._safe_reset_btree_node_color(node, original_bg_color))
                else:
                    # Для обычных узлов
                    original_color = node.circleColor if hasattr(node, 'circleColor') else node.default_color
                    node.highlight(QColor("#FFD700"))
                    
                    # Возвращаем исходный цвет через некоторое время
                    QTimer.singleShot(600, lambda: self._safe_reset_node_color(node, original_color))
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
        except Exception as e:
            print(f"Ошибка при подсветке узла: {e}")
    
    def _safe_reset_node_color(self, node, color):
        """Безопасный сброс цвета узла."""
        try:
            self._reset_node_color(node, color)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
    
    def _reset_node_color(self, node, color):
        """Сбрасывает цвет узла."""
        try:
            if node and hasattr(node, 'scene') and node.scene() and hasattr(node, '_is_valid') and node._is_valid:
                if hasattr(node, 'highlight'):
                    node.highlight(color)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
        except Exception as e:
            print(f"Ошибка при сбросе цвета узла: {e}")
    
    def _safe_reset_btree_node_color(self, node, color):
        """Безопасный сброс цвета узла B-дерева."""
        try:
            self._safe_reset_btree_node_color(node, color)
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
    
    def _reset_btree_node_color(self, node, color):
        """Сбрасывает цвет узла B-дерева."""
        try:
            if node and hasattr(node, 'scene') and node.scene() and hasattr(node, '_is_valid') and node._is_valid:
                if hasattr(node, 'bg_color'):
                    node.bg_color = color
                    node.update()
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                return
            raise e
        except Exception as e:
            print(f"Ошибка при сбросе цвета B-дерева узла: {e}")
    
    def _auto_fit_view(self):
        """Автоматическое подгонка вида (вызывается только при инициализации)."""
        view = self.scene.views()[0] if self.scene.views() else None
        if not view:
            return
        
        rect = self.scene.itemsBoundingRect()
        if rect.isValid():
            rect.adjust(-200, -200, 200, 200)  # небольшой паддинг
            view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)