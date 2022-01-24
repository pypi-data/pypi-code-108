import os
from typing import List, Optional

from DKCloudCommand.modules.DKFileHelper import DKFileHelper

KITCHEN_META = "KITCHEN_META"
DK_DIR = ".dk"
DK_RECIPES_META_DIR = "recipes"


class DKKitchenDisk:
    def __init__(self) -> None:
        pass

    @staticmethod
    def check_kitchen_folder(kitchen_name: str, root_dir: str) -> bool:
        kitchen_dir = os.path.join(root_dir, kitchen_name)
        # Is the directory empty?
        for root, subdirs, files in os.walk(kitchen_dir):
            if len(subdirs) != 0 or len(files) != 0:
                return False
        return True

    @staticmethod
    def create_kitchen_meta_dir(kitchen_dir: str) -> str:
        kitchen_meta_dir = os.path.join(kitchen_dir, DK_DIR)
        if not os.path.exists(kitchen_meta_dir):
            os.makedirs(kitchen_meta_dir)
        DKKitchenDisk.create_recipes_meta_dir(kitchen_meta_dir)
        return kitchen_meta_dir

    @staticmethod
    def create_recipes_meta_dir(kitchen_meta_dir: Optional[str]) -> str:
        recipes_meta_dir = os.path.join(kitchen_meta_dir, DK_RECIPES_META_DIR)
        if not os.path.isdir(recipes_meta_dir):
            try:
                os.makedirs(recipes_meta_dir)
            except OSError as e:
                print(f"{e.filename} - {e.errno} - {e}")
                return None
        return recipes_meta_dir

    @staticmethod
    def get_recipe_meta_dir(recipe_name: str, start_dir: Optional[str] = None) -> Optional[str]:
        recipes_meta = DKKitchenDisk.get_recipes_meta_dir(start_dir)
        if recipes_meta is None:
            return None
        recipe_meta = os.path.join(recipes_meta, recipe_name)
        return recipe_meta

    @staticmethod
    def get_recipes_meta_dir(start_dir: Optional[str] = None) -> Optional[str]:
        kitchen_meta_dir = DKKitchenDisk.find_kitchen_meta_dir(start_dir)
        if kitchen_meta_dir is None:
            return None
        return os.path.join(kitchen_meta_dir, DK_RECIPES_META_DIR)

    @staticmethod
    def write_kitchen(kitchen_name: str, root_dir: str) -> bool:
        kitchen_dir = os.path.join(root_dir, kitchen_name)
        if not os.path.exists(kitchen_dir):
            os.makedirs(kitchen_dir)
        plug_dir = DKKitchenDisk.create_kitchen_meta_dir(kitchen_dir)
        DKFileHelper.write_file(os.path.join(plug_dir, KITCHEN_META), kitchen_name)
        return True

    @staticmethod
    def find_kitchen_meta_dir(walk_dir: Optional[str] = None) -> Optional[str]:
        return DKKitchenDisk._find_kitchen(walk_dir, return_meta_path=True)

    @staticmethod
    def find_kitchens_root(reference_kitchen_names: List[str]) -> Optional[str]:
        # check if we are in a kitchen path
        cwd = os.getcwd()
        kitchen_root = DKKitchenDisk.find_kitchen_root_dir(cwd)

        # if not, check if we are one level above kitchens
        for reference_kitchen in reference_kitchen_names:
            if kitchen_root:
                break
            possible_kitchen_path = os.path.join(cwd, reference_kitchen)
            kitchen_root = DKKitchenDisk.find_kitchen_root_dir(possible_kitchen_path)

        # return one level above kitchen root
        if kitchen_root:
            one_folder_up = os.path.dirname(kitchen_root)
            return one_folder_up

    @staticmethod
    def find_kitchen_root_dir(walk_dir: Optional[str] = None) -> Optional[str]:
        rv = DKKitchenDisk._find_kitchen(walk_dir, return_meta_path=True)
        if rv is None:
            return None
        else:
            parts = os.path.split(rv)
            return parts[0]

    @staticmethod
    def find_kitchen_name(walk_dir: Optional[str] = None) -> Optional[str]:
        return DKKitchenDisk._find_kitchen(walk_dir, return_meta_path=False)

    @staticmethod
    def is_kitchen_root_dir(walk_dir: Optional[str] = None) -> bool:
        rv = DKKitchenDisk._find_kitchen(walk_dir, recurse=False)
        if rv is None:
            return False
        else:
            return True

    @staticmethod
    # UNUSED METHOD?
    def find_available_recipes(walk_dir: Optional[str] = None) -> Optional[str]:
        meta_dir = DKKitchenDisk.find_kitchen_meta_dir(walk_dir)
        if meta_dir is None:
            return None

        recipes_dir = DKKitchenDisk.get_recipes_meta_dir(meta_dir)
        recipe_names = next(os.walk(recipes_dir))[1]
        return recipe_names

    @staticmethod
    def _find_kitchen(
        walk_dir: Optional[str] = None, return_meta_path: bool = False, recurse: bool = True
    ) -> Optional[str]:

        if walk_dir is None:
            walk_dir = os.getcwd()

        if not os.path.isdir(walk_dir):
            return None

        subdirs = next(os.walk(walk_dir))[1]
        if DK_DIR in subdirs:
            try:
                kitchen_name = DKFileHelper.read_file(os.path.join(walk_dir, DK_DIR, KITCHEN_META))

                if kitchen_name is not None and len(kitchen_name) > 0:
                    if return_meta_path:
                        return os.path.join(walk_dir, DK_DIR)
                    else:
                        return kitchen_name
                else:
                    # Maybe throw an error here. The .dk folder is in a bad state
                    return None
            except IOError:
                return None
        else:
            if recurse:
                parts = os.path.split(walk_dir)
                if len(parts) != 2:
                    return None
                else:
                    if parts[0] != walk_dir:
                        return DKKitchenDisk._find_kitchen(parts[0], return_meta_path=return_meta_path)
                    else:
                        # We are at the top of the directory structure.
                        # There was nothing to tokenize out
                        return None
            else:
                return None
