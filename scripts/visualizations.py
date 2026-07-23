from collections.abc import Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_histogram(
    data: pd.DataFrame,
    variable: str,
    bins: int = 15,
) -> go.Figure:
    """
    Create an interactive histogram with a marginal boxplot.
    """
    figure = px.histogram(
        data,
        x=variable,
        nbins=bins,
        marginal="box",
        title=f"Distribution of {variable}",
    )

    figure.update_layout(
        template="plotly_white",
        xaxis_title=variable,
        yaxis_title="Count",
    )

    return figure


def create_scatterplot(
    data: pd.DataFrame,
    x_variable: str,
    y_variable: str,
    hover_columns: Sequence[str] | None = None,
    add_trendline: bool = False,
) -> go.Figure:
    """
    Create an interactive scatterplot.
    """
    if hover_columns is None:
        hover_columns = []

    valid_hover_columns = [
        column
        for column in hover_columns
        if column in data.columns
    ]

    trendline = (
        "ols"
        if add_trendline
        else None
    )

    figure = px.scatter(
        data,
        x=x_variable,
        y=y_variable,
        hover_data=valid_hover_columns,
        trendline=trendline,
        title=f"{y_variable} vs {x_variable}",
    )

    figure.update_layout(
        template="plotly_white",
    )

    return figure


def create_boxplot(
    data: pd.DataFrame,
    numeric_variable: str,
    category_variable: str | None = None,
    show_points: bool = True,
) -> go.Figure:
    """
    Create a grouped or ungrouped boxplot.
    """
    points = "all" if show_points else False

    if category_variable is None:
        figure = px.box(
            data,
            y=numeric_variable,
            points=points,
            title=f"Distribution of {numeric_variable}",
        )

    else:
        figure = px.box(
            data,
            x=category_variable,
            y=numeric_variable,
            points=points,
            title=(
                f"{numeric_variable} by "
                f"{category_variable}"
            ),
        )

    figure.update_layout(
        template="plotly_white",
    )

    return figure


def create_violin_plot(
    data: pd.DataFrame,
    numeric_variable: str,
    category_variable: str | None = None,
) -> go.Figure:
    """
    Create a grouped or ungrouped violin plot.
    """
    if category_variable is None:
        figure = px.violin(
            data,
            y=numeric_variable,
            box=True,
            points="all",
            title=f"Distribution of {numeric_variable}",
        )

    else:
        figure = px.violin(
            data,
            x=category_variable,
            y=numeric_variable,
            box=True,
            points="all",
            title=(
                f"{numeric_variable} by "
                f"{category_variable}"
            ),
        )

    figure.update_layout(
        template="plotly_white",
    )

    return figure


def create_correlation_heatmap(
    data: pd.DataFrame,
    variables: Sequence[str],
    method: str = "pearson",
) -> tuple[go.Figure, pd.DataFrame]:
    """
    Create a correlation matrix and heatmap.
    """
    correlation_matrix = (
        data[list(variables)]
        .corr(method=method)
    )

    figure = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=(
            f"{method.title()} Correlation Matrix"
        ),
    )

    figure.update_layout(
        template="plotly_white",
    )

    return figure, correlation_matrix


def create_frequency_plot(
    data: pd.DataFrame,
    variable: str,
) -> tuple[go.Figure, pd.DataFrame]:
    """
    Create a frequency table and categorical bar chart.
    """
    frequency_table = (
        data[variable]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .rename_axis(variable)
        .reset_index(name="Count")
    )

    figure = px.bar(
        frequency_table,
        x=variable,
        y="Count",
        title=f"Frequency of {variable}",
    )

    figure.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45,
    )

    return figure, frequency_table


def create_missing_data_plot(
    data: pd.DataFrame,
) -> tuple[go.Figure | None, pd.DataFrame]:
    """
    Create a missing-data summary and optional bar chart.
    """
    missing_summary = (
        data
        .isna()
        .sum()
        .rename("Missing Values")
        .reset_index()
        .rename(
            columns={
                "index": "Variable",
            }
        )
    )

    missing_summary["Percent Missing"] = (
        missing_summary["Missing Values"]
        / len(data)
        * 100
    )

    missing_summary = (
        missing_summary
        .sort_values(
            "Missing Values",
            ascending=False,
        )
    )

    plot_data = missing_summary[
        missing_summary["Missing Values"] > 0
    ]

    if plot_data.empty:
        return None, missing_summary

    figure = px.bar(
        plot_data,
        x="Variable",
        y="Percent Missing",
        hover_data=["Missing Values"],
        title="Missing Data by Variable",
    )

    figure.update_layout(
        template="plotly_white",
        xaxis_tickangle=-45,
        yaxis_title="Percent Missing",
    )

    return figure, missing_summary


def dataframe_to_csv_bytes(
    data: pd.DataFrame,
    include_index: bool = False,
) -> bytes:
    """
    Convert a DataFrame to downloadable CSV bytes.
    """
    return data.to_csv(
        index=include_index,
    ).encode("utf-8")