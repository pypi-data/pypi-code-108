class QuaNodeVisitor:
    def _default_enter(self, node):
        return True

    def _default_leave(self, node):
        pass

    def _default_visit(self, node):
        fields = node.ListFields()
        for (_descriptor, field) in fields:
            self.__visit(field)

    def __call(self, name, node, t):
        attr_name = f"{t}_{name}".replace(".", "_")
        attr = getattr(self, attr_name, None)
        if attr:
            ret = attr(node)
            if t == "enter":
                return ret
        elif t == "enter":
            return self._default_enter(node)
        elif t == "leave":
            self._default_leave(node)
        elif t == "visit":
            self._default_visit(node)
        else:
            raise Exception(
                f"unknown call type {t}. only 'enter', 'leave' or 'visit' are supported"
            )

    def __call_enter(self, name, node):
        return self.__call(name, node, "enter")

    def __call_visit(self, name, node):
        return self.__call(name, node, "visit")

    def __call_leave(self, name, node):
        return self.__call(name, node, "leave")

    def visit(self, node):
        type_name = type(node).__name__
        type_module = type(node).__module__
        type_fullname = f"{type_module}.{type_name}"
        if type_fullname == "qm.program._Program._Program":
            return self.visit(node._program)

        if hasattr(node, "DESCRIPTOR"):
            self.__visit(node)
        else:
            raise Exception("Failed to find descriptor on " + node)

    def __visit(self, node):
        if not hasattr(node, "DESCRIPTOR"):
            if type(node).__name__ in set(
                ["RepeatedCompositeFieldContainer", "RepeatedCompositeContainer"]
            ):
                for n in node[:]:
                    self.__visit(n)
            return
        descriptor = node.DESCRIPTOR
        if self.__call_enter(descriptor.full_name, node) is True:
            self.__call_visit(descriptor.full_name, node)
        self.__call_leave(descriptor.full_name, node)
