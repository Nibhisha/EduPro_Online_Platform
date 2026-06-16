import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="EduPro Demand & Revenue Forecasting",
    page_icon="📊",
    layout="wide"
)

st.title("📊 EduPro Course Demand & Revenue Forecasting Dashboard")
st.caption("Predictive-style business dashboard for course demand, revenue forecasting, and category-level planning.")

DATA_FILE = "EduPro Online Platform.xlsx"

@st.cache_data
def load_data():
    if not Path(DATA_FILE).exists():
        st.error("Please upload 'EduPro Online Platform.xlsx' in the same folder as this app.")
        st.stop()

    courses = pd.read_excel(DATA_FILE, sheet_name="Courses")
    teachers = pd.read_excel(DATA_FILE, sheet_name="Teachers")
    transactions = pd.read_excel(DATA_FILE, sheet_name="Transactions")
    users = pd.read_excel(DATA_FILE, sheet_name="Users")

    transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"], errors="coerce")
    return courses, teachers, transactions, users

courses, teachers, transactions, users = load_data()

@st.cache_data
def prepare_data(courses, teachers, transactions):
    txn_course = (
        transactions.groupby("CourseID")
        .agg(
            EnrollmentCount=("TransactionID", "count"),
            CourseRevenue=("Amount", "sum"),
            AvgTransactionAmount=("Amount", "mean"),
            UniqueLearners=("UserID", "nunique"),
            TeacherID=("TeacherID", lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0])
        )
        .reset_index()
    )

    df = courses.merge(txn_course, on="CourseID", how="left")
    df = df.merge(
        teachers[["TeacherID", "TeacherName", "Expertise", "YearsOfExperience", "TeacherRating"]],
        on="TeacherID",
        how="left"
    )

    for c in ["EnrollmentCount", "CourseRevenue", "AvgTransactionAmount", "UniqueLearners"]:
        df[c] = df[c].fillna(0)

    df["CourseRating"] = df["CourseRating"].fillna(df["CourseRating"].median())
    df["TeacherRating"] = df["TeacherRating"].fillna(df["TeacherRating"].median())
    df["YearsOfExperience"] = df["YearsOfExperience"].fillna(df["YearsOfExperience"].median())

    df["RevenuePerEnrollment"] = np.where(df["EnrollmentCount"] > 0, df["CourseRevenue"] / df["EnrollmentCount"], 0)

    df["PriceBand"] = pd.cut(
        df["CoursePrice"],
        bins=[-np.inf, 100, 300, np.inf],
        labels=["Low", "Medium", "High"]
    ).astype(str)

    df["DurationBucket"] = pd.cut(
        df["CourseDuration"],
        bins=[-np.inf, 10, 30, np.inf],
        labels=["Short", "Medium", "Long"]
    ).astype(str)

    df["ExperienceBucket"] = pd.cut(
        df["YearsOfExperience"],
        bins=[-np.inf, 5, 10, np.inf],
        labels=["0-5 Years", "6-10 Years", "10+ Years"]
    ).astype(str)

    df["ExpertiseCategoryMatch"] = (
        df["Expertise"].astype(str).str.lower().str.strip()
        == df["CourseCategory"].astype(str).str.lower().str.strip()
    ).astype(int)

    return df

df = prepare_data(courses, teachers, transactions)

def predict_enrollments(category, level, price, duration, course_rating, teacher_rating, experience, expertise_match):
    base = df["EnrollmentCount"].mean()

    category_avg = df.groupby("CourseCategory")["EnrollmentCount"].mean().to_dict()
    level_avg = df.groupby("CourseLevel")["EnrollmentCount"].mean().to_dict()

    category_factor = category_avg.get(category, base) / base if base else 1
    level_factor = level_avg.get(level, base) / base if base else 1

    price_factor = 1.10 if price < 100 else 1.00 if price <= 300 else 0.90
    duration_factor = 1.05 if duration <= 10 else 1.00 if duration <= 30 else 0.95
    rating_factor = 0.85 + (course_rating / 5) * 0.35
    teacher_factor = 0.90 + (teacher_rating / 5) * 0.20
    experience_factor = 1.05 if experience >= 10 else 1.00 if experience >= 5 else 0.95
    match_factor = 1.05 if expertise_match else 0.98

    return max(0, base * category_factor * level_factor * price_factor * duration_factor * rating_factor * teacher_factor * experience_factor * match_factor)

def predict_revenue(category, level, price, duration, course_rating, teacher_rating, experience, expertise_match):
    enrollments = predict_enrollments(category, level, price, duration, course_rating, teacher_rating, experience, expertise_match)
    category_rpe = df.groupby("CourseCategory")["RevenuePerEnrollment"].mean().to_dict().get(
        category, df["RevenuePerEnrollment"].mean()
    )
    expected_amount = (0.60 * price) + (0.40 * category_rpe)
    return max(0, enrollments * expected_amount)

