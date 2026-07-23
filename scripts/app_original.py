# -------------------------
# Imports
# -------------------------

from pathlib import Path

import pandas as pd
import streamlit as st

from data_processing import (
    TMB,
    create_analysis_dataset,
    get_categorical_columns,
    get_numeric_columns,
    load_clinical_data,
    prepare_survival_data,
    assign_binary_tmb_groups,
)

from survival_analysis import (
    run_binary_survival_analysis,
)

from visualizations import (
    create_boxplot,
    create_correlation_heatmap,
    create_frequency_plot,
    create_histogram,
    create_missing_data_plot,
    create_scatterplot,
    create_violin_plot,
    dataframe_to_csv_bytes,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Rhabdomyosarcoma TMB & Survival Explorer",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# PROJECT PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

DATA_FILE = (
    PROJECT_DIR
    / "data"
    / "soft_tissue_msk_2023_clinical_data.tsv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(
    file_path: str,
) -> pd.DataFrame:
    """
    Load and validate the clinical dataset.
    """
    return load_clinical_data(file_path)


try:
    df = load_data(str(DATA_FILE))

except (FileNotFoundError, ValueError) as error:
    st.error(
        f"Unable to load the dataset: {error}"
    )

    st.info(
        f"Expected dataset location: {DATA_FILE}"
    )

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title(
    "Rhabdomyosarcoma TMB & Survival Explorer"
)

st.write(
    """
    This interactive application explores tumor mutational
    burden, clinical characteristics, and overall survival in
    the MSK rhabdomyosarcoma dataset.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Analysis Settings")

analysis_type = st.sidebar.selectbox(
    "Select analysis",
    [
        "Data Overview",
        "Exploratory Analysis",
        "Survival Analysis",
    ],
)


# ============================================================
# DATA OVERVIEW
# ============================================================

if analysis_type == "Data Overview":

    st.header("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Samples",
            len(df),
        )

    with col2:
        st.metric(
            "Patients",
            df["Patient ID"].nunique(),
        )

    with col3:
        st.metric(
            "Variables",
            df.shape[1],
        )

    with col4:
        st.metric(
            "Missing Values",
            int(df.isna().sum().sum()),
        )

    st.subheader("Dataset Preview")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download dataset as CSV",
        data=dataframe_to_csv_bytes(df),
        file_name="rhabdomyosarcoma_dataset.csv",
        mime="text/csv",
    )

    st.subheader("Variable Information")

    variable_information = pd.DataFrame(
        {
            "Variable": df.columns,
            "Data Type": (
                df.dtypes.astype(str).values
            ),
            "Missing Values": (
                df.isna().sum().values
            ),
            "Percent Missing": (
                df.isna().mean().values
                * 100
            ),
        }
    )

    st.dataframe(
        variable_information,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Missing Data")

    missing_figure, missing_summary = (
        create_missing_data_plot(df)
    )

    if missing_figure is None:
        st.success(
            "No missing values were identified."
        )

    else:
        st.plotly_chart(
            missing_figure,
            use_container_width=True,
        )

    with st.expander(
        "View missing-data summary"
    ):
        st.dataframe(
            missing_summary,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Summary Statistics")

    summary_statistics = (
        df.describe(
            include="all"
        )
        .transpose()
        .reset_index()
        .rename(
            columns={
                "index": "Variable",
            }
        )
    )

    st.dataframe(
        summary_statistics,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# EXPLORATORY ANALYSIS
# ============================================================

elif analysis_type == "Exploratory Analysis":

    st.header("Exploratory Data Analysis")

    st.write(
        """
        Explore variable distributions and relationships using
        sample-level or patient-level data.
        """
    )

    analysis_level = st.sidebar.selectbox(
        "Analysis level",
        [
            "Sample",
            "Patient",
        ],
    )

    patient_aggregation = "mean"

    if analysis_level == "Patient":

        patient_aggregation = (
            st.sidebar.selectbox(
                "Patient numeric aggregation",
                [
                    "mean",
                    "median",
                    "min",
                    "max",
                ],
                format_func=lambda value: (
                    value.title()
                ),
            )
        )

    analysis_df = create_analysis_dataset(
        data=df,
        analysis_level=analysis_level,
        patient_aggregation=patient_aggregation,
    )

    if analysis_level == "Sample":
        st.info(
            f"Sample-level analysis includes "
            f"{len(analysis_df)} samples."
        )

    else:
        st.info(
            f"Patient-level analysis includes "
            f"{len(analysis_df)} patients. "
            f"Numeric variables were aggregated "
            f"using the {patient_aggregation}."
        )

    numeric_columns = get_numeric_columns(
        analysis_df
    )

    categorical_columns = (
        get_categorical_columns(
            analysis_df
        )
    )

    plot_type = st.selectbox(
        "Select visualization",
        [
            "Histogram",
            "Scatter Plot",
            "Box Plot",
            "Violin Plot",
            "Correlation Heatmap",
            "Categorical Frequency Plot",
        ],
    )

    # --------------------------------------------------------
    # HISTOGRAM
    # --------------------------------------------------------

    if plot_type == "Histogram":

        if not numeric_columns:
            st.warning(
                "No numeric variables are available."
            )

        else:
            variable = st.selectbox(
                "Select numeric variable",
                numeric_columns,
            )

            bins = st.slider(
                "Number of bins",
                min_value=5,
                max_value=50,
                value=15,
            )

            figure = create_histogram(
                data=analysis_df,
                variable=variable,
                bins=bins,
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # SCATTER PLOT
    # --------------------------------------------------------

    elif plot_type == "Scatter Plot":

        if len(numeric_columns) < 2:
            st.warning(
                "At least two numeric variables "
                "are required."
            )

        else:
            col1, col2 = st.columns(2)

            with col1:
                x_variable = st.selectbox(
                    "Select X variable",
                    numeric_columns,
                    index=0,
                )

            with col2:
                y_variable = st.selectbox(
                    "Select Y variable",
                    numeric_columns,
                    index=min(
                        1,
                        len(numeric_columns) - 1,
                    ),
                )

            add_trendline = st.checkbox(
                "Add ordinary least-squares trendline",
                value=True,
            )

            hover_columns = [
                column
                for column in [
                    "Patient ID",
                    "Sample ID",
                ]
                if column in analysis_df.columns
            ]

            figure = create_scatterplot(
                data=analysis_df,
                x_variable=x_variable,
                y_variable=y_variable,
                hover_columns=hover_columns,
                add_trendline=add_trendline,
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # BOX PLOT
    # --------------------------------------------------------

    elif plot_type == "Box Plot":

        if not numeric_columns:
            st.warning(
                "No numeric variables are available."
            )

        else:
            numeric_variable = st.selectbox(
                "Select numeric variable",
                numeric_columns,
            )

            category_options = [
                "None",
                *categorical_columns,
            ]

            category_variable = st.selectbox(
                "Group by categorical variable",
                category_options,
            )

            show_points = st.checkbox(
                "Display individual observations",
                value=True,
            )

            selected_category = (
                None
                if category_variable == "None"
                else category_variable
            )

            figure = create_boxplot(
                data=analysis_df,
                numeric_variable=numeric_variable,
                category_variable=(
                    selected_category
                ),
                show_points=show_points,
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # VIOLIN PLOT
    # --------------------------------------------------------

    elif plot_type == "Violin Plot":

        if not numeric_columns:
            st.warning(
                "No numeric variables are available."
            )

        else:
            numeric_variable = st.selectbox(
                "Select numeric variable",
                numeric_columns,
            )

            category_options = [
                "None",
                *categorical_columns,
            ]

            category_variable = st.selectbox(
                "Group by categorical variable",
                category_options,
            )

            selected_category = (
                None
                if category_variable == "None"
                else category_variable
            )

            figure = create_violin_plot(
                data=analysis_df,
                numeric_variable=numeric_variable,
                category_variable=(
                    selected_category
                ),
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # CORRELATION HEATMAP
    # --------------------------------------------------------

    elif plot_type == "Correlation Heatmap":

        if len(numeric_columns) < 2:
            st.warning(
                "At least two numeric variables "
                "are required."
            )

        else:
            default_variables = (
                numeric_columns[:4]
            )

            selected_variables = st.multiselect(
                "Select numeric variables",
                numeric_columns,
                default=default_variables,
            )

            correlation_method = st.selectbox(
                "Correlation method",
                [
                    "pearson",
                    "spearman",
                    "kendall",
                ],
                format_func=lambda value: (
                    value.title()
                ),
            )

            if len(selected_variables) < 2:
                st.warning(
                    "Select at least two variables."
                )

            else:
                figure, correlation_matrix = (
                    create_correlation_heatmap(
                        data=analysis_df,
                        variables=(
                            selected_variables
                        ),
                        method=(
                            correlation_method
                        ),
                    )
                )

                st.plotly_chart(
                    figure,
                    use_container_width=True,
                )

                with st.expander(
                    "View correlation matrix"
                ):
                    st.dataframe(
                        correlation_matrix,
                        use_container_width=True,
                    )

                    st.download_button(
                        label=(
                            "Download correlation "
                            "matrix"
                        ),
                        data=dataframe_to_csv_bytes(
                            correlation_matrix,
                            include_index=True,
                        ),
                        file_name=(
                            "correlation_matrix.csv"
                        ),
                        mime="text/csv",
                    )

    # --------------------------------------------------------
    # CATEGORICAL FREQUENCY PLOT
    # --------------------------------------------------------

    elif (
        plot_type
        == "Categorical Frequency Plot"
    ):

        if not categorical_columns:
            st.warning(
                "No categorical variables are "
                "available."
            )

        else:
            categorical_variable = (
                st.selectbox(
                    "Select categorical variable",
                    categorical_columns,
                )
            )

            figure, frequency_table = (
                create_frequency_plot(
                    data=analysis_df,
                    variable=(
                        categorical_variable
                    ),
                )
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

            st.dataframe(
                frequency_table,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                label="Download frequency table",
                data=dataframe_to_csv_bytes(
                    frequency_table
                ),
                file_name=(
                    f"{categorical_variable}"
                    "_frequency_table.csv"
                ),
                mime="text/csv",
            )

    with st.expander(
        "View analysis dataset"
    ):
        st.dataframe(
            analysis_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Download analysis dataset",
            data=dataframe_to_csv_bytes(
                analysis_df
            ),
            file_name=(
                f"{analysis_level.lower()}"
                "_level_analysis.csv"
            ),
            mime="text/csv",
        )


# ============================================================
# SURVIVAL ANALYSIS
# ============================================================

elif analysis_type == "Survival Analysis":

    st.header(
        "Kaplan–Meier Survival Analysis"
    )

    st.write(
        """
        Compare overall survival between patients or samples
        classified into low- and high-TMB groups.
        Patient-level analysis is the recommended default
        because each patient contributes one independent
        survival observation.
        """
    )

    survival_level = st.sidebar.selectbox(
        "Survival analysis level",
        [
            "Patient",
            "Sample",
        ],
    )

    tmb_aggregation = "mean"

    if survival_level == "Patient":
        tmb_aggregation = (
            st.sidebar.selectbox(
                "Patient TMB aggregation",
                [
                    "mean",
                    "median",
                    "min",
                    "max",
                ],
                format_func=lambda value: (
                    value.title()
                ),
            )
        )

    show_confidence_interval = (
        st.sidebar.checkbox(
            "Show 95% confidence intervals",
            value=True,
        )
    )

    survival_df = prepare_survival_data(
        data=df,
        analysis_level=survival_level,
        tmb_aggregation=tmb_aggregation,
    )

    if survival_df.empty:
        st.error(
            "No complete observations are "
            "available for survival analysis."
        )

        st.stop()

    tmb_method = st.sidebar.selectbox(
        "TMB grouping method",
        [
            "Median",
            "Custom Cutoff",
        ],
    )

    median_tmb = float(
        survival_df[TMB].median()
    )

    if tmb_method == "Median":
        tmb_cutoff = median_tmb

    else:
        tmb_cutoff = st.sidebar.number_input(
            "TMB cutoff",
            min_value=0.0,
            value=median_tmb,
            step=0.1,
            format="%.3f",
        )

    survival_df = assign_binary_tmb_groups(
        survival_data=survival_df,
        cutoff=tmb_cutoff,
    )

    if survival_level == "Sample":
        st.warning(
            """
            Sample-level survival analysis is exploratory.
            Patients with multiple tumor samples may contribute
            more than one survival observation.
            """
        )

    else:
        st.info(
            f"Patient-level survival analysis uses "
            f"{tmb_aggregation} TMB aggregation."
        )

    st.metric(
        "TMB cutoff",
        f"{tmb_cutoff:.3f}",
    )

    st.caption(
        """
        TMB values greater than the cutoff are classified as
        High TMB. Values equal to or below the cutoff are
        classified as Low TMB.
        """
    )

    group_summary = (
        survival_df
        .groupby(
            "TMB Group",
            as_index=False,
        )
        .agg(
            Observations=(
                "Patient ID",
                "count",
            ),
            Deaths=(
                "Event",
                "sum",
            ),
            Median_TMB=(
                TMB,
                "median",
            ),
            Median_Survival_Time=(
                "Overall Survival (Months)",
                "median",
            ),
        )
    )

    group_summary["Censored"] = (
        group_summary["Observations"]
        - group_summary["Deaths"]
    )

    st.subheader("TMB Group Summary")

    st.dataframe(
        group_summary,
        use_container_width=True,
        hide_index=True,
    )

    group_names = set(
        survival_df[
            "TMB Group"
        ].dropna()
    )

    required_groups = {
        "High TMB",
        "Low TMB",
    }

    if not required_groups.issubset(
        group_names
    ):
        st.error(
            """
            The selected cutoff does not create both a high-TMB
            and low-TMB group. Select a cutoff within the
            observed TMB range.
            """
        )

        st.stop()

    try:
        survival_results = (
            run_binary_survival_analysis(
                data=survival_df,
                show_confidence_interval=(
                    show_confidence_interval
                ),
            )
        )

    except ValueError as error:
        st.error(str(error))
        st.stop()

    st.plotly_chart(
        survival_results.figure,
        use_container_width=True,
    )

    st.subheader(
        "Survival Analysis Results"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Observations",
            len(survival_df),
        )

    with col2:
        st.metric(
            "Log-rank statistic",
            (
                f"{survival_results."
                f"test_statistic:.3f}"
            ),
        )

    with col3:
        st.metric(
            "Log-rank p-value",
            (
                f"{survival_results."
                f"p_value:.4f}"
            ),
        )

    if survival_results.p_value < 0.05:
        st.success(
            """
            The log-rank test detected a statistically
            significant difference between the survival
            distributions at an alpha level of 0.05.
            """
        )

    else:
        st.info(
            """
            The log-rank test did not detect a statistically
            significant difference between the survival
            distributions at an alpha level of 0.05.
            This does not prove that the groups have identical
            survival, particularly given the small cohort.
            """
        )

    st.subheader(
        "Median Survival Estimates"
    )

    st.dataframe(
        survival_results.summary_table,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download survival summary",
        data=dataframe_to_csv_bytes(
            survival_results.summary_table
        ),
        file_name="survival_summary.csv",
        mime="text/csv",
    )

    with st.expander(
        "View survival analysis dataset"
    ):
        st.dataframe(
            survival_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label=(
                "Download survival analysis "
                "dataset"
            ),
            data=dataframe_to_csv_bytes(
                survival_df
            ),
            file_name=(
                "survival_analysis_dataset.csv"
            ),
            mime="text/csv",
        )