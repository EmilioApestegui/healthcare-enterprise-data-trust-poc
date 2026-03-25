from __future__ import annotations

import pandas as pd
import streamlit as st

from healthcare_enterprise_data_trust_poc.config import WORKBOOK_PATH, export_paths
from healthcare_enterprise_data_trust_poc.db import (
    app_engine,
    export_summary_to_desktop,
    get_adoption,
    get_before_state,
    get_dq_results,
    get_feed_monitor,
    get_incidents,
    get_issue_log,
    get_kpi_registry,
    load_workbook_to_postgres,
    run_certified_pipeline,
    test_connection,
)

st.set_page_config(page_title="Healthcare Enterprise Data Trust Workbench", layout="wide")

if "engine" not in st.session_state:
    st.session_state.engine = None
if "summary_df" not in st.session_state:
    st.session_state.summary_df = None


def connect_app_engine():
    engine = app_engine()
    test_connection(engine)

    tables = pd.read_sql(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'",
        engine
    )

    if len(tables) == 0:
        load_workbook_to_postgres(engine)

    return engine


def certification_badge(status: str) -> str:
    mapping = {
        "Certified": "✅ Certified",
        "Pending": "⚠️ Pending",
        "Pending Review": "⚠️ Pending Review",
        "Not Trusted": "❌ Not Trusted",
    }
    return mapping.get(status, status)


st.title("Healthcare Enterprise Data Trust Workbench")
st.caption("A static PoC showing how governance, lineage, data quality, and adoption create trusted healthcare analytics.")

with st.sidebar:
    st.subheader("Application")
    st.success("Railway auto-connect enabled")
    st.write("Sample workbook")
    st.code(str(WORKBOOK_PATH))

    paths = export_paths()
    st.write("Export paths")
    st.code(f'Excel: {paths["xlsx"]}\nCSV: {paths["csv"]}')

    if st.button("Connect app", use_container_width=True):
        try:
            st.session_state.engine = connect_app_engine()
            st.success("Connected to application database.")
        except Exception as exc:
            st.error(str(exc))

    if st.button("Reload static sample data", use_container_width=True):
        try:
            engine = connect_app_engine()
            loaded = load_workbook_to_postgres(engine, WORKBOOK_PATH)
            st.session_state.engine = engine
            st.success("Reloaded workbook tables into Postgres.")
            st.json(loaded)
        except Exception as exc:
            st.error(str(exc))

if st.session_state.engine is None:
    try:
        st.session_state.engine = connect_app_engine()
    except Exception as exc:
        st.error(f"Database connection failed: {exc}")
        st.stop()

engine = st.session_state.engine

before_df = get_before_state(engine)
registry_df = get_kpi_registry(engine)
feed_df = get_feed_monitor(engine)
incidents_df = get_incidents(engine)
dq_df = get_dq_results(engine)
issue_df = get_issue_log(engine)
adoption_df = get_adoption(engine)

tabs = st.tabs([
    "1) Problem / Before State",
    "2) Governance & Certification",
    "3) Integration & Lineage",
    "4) Data Quality",
    "5) Executive View",
    "6) Adoption & Value",
])

with tabs[0]:
    st.subheader("Why clinical and finance leaders do not trust the numbers")
    c1, c2, c3 = st.columns(3)
    if not before_df.empty:
        spread_value = float(before_df["spread"].iloc[0])
        c1.metric("Patient revenue spread across departments", f"${spread_value:,.0f}")
    c2.metric("Competing definitions", "3")
    c3.metric("Single trusted clinical KPI", "0 before certification")

    st.markdown("**Same KPI, different answers**")
    raw_submissions = pd.read_sql("SELECT * FROM kpi_submissions", engine)
    st.dataframe(raw_submissions, use_container_width=True, hide_index=True)

    if not before_df.empty:
        st.markdown("**Conflict summary**")
        st.dataframe(before_df, use_container_width=True, hide_index=True)

    st.warning("This is the pain point: Finance, Clinical Operations, and Revenue Cycle all report a different number because ownership, timing, and definitions are inconsistent.")

with tabs[1]:
    st.subheader("Governance turns clinical metrics into trusted products")
    trusted_count = int((registry_df["certification_status"] == "Certified").sum())
    pending_count = int((registry_df["certification_status"] == "Pending").sum())
    untrusted_count = int((registry_df["certification_status"] == "Not Trusted").sum())

    g1, g2, g3 = st.columns(3)
    g1.metric("Certified KPIs", trusted_count)
    g2.metric("Pending KPIs", pending_count)
    g3.metric("Untrusted KPIs", untrusted_count)

    show_registry = registry_df.copy()
    show_registry["certification_status"] = show_registry["certification_status"].map(certification_badge)
    st.dataframe(show_registry, use_container_width=True, hide_index=True)

    selected_kpi = st.selectbox("Inspect KPI", registry_df["kpi_name"].tolist())
    kpi_row = registry_df.loc[registry_df["kpi_name"] == selected_kpi].iloc[0]
    st.markdown(f"### {selected_kpi} — {certification_badge(kpi_row['certification_status'])}")
    d1, d2 = st.columns(2)
    with d1:
        st.write(f"**Definition**: {kpi_row['business_definition']}")
        st.write(f"**Owner**: {kpi_row['owner'] if str(kpi_row['owner']).strip() else 'Missing'}")
        st.write(f"**Data steward**: {kpi_row['data_steward']}")
    with d2:
        st.write(f"**Source object**: {kpi_row['source_object']}")
        st.write(f"**Consumer group**: {kpi_row['consumer_group']}")
        st.write(f"**Last validated**: {pd.to_datetime(kpi_row['last_validated_date']).date()}")
    st.info(kpi_row["certification_reason"])