with st.sidebar:
    st.header("Filters")
    categories = sorted(df["CourseCategory"].dropna().unique())
    levels = sorted(df["CourseLevel"].dropna().unique())

    selected_categories = st.multiselect("Course Category", categories, default=categories)
    selected_levels = st.multiselect("Course Level", levels, default=levels)

    price_range = st.slider(
        "Course Price Range",
        float(df["CoursePrice"].min()),
        float(df["CoursePrice"].max()),
        (float(df["CoursePrice"].min()), float(df["CoursePrice"].max()))
    )

filtered = df[
    df["CourseCategory"].isin(selected_categories)
    & df["CourseLevel"].isin(selected_levels)
    & df["CoursePrice"].between(price_range[0], price_range[1])
].copy()

tabs = st.tabs([
    "Executive Overview",
    "Demand Prediction",
    "Revenue Forecasting",
    "Category Analysis",
    "Feature Impact",
    "Data Explorer"
])

with tabs[0]:
    st.subheader("Executive Overview")

    total_revenue = filtered["CourseRevenue"].sum()
    total_enrollments = filtered["EnrollmentCount"].sum()
    avg_revenue = filtered["CourseRevenue"].mean() if len(filtered) else 0
    top_category = filtered.groupby("CourseCategory")["CourseRevenue"].sum().idxmax() if len(filtered) else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.0f}")
    c2.metric("Total Enrollments", f"{total_enrollments:,.0f}")
    c3.metric("Avg Revenue / Course", f"${avg_revenue:,.0f}")
    c4.metric("Top Category", top_category)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total Courses", f"{len(filtered):,.0f}")
    c6.metric("Total Teachers", f"{teachers['TeacherID'].nunique():,.0f}")
    c7.metric("Total Transactions", f"{transactions['TransactionID'].nunique():,.0f}")
    c8.metric("Total Users", f"{users['UserID'].nunique():,.0f}")

    col1, col2 = st.columns(2)

    with col1:
        revenue_by_cat = filtered.groupby("CourseCategory", as_index=False)["CourseRevenue"].sum().sort_values("CourseRevenue", ascending=False)
        st.plotly_chart(
            px.bar(revenue_by_cat, x="CourseCategory", y="CourseRevenue", title="Revenue by Course Category", text_auto=".2s"),
            use_container_width=True
        )

    with col2:
        enrollment_by_cat = filtered.groupby("CourseCategory", as_index=False)["EnrollmentCount"].sum().sort_values("EnrollmentCount", ascending=False)
        st.plotly_chart(
            px.bar(enrollment_by_cat, x="CourseCategory", y="EnrollmentCount", title="Enrollments by Course Category", text_auto=".2s"),
            use_container_width=True
        )

    st.plotly_chart(
        px.scatter(
            filtered,
            x="EnrollmentCount",
            y="CourseRevenue",
            color="CourseCategory",
            size="CoursePrice",
            hover_data=["CourseName", "CourseLevel", "CourseRating", "TeacherRating"],
            title="Course Revenue vs Enrollment Count"
        ),
        use_container_width=True
    )

with tabs[1]:
    st.subheader("Course Demand Prediction")

    st.info("This version uses business-rule forecasting so it works in Streamlit Editor without scikit-learn.")

    col1, col2, col3 = st.columns(3)

    with col1:
        category = st.selectbox("Course Category", categories)
        level = st.selectbox("Course Level", levels)
        course_type = st.selectbox("Course Type", sorted(df["CourseType"].dropna().unique()))

    with col2:
        price = st.slider("Course Price", float(df["CoursePrice"].min()), float(df["CoursePrice"].max()), float(df["CoursePrice"].median()))
        duration = st.slider("Course Duration", float(df["CourseDuration"].min()), float(df["CourseDuration"].max()), float(df["CourseDuration"].median()))
        course_rating = st.slider("Course Rating", 1.0, 5.0, float(df["CourseRating"].median()), 0.1)

    with col3:
        expertise = st.selectbox("Instructor Expertise", sorted(df["Expertise"].astype(str).dropna().unique()))
        experience = st.slider("Instructor Experience", float(df["YearsOfExperience"].min()), float(df["YearsOfExperience"].max()), float(df["YearsOfExperience"].median()))
        teacher_rating = st.slider("Teacher Rating", 1.0, 5.0, float(df["TeacherRating"].median()), 0.1)

    expertise_match = str(expertise).lower().strip() == str(category).lower().strip()
    predicted = predict_enrollments(category, level, price, duration, course_rating, teacher_rating, experience, expertise_match)

    st.metric("Predicted Enrollment Count", f"{predicted:,.0f}")

