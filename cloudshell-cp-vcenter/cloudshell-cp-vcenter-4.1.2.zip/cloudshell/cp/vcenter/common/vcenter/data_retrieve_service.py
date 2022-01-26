from typing import List, Type, Union

from pyVmomi import vim, vmodl


class VcenterDataRetrieveService:
    def get_vm_object(self, si, root, vm_path):
        vcenter_object = root
        for path in vm_path.split("/"):
            vcenter_object = si.content.searchIndex.FindChild(vcenter_object, path)
        return vcenter_object

    def get_all_objects_with_properties(
        self,
        vim_type: Type[
            Union[
                vim.Folder,
                vim.VirtualMachine,
                vim.HostSystem,
                vim.ClusterComputeResource,
                vim.Datastore,
                vim.StoragePod,
            ]
        ],
        properties: List[str],
        si: vim.ServiceInstance,
        root: vim.ManagedEntity = None,
    ):
        """Get all objects of the given vim_type with the pre-loaded properties."""
        view_ref = si.content.viewManager.CreateContainerView(
            container=root or si.content.rootFolder, type=[vim_type], recursive=True
        )
        # noinspection PyUnresolvedReferences
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec()
        traversal_spec.name = "traverseEntries"
        traversal_spec.path = "view"
        traversal_spec.skip = False
        traversal_spec.type = type(view_ref)

        # noinspection PyUnresolvedReferences
        obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
        obj_spec.obj = view_ref
        obj_spec.skip = True
        obj_spec.selectSet = [traversal_spec]

        # noinspection PyUnresolvedReferences
        prop_spec = vmodl.query.PropertyCollector.PropertySpec()
        prop_spec.type = vim_type
        prop_spec.pathSet = properties

        # noinspection PyUnresolvedReferences
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = [obj_spec]
        filter_spec.propSet = [prop_spec]

        collector = si.content.propertyCollector

        return collector.RetrieveProperties([filter_spec])

    # noinspection PyUnresolvedReferences
    def get_object_property(
        self, name: str, obj_with_props: vmodl.query.PropertyCollector.ObjectContent
    ):
        """Get pre-loaded property from object by its name."""
        for prop in obj_with_props.propSet:
            if prop.name == name:
                return prop.val

        raise Exception(
            f"Unable to find pre-loaded property '{name}' "
            f"on the object {obj_with_props.obj.name}"
        )
