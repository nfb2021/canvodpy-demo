import marimo

__generated_with = "0.19.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # canVODpy New API: Custom Components

        Learn how to **extend canVODpy** with your own implementations.
        The factory pattern makes it easy to register custom readers, grids,
        and VOD calculators.

        ## What You'll Learn
        1. Implement a custom grid builder
        2. Register it with the factory
        3. Use it in workflows
        4. Best practices for community contributions
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Setup: Imports")
    return


@app.cell
def _():
    from abc import abstractmethod
    import numpy as np
    import polars as pl
    from canvod.grids.core.grid_builder import BaseGridBuilder
    from canvod.grids.core.grid_data import GridData
    from canvodpy.factories import GridFactory
    return (
        BaseGridBuilder,
        GridData,
        GridFactory,
        abstractmethod,
        np,
        pl,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## 1. Implement Custom Grid Builder

        Create a simple square grid for demonstration.
        **Must inherit from `BaseGridBuilder` ABC.**
        """
    )
    return


@app.cell
def _(BaseGridBuilder, GridData, np, pl):
    class SimpleSquareGrid(BaseGridBuilder):
        """
        Simple square grid for demonstration.

        Divides the hemisphere into square cells.
        """

        def __init__(self, n_divisions: int = 8):
            """Initialize with number of divisions per axis."""
            self.n_divisions = n_divisions
            self.angular_resolution = 90.0 / n_divisions

        def _build_grid(self):
            """Build simple square grid."""
            cells = []
            cell_id = 0

            theta_edges = np.linspace(0, np.pi / 2, self.n_divisions + 1)
            phi_edges = np.linspace(0, 2 * np.pi, self.n_divisions + 1)

            for i in range(self.n_divisions):
                for j in range(self.n_divisions):
                    theta_min = theta_edges[i]
                    theta_max = theta_edges[i + 1]
                    phi_min = phi_edges[j]
                    phi_max = phi_edges[j + 1]

                    cells.append(
                        {
                            "cell_id": cell_id,
                            "phi": (phi_min + phi_max) / 2,
                            "theta": (theta_min + theta_max) / 2,
                            "phi_min": phi_min,
                            "phi_max": phi_max,
                            "theta_min": theta_min,
                            "theta_max": theta_max,
                        }
                    )
                    cell_id += 1

            df = pl.DataFrame(cells)

            return (
                df,
                theta_edges[1:],
                [phi_edges[:-1] for _ in range(self.n_divisions)],
                [np.arange(self.n_divisions) for _ in range(self.n_divisions)],
            )

        @property
        def definition(self) -> str:
            return f"simple_square_{self.n_divisions}x{self.n_divisions}"
    return (SimpleSquareGrid,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 2. Register with Factory

        Once implemented, register your custom grid with the factory.
        """
    )
    return


@app.cell
def _(GridFactory, SimpleSquareGrid):
    GridFactory.register("simple_square", SimpleSquareGrid)
    return


@app.cell
def _(GridFactory, mo):
    mo.md(
        f"""
        **Registration Successful!**

        Available grids now include: `{', '.join(GridFactory.list_available())}`
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## 3. Create Custom Grid")
    return


@app.cell
def _(mo):
    n_divisions = mo.ui.slider(
        4, 16, value=8, label="Grid Divisions", step=1
    )
    n_divisions
    return (n_divisions,)


@app.cell
def _(GridFactory, mo, n_divisions):
    custom_builder = GridFactory.create(
        "simple_square",
        n_divisions=n_divisions.value,
    )

    custom_grid = custom_builder.build()

    mo.md(
        f"""
        **Custom Grid Built!**

        - Type: {custom_grid.definition}
        - Total cells: {custom_grid.ncells}
        - Cells per axis: {n_divisions.value}
        """
    )
    return custom_builder, custom_grid


@app.cell
def _(custom_grid):
    custom_grid.df.head(10)
    return


@app.cell
def _(mo):
    mo.md("## 4. Visualize Custom Grid")
    return


@app.cell
def _():
    import altair as alt
    return (alt,)


@app.cell
def _(alt, custom_grid, pl):
    _plot_data = custom_grid.df.with_columns(
        [
            (pl.col("phi") * 180 / 3.14159).alias("phi_deg"),
            (pl.col("theta") * 180 / 3.14159).alias("theta_deg"),
        ]
    )

    _chart = (
        alt.Chart(_plot_data)
        .mark_square(size=200, opacity=0.6)
        .encode(
            x=alt.X("phi_deg:Q", title="Azimuth (°)"),
            y=alt.Y("theta_deg:Q", title="Elevation (°)"),
            color=alt.Color("theta_deg:Q", title="Elevation"),
            tooltip=["phi_deg", "theta_deg", "cell_id"],
        )
        .properties(
            title="Custom Simple Square Grid",
            width=600,
            height=400,
        )
    )

    _chart
    return


@app.cell
def _(mo):
    mo.md("## 5. Use in Workflow")
    return


@app.cell
def _(VODWorkflow, mo):
    try:
        workflow_custom = VODWorkflow(
            site="Rosalia",
            grid="simple_square",
            grid_params={"n_divisions": 10},
        )

        mo.md(
            f"""
            **Workflow with Custom Grid!**

            - Grid type: {workflow_custom.grid.definition}
            - Total cells: {workflow_custom.grid.ncells}

            The workflow seamlessly uses your custom grid implementation!
            """
        )
    except Exception as e:
        mo.md(f"⚠️ {e}")
    return (workflow_custom,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 6. Best Practices

        ### ✅ Inherit from ABC
        Always inherit from the correct abstract base class:
        - Grids: `BaseGridBuilder`
        - Readers: `GNSSDataReader`
        - VOD: `VODCalculator`

        ### ✅ Type Hints
        Add full type hints to all methods.

        ### ✅ Docstrings
        Use numpy-style docstrings.

        ### ✅ Validation
        Add Pydantic validators for parameters.

        ### ✅ Testing
        Include unit tests for your implementation.

        ### ✅ Documentation
        Document parameters and return values clearly.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 7. Publishing Custom Components

        ### Package Structure
        ```
        my-canvodpy-extension/
        ├── pyproject.toml
        ├── src/
        │   └── my_extension/
        │       ├── __init__.py
        │       ├── grids.py       # Custom grids
        │       ├── readers.py     # Custom readers
        │       └── calculators.py # Custom VOD methods
        └── tests/
        ```

        ### User Integration
        ```python
        # Install extension
        pip install my-canvodpy-extension

        # Import and register
        from canvodpy.factories import GridFactory
        from my_extension.grids import MyCustomGrid

        GridFactory.register("my_grid", MyCustomGrid)

        # Use in workflow
        workflow = VODWorkflow(
            site="MySite",
            grid="my_grid",
            grid_params={...}
        )
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## 8. Community Contributions

        Want to contribute your components to canVODpy?

        1. **Fork** the repository
        2. **Implement** your component with tests
        3. **Document** with examples
        4. **Submit** a pull request

        See `docs/guides/API_REDESIGN.md` for the full contribution guide!

        ---

        ## Summary

        You've learned how to:
        - ✅ Create custom grid builders
        - ✅ Register with factories
        - ✅ Use in workflows
        - ✅ Follow best practices
        - ✅ Publish extensions

        The factory pattern makes canVODpy truly extensible!
        """
    )
    return


@app.cell
def _():
    from canvodpy import VODWorkflow
    return (VODWorkflow,)


if __name__ == "__main__":
    app.run()
