import streamlit as st
import streamlit_analytics
from datetime import datetime
import altair as alt
import pandas as pd


# Initialize the streamlit-analytics tracker
#streamlit_analytics.init()

def show_results(counts, reset_callback, unsafe_password=None):
    """Show analytics results in Streamlit, asking for a password if given."""

    # Show header.
    st.title("Analytics Dashboard")

    # Ask for password if one was given.
    show = True
    if unsafe_password is not None:
        password_input = st.text_input(
            "Enter password to show results", type="password"
        )
        if password_input != unsafe_password:
            show = False
            if len(password_input) > 0:
                st.write("Nope, that's not correct ☝️")

    # Show traffic.
    st.header("Traffic")
    st.write(f"since {counts['start_time']}")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Pageviews",
        counts["total_pageviews"],
        help="Every time a user (re-)loads the site.",
    )
    col2.metric(
        "Script runs",
        counts["total_script_runs"],
        help="Every time Streamlit reruns upon changes or interactions.",
    )
    col3.metric(
        "Time spent",
        utils.format_seconds(counts["total_time_seconds"]),
        help="Time from initial page load to last widget interaction, summed over all users.",
    )
    st.write("")

    # Plot altair chart with pageviews and script runs.
    try:
        alt.themes.enable("streamlit")
    except:
        pass  # probably an old Streamlit version
    df = pd.DataFrame(counts["per_day"])
    base = alt.Chart(df).encode(
        x=alt.X("monthdate(days):O", axis=alt.Axis(title="", grid=True))
    )
    line1 = base.mark_line(point=True, stroke="#5276A7").encode(
        alt.Y(
            "pageviews:Q",
            axis=alt.Axis(
                titleColor="#5276A7",
                tickColor="#5276A7",
                labelColor="#5276A7",
                format=".0f",
                tickMinStep=1,
            ),
            scale=alt.Scale(domain=(0, df["pageviews"].max() + 1)),
        )
    )
    line2 = base.mark_line(point=True, stroke="#57A44C").encode(
        alt.Y(
            "script_runs:Q",
            axis=alt.Axis(
                title="script runs",
                titleColor="#57A44C",
                tickColor="#57A44C",
                labelColor="#57A44C",
                format=".0f",
                tickMinStep=1,
            ),
        )
    )
    layer = (
        alt.layer(line1, line2)
        .resolve_scale(y="independent")
        .configure_axis(titleFontSize=15, labelFontSize=12, titlePadding=10)
    )
    st.altair_chart(layer, use_container_width=True)

    # Show widget interactions.
    st.header("Widget interactions")
    st.markdown(
        """
        Find out how users interacted with your app!
        <br>
        Numbers indicate how often a button was clicked, how often a specific text 
        input was given, ...
        <br>
        <sub>Note: Numbers only increase if the state of the widget
        changes, not every time Streamlit runs the script.</sub>
        """,
        unsafe_allow_html=True,
    )
    st.write(counts["widgets"])

# Initialize or load counts data
counts = {
    "total_script_runs": 0,
    "total_time_seconds": 0,
    "total_pageviews": 0,
    "per_day": {"days": [], "pageviews": [], "script_runs": []},
}

if "last_time" not in st.session_state:
    st.session_state.last_time = datetime.now()  # Corrected instantiation

if "user_tracked" not in st.session_state:
    st.session_state.user_tracked = False

def _track_user():
    """Track individual pageviews by storing user id to session state."""
    today = str(datetime.date.today())
    if counts["per_day"]["days"][-1] != today:
        # Insert 0 for all days between today and the last entry.
        while counts["per_day"]["days"][-1] != today:
            counts["per_day"]["days"].append(today)
            counts["per_day"]["pageviews"].append(0)
            counts["per_day"]["script_runs"].append(0)
    counts["total_script_runs"] += 1
    counts["per_day"]["script_runs"][-1] += 1
    now = datetime.now()  # Corrected instantiation
    counts["total_time_seconds"] += (now - st.session_state.last_time).total_seconds()
    st.session_state.last_time = now
    if not st.session_state.user_tracked:
        st.session_state.user_tracked = True
        counts["total_pageviews"] += 1
        counts["per_day"]["pageviews"][-1] += 1

# Create an Altair chart for tracking user data
def user_tracking_chart(counts):
    df = pd.DataFrame(counts["per_day"])
    chart = alt.Chart(df).encode(
        x=alt.X("days:T", title="Date"),
        y=alt.Y("pageviews:Q", title="Pageviews"),
        color=alt.Color("type:N", title="Metric"),
    ).properties(
        width=600,
        height=400,
        title="User Tracking Data",
    )
    
    pageviews_line = chart.mark_line().encode(
        y=alt.Y("pageviews:Q", title="Pageviews"),
    )

    script_runs_line = chart.mark_line().encode(
        y=alt.Y("script_runs:Q", title="Script Runs"),
    )

    return (pageviews_line + script_runs_line)

