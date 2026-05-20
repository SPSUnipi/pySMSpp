# Architecture

pySMSpp is the Python interface layer around SMS++ models. Its main job is to let
users build, inspect, edit, serialize, and optimize SMS++ block-structured models
from Python while preserving the model hierarchy expected by SMS++.

At a high level, pySMSpp keeps an in-memory representation of an SMS++ model,
writes that representation to a netCDF4 file, and delegates optimization to an
external SMS++ solver executable.

## Big picture

```text
Python user code
    |
    v
SMSNetwork
    |
    v
Block hierarchy
    |
    v
Attributes, dimensions, variables, nested blocks
    |
    v
netCDF4 SMS++ file
    |
    v
SMS++ solver executable
    |
    v
Solver log and optional solution file
    |
    v
SMSPPSolverTool result object
```

This architecture mirrors the SMS++ model format: models are hierarchical, each
node in the hierarchy is a block, and model data are stored as attributes,
dimensions, variables, and child blocks.

## Repository layout

The package is intentionally compact. Most user-facing behavior lives in three
Python modules and a small metadata layer:

- `pysmspp/block.py` defines the in-memory model objects, netCDF4 input/output,
  and the `SMSNetwork.optimize()` entry point.
- `pysmspp/smspp_tools.py` defines wrappers around SMS++ command-line solver
  tools.
- `pysmspp/components.py` defines `Dict`, a small dictionary subclass used for
  attribute-style access to model collections.
- `pysmspp/data/components.csv` describes the base SMS++ component categories
  used by `Block.add()`.
- `pysmspp/data/blocks/*.csv` describes known SMS++ block types and their
  expected attributes, dimensions, variables, and nested blocks.
- `pysmspp/data/configs/` contains packaged solver configuration templates used
  by `SMSConfig`.

The documentation, examples, and tests are outside the package code:

- `docs/` contains the MkDocs documentation site.
- `docs/examples/` contains executable notebook examples.
- `test/` contains regression tests and small netCDF4 fixtures.

## Core objects

### `SMSNetwork`

`SMSNetwork` is the top-level model container and the main entry point for users.
It inherits from `Block`, so it has the same attributes, dimensions, variables,
and nested blocks as every other block.

In addition, `SMSNetwork` stores the SMS++ file type through the
`SMS++_file_type` attribute and provides `optimize()`, which writes the current
model to a temporary netCDF4 file and launches an SMS++ solver wrapper.

### `Block`

`Block` is the fundamental modeling object. A block represents one node in the
SMS++ hierarchy and can contain four collections:

- `attributes`: scalar metadata such as the block `type`.
- `dimensions`: named sizes used by variables.
- `variables`: typed scalar or array data.
- `blocks`: nested `Block` objects.

Because blocks can contain other blocks, complete SMS++ models are represented
as trees. A simple unit commitment model, for example, can be viewed as:

```text
SMSNetwork
+-- Block_0 [UCBlock]
    +-- UnitBlock_0 [ThermalUnitBlock]
```

The `print_tree()` method is useful for inspecting this hierarchy after loading
or constructing a model.

### `Attribute`, `Dimension`, and `Variable`

These classes are lightweight containers for the objects stored inside a block:

- `Attribute(name, value)` stores scalar metadata or configuration values.
- `Dimension(name, value)` stores a named array size.
- `Variable(name, var_type, dimensions, data)` stores typed data, where
  `dimensions` names the dimensions that define the data shape.

The netCDF4 writer maps these objects directly to netCDF4 attributes,
dimensions, variables, and groups.

### `SMSConfig`

`SMSConfig` resolves solver configuration files. It can point to an explicit file
path or to one of the packaged templates under `pysmspp/data/configs/`.

`SMSNetwork.optimize()` accepts an `SMSConfig`, a path to a configuration file, or
a template-backed configuration object.

### `SMSPPSolverTool` and solver wrappers