with tabs[2]:
    st.subheader("Revenue Forecasting")

    col1, col2, col3 = st.columns(3)

    with col1:
        r_category = st.selectbox("Course Category", categories, key="rev_cat")
        r_level = st.selectbox("Course Level", levels, key="rev_level")
        r_course_type = st.selectbox("Course Type", sorted(df["CourseType"].dropna().unique()), key="rev_type")

    with col2:
        r_price = st.slider("Course Price", float(df["CoursePrice"].min()), float(df["CoursePrice"].max()), float(df["CoursePrice"].median()), key="rev_price")
        r_duration = st.slider("Course Duration", float(df["CourseDuration"].min()), float(df["CourseDuration"].max()), float(df["CourseDuration"].median()), key="rev_duration")
        r_course_rating = st.slider("Course Rating", 1.0, 5.0, float(df["CourseRating"].median()), 0.1, key="rev_rating")

    with col3:
        r_expertise = st.selectbox("Instructor Expertise", sorted(df["Expertise"].astype(str).dropna().unique()), key="rev_expertise")
        r_experience = st.slider("Instructor Experience", float(df["YearsOfExperience"].min()), float(df["YearsOfExperience"].max()), float(df["YearsOfExperience"].median()), key="rev_experience")
        r_teacher_rating = st.slider("Teacher Rating", 1.0, 5.0, float(df["TeacherRating"].median()), 0.1, key="rev_teacher_rating")

    r_expertise_match = str(r_expertise).lower().strip() == str(r_category).lower().strip()

    predicted_enrollments = predict_enrollments(
        r_category, r_level, r_price, r_duration, r_course_rating, r_teacher_rating, r_experience, r_expertise_match
    )

    predicted_revenue = predict_revenue(
        r_category, r_level, r_price, r_duration, r_course_rating, r_teacher_rating, r_experience, r_expertise_match
    )

    c1, c2 = st.columns(2)
    c1.metric("Predicted Revenue", f"${predicted_revenue:,.0f}")
    c2.metric("Predicted Enrollments", f"{predicted_enrollments:,.0f}")

with tabs[3]:
    st.subheader("Category-Level Analysis")

    category_table = (
        df.groupby("CourseCategory")
        .agg(
            Courses=("CourseID", "count"),
            TotalEnrollments=("EnrollmentCount", "sum"),
            TotalRevenue=("CourseRevenue", "sum"),
            AvgCourseRevenue=("CourseRevenue", "mean"),
            AvgCoursePrice=("CoursePrice", "mean"),
            AvgCourseRating=("CourseRating", "mean"),
            AvgTeacherRating=("TeacherRating", "mean")
        )
        .reset_index()
        .sort_values("TotalRevenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            px.pie(category_table, names="CourseCategory", values="TotalRevenue", title="Category Revenue Share"),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            px.scatter(
                category_table,
                x="TotalEnrollments",
                y="TotalRevenue",
                color="CourseCategory",
                size="Courses",
                title="Category Demand vs Revenue",
                hover_data=["AvgCourseRevenue", "AvgCoursePrice", "AvgCourseRating", "AvgTeacherRating"]
            ),
            use_container_width=True
        )

    st.dataframe(category_table, use_container_width=True)

with tabs[4]:
    st.subheader("Feature Impact")

    numeric_cols = [
        "CoursePrice",
        "CourseDuration",
        "CourseRating",
        "YearsOfExperience",
        "TeacherRating",
        "ExpertiseCategoryMatch",
        "EnrollmentCount",
        "CourseRevenue"
    ]

    target = st.selectbox("Target Variable", ["EnrollmentCount", "CourseRevenue"])
    corr = df[numeric_cols].corr(numeric_only=True)

    impact = (
        corr[target]
        .drop(labels=[target])
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    impact.columns = ["Feature", "Absolute Correlation"]

    st.plotly_chart(
        px.bar(
            impact.sort_values("Absolute Correlation"),
            x="Absolute Correlation",
            y="Feature",
            orientation="h",
            title=f"Feature Impact Proxy for {target}"
        ),
        use_container_width=True
    )

    st.dataframe(impact, use_container_width=True)

with tabs[5]:
    st.subheader("Data Explorer")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Processed Modeling Dataset",
        data=csv,
        file_name="edupro_modeling_dataset.csv",
        mime="text/csv"
    )

st.divider()
st.caption("EduPro Dashboard | Built with Streamlit, Pandas, NumPy, and Plotly")
