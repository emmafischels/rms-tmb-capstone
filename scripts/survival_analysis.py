from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test


@dataclass
class SurvivalAnalysisResults:
    figure: go.Figure
    summary_table: pd.DataFrame
    test_statistic: float
    p_value: float


def add_kaplan_meier_group(
    figure: go.Figure,
    data: pd.DataFrame,
    group_name: str,
    duration_column: str,
    event_column: str,
    show_confidence_interval: bool = True,
) -> KaplanMeierFitter:
    """
    Fit and add one Kaplan-Meier curve to a Plotly figure.
    """
    fitter = KaplanMeierFitter()

    fitter.fit(
        durations=data[duration_column],
        event_observed=data[event_column],
        label=group_name,
    )

    survival_function = (
        fitter.survival_function_
    )

    if show_confidence_interval:
        confidence_interval = (
            fitter.confidence_interval_
        )

        figure.add_trace(
            go.Scatter(
                x=confidence_interval.index,
                y=confidence_interval.iloc[:, 1],
                mode="lines",
                line={"width": 0},
                hoverinfo="skip",
                showlegend=False,
                name=f"{group_name} upper CI",
            )
        )

        figure.add_trace(
            go.Scatter(
                x=confidence_interval.index,
                y=confidence_interval.iloc[:, 0],
                mode="lines",
                line={"width": 0},
                fill="tonexty",
                opacity=0.2,
                hoverinfo="skip",
                showlegend=False,
                name=f"{group_name} 95% CI",
            )
        )

    figure.add_trace(
        go.Scatter(
            x=survival_function.index,
            y=survival_function.iloc[:, 0],
            mode="lines",
            line_shape="hv",
            name=group_name,
            hovertemplate=(
                "Time: %{x:.1f} months"
                "<br>Survival probability: %{y:.3f}"
                "<extra></extra>"
            ),
        )
    )

    return fitter


def run_binary_survival_analysis(
    data: pd.DataFrame,
    group_column: str = "TMB Group",
    duration_column: str = "Overall Survival (Months)",
    event_column: str = "Event",
    high_group: str = "High TMB",
    low_group: str = "Low TMB",
    show_confidence_interval: bool = True,
) -> SurvivalAnalysisResults:
    """
    Run a two-group Kaplan-Meier and log-rank analysis.
    """
    high_data = data[
        data[group_column] == high_group
    ].copy()

    low_data = data[
        data[group_column] == low_group
    ].copy()

    if high_data.empty or low_data.empty:
        raise ValueError(
            "Both TMB groups must contain at least one observation."
        )

    figure = go.Figure()

    high_fitter = add_kaplan_meier_group(
        figure=figure,
        data=high_data,
        group_name=high_group,
        duration_column=duration_column,
        event_column=event_column,
        show_confidence_interval=(
            show_confidence_interval
        ),
    )

    low_fitter = add_kaplan_meier_group(
        figure=figure,
        data=low_data,
        group_name=low_group,
        duration_column=duration_column,
        event_column=event_column,
        show_confidence_interval=(
            show_confidence_interval
        ),
    )

    test_results = logrank_test(
        high_data[duration_column],
        low_data[duration_column],
        event_observed_A=high_data[event_column],
        event_observed_B=low_data[event_column],
    )

    figure.update_layout(
        title=(
            "Kaplan–Meier Overall Survival "
            "by TMB Group"
        ),
        xaxis_title="Overall Survival (Months)",
        yaxis_title="Survival Probability",
        yaxis={
            "range": [0, 1.05],
        },
        hovermode="x unified",
        template="plotly_white",
    )

    summary_table = pd.DataFrame(
        {
            "TMB Group": [
                high_group,
                low_group,
            ],
            "Observations": [
                len(high_data),
                len(low_data),
            ],
            "Deaths": [
                int(high_data[event_column].sum()),
                int(low_data[event_column].sum()),
            ],
            "Censored": [
                int(
                    (
                        high_data[event_column] == 0
                    ).sum()
                ),
                int(
                    (
                        low_data[event_column] == 0
                    ).sum()
                ),
            ],
            "Median Survival Months": [
                high_fitter.median_survival_time_,
                low_fitter.median_survival_time_,
            ],
        }
    )

    return SurvivalAnalysisResults(
        figure=figure,
        summary_table=summary_table,
        test_statistic=float(
            test_results.test_statistic
        ),
        p_value=float(
            test_results.p_value
        ),
    )