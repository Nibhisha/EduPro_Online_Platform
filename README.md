[README.md](https://github.com/user-attachments/files/28997106/README.md)
# EduPro Course Demand and Revenue Forecasting Dashboard

## Project Overview

This project develops a predictive-style analytics dashboard for EduPro, an online learning platform.  
The dashboard helps analyze course demand, forecast revenue potential, compare category-level performance, and support course planning decisions.

EduPro can use this analysis to answer key business questions such as:

- Which course categories generate the highest revenue?
- Which courses attract the most enrollments?
- How do price, duration, ratings, and instructor experience affect demand?
- What is the expected enrollment and revenue for a planned course?
- Which categories should EduPro prioritize for future growth?

## Problem Statement

EduPro currently lacks a structured forecasting and analytics framework for course demand and revenue planning.  
Without predictive intelligence, decisions around course launches, pricing, instructor allocation, and category expansion rely heavily on historical intuition.

This project introduces a data-driven dashboard to support proactive planning.

## Dataset

The project uses an Excel workbook containing four sheets:

- `Users`
- `Teachers`
- `Courses`
- `Transactions`

Main fields used include:

- CourseID
- CourseCategory
- CourseType
- CourseLevel
- CoursePrice
- CourseDuration
- CourseRating
- TeacherID
- Expertise
- YearsOfExperience
- TeacherRating
- TransactionDate
- Amount

## Key Features

### Executive Overview
- Total revenue
- Total enrollments
- Average revenue per course
- Top performing category
- Course, teacher, transaction, and user counts

### Demand Prediction
- Rule-based course enrollment prediction
- Inputs include course category, level, price, duration, course rating, instructor rating, and experience

### Revenue Forecasting
- Estimated course revenue
- Predicted enrollments
- Price and category-based revenue adjustment

### Category Analysis
- Revenue by category
- Enrollment by category
- Category revenue share
- Demand versus revenue comparison

### Feature Impact
- Correlation-based feature impact analysis
- Helps identify variables influencing enrollment and revenue

### Data Explorer
- Displays the processed modeling dataset
- Allows CSV download

## Tools and Technologies

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenPyXL

## Project Structure

```text
EduPro_GitHub_Project/
│
├── streamlit_app.py
├── EduPro Online Platform.xlsx
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run Locally

1. Clone the repository:

```bash
git clone <your-repository-link>
cd EduPro_GitHub_Project
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment

1. Upload all project files to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Select the GitHub repository.
4. Set the main file path as:

```text
streamlit_app.py
```

5. Deploy the app.

## Business Impact

This dashboard helps EduPro move from reactive reporting to proactive course planning.  
It supports better decisions in:

- Course launch planning
- Pricing strategy
- Instructor allocation
- Category expansion
- Revenue forecasting
- Demand estimation

## Author

**Nibhisha S. Kakrania**  
MBA - Business Analytics