# Run the Streamlit app and track analytics
if __name__ == "__main__":
    # Track analytics for the entire Streamlit app
    with streamlit_analytics.track():
        import requests
        import streamlit as st
        import numpy as np
        import pandas as pd
        import plotly.graph_objects as go
        from streamlit_lottie import st_lottie
        import calendar
        
        
        st.write("A tool that helps you estimate your monthly loan payments and the total interest you will pay over the life of the loan. ")
        st.sidebar.subheader("Input your loan details below:")
        
        # Input fields for loan details
        loan_amount = st.sidebar.number_input("Loan Amount (R)", value=100000, step=1000)
        interest_rate = st.sidebar.number_input("Interest Rate (%)", value=11.75, step=0.1)
        loan_term = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)
        
        # Dropdown for selecting the start month
        start_month_options = [
            f"{calendar.month_name[month]} ({year})"
            for year in range(2023, 2025)
            for month in range(1, 13)
        ]
        start_month = st.sidebar.selectbox("Select Start Month", start_month_options, index=0)
        st.sidebar.markdown("---")
        
        # Extract the selected start month and year
        selected_start_month, selected_start_year_with_parentheses = start_month.split()
        selected_start_month = list(calendar.month_name).index(selected_start_month)
        selected_start_year = int(selected_start_year_with_parentheses.strip("()"))
        
        # Calculate monthly payment
        monthly_interest_rate = interest_rate / 12 / 100
        num_payments = loan_term * 12
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)
        
        # Calculate amortization schedule
        amortization_schedule = []
        
        remaining_principal = loan_amount
        for month in range(1, num_payments + 1):
            interest_payment = remaining_principal * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment
            amortization_schedule.append([month, monthly_payment, principal_payment, interest_payment, remaining_principal])
        
        # Create a DataFrame for the amortization schedule
        amortization_df = pd.DataFrame(amortization_schedule, columns=['Month', 'Monthly Payment', 'Principal Payment', 'Interest Payment', 'Remaining Principal'])
        
        # Calculate payoff date based on the last date in the amortization table
        last_month = amortization_df.iloc[-1]['Month']
        payoff_date = pd.to_datetime(f"{selected_start_year}-{selected_start_month}-01") + pd.DateOffset(months=last_month)
        
        
        st.subheader("Loan Summary:")
        # Create a summary box
        st.markdown('<div class="summary-box-container pos-sticky box-shadow-1 bg-white rounded-md p-6 mx-4">', unsafe_allow_html=True)
        
        
        # Place the columns within the container
        col1, col2, col3, col4 = st.columns(4)
        
        # Loan Amount
        with col1:
            st.markdown(f"""
                <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Loan Amount</p>
                <span style="font-size: 20px; color: #000;">R{loan_amount:,.2f}</span>
            """, unsafe_allow_html=True)
          
        # Total interest paid
        with col2:
            st.markdown(f"""
                <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Total interest paid</p>
                <span style="font-size: 20px; color: #000;">R{amortization_df['Interest Payment'].sum():,.2f}</span>
            """, unsafe_allow_html=True)
        
        # Monthly Payment
        with col3:
            st.markdown(f"""
                <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Monthly payment</p>
                <span style="font-size: 20px; color: #000;">R{monthly_payment:,.2f}</span>
            """, unsafe_allow_html=True)
        
        # Payoff date
        with col4:
            st.markdown(f"""
                <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Payoff date</p>
                <span style="font-size: 20px; color: #000;">{payoff_date.strftime('%b %Y')}</span>
            """, unsafe_allow_html=True)
        
        # Close the summary box
        st.markdown('</div>', unsafe_allow_html=True)
        
        
        # Create an empty DataFrame with column names
        amortization_df = pd.DataFrame(columns=["Month", "Payment", "Principal", "Interest", "Balance"])
        
        balance = loan_amount
        total_interest_paid = 0  # Initialize total interest paid
        
        # Initialize an empty list to store row data
        row_data_list = []
        
        for month in range(1, num_payments + 1):
            interest_payment = balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
            total_interest_paid += interest_payment  # Accumulate interest payments
        
            # Append the data to the list with thousand separators
            row_data = {
                "Month": f"{calendar.month_name[selected_start_month]} {selected_start_year}",
                "Payment": f"R{monthly_payment:,.2f}",
                "Principal": f"R{principal_payment:,.2f}",
                "Interest": f"R{interest_payment:,.2f}",
                "Balance": f"R{balance:,.2f}",
            }
            row_data_list.append(row_data)
        
            # Update the selected month and year
            selected_start_month += 1
            if selected_start_month > 12:
                selected_start_month = 1
                selected_start_year += 1
        
        # Create a DataFrame from the list of row data
        amortization_df = pd.DataFrame(row_data_list)
        
        # Update the selected month and year
        selected_start_month += 1
        if selected_start_month > 12:
            selected_start_month = 1
            selected_start_year += 1
        
        selected_month = list(amortization_df["Month"])
        
        if st.checkbox("Show Amortization Table"):    
            st.write(f"Below is the amortization schedule for a R{loan_amount:,} home loan, for {loan_term} years with a {interest_rate}% fixed rate: ")
            st.dataframe(amortization_df, hide_index=True, use_container_width=True)
        st.markdown("---")
        
        
        # Create a function to calculate the new total payment
        def calculate_new_total_payment(
            loan_amount, new_interest_rate, new_loan_term, new_extra_payment
        ):
            new_monthly_interest_rate = new_interest_rate / 12 / 100
            new_num_payments = new_loan_term * 12
            new_monthly_payment = (
                loan_amount
                * new_monthly_interest_rate
                * (1 + new_monthly_interest_rate) ** new_num_payments
            ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
            
            if new_extra_payment > 0:
                return new_monthly_payment + new_extra_payment
            else:
                return new_monthly_payment
        
        # Sidebar inputs
        st.sidebar.subheader('Change Variables below:')
        new_interest_rate = st.sidebar.number_input("New Interest Rate (%)", value=interest_rate, step=0.1)
        new_loan_term = st.sidebar.number_input("New Loan Term (Years)", value=loan_term, step=1)
        new_extra_payment = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)
        
        # Initialize new_total_payment with the original payment
        new_total_payment = monthly_payment
        
        # Initialize new_loan_term_difference with a default value
        new_loan_term_difference = 0
        
        # Create an empty container to hold the summary box
        summary_container = st.empty()
        
        # Function to calculate loan term based on changes
        def calculate_loan_term(loan_amount, interest_rate, monthly_payment, extra_payment=0):
            monthly_interest_rate = interest_rate / 12 / 100
            unpaid_balance = loan_amount
            months_elapsed = 0
        
            while unpaid_balance > 0:
                interest_payment = unpaid_balance * monthly_interest_rate
                principal_payment = monthly_payment - interest_payment - extra_payment
                unpaid_balance -= principal_payment
                months_elapsed += 1
        
            return months_elapsed
        
        # Initialize new_total_payment with the original payment
        new_total_payment = monthly_payment
        
        # Calculate the impact of changes when the "Calculate" button is clicked
        if st.sidebar.button("Calculate"):
            new_monthly_interest_rate = new_interest_rate / 12 / 100
            new_num_payments = calculate_loan_term(loan_amount, new_interest_rate, new_total_payment, new_extra_payment)
        
            if new_extra_payment > 0:
                new_monthly_payment = (
                    loan_amount
                    * new_monthly_interest_rate
                    * (1 + new_monthly_interest_rate) ** new_num_payments
                ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
                new_total_payment = new_monthly_payment + new_extra_payment
        
            if new_monthly_interest_rate != interest_rate / 12 / 100:
                new_monthly_payment_with_interest_rate = (
                    loan_amount
                    * new_monthly_interest_rate
                    * (1 + new_monthly_interest_rate) ** new_num_payments
                ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
        
            # Calculate the payment difference
            payment_difference = monthly_payment - new_total_payment
        
            # Calculate the loan term difference for changes in new_extra_payment
            original_num_payments = calculate_loan_term(loan_amount, interest_rate, monthly_payment)
            new_loan_term_difference = new_num_payments - original_num_payments
        
            
            # Create the summary box
            summary_container.markdown('<div class="summary-box-container pos-sticky box-shadow-1 bg-white rounded-md p-6 mx-4">', unsafe_allow_html=True)
        
            # Place the columns within the container
            col1, col2, col3 = st.columns(3)
        
            # New Monthly Payment
            with col1:
                st.markdown(f"""
                    <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">New Monthly payment</p>
                    <span style="font-size: 20px; color: #000;">R{new_total_payment:.2f}</span>
                """, unsafe_allow_html=True)
              
            # Payment Difference
            with col2:
                st.markdown(f"""
                    <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Payment Difference</p>
                    <span style="font-size: 20px; color: #000;">R{payment_difference:.2f}</span>
                """, unsafe_allow_html=True)
        
            # New Payoff date
            with col3:
                st.markdown(f"""
                    <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Loan Term Difference</p>
                    <span style="font-size: 20px; color: #000;">{abs(new_loan_term_difference) / 12} years {'shorter' if new_loan_term_difference < 0 else 'longer'}</span>
                """, unsafe_allow_html=True)
        
            # Close the summary box
            summary_container.markdown('</div>', unsafe_allow_html=True)
            
        st.write("##")
        

# Show user tracking chart
st.header("User Tracking Chart")
chart = user_tracking_chart(counts)
st.altair_chart(chart, use_container_width=True)
