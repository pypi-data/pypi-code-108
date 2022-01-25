从 enum 导入 *
从 types 导入 DynamicClassAttribute


类 自动(auto):
    """
    实例用枚举类成员的适当值替换.
    """

类 〇枚举(Enum):
    """从该类派生来定义新的枚举对象."""

    @DynamicClassAttribute
    套路 名称(分身):
        """枚举类成员的名称."""
        返回 分身._name_

    @DynamicClassAttribute
    套路 值(分身):
        """枚举类成员的值."""
        返回 分身._value_

类 〇整数枚举(IntEnum):
    """成员也是 (而且必须是) 整数的枚举对象."""

类 〇标志(Flag):
    """支持标志."""

类 〇整数标志(IntFlag):
    """支持基于整数的标志."""

套路 唯一(枚举对象):
    """枚举对象的类装饰器, 确保成员值唯一."""
    duplicates = []
    for name, member in 枚举对象.__members__.items():
        if name != member.name:
            duplicates.append((name, member.name))
    if duplicates:
        alias_details = ', '.join(
                ["%s -> %s" % (alias, name) for (alias, name) in duplicates])
        raise 值错误类('%r 中发现重复值: %s' %
                (枚举对象, alias_details))
    return 枚举对象

