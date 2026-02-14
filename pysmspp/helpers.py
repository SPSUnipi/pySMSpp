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
    # Get block type
    block_type = "Unknown"
    if hasattr(block, "block_type") and block.block_type:
        block_type = block.block_type

    # Print the current block
    if _is_root:
        # Root level - no connector
        print(f"{name} [{block_type}]")
        child_indent = ""
    else:
        connector = "└── " if _is_last else "├── "
        print(f"{_indent}{connector}{name} [{block_type}]")
        child_indent = _indent + ("    " if _is_last else "│   ")

    # Print dimensions if requested
    if show_dimensions and block.dimensions:
        dims_str = ", ".join(
            f"{key}={value}" for key, value in block.dimensions.items()
        )
        detail_indent = child_indent if not _is_root else "  "
        print(f"{detail_indent}Dimensions: {dims_str}")

    # Print variables if requested
    if show_variables and block.variables:
        vars_list = list(block.variables.keys())
        if len(vars_list) <= 5:
            vars_str = ", ".join(vars_list)
        else:
            vars_str = ", ".join(vars_list[:5]) + f", ... ({len(vars_list)} total)"
        detail_indent = child_indent if not _is_root else "  "
        print(f"{detail_indent}Variables: {vars_str}")

    # Print attributes if requested (exclude 'type' since it's shown in brackets)
    if show_attributes and block.attributes:
        attrs = {k: v for k, v in block.attributes.items() if k != "type"}
        if attrs:
            attrs_list = [f"{k}={v}" for k, v in list(attrs.items())[:5]]
            if len(attrs) <= 5:
                attrs_str = ", ".join(attrs_list)
            else:
                attrs_str = ", ".join(attrs_list) + f", ... ({len(attrs)} total)"
            detail_indent = child_indent if not _is_root else "  "
            print(f"{detail_indent}Attributes: {attrs_str}")

    # Recursively print sub-blocks
    if block.blocks:
        sub_blocks = list(block.blocks.items())
        for i, (sub_name, sub_block) in enumerate(sub_blocks):
            is_last_child = i == len(sub_blocks) - 1
            print_block_tree(
                sub_block,
                sub_name,
                show_dimensions,
                show_variables,
                show_attributes,
                child_indent,
                is_last_child,
                False,
            )
