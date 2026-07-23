from pathlib import Path
from typing import Literal

import pandas as pd


PATIENT_ID = "Patient ID"
SAMPLE_ID = "Sample ID"
TMB = "TMB (nonsynonymous)"
SURVIVAL_TIME = "Overall Survival (Months)"
SURVIVAL_STATUS = "Overall Survival Status"

AggregationMethod = Literal[
    "mean",
    "median",
    "min",
    "max",
]

REQUIRED_COLUMNS = [
    PATIENT_ID,
    SAMPLE_ID,
    TMB,
    SURVIVAL_TIME,
    SURVIVAL_STATUS,
]


def load_clinical_data(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Load the tab-separated clinical dataset.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path.resolve()}"
        )

    data = pd.read_csv(
        file_path,
        sep="\t",
    )

    validate_required_columns(data)

    return data


def validate_required_columns(
    data: pd.DataFrame,
) -> None:
    """
    Confirm that columns required by the app are present.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


def get_numeric_columns(
    data: pd.DataFrame,
) -> list[str]:
    """
    Return numeric columns containing at least one value.
    """
    return [
        column
        for column in data.select_dtypes(
            include="number"
        ).columns
        if data[column].notna().any()
    ]


def get_categorical_columns(
    data: pd.DataFrame,
) -> list[str]:
    """
    Return nonnumeric columns containing at least one value.
    """
    return [
        column
        for column in data.select_dtypes(
            exclude="number"
        ).columns
        if data[column].notna().any()
    ]


def create_patient_level_data(
    data: pd.DataFrame,
    numeric_aggregation: AggregationMethod = "mean",
) -> pd.DataFrame:
    """
    Collapse sample-level records into one row per patient.

    Numeric columns use the selected aggregation method.
    Nonnumeric columns use the first nonmissing value.
    """
    valid_methods = {
        "mean",
        "median",
        "min",
        "max",
    }

    if numeric_aggregation not in valid_methods:
        raise ValueError(
            f"Aggregation must be one of {valid_methods}."
        )

    numeric_columns = [
        column
        for column in get_numeric_columns(data)
        if column not in {
            PATIENT_ID,
            SAMPLE_ID,
        }
    ]

    categorical_columns = [
        column
        for column in data.columns
        if column not in numeric_columns
        and column not in {
            PATIENT_ID,
            SAMPLE_ID,
        }
    ]

    aggregation_rules: dict[str, str] = {}

    for column in numeric_columns:
        aggregation_rules[column] = (
            numeric_aggregation
        )

    for column in categorical_columns:
        aggregation_rules[column] = "first"

    patient_data = (
        data
        .groupby(
            PATIENT_ID,
            as_index=False,
        )
        .agg(aggregation_rules)
    )

    sample_counts = (
        data
        .groupby(PATIENT_ID)
        .size()
        .rename("Number of Samples")
        .reset_index()
    )

    patient_data = patient_data.merge(
        sample_counts,
        on=PATIENT_ID,
        how="left",
    )

    return patient_data


def create_analysis_dataset(
    data: pd.DataFrame,
    analysis_level: str,
    patient_aggregation: AggregationMethod = "mean",
) -> pd.DataFrame:
    """
    Return a sample-level or patient-level dataset.
    """
    if analysis_level == "Sample":
        return data.copy()

    if analysis_level == "Patient":
        return create_patient_level_data(
            data=data,
            numeric_aggregation=patient_aggregation,
        )

    raise ValueError(
        "Analysis level must be Sample or Patient."
    )


def convert_survival_status_to_event(
    survival_status: pd.Series,
) -> pd.Series:
    """
    Convert survival status into a binary event variable.

    1 = deceased
    0 = living/censored
    """
    normalized_status = (
        survival_status
        .astype("string")
        .str.strip()
        .str.upper()
    )

    event = pd.Series(
        pd.NA,
        index=survival_status.index,
        dtype="Int64",
    )

    deceased_mask = normalized_status.str.contains(
        "DECEASED",
        na=False,
    )

    living_mask = normalized_status.str.contains(
        "LIVING",
        na=False,
    )

    event.loc[deceased_mask] = 1
    event.loc[living_mask] = 0

    return event


def prepare_survival_data(
    data: pd.DataFrame,
    analysis_level: str = "Patient",
    tmb_aggregation: AggregationMethod = "mean",
) -> pd.DataFrame:
    """
    Create a clean dataset for survival analysis.
    """
    if analysis_level == "Patient":
        survival_data = (
            data
            .groupby(
                PATIENT_ID,
                as_index=False,
            )
            .agg(
                {
                    TMB: tmb_aggregation,
                    SURVIVAL_TIME: "first",
                    SURVIVAL_STATUS: "first",
                }
            )
        )

    elif analysis_level == "Sample":
        survival_data = data[
            [
                PATIENT_ID,
                SAMPLE_ID,
                TMB,
                SURVIVAL_TIME,
                SURVIVAL_STATUS,
            ]
        ].copy()

    else:
        raise ValueError(
            "Analysis level must be Sample or Patient."
        )

    survival_data[TMB] = pd.to_numeric(
        survival_data[TMB],
        errors="coerce",
    )

    survival_data[SURVIVAL_TIME] = (
        pd.to_numeric(
            survival_data[SURVIVAL_TIME],
            errors="coerce",
        )
    )

    survival_data["Event"] = (
        convert_survival_status_to_event(
            survival_data[SURVIVAL_STATUS]
        )
    )

    survival_data = survival_data.dropna(
        subset=[
            TMB,
            SURVIVAL_TIME,
            "Event",
        ]
    ).copy()

    survival_data = survival_data[
        survival_data[SURVIVAL_TIME] >= 0
    ].copy()

    survival_data["Event"] = (
        survival_data["Event"]
        .astype(int)
    )

    return survival_data


def assign_binary_tmb_groups(
    survival_data: pd.DataFrame,
    cutoff: float,
) -> pd.DataFrame:
    """
    Divide observations into low- and high-TMB groups.
    """
    grouped_data = survival_data.copy()

    grouped_data["TMB Group"] = (
        grouped_data[TMB] > cutoff
    ).map(
        {
            True: "High TMB",
            False: "Low TMB",
        }
    )

    return grouped_data


def assign_tmb_quartiles(
    survival_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Divide TMB into quartile groups.
    """
    grouped_data = survival_data.copy()

    grouped_data["TMB Quartile"] = pd.qcut(
        grouped_data[TMB],
        q=4,
        labels=[
            "Q1",
            "Q2",
            "Q3",
            "Q4",
        ],
        duplicates="drop",
    )

    return grouped_data