`SMSPPSolverTool` is the base wrapper for external SMS++ solver executables. It
builds the command-line call, runs the subprocess, captures logs, tracks basic
resource usage, parses solver output, and optionally loads a solution file back
as an `SMSNetwork`.

Concrete wrappers provide executable defaults and solver-specific log parsing.
The package currently includes wrappers such as:

- `UCBlockSolver`
- `InvestmentBlockTestSolver`
- `InvestmentBlockSolver`
- `InvestmentSolver`
- `SDDPSolver`
- `TSSBSolver`

These wrappers do not implement the mathematical solver in Python. They bridge
the Python model representation to installed SMS++ command-line tools.

## Metadata-driven construction

pySMSpp uses CSV metadata to decide how named model fields should be represented
inside a block.

When using `Block(...)`, `Block.from_kwargs(...)`, or `Block.add(...)`, the package consults:

- `pysmspp/data/components.csv` to map a component category to its storage
  collection (`attributes`, `dimensions`, `variables`, or `blocks`).
- `pysmspp/data/blocks/<BlockType>.csv` to infer whether a field of a known block
  type is an attribute, dimension, variable, or nested block.

For example, after a block is identified as a `UCBlock`, pySMSpp can interpret
fields such as `TimeHorizon`, `NumberUnits`, and `ActivePowerDemand` according
to the `UCBlock.csv` metadata.

This keeps user code concise while still preserving the SMS++ structure:

```python
from pysmspp import SMSNetwork, SMSFileType, Variable

sn = SMSNetwork(file_type=SMSFileType.eBlockFile)

sn.add(
    "UCBlock",
    "Block_0",
    TimeHorizon=24,
    NumberUnits=1,
    NumberNodes=1,
    ActivePowerDemand=Variable(
        "ActivePowerDemand",
        "float",
        ("NumberNodes", "TimeHorizon"),
        [[50.0] * 24],
    ),
)
```

## File and execution flow

A typical workflow has six steps:

1. Create or load an `SMSNetwork`.
2. Add or edit blocks, attributes, dimensions, and variables.
3. Write the model with `to_netcdf()`, or let `optimize()` write a temporary
   netCDF4 file.
4. Resolve a solver configuration with `SMSConfig`.
5. Launch an SMS++ solver through `SMSPPSolverTool` or one of its subclasses.
6. Read solver status, objective values, logs, and optionally a solution network
   from the result object.

`SMSNetwork.optimize()` can select a default solver when `smspp_solver="auto"`.
The automatic choice is based on the type of the configured inner block, usually
`Block_0`. Users can also pass an explicit solver wrapper when they need full
control over the executable path or command-line options.

## Loading and saving models

Both `Block` and `SMSNetwork` support netCDF4 input/output:

```python
from pysmspp import SMSNetwork

sn = SMSNetwork(fp="model.nc4")
sn.print_tree(show_all=True)

sn.to_netcdf("copy.nc4", force=True)
```

Nested blocks become netCDF4 groups. Block attributes become netCDF4 attributes.
Dimensions and variables become netCDF4 dimensions and variables. This direct
mapping is what allows pySMSpp to preserve the SMS++ hierarchy across Python and
SMS++ tools.

## What pySMSpp does not hide

pySMSpp intentionally exposes SMS++ concepts rather than replacing them with a
separate modeling language. Users still work with SMS++ block types, solver
configuration files, and installed SMS++ executables.

This makes pySMSpp especially useful when you want to:

- build SMS++ input files programmatically;
- inspect or edit existing SMS++ netCDF4 models;
- run installed SMS++ solvers from Python;
- analyze logs and solution files in Python workflows.

## Where to go next

- Start with the [Quick Start](../getting-started/quick-start.md) for a minimal
  model construction and optimization example.
- Use [Navigating SMS Blocks](../examples/navigating_sms_blocks.ipynb) to learn
  how to inspect loaded model trees.
- Use [Input/Output Operations](../examples/io_operations.ipynb) to learn how
  pySMSpp reads and writes netCDF4 files.
- Use the [API Reference](../api_reference.md) for class and method details.