with tabs[2]:
    st.subheader("EMR integration reliability and lineage")
    i1, i2, i3 = st.columns(3)
    i1.metric("Open incidents", int((incidents_df["status"] == "Open").sum()))
    i2.metric("Late / failed interfaces", int(feed_df["status"].isin(["Late", "Failed"]).sum()))
    i3.metric("Critical business dependency", "Claims feed")

    st.markdown("**Interface health**")
    st.dataframe(feed_df, use_container_width=True, hide_index=True)

    st.markdown("**Incident log**")
    st.dataframe(incidents_df, use_container_width=True, hide_index=True)

    st.markdown("**Lineage**")
    st.graphviz_chart(
        """
        digraph {
            rankdir=LR;
            node [shape=box, style="rounded,filled", fillcolor="#EDF3FF"];
            EPIC [label="Epic ADT"];
            CLAIMS [label="Claims feed"];
            LAB [label="Lab interface"];
            PLAN [label="Budget plan"];
            STAGE [label="Standardized source tables"];
            CERT [label="Certified clinical summary"];
            KPI [label="Certified KPIs"];
            EXEC [label="Clinical operations dashboard"];
            EPIC -> STAGE;
            CLAIMS -> STAGE;
            LAB -> STAGE;
            PLAN -> STAGE;
            STAGE -> CERT;
            CERT -> KPI;
            KPI -> EXEC;
        }
        """
    )

with tabs[3]:
    st.subheader("Clinical data quality makes trust measurable")
    avg_score = float(dq_df["quality_score"].mean())
    fail_count = int((dq_df["status"] == "Fail").sum())
    pass_count = int((dq_df["status"] == "Pass").sum())

    q1, q2, q3 = st.columns(3)
    q1.metric("Average DQ score", f"{avg_score:.1f}")
    q2.metric("Passing checks", pass_count)
    q3.metric("Failing checks", fail_count)

    st.dataframe(dq_df, use_container_width=True, hide_index=True)
    st.markdown("**Open issues tracked like a real operating program**")
    st.dataframe(issue_df, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Executive view: trusted healthcare analytics")

    actuals = pd.read_sql(
        "SELECT DISTINCT month_start, region, product_category FROM sales_actuals ORDER BY month_start, region, product_category",
        engine,
        parse_dates=["month_start"]
    )
    months = ["All"] + [d.strftime("%Y-%m-%d") for d in sorted(actuals["month_start"].dropna().unique())]
    regions = ["All"] + sorted(actuals["region"].dropna().unique().tolist())
    products = ["All"] + sorted(actuals["product_category"].dropna().unique().tolist())

    f1, f2, f3 = st.columns(3)
    start_month = f1.selectbox("Start month", months, index=0)
    region = f2.selectbox("Facility", regions, index=0)
    product = f3.selectbox("Service line", products, index=0)

    end_month = st.selectbox("End month", months, index=0)

    if st.button("Run trusted pipeline", type="primary", use_container_width=True):
        summary_df = run_certified_pipeline(engine)

        if start_month != "All":
            summary_df = summary_df[summary_df["month_start"].astype(str).str.startswith(start_month)]
        if end_month != "All":
            summary_df = summary_df[summary_df["month_start"].astype(str).str.startswith(end_month)]
        if region != "All":
            summary_df = summary_df[summary_df["region"] == region]
        if product != "All":
            summary_df = summary_df[summary_df["product_category"] == product]

        st.session_state.summary_df = summary_df

    if st.session_state.summary_df is not None and not st.session_state.summary_df.empty:
        summary_df = st.session_state.summary_df.copy()

        total_actual = float(summary_df["actual_revenue"].sum())
        total_plan = float(summary_df["plan_revenue"].fillna(0).sum())
        total_variance = float(summary_df["variance"].fillna(0).sum())

        variance_pct = (total_variance / total_plan) if total_plan else 0.0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Actual patient revenue", f"${total_actual:,.0f}")
        k2.metric("Budgeted revenue", f"${total_plan:,.0f}")
        k3.metric("Variance", f"${total_variance:,.0f}")
        k4.metric("Variance %", f"{variance_pct:.1%}")

        status_counts = summary_df["kpi_status"].value_counts().to_dict()

        st.write(
            f"Certified rows: {status_counts.get('Certified', 0)} | Pending review rows: {status_counts.get('Pending Review', 0)}"
        )

        month_chart = (
            summary_df
            .groupby("month_start", as_index=False)[["actual_revenue", "plan_revenue"]]
            .sum()
            .set_index("month_start")
        )
        st.line_chart(month_chart)

        variance_by_region = (
            summary_df
            .groupby("region", as_index=False)["variance"]
            .sum()
            .set_index("region")
        )
        st.bar_chart(variance_by_region)

        st.markdown("**Certified summary**")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        if st.button("Export certified summary", use_container_width=True):
            try:
                paths = export_summary_to_desktop(summary_df)
                st.success(f'Excel exported to {paths["xlsx"]}')
                st.success(f'CSV exported to {paths["csv"]}')
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info("Run the trusted pipeline to populate the executive view.")

with tabs[5]:
    st.subheader("Adoption and business value")
    latest = adoption_df.sort_values("month_start").iloc[-1]
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Active users", int(latest["active_users"]))
    a2.metric("Trusted KPIs", int(latest["trusted_kpis"]))
    a3.metric("Manual reports eliminated", int(latest["manual_reports_eliminated"]))
    a4.metric("Hours saved / week", int(latest["hours_saved_per_week"]))

    st.line_chart(adoption_df.set_index("month_start")[["active_users", "trusted_kpis", "hours_saved_per_week"]])
    st.dataframe(adoption_df, use_container_width=True, hide_index=True)
