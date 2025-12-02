import logging

"""Tree structure builder for hierarchical data.

This module provides functionality to build and manage tree structures from
pandas DataFrames containing parent-child relationships. It creates a nested
tree representation with additional metadata such as tree IDs, levels, and
right tree IDs for efficient tree traversal.

Classes:
    TreeEntry: A dataclass representing a single node in the tree structure.
    Tree: Main class for building and managing tree structures from DataFrames.

Example:
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'id': [1, 2, 3, 4],
    ...     'parent_id': [None, 1, 1, 2]
    ... })
    >>> tree = Tree(df, id_name='id', parent_id_name='parent_id')
    >>> tree_df, root_id = tree.get_tree()"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TreeEntry:
    tree_id: int
    tree_parent_id: Optional[int]
    db_id: int  # original ID from the database
    level: int
    right_tree_id: Optional[int] = None
    is_leaf: Optional[bool] = False


class Tree:
    def __init__(self, df: pd.DataFrame, id_name: str, parent_id_name: str) -> None:
        # check columns exist
        self.df = df
        for col_name in [id_name, parent_id_name]:
            if col_name not in df.columns:
                raise ValueError(f"Column '{col_name}' not found in DataFrame.")
        self.id_name = id_name
        self.parent_id_name = parent_id_name

    def __get_parent_childs_dict(self) -> dict[int, list[int]]:
        """Get parent-child relationships as a dictionary."""
        df_tree = (
            self.df[
                [
                    self.id_name,
                    self.parent_id_name,
                ]
            ]
            .dropna()
            .drop_duplicates()
        )
        if df_tree.empty:
            raise ValueError("DataFrame is empty after dropping NaN and duplicates.")
        # if parent id id not int convert to int
        if not pd.api.types.is_integer_dtype(df_tree[self.parent_id_name]):
            df_tree[self.parent_id_name] = df_tree[self.parent_id_name].astype(int)
        if not pd.api.types.is_integer_dtype(df_tree[self.id_name]):
            df_tree[self.id_name] = df_tree[self.id_name].astype(int)
        return df_tree.groupby(self.parent_id_name)[self.id_name].apply(list).to_dict()

    def get_tree(self) -> tuple[pd.DataFrame, int]:
        """Builds the tree structure and returns it as a DataFrame."""
        logger.info("Building tree structure")
        pc_dict = self.__get_parent_childs_dict()
        all_children = set([x for y in pc_dict.values() for x in y])
        roots = [k for k in pc_dict.keys() if k not in all_children]
        if len(roots) == 0:
            raise ValueError("No root nodes found in the tree.")
        elif len(roots) == 1:
            root_id = roots[0]
        else:
            # multiple roots found, create a fake root and add all roots as its children
            root_id = max(pc_dict.keys()) + 1
            pc_dict[root_id] = roots
        root = TreeEntry(
            tree_id=1,
            db_id=root_id,
            tree_parent_id=None,
            level=0,
            is_leaf=False,
        )
        tree, _ = self.__build_tree_recursive(root, pc_dict)
        self.set_right_tree_ids(tree)
        # rename back to the original id name
        df = (
            pd.DataFrame([x for x in tree.values()])
            .rename(columns={"db_id": self.id_name})
            .set_index("tree_id", drop=True)
        )
        return df, root_id

    def __build_tree_recursive(
        self,
        tree_entry: TreeEntry,
        pc_dict: dict[int, list[int]],
        level=0,
        tree_id=1,
        tree: dict[int, TreeEntry] = {},
    ):
        """
        Recursively builds a tree structure from parent-child relationships.

        Args:
            tree_entry (TreeEntry): The current tree entry being processed.
            pc_dict (dict[int, list[int]]): A dictionary mapping parent db_id to
                a list of child db_ids.
            level (int): The current level in the tree.
            tree_id (int): The current tree ID.
            tree (dict[int, TreeEntry]): The tree structure being built.
        """
        db_id = tree_entry.db_id
        tree[tree_entry.tree_id] = tree_entry
        children = pc_dict.get(db_id, [])
        level += 1
        for child_db_id in children:
            new_tree_id = tree_id + 1
            new_tree_entry = TreeEntry(
                tree_id=new_tree_id,
                tree_parent_id=tree_entry.tree_id,
                db_id=child_db_id,
                level=level,
                is_leaf=not bool(child_db_id in pc_dict),
            )
            tree, tree_id = self.__build_tree_recursive(
                tree_entry=new_tree_entry,
                pc_dict=pc_dict,
                level=level,
                tree_id=new_tree_id,
                tree=tree,
            )
        return tree, tree_id

    def set_right_tree_ids(self, tree: dict[int, TreeEntry]):
        """
        Assigns the `right_tree_id` attribute for each entry in the tree.

        Calculates and sets the `right_tree_id` for each `TreeEntry` in the
        provided tree structure. The `right_tree_id` is determined based on the tree's
        hierarchical relationships and sibling positions.

        Args:
            tree (dict[int, TreeEntry]): A dictionary representing the tree structure,
                where the keys are tree IDs and the values are `TreeEntry` objects.

        Modifies:
            The `right_tree_id` attribute of each `TreeEntry` in the `tree` dictionary.
        """

        tree_pc_dict = defaultdict(list)
        for child_tree_id, e in tree.items():
            if e.tree_parent_id:
                tree_pc_dict[e.tree_parent_id].append(child_tree_id)

        tree_cp_dict = {}
        for child_tree_id, tree_entry in tree.items():
            if tree_entry.tree_parent_id:
                tree_cp_dict[child_tree_id] = tree_entry.tree_parent_id

        max_tree_id = max(tree_cp_dict)
        e: TreeEntry
        for tree_id, e in tree.items():
            if tree_id == 1:
                e.right_tree_id = max_tree_id + 1
            # check if id not leaf and parent tree id exists
            elif not e.is_leaf and e.tree_parent_id != None:
                # get all siblings right to entry
                sibling_tree_ids = [
                    x for x in tree_pc_dict[e.tree_parent_id] if x > tree_id
                ]
                # if siblings right to entry exists get sibling with the lowest tree id
                if sibling_tree_ids:
                    e.right_tree_id = min(sibling_tree_ids)
                else:
                    e.right_tree_id = tree[e.tree_parent_id].right_tree_id
