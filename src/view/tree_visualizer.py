"""Визуализатор деревьев с поддержкой интерактивных операций."""
import faulthandler
faulthandler.enable()

from PyQt6.QtCore import QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve, QRectF, Qt, QPointF
from PyQt6.QtGui import QColor, QLinearGradient, QFont, QPen, QBrush
from view.scene_items import TreeNodeItem, TreeConnectionItem, BTreeNodeItem
from view.tree_layout import CenteredTreeLayout, CompactTreeLayout


class TreeVisualizer:
    """Класс для визуализации деревьев с поддержкой интерактивных операций."""
    
    def __init__(self, scene):
        self.scene = scene
        self.nodes = []
        self.connections = []
        self.layout_algorithm = CenteredTreeLayout(x_spacing=850, y_spacing=850)
        self.value_to_node = {}  # Словарь для быстрого доступа к узлам по значению
        self.current_tree_type = "BST"
        self._node_counter = 0  # Счетчик для уникальных ID узлов
        
        # Менеджер анимаций и таймеров
        self._active_timers = []
        self._active_animations = []
        self._animation_in_progress = False
        self._animation_lock = False
    
    def clear(self):
        """Очищает сцену от всех элементов дерева."""
        # Останавливаем все анимации и таймеры
        self._stop_all_animations_and_timers()
        
        # Безопасно удаляем элементы
        items_to_remove = []
        
        for item in self.nodes + self.connections:
            try:
                if item is None:
                    continue
                    
                if hasattr(item, 'scene'):
                    scene = item.scene()
                    if scene is not None and scene == self.scene:
                        items_to_remove.append(item)
            except RuntimeError:
                continue
            except AttributeError:
                continue
        
        # Удаляем элементы
        for item in items_to_remove:
            try:
                if hasattr(item, 'prepareForRemoval'):
                    try:
                        item.prepareForRemoval()
                    except RuntimeError:
                        pass
                
                self.scene.removeItem(item)
            except RuntimeError as e:
                if "wrapped C/C++ object" not in str(e):
                    pass
            except Exception as e:
                pass
        
        # Очищаем списки
        self.nodes.clear()
        self.connections.clear()
        self.value_to_node.clear()
        self._node_counter = 0
        self._animation_in_progress = False
        self._animation_lock = False
    
    def _stop_all_animations_and_timers(self):
        """Останавливает все активные анимации и таймеры."""
        # Останавливаем таймеры
        for timer in self._active_timers[:]:
            try:
                if timer and timer.isActive():
                    timer.stop()
                    timer.deleteLater()
            except RuntimeError:
                pass
            except Exception:
                pass
        
        self._active_timers.clear()
        
        # Останавливаем анимации
        for anim in self._active_animations[:]:
            try:
                if anim and hasattr(anim, 'stop'):
                    anim.stop()
                    anim.deleteLater()
            except RuntimeError:
                pass
            except Exception:
                pass
        
        self._active_animations.clear()
        
        # Останавливаем анимации узлов
        for node in self.nodes:
            try:
                if node is None:
                    continue
                    
                if hasattr(node, '_entry_anims'):
                    for anim in node._entry_anims[:]:
                        try:
                            if anim and hasattr(anim, 'stop'):
                                anim.stop()
                        except RuntimeError:
                            pass
                        except Exception:
                            pass
                    node._entry_anims = []
                
                if hasattr(node, '_fade_anim'):
                    try:
                        node._fade_anim.stop()
                    except:
                        pass
                    
                if hasattr(node, '_scale_anim'):
                    try:
                        node._scale_anim.stop()
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
                    for anim in connection._fade_anims[:]:
                        try:
                            if anim and hasattr(anim, 'stop'):
                                anim.stop()
                        except RuntimeError:
                            pass
                        except Exception:
                            pass
                    connection._fade_anims = []
                    
                if hasattr(connection, '_animations'):
                    for anim in connection._animations[:]:
                        try:
                            if anim and hasattr(anim, 'stop'):
                                anim.stop()
                        except RuntimeError:
                            pass
                        except Exception:
                            pass
                    connection._animations = []
                    
            except RuntimeError:
                pass
            except Exception:
                pass
    
    def set_tree_type(self, tree_type):
        """Устанавливает тип дерева для цветового кодирования."""
        self.current_tree_type = tree_type
    
    def create_tree_from_structure(self, tree_structure, animate=True):
        """Создает дерево из структуры данных."""
        # Проверяем блокировку анимации
        if self._animation_lock:
            return None
        
        # Останавливаем все предыдущие анимации
        self._stop_all_animations_and_timers()
        
        # Очищаем старое дерево
        self.clear()
        
        if not tree_structure:
            return None
        
        try:
            # Устанавливаем блокировку
            if animate:
                self._animation_lock = True
                self._animation_in_progress = True
            
            # Проверяем тип дерева
            if isinstance(tree_structure, list) and tree_structure and 'keys' in tree_structure[0]:
                # Это B-дерево
                root = self._create_btree_from_list(tree_structure, animate)
            else:
                # Обычное дерево
                root = self._create_regular_tree(tree_structure, animate)
            
            # Если анимация, запускаем завершение
            if animate and root:
                # Создаем таймер для снятия блокировки
                timer = QTimer()
                timer.setSingleShot(True)
                
                def unlock_animation():
                    try:
                        self._animation_lock = False
                        self._animation_in_progress = False
                    except:
                        pass
                    finally:
                        self._remove_timer(timer)
                
                timer.timeout.connect(unlock_animation)
                self._add_timer(timer)
                
                # Вычисляем время анимации
                animation_time = len(self.nodes) * 150 + len(self.connections) * 50 + 1000
                timer.start(animation_time)
            
            return root
                
        except Exception as e:
            # В случае ошибки снимаем блокировку
            self._animation_lock = False
            self._animation_in_progress = False
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
            self._register_node(root, tree_structure['keys'])
        elif 'value' in tree_structure:
            self._register_node(root, tree_structure['value'])
        
        # Рекурсивно создаем остальные узлы
        self._build_tree_recursive(root, tree_structure)
        
        # Вычисляем расположение
        self.layout_algorithm.calculate_layout(root)
        
        # Добавляем соединения
        self._create_connections(root)
        
        # Для интерактивных операций НЕ используем анимацию
        if animate:
            # Только для начального построения используем анимацию
            self._add_all_to_scene()
            self._animate_tree_construction_safe(root)
        else:
            # Для интерактивных операций - без анимации
            self._add_all_to_scene()
            # Сразу показываем все элементы
            for node in self.nodes:
                if hasattr(node, 'setOpacity'): 
                    node.setOpacity(1.0)
            for conn in self.connections:
                if hasattr(conn, 'setOpacity'): 
                    conn.setOpacity(1.0)
        
        return root
    
    def _register_node(self, node, value):
        """Регистрирует узел в словаре для быстрого доступа."""
        node_id = self._node_counter
        self._node_counter += 1
        
        # Сохраняем ID в узле
        node._tree_node_id = node_id
        
        # Регистрируем по значению
        if isinstance(value, list):
            # Для B-дерева: регистрируем по строковому представлению ключей
            key_str = str(value)
            self.value_to_node[key_str] = node
            
            # Также регистрируем каждый ключ отдельно
            for key in value:
                self.value_to_node[f"key_{key}"] = node
        else:
            # Для обычных деревьев: регистрируем по значению
            self.value_to_node[value] = node
        
        return node_id
    
    def _create_btree_from_list(self, btree_nodes, animate=True):
        """Создает B-дерево из списка узлов."""
        try:
            if not btree_nodes:
                return None
            
            # 1. Создаем все узлы
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
                    
                    # Регистрируем узел
                    self.nodes.append(node)
                    node_map[node_id] = node
                    self._register_node(node, keys)
                    
                except Exception:
                    continue
            
            if not self.nodes:
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
                            except Exception:
                                pass
                                
                except Exception:
                    pass
            
            # 3. Находим корень
            root = self._find_btree_root(node_map, btree_nodes)
            
            if root:
                # 4. Вычисляем позиции
                self._calculate_b_tree_positions(root)
                
                # 5. Добавляем все на сцену
                self._add_all_to_scene()
                
                # 6. Анимация - только если включена
                if animate:
                    self._animate_btree_appearance_safe()
                else:
                    # Без анимации
                    for node in self.nodes:
                        if hasattr(node, 'setOpacity'): 
                            node.setOpacity(1.0)
                    for conn in self.connections:
                        if hasattr(conn, 'setOpacity'): 
                            conn.setOpacity(1.0)
                
                return root
            else:
                return None
                
        except Exception:
            return None
    
    def _find_btree_root(self, node_map, btree_nodes):
        """Находит корневой узел B-дерева."""
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
                return node
        
        # Если корень не найден, берем первый узел
        if self.nodes:
            return self.nodes[0]
        
        return None
    
    def _calculate_b_tree_positions(self, root):
        """Вычисляет позиции для B-дерева."""
        if not root:
            return
        
        # Очищаем старые позиции
        for node in self.nodes:
            node.setPos(0, 0)
        
        # Обход в ширину для расчета уровней
        from collections import deque
        
        X_SPACING = 220
        Y_SPACING = 180
        
        queue = deque([(root, 0, 0)])  # (node, x, y)
        visited = set()
        level_nodes = {}
        
        while queue:
            node, x, y = queue.popleft()
            
            if node in visited:
                continue
            
            visited.add(node)
            
            # Группируем по уровням
            if y not in level_nodes:
                level_nodes[y] = []
            level_nodes[y].append((x, node))
            
            # Добавляем детей
            if hasattr(node, 'children') and node.children:
                num_children = len(node.children)
                total_width = num_children * X_SPACING
                start_x = x - total_width / 2 + X_SPACING / 2
                
                for i, child in enumerate(node.children):
                    if child not in visited:
                        child_x = start_x + i * X_SPACING
                        queue.append((child, child_x, y + 1))
        
        # Устанавливаем позиции
        self._layout_btree_levels(level_nodes, Y_SPACING, X_SPACING)
    
    def _layout_btree_levels(self, level_nodes, y_spacing, x_spacing):
        """Раскладывает уровни, центрируя их."""
        max_y = max(level_nodes.keys()) if level_nodes else 0
        
        for y in range(max_y + 1):
            if y not in level_nodes:
                continue
                
            nodes = level_nodes[y]
            nodes.sort(key=lambda item: item[0])  # Сортируем по x
            
            # Вычисляем общую ширину уровня
            level_width = len(nodes) * (x_spacing + 50)
            start_x = -level_width / 2
            
            current_x = start_x
            for _, node in nodes:
                node_width = getattr(node, 'node_width', 160)
                node.setPos(current_x + node_width/2, y * y_spacing)
                current_x += max(node_width + 20, x_spacing)
    
    def _animate_btree_appearance_safe(self):
        """Безопасная анимация появления B-дерева."""
        # Сначала скрываем все элементы
        for node in self.nodes:
            if hasattr(node, 'setOpacity'):
                node.setOpacity(0.0)
                node.setScale(0.8)
        
        for connection in self.connections:
            if hasattr(connection, 'setOpacity'):
                connection.setOpacity(0.0)
        
        # Постепенно показываем элементы с проверкой
        for i, node in enumerate(self.nodes):
            if hasattr(node, 'setOpacity'):
                timer = QTimer()
                timer.setSingleShot(True)
                
                def create_show_node_func(n=node):
                    def show_node():
                        try:
                            self._fade_in_node_safe(n)
                        finally:
                            self._remove_timer(timer)
                    return show_node
                
                timer.timeout.connect(create_show_node_func())
                self._add_timer(timer)
                timer.start(i * 100)
        
        # Показываем соединения
        connection_delay = len(self.nodes) * 100 + 200
        for i, connection in enumerate(self.connections):
            if hasattr(connection, 'setOpacity'):
                timer = QTimer()
                timer.setSingleShot(True)
                
                def create_show_connection_func(c=connection):
                    def show_connection():
                        try:
                            self._fade_in_connection_safe(c)
                        finally:
                            self._remove_timer(timer)
                    return show_connection
                
                timer.timeout.connect(create_show_connection_func())
                self._add_timer(timer)
                timer.start(connection_delay + i * 50)
    
    def _fade_in_node_safe(self, node):
        """Безопасное плавное появление узла."""
        try:
            # Проверяем валидность узла
            if not node or not hasattr(node, '_is_valid') or not node._is_valid:
                return
            
            # Проверяем, что узел все еще в сцене
            if not node.scene():
                return
            
            if hasattr(node, 'setOpacity'):
                anim = QPropertyAnimation(node, b"opacity", node)
                anim.setDuration(500)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # Добавляем в список активных анимаций
                self._add_animation(anim)
                
                # Удаляем после завершения
                anim.finished.connect(lambda: self._remove_animation(anim))
                anim.start()
            
            if hasattr(node, 'setScale'):
                node.setScale(0.8)
                anim_scale = QPropertyAnimation(node, b"scale", node)
                anim_scale.setDuration(500)
                anim_scale.setStartValue(0.8)
                anim_scale.setEndValue(1.0)
                anim_scale.setEasingCurve(QEasingCurve.Type.OutBack)
                
                # Добавляем в список активных анимаций
                self._add_animation(anim_scale)
                
                # Удаляем после завершения
                anim_scale.finished.connect(lambda: self._remove_animation(anim_scale))
                anim_scale.start()
                
        except Exception:
            # В случае ошибки просто показываем узел
            try:
                if node and hasattr(node, 'setOpacity'):
                    node.setOpacity(1.0)
                if node and hasattr(node, 'setScale'):
                    node.setScale(1.0)
            except:
                pass
    
    def _fade_in_connection_safe(self, connection):
        """Безопасное плавное появление соединения."""
        if not connection or not hasattr(connection, '_is_valid') or not connection._is_valid:
            return
        
        try:
            # Проверяем, что соединение все еще в сцене
            if not connection.scene():
                return
            
            connection.setOpacity(0.0)
            
            anim = QPropertyAnimation(connection, b"opacity", connection)
            anim.setDuration(500)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Добавляем в список активных анимаций
            self._add_animation(anim)
            
            # Удаляем после завершения
            anim.finished.connect(lambda: self._remove_animation(anim))
            anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            
        except Exception as e:
            # В случае ошибки просто показываем соединение
            try:
                if connection and hasattr(connection, 'setOpacity'):
                    connection.setOpacity(1.0)
            except:
                pass
    
    def _add_timer(self, timer):
        """Добавляет таймер в список активных."""
        if timer:
            self._active_timers.append(timer)
    
    def _remove_timer(self, timer):
        """Удаляет таймер из списка."""
        try:
            if timer in self._active_timers:
                self._active_timers.remove(timer)
                if timer.isActive():
                    timer.stop()
                timer.deleteLater()
        except:
            pass
    
    def _add_animation(self, animation):
        """Добавляет анимацию в список активных."""
        if animation:
            self._active_animations.append(animation)
    
    def _remove_animation(self, animation):
        """Удаляет анимацию из списка."""
        try:
            if animation in self._active_animations:
                self._active_animations.remove(animation)
        except:
            pass
    
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
                
                node = BTreeNodeItem(x, y, keys, is_leaf, key_count)
                node.set_tree_type_color("BTree")
                
                return node
            
            # Для обычных деревьев
            value = node_data.get('value', '?')
            
            # Определяем цвет в зависимости от типа дерева
            tree_type = self.current_tree_type
            if "(" in str(value) and ")" in str(value):
                if "R)" in str(value) or "(R" in str(value):
                    tree_type = "RedBlackTree_RED"
                elif "B)" in str(value) or "(B" in str(value):
                    tree_type = "RedBlackTree_BLACK"
                elif "h:" in str(value):
                    tree_type = "AVL"
                elif "p:" in str(value):
                    tree_type = "Treap"
            
            node = TreeNodeItem(x, y, value, radius=95)
            node.set_tree_type_color(tree_type)
            
            return node
        except Exception:
            return None
    
    def _build_tree_recursive(self, parent_node, parent_data):
        """Рекурсивно строит дерево из данных."""
        if not parent_node:
            return
            
        children_data = parent_data.get('children', [])
        
        for child_data in children_data:
            child_node = self._create_node_from_data(child_data, 0, 0)
            if child_node:
                if hasattr(parent_node, 'add_child'):
                    parent_node.add_child(child_node)
                elif hasattr(parent_node, 'children'):
                    parent_node.children.append(child_node)
                    
                self.nodes.append(child_node)
                
                # Регистрируем узел
                if 'keys' in child_data:
                    self._register_node(child_node, child_data['keys'])
                elif 'value' in child_data:
                    self._register_node(child_node, child_data['value'])
                
                # Рекурсивно строим поддерево
                self._build_tree_recursive(child_node, child_data)
    
    def _create_connections(self, node):
        """Создает соединения для узла и его детей."""
        if not node or not hasattr(node, 'children'):
            return
            
        for child in node.children:
            if child:
                try:
                    connection = TreeConnectionItem(node, child)
                    if connection:
                        self.connections.append(connection)
                        connection._is_valid = True
                        
                        # Добавляем соединение к узлам
                        if hasattr(node, 'add_connection'):
                            node.add_connection(connection)
                        if hasattr(child, 'add_connection'):
                            child.add_connection(connection)
                except Exception:
                    pass
                
                # Рекурсивно создаем соединения для детей
                self._create_connections(child)
    
    def _add_all_to_scene(self):
        """Добавляет все узлы и соединения на сцену."""
        # Добавляем все узлы
        for node in self.nodes:
            try:
                if node is None:
                    continue
                    
                if hasattr(node, '_is_valid') and not node._is_valid:
                    continue
                    
                try:
                    current_scene = node.scene() if hasattr(node, 'scene') else None
                    if current_scene != self.scene:
                        self.scene.addItem(node)
                except RuntimeError:
                    continue
                    
            except Exception:
                pass
        
        # Добавляем соединения
        for connection in self.connections:
            try:
                if connection is None:
                    continue
                    
                if hasattr(connection, '_is_valid') and not connection._is_valid:
                    continue
                    
                try:
                    current_scene = connection.scene() if hasattr(connection, 'scene') else None
                    if current_scene != self.scene:
                        self.scene.addItem(connection)
                except RuntimeError:
                    continue
                    
            except Exception:
                pass
    
    def _animate_tree_construction_safe(self, root):
        """Безопасная анимация построения дерева."""
        if not root:
            return
        
        # Сначала скрываем все элементы
        for node in self.nodes:
            if hasattr(node, 'setVisible'):
                node.setVisible(False)
        
        for connection in self.connections:
            if hasattr(connection, 'setVisible'):
                connection.setVisible(False)
        
        # Анимируем появление узлов и соединений с проверками
        self._animate_nodes_appearance_safe(root, 360)
    
    def _animate_nodes_appearance_safe(self, node, delay, current_delay=0):
        """Безопасное рекурсивное анимирование появления узлов."""
        if not node or not hasattr(node, 'setVisible'):
            return
        
        # Создаем таймер для анимации узла
        node_timer = QTimer()
        node_timer.setSingleShot(True)
        
        def show_node_func(n=node):
            try:
                self._animate_node_appearance_safe(n)
            finally:
                self._remove_timer(node_timer)
        
        node_timer.timeout.connect(show_node_func)
        self._add_timer(node_timer)
        node_timer.start(current_delay)
        
        # Анимация соединений с детьми
        if hasattr(node, 'children'):
            for child in node.children:
                if child and hasattr(child, 'scenePos'):
                    connection_delay = current_delay + int(delay * 0.5)
                    
                    connection_timer = QTimer()
                    connection_timer.setSingleShot(True)
                    
                    def show_connection_func(parent=node, child_node=child):
                        try:
                            self._animate_connection_appearance_safe(parent, child_node)
                        finally:
                            self._remove_timer(connection_timer)
                    
                    connection_timer.timeout.connect(show_connection_func)
                    self._add_timer(connection_timer)
                    connection_timer.start(connection_delay)
                    
                    # Рекурсивно анимируем детей
                    self._animate_nodes_appearance_safe(child, delay, current_delay + delay)
    
    def _animate_node_appearance_safe(self, node):
        """Безопасное анимирование появления узла."""
        if not node:
            return
            
        try:
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
            
            # Добавляем анимации в список
            self._add_animation(scale_anim)
            self._add_animation(opacity_anim)
            
            # Удаляем после завершения
            scale_anim.finished.connect(lambda: self._remove_animation(scale_anim))
            opacity_anim.finished.connect(lambda: self._remove_animation(opacity_anim))
            
            # Сохраняем ссылки в узле для управления
            if not hasattr(node, "_entry_anims"):
                node._entry_anims = []
            node._entry_anims.extend([scale_anim, opacity_anim])
            
            scale_anim.start()
            opacity_anim.start()
                
        except RuntimeError:
            pass
        except Exception:
            pass
    
    def _animate_connection_appearance_safe(self, parent, child):
        """Безопасное анимирование появления соединения."""
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
                anim = QPropertyAnimation(connection, b"opacity", connection)
                anim.setDuration(520)
                anim.setStartValue(0.0)
                anim.setEndValue(1.0)
                anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                
                # Добавляем анимацию в список
                self._add_animation(anim)
                
                # Удаляем после завершения
                anim.finished.connect(lambda: self._remove_animation(anim))
                
                # Сохраняем ссылку
                if not hasattr(connection, "_fade_anims"):
                    connection._fade_anims = []
                connection._fade_anims.append(anim)
                
                anim.start()
            except RuntimeError:
                pass
            except Exception:
                pass
    
    # ИНТЕРАКТИВНЫЕ ОПЕРАЦИИ
    
    def highlight_node_by_value(self, value, color="#FFD700", duration=2000):
        """Подсвечивает узел по значению."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return False
            
        # 1. Поиск узла
        node = self.value_to_node.get(value)
        if not node:
            node = self.value_to_node.get(f"key_{value}")
            
        # 2. Если в словаре не нашли, используем поиск с перебором
        if not node:
            node = self._find_node_by_value(value)
            
        if node and self._is_node_valid(node):
            # 3. Сохраняем оригинальный цвет
            if not hasattr(node, '_original_color'):
                node._original_color = self._get_node_color(node)
            
            # 4. Применяем подсветку
            self._set_node_color(node, color)
            
            # 5. Возвращаем исходный цвет через указанное время
            if duration > 0:
                timer = QTimer()
                timer.setSingleShot(True)
                
                def reset_color_func():
                    try:
                        self._reset_node_color(node)
                    finally:
                        self._remove_timer(timer)
                
                timer.timeout.connect(reset_color_func)
                self._add_timer(timer)
                timer.start(duration)
                
            return True
            
        return False
    
    def highlight_btree_node_by_keys(self, keys, color="#FFD700", duration=2000):
        """Подсвечивает узел B-дерева по ключам."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return False
            
        node = self._find_btree_node_by_keys(keys)
        
        if node:
            # Сохраняем оригинальный цвет
            original_color = node.bg_color
            node._original_color = original_color
            
            # Подсвечиваем
            node.bg_color = QColor(color)
            node.update()
            
            # Возвращаем цвет через время
            if duration > 0:
                timer = QTimer()
                timer.setSingleShot(True)
                
                def reset_color_func():
                    try:
                        self._reset_btree_node_color(node)
                    finally:
                        self._remove_timer(timer)
                
                timer.timeout.connect(reset_color_func)
                self._add_timer(timer)
                timer.start(duration)
                
            return True
        
        return False
    
    def highlight_traversal(self, node_values, delay=900):
        """Подсвечивает последовательность узлов по их значениям."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return
            
        for i, value in enumerate(node_values):
            timer = QTimer()
            timer.setSingleShot(True)
            
            def create_highlight_func(v=value):
                def highlight():
                    try:
                        self.highlight_node_by_value(v, "#4ECDC4", 600)
                    finally:
                        self._remove_timer(timer)
                return highlight
            
            timer.timeout.connect(create_highlight_func())
            self._add_timer(timer)
            timer.start(i * delay)
    
    def highlight_path(self, values, color="#4ECDC4", delay=300):
        """Подсвечивает путь поиска через несколько узлов."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return
            
        for i, value in enumerate(values):
            timer = QTimer()
            timer.setSingleShot(True)
            
            def create_highlight_func(v=value):
                def highlight():
                    try:
                        self.highlight_node_by_value(v, color, delay * 2)
                    finally:
                        self._remove_timer(timer)
                return highlight
            
            timer.timeout.connect(create_highlight_func())
            self._add_timer(timer)
            timer.start(i * delay)
    
    def _find_node_by_value(self, value):
        """Находит узел по значению."""
        # Пробуем найти в словаре
        if value in self.value_to_node:
            node = self.value_to_node[value]
            if self._is_node_valid(node):
                return node
        
        # Ищем во всех узлах
        for node in self.nodes:
            if isinstance(node, TreeNodeItem):
                # Для красно-черного дерева проверяем значение с учетом цвета
                node_value_str = str(node.value)
                # Проверяем разные форматы: "10", "10(R)", "10(B)"
                if (node_value_str == str(value) or 
                    node_value_str.startswith(f"{value}(")):
                    if self._is_node_valid(node):
                        return node
        
        return None
    
    def _find_btree_node_by_keys(self, keys):
        """Находит узел B-дерева по ключам."""
        key_str = str(keys)
        if key_str in self.value_to_node:
            node = self.value_to_node[key_str]
            if self._is_node_valid(node):
                return node
        
        for node in self.nodes:
            if isinstance(node, BTreeNodeItem):
                if hasattr(node, 'keys') and node.keys == keys and self._is_node_valid(node):
                    return node
        
        return None
    
    def _is_node_valid(self, node):
        """Проверяет, валиден ли узел."""
        if not node:
            return False
        
        try:
            if hasattr(node, '_is_valid'):
                return node._is_valid
            
            # Проверяем, есть ли узел на сцене
            if hasattr(node, 'scene'):
                scene = node.scene()
                return scene is not None
            
            return True
        except RuntimeError:
            return False
    
    def _get_node_color(self, node):
        """Получает цвет узла."""
        if isinstance(node, BTreeNodeItem):
            return node.bg_color
        elif hasattr(node, 'circleColor'):
            return node.circleColor
        elif hasattr(node, 'default_color'):
            return node.default_color
        else:
            return QColor("#5A9BD5")  # Цвет по умолчанию
    
    def _set_node_color(self, node, color):
        """Устанавливает цвет узла."""
        color_obj = QColor(color) if isinstance(color, str) else color
        
        if isinstance(node, BTreeNodeItem):
            node.bg_color = color_obj
            node.update()
        elif hasattr(node, 'highlight'):
            node.highlight(color_obj)
        elif hasattr(node, 'circleColor'):
            node.circleColor = color_obj
            if hasattr(node, 'update'):
                node.update()
    
    def _reset_node_color(self, node):
        """Сбрасывает цвет узла к оригинальному."""
        if not node or not hasattr(node, '_original_color'):
            return
        
        try:
            if self._is_node_valid(node):
                original_color = node._original_color
                self._set_node_color(node, original_color)
                delattr(node, '_original_color')
        except RuntimeError:
            pass
        except Exception:
            pass
    
    def _reset_btree_node_color(self, node):
        """Сбрасывает цвет узла B-дерева."""
        if not node or not hasattr(node, '_original_color'):
            return
        
        try:
            if self._is_node_valid(node):
                node.bg_color = node._original_color
                node.update()
                delattr(node, '_original_color')
        except RuntimeError:
            pass
        except Exception:
            pass
    
    def remove_node_by_value(self, value):
        """Удаляет узел по значению."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return False
            
        node = self._find_node_by_value(value)
        
        if node:
            # Останавливаем анимации узла
            if hasattr(node, '_entry_anims'):
                for anim in node._entry_anims[:]:
                    try:
                        anim.stop()
                    except:
                        pass
                node._entry_anims = []
            
            # Удаляем из словаря
            keys_to_remove = []
            for key, val_node in self.value_to_node.items():
                if val_node == node:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.value_to_node[key]
            
            # Удаляем из списка узлов
            if node in self.nodes:
                self.nodes.remove(node)
            
            # Удаляем соединения с этим узлом
            connections_to_remove = []
            for conn in self.connections:
                if conn.start_node == node or conn.end_node == node:
                    connections_to_remove.append(conn)
            
            for conn in connections_to_remove:
                self.connections.remove(conn)
                try:
                    self.scene.removeItem(conn)
                except:
                    pass
            
            # Удаляем узел из сцены
            try:
                self.scene.removeItem(node)
            except:
                pass
            
            # Перестраиваем дерево
            if self.nodes:
                # Находим новый корень (первый узел, который не является чьим-то ребенком)
                all_children = set()
                for n in self.nodes:
                    if hasattr(n, 'children'):
                        for child in n.children:
                            if child in self.nodes:
                                all_children.add(child)
                
                for n in self.nodes:
                    if n not in all_children:
                        self.layout_algorithm.calculate_layout(n)
                        break
            
            return True
        
        return False
    
    def update_node_value(self, old_value, new_value):
        """Обновляет значение узла."""
        # Проверяем, идет ли анимация
        if self._animation_in_progress:
            return False
            
        node = self._find_node_by_value(old_value)
        
        if node:
            # Обновляем значение в узле
            if isinstance(node, TreeNodeItem):
                node.value = new_value
                node.update()
                
                # Обновляем текст
                if hasattr(node, 'text_item'):
                    node.text_item.setPlainText(str(new_value))
            
            # Обновляем словарь
            if old_value in self.value_to_node:
                del self.value_to_node[old_value]
            self.value_to_node[new_value] = node
            
            return True
        
        return False
    
    def update_btree_visualization(self, btree_data, animate=False):
        """Быстрое обновление визуализации B-дерева."""
        # Проверяем блокировку анимации
        if self._animation_lock:
            return None
            
        # Останавливаем все предыдущие анимации
        self._stop_all_animations_and_timers()
        
        # Очищаем старое дерево
        self.clear()
        
        if not btree_data:
            return None
        
        try:
            # Устанавливаем блокировку
            if animate:
                self._animation_lock = True
                self._animation_in_progress = True
            
            # Создаем новое дерево
            root = self._create_btree_from_list(btree_data, animate)
            
            # Если анимация отключена, сразу показываем
            if not animate and root:
                for node in self.nodes:
                    if hasattr(node, 'setOpacity'):
                        node.setOpacity(1.0)
                for conn in self.connections:
                    if hasattr(conn, 'setOpacity'):
                        conn.setOpacity(1.0)
                
                # Добавляем на сцену
                self._add_all_to_scene()
            
            # Снимаем блокировку
            if animate:
                self._animation_lock = False
                self._animation_in_progress = False
            
            return root
        except Exception:
            # В случае ошибки снимаем блокировку
            self._animation_lock = False
            self._animation_in_progress = False
            return None
    
    def reset_styles(self):
        """Сбрасывает стили всех узлов дерева к стандартным."""
        if not hasattr(self, 'value_to_node'):
            return
        
        for node_item in self.value_to_node.values():
            try:
                # Сбрасываем цвет узла
                if hasattr(node_item, 'reset_color'):
                    node_item.reset_color()
                elif hasattr(node_item, 'circleColor'):
                    # Для TreeNodeItem
                    node_item.circleColor = QColor("#5A9BD5")
                    node_item.update()
                elif hasattr(node_item, 'bg_color'):
                    # Для BTreeNodeItem
                    node_item.bg_color = QColor("#20B2AA")
                    node_item.update()
            except Exception as e:
                pass