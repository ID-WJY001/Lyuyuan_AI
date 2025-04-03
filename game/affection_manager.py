from typing import Dict, Any, Optional, List, Tuple
import logging

class AffectionManager:
    """
    亲密度统一管理系统
    
    负责统一管理和同步游戏中所有与亲密度/好感度相关的组件的数值，
    确保在任何时刻所有系统中的亲密度值保持一致。
    """
    
    def __init__(self, initial_value: float = 30.0):
        """
        初始化亲密度管理系统
        
        Args:
            initial_value: 初始亲密度值，默认为30
        """
        self.logger = logging.getLogger("AffectionManager")
        
        # 存储所有需要同步亲密度的系统引用
        self._systems = {}
        
        # 当前亲密度值
        self._current_value = float(initial_value)
        
        # 上一次亲密度值
        self._previous_value = float(initial_value)
        
        # 调试模式
        self.debug_mode = False
    
    def register_system(self, system_name: str, 
                        getter_method: Optional[callable] = None,
                        setter_method: Optional[callable] = None,
                        system_obj: Any = None) -> None:
        """
        注册一个需要同步亲密度的系统
        
        Args:
            system_name: 系统名称
            getter_method: 获取该系统亲密度值的方法(可选)
            setter_method: 设置该系统亲密度值的方法(可选)
            system_obj: 系统对象(可选)
        """
        self._systems[system_name] = {
            "getter": getter_method,
            "setter": setter_method,
            "object": system_obj
        }
        
        # 如果提供了getter方法，获取当前值并进行一次初始同步
        if getter_method and system_obj:
            try:
                current_value = getter_method(system_obj)
                if current_value is not None:
                    # 记录但不同步，避免循环
                    if self.debug_mode:
                        self.logger.debug(f"系统[{system_name}]当前亲密度为{current_value}")
            except Exception as e:
                self.logger.error(f"获取系统[{system_name}]亲密度时出错: {str(e)}")
    
    def update_value(self, new_value: float, source: str = "unknown") -> Dict[str, Any]:
        """
        更新亲密度值并同步到所有系统
        
        Args:
            new_value: 新的亲密度值
            source: 更新来源，用于调试
            
        Returns:
            包含更新结果的字典
        """
        # 保存上一次的值
        self._previous_value = self._current_value
        
        # 确保亲密度在有效范围内
        new_value = max(0.0, min(100.0, float(new_value)))
        
        # 设置新值
        self._current_value = new_value
        
        # 同步到所有系统
        self._sync_all_systems()
        
        # 返回更新结果
        return {
            "current": self._current_value,
            "previous": self._previous_value,
            "delta": self._current_value - self._previous_value,
            "source": source
        }
    
    def get_value(self) -> float:
        """获取当前亲密度值"""
        return self._current_value
    
    def get_previous_value(self) -> float:
        """获取上一次的亲密度值"""
        return self._previous_value
    
    def get_delta(self) -> float:
        """获取亲密度变化值"""
        return self._current_value - self._previous_value
    
    def _sync_all_systems(self) -> List[Tuple[str, bool]]:
        """
        同步亲密度值到所有注册的系统
        
        Returns:
            同步结果列表，每项包含系统名称和同步是否成功
        """
        results = []
        
        for system_name, system_info in self._systems.items():
            setter = system_info.get("setter")
            system_obj = system_info.get("object")
            
            if setter and system_obj:
                try:
                    setter(system_obj, self._current_value)
                    results.append((system_name, True))
                    
                    if self.debug_mode:
                        self.logger.debug(f"已同步亲密度{self._current_value}到系统[{system_name}]")
                except Exception as e:
                    results.append((system_name, False))
                    self.logger.error(f"同步亲密度到系统[{system_name}]时出错: {str(e)}")
        
        return results
    
    def verify_consistency(self) -> Dict[str, Any]:
        """
        验证所有系统中的亲密度值是否一致
        
        Returns:
            验证结果，包含每个系统的亲密度值和一致性状态
        """
        values = {}
        consistent = True
        
        for system_name, system_info in self._systems.items():
            getter = system_info.get("getter")
            system_obj = system_info.get("object")
            
            if getter and system_obj:
                try:
                    system_value = getter(system_obj)
                    values[system_name] = system_value
                    
                    # 检查一致性，允许1的误差(整数/浮点数转换)
                    if abs(float(system_value) - self._current_value) > 1:
                        consistent = False
                except Exception as e:
                    values[system_name] = None
                    consistent = False
                    self.logger.error(f"获取系统[{system_name}]亲密度时出错: {str(e)}")
        
        return {
            "consistent": consistent,
            "master_value": self._current_value,
            "system_values": values
        }
    
    def force_sync(self) -> Dict[str, Any]:
        """
        强制同步所有系统的亲密度值
        
        Returns:
            同步结果
        """
        return {
            "sync_results": self._sync_all_systems(),
            "current_value": self._current_value
        } 