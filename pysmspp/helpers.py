from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pysmspp.block import Block


def print_block_tree(
    block: "Block",
    name: str = "Block",
    show_dimensions: bool = False,
    show_variables: bool = False,
    show_attributes: bool = False,
    _indent: str = "",
    _is_last: bool = True,
    _is_root: bool = True,
) -> None:
    """
    Print a tree representation of the block structure.

    This function displays the hierarchical structure of blocks in a tree format,
    with optional display of dimensions, variables, and attributes.

    Note: This is a convenience function that calls the Block.print_tree() method.
    You can also call block.print_tree() directly on any Block instance.

    Parameters
    ----------
    block : Block
        The block object to visualize.
    name : str, optional
        The name of the block (default: "Block").
    show_dimensions : bool, optional
        Whether to display dimensions (default: False).
    show_variables : bool, optional
        Whether to display variables (default: False).
    show_attributes : bool, optional
        Whether to display attributes (default: False).
    _indent : str, optional
        Internal parameter for indentation (default: "").
    _is_last : bool, optional
        Internal parameter to track if this is the last child (default: True).
    _is_root : bool, optional
        Internal parameter to track if this is the root node (default: True).

    Examples
    --------
    >>> from pysmspp import Block, print_block_tree
    >>> block = Block(fp="network.nc4")
    >>> print_block_tree(block, "MyNetwork")
    MyNetwork [BlockType]
    └── Block_0 [UCBlock]
        ├── UnitBlock_0 [ThermalUnitBlock]
        └── UnitBlock_1 [BatteryUnitBlock]

    >>> print_block_tree(block, "MyNetwork", show_dimensions=True, show_variables=True)
    MyNetwork [BlockType]
      Dimensions: n=10, m=5
      Variables: var1, var2, var3
    └── Block_0 [UCBlock]
        ...
    """
    # Delegate to the Block.print_tree() method
    block.print_tree(
        name=name,
        show_dimensions=show_dimensions,
        show_variables=show_variables,
        show_attributes=show_attributes,
        _indent=_indent,
        _is_last=_is_last,
        _is_root=_is_root,
    )
