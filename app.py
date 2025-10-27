import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# ====== THEME COLORS (PulseFit-Inspired Palette) ======
PRIMARY = "#57C0BE"         # Dark gray for main content areas
SECONDARY = "#6669C1"       # Off-white for main background
ACCENT = "#35353500"        # Vibrant orange for buttons and highlights
SUPPORT = "#6AA7A3"         # Soft gray for inputs/borders
HIGHLIGHT = "#11010100"     # Warm cream for hover or subtle highlights

# ====== PAGE CONFIG ======
st.set_page_config(page_title="LoanEase 💸", layout="wide")

# ====== SESSION STATE & NAVIGATION SETUP ======
# Initialising state variables for navigation and cross-tab data sharing
if "page" not in st.session_state:
    st.session_state.page = "home"
if "eligibility_inputs" not in st.session_state:
    # Default values used for pre-filling SHAP
    st.session_state.eligibility_inputs = {
        'loan_amount': 2500000,
        'interest_rate': 10.0,
        'tenure': 15,
        'income': 75000,
        'credit_score': 780
    }

def go_to(page):
    st.session_state.page = page

# ====== GLOBAL STYLING & POSITIONING ======
def setup_page_styles():
    # Inject CSS for global styles, feature cards, and button positioning
    st.markdown(f"""
    <style>
    /* Remove top space and header */
    div.block-container {{padding-top: 0rem;}}
    header {{visibility: hidden;}}
        
    /* Global App View Container Background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
        /* Deep Navy Blue */
        background: #151E28 !important; 
        color: #F9F9F9 !important;
    }}

    /* Custom Title & Subtitle Style (Override to white) */
    h1, h2, h3, p, label {{
        color: #FFFFFF !important;
    }}

    /* ---- Feature Buttons: Forest & Clay theme ---- */
    /* This targets the main navigation buttons on the home page */
    div[data-testid="stButton"] button {{
        background-color: #1C1C1A !important;   
        color: #E8E6E1 !important;          
        border: 1.5px solid #A68A64 !important; 
        border-radius: 16px !important;
        padding: 1.8rem 2.2rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease-in-out;
        width: 320px !important;
        height: 150px !important;
    }}
    div[data-testid="stButton"] button:hover {{
        background-color: #292924 !important;   
        border-color: #B69B75 !important;       
        box-shadow: 0 0 15px rgba(166, 138, 100, 0.45);
        transform: translateY(-2px);
    }}

    /* NEW: Target the Explain Decision button using its key 'explain_decision_btn' */
    /* Streamlit automatically adds the key as an ID for the surrounding div */
    div[data-testid="stButton"] button[key="explain_decision_btn"] {{
        background-color: #6AA7A3 !important; 
        color: #151E28 !important;
        border-color: #6AA7A3 !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 1.5rem !important;
        width: auto !important;
        height: auto !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(106, 167, 163, 0.4) !important;
    }}
    div[data-testid="stButton"] button[key="explain_decision_btn"]:hover {{
        background-color: #8CBBB7 !important;
        border-color: #8CBBB7 !important;
    }}

    /* Target Specific Buttons (e.g., Explain Decision button) to be more prominent */
    /* OLD CSS: button[kind="explain-decision"] { ... } -> REMOVED IN FAVOR OF THE NEW TARGETING ABOVE */

    /* === HOME/DEPLOY BUTTON STYLING & POSITIONING === */
    /* This styles the small fixed 'Home' button */
    div[data-testid="stHorizontalBlock"] > div:last-child > div:last-child > div:last-child button {{
        position: fixed;
        top: 12px;
        right: 20px;
        z-index: 1000;
        
        background-color: #353840 !important; 
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        height: auto !important; 
        width: auto !important; 
        font-size: 14px !important; 
        font-weight: 400 !important;
        box-shadow: none !important;
    }}

    div[data-testid="stHorizontalBlock"] > div:last-child > div:last-child > div:last-child button:hover {{
        background-color: #4D515A !important; 
        transform: none !important; 
        box-shadow: none !important;
    }}
    
    /* Customizing the Radio Button look */
    div[data-testid="stRadio"] label {{
        /* General styling for radio options */
        background-color: #293749; /* Darker background for options */
        border-radius: 8px;
        padding: 10px 15px;
        margin-right: 10px;
        border: 1px solid #3d4a5c;
    }}

    /* Fix: Force horizontal radio button options to align left */
    div[data-testid="stRadio"] > div {{
        justify-content: flex-start !important;
        width: 100% !important;
    }}

    .footer {{
        text-align:center;
        color:#CFCFCF;
        margin-top:30px;
        font-size:13px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Call the style setup once
setup_page_styles()

# Function to display the fixed header with the home button
def display_header_and_home_button():
    # Create a placeholder for the fixed Home button on the top right
    st.columns([1, 0.05, 0.15])[2].button(
        "🏠 Home", 
        key="fixed_home_button", 
        on_click=go_to, 
        args=("home",)
    )

    # Custom title + subtitle at top-left
    st.markdown(
        """
        <div style='padding: 5px 0px 0px 20px;'>
            <h1 style='text-align: center; font-size: 30px; margin-bottom: 3px;'>
                LOAN ELIGIBILITY & FINANCIAL RISK PORTAL
            </h1>
            <p style='text-align: center; font-size: 15px; margin-top: 0px;'>
                Assess your financial profile and estimate your loan approval chances in seconds
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# Function to calculate EMI
def calculate_emi(principal, annual_rate, tenure_years):
    # Monthly interest rate
    r = annual_rate / (12 * 100)
    # Total number of payments
    n = tenure_years * 12

    if r == 0:
        emi = principal / n if n > 0 else 0
    else:
        try:
            emi = (principal * r * (1 + r)**n) / ((1 + r)**n - 1)
        except ZeroDivisionError:
            emi = principal / n
            
    return emi if emi > 0 else 0

# Function to create a simplified amortization schedule (for visualization)
def create_amortization_summary(principal, annual_rate, emi, tenure_years):
    monthly_rate = annual_rate / (12 * 100)
    num_months = tenure_years * 12
    
    if num_months == 0 or emi == 0:
        return None, 0, 0
    
    outstanding_balance = principal
    total_interest = 0
    
    # Simplified summary for visualization (quarterly breakdown)
    summary_data = []
    
    for month in range(1, num_months + 1):
        interest_paid = outstanding_balance * monthly_rate
        
        principal_paid = emi - interest_paid
        if outstanding_balance < principal_paid:
            principal_paid = outstanding_balance
            interest_paid = emi - principal_paid # Recalculate interest if we pay off early
            
        outstanding_balance -= principal_paid
        total_interest += interest_paid
        
        # Add data for summary (quarterly)
        if month % 3 == 0 or month == num_months: # Log every quarter or the final month
            summary_data.append({
                'Month': month,
                'Year': (month - 1) // 12 + 1,
                'Principal Component': principal_paid,
                'Interest Component': interest_paid,
                'Remaining Balance': outstanding_balance
            })
        
    return pd.DataFrame(summary_data), total_interest, principal + total_interest

# Function for SHAP simulation
def simulate_shap_explanation(credit_score, monthly_income, desired_loan_amount, loan_tenure_years, annual_rate):
    """Simulates SHAP values based on common lending model logic."""
    
    # 1. Calculate EMI to find the Debt-to-Income (DTI) ratio
    emi = calculate_emi(desired_loan_amount, annual_rate, loan_tenure_years)
    dti_ratio = (emi / monthly_income) * 100 if monthly_income > 0 else 100

    # 2. Initialize SHAP base value (baseline approval probability)
    base_value = 0.50 
    
    # List to store SHAP contributions (Feature, Value, Color, Description)
    contributions = []
    
    # --- Credit Score Contribution ---
    score_shap = 0
    score_desc = ""
    if credit_score >= 750:
        score_shap = 0.20 # +20 percentage points
        score_desc = "Excellent score, significantly boosting approval probability."
    elif credit_score >= 650:
        score_shap = 0.05 # +5 percentage points
        score_desc = "Good score, slight positive impact."
    else:
        score_shap = -0.15 # -15 percentage points
        score_desc = "Low score, significantly lowering approval probability."
    contributions.append({
        'Feature': f"Credit Score ({credit_score})", 
        'SHAP_Value': score_shap, 
        'Group': 'Positive' if score_shap > 0 else 'Negative',
        'Description': score_desc
    })

    # --- DTI Ratio Contribution ---
    dti_shap = 0
    dti_desc = ""
    if dti_ratio <= 30:
        dti_shap = 0.15
        dti_desc = f"Low DTI ({dti_ratio:,.1f}%), strong factor for approval (manageable debt)."
    elif dti_ratio <= 45:
        dti_shap = -0.05
        dti_desc = f"Moderate DTI ({dti_ratio:,.1f}%), slight negative impact."
    else:
        dti_shap = -0.25
        dti_desc = f"High DTI ({dti_ratio:,.1f}%), major factor against approval (high risk of default)."
    contributions.append({
        'Feature': f"Debt-to-Income (DTI)", 
        'SHAP_Value': dti_shap, 
        'Group': 'Positive' if dti_shap > 0 else 'Negative',
        'Description': dti_desc
    })

    # --- Monthly Income Contribution ---
    income_shap = 0
    income_desc = ""
    if monthly_income >= 100000:
        income_shap = 0.10
        income_desc = f"High income (₹{monthly_income:,.0f}/mo) provides strong repayment capacity."
    elif monthly_income >= 50000:
        income_shap = 0.03
        income_desc = f"Moderate income (₹{monthly_income:,.0f}/mo), slight positive support."
    else:
        income_shap = -0.05
        income_desc = f"Lower income (₹{monthly_income:,.0f}/mo) is a mild risk factor."
    contributions.append({
        'Feature': f"Monthly Income", 
        'SHAP_Value': income_shap, 
        'Group': 'Positive' if income_shap > 0 else 'Negative',
        'Description': income_desc
    })
    
    # Calculate final probability
    final_prob = base_value + sum(c['SHAP_Value'] for c in contributions)
    final_prob = np.clip(final_prob, 0.01, 0.99) # Clip between 1% and 99%
    
    # Convert to DataFrame for easier plotting
    df_shap = pd.DataFrame(contributions)
    
    return base_value, final_prob, df_shap

# ====== MAIN CONTENT ======

display_header_and_home_button()

if st.session_state.page == "home":
    
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

    # ====== ROW 1: 2 CARDS ======
    _, col1, col2, _ = st.columns([0.5, 1, 1, 0.5])
    with col1:
        st.button("🏛️ Loan Eligibility Check", 
                      key="eligibility-feature-card-btn", 
                      on_click=go_to, 
                      args=("eligibility",), 
                      use_container_width=True)

    with col2:
        st.button("📊 Financial Risk Calculator", 
                      key="risk-feature-card-btn", 
                      on_click=go_to, 
                      args=("risk",), 
                      use_container_width=True)

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # ====== ROW 2: 2 CARDS ======
    _, col3, col4, _ = st.columns([0.5, 1, 1, 0.5])
    with col3:
        st.button("💰 EMI Calculator", 
                      key="emi-feature-card-btn", 
                      on_click=go_to, 
                      args=("emi",), 
                      use_container_width=True)

    with col4:
        st.button("🧠 Explainability (SHAP)", 
                      key="shap-feature-card-btn", 
                      on_click=go_to, 
                      args=("shap",), 
                      use_container_width=True)


# ====== ELIGIBILITY SECTION ======
elif st.session_state.page == "eligibility":
    st.markdown("---")
    st.markdown("<h2 style='color:white;'>🏛️ Eligibility Check</h2>", unsafe_allow_html=True)
    st.write("Fill in your details to check loan eligibility and estimate your EMI:")

    with st.form(key='eligibility_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        # Load inputs from session state for persistence
        with col1:
            loan_amount = st.slider("Desired Loan Amount (₹)",min_value=100000, max_value=4000000, step=5000, 
                                     value=st.session_state.eligibility_inputs['loan_amount'])
            interest_rate = st.slider("Interest Rate (%)", min_value=1.0, max_value=20.0, step=0.1, 
                                      value=st.session_state.eligibility_inputs['interest_rate'])
            tenure = st.slider("Loan Tenure (Years)", min_value=1, max_value=30, step=1, 
                                 value=st.session_state.eligibility_inputs['tenure'])

        with col2:
            income = st.slider("Monthly Income (₹)", min_value=20000,max_value=200000,  step=1000, 
                               value=st.session_state.eligibility_inputs['income'])
            credit_score = st.slider("Credit Score (Simulated)", min_value=300, max_value=900, 
                                             value=st.session_state.eligibility_inputs['credit_score'])
            
        submit_button = st.form_submit_button(label="🔍 Check Eligibility")

    if submit_button:
        # Save the current inputs to session state
        st.session_state.eligibility_inputs = {
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'tenure': tenure,
            'income': income,
            'credit_score': credit_score
        }
        
        if interest_rate > 0 and tenure > 0 and loan_amount > 0 and income > 0:
            
            other_emis = 0 
            emi = calculate_emi(loan_amount, interest_rate, tenure)
            total_emi = emi + other_emis
            dti_ratio = (total_emi / income) * 100
            

            st.markdown("---")
            st.markdown("<h3 style='color:#2BB3FF;'>Assessment Results</h3>", unsafe_allow_html=True)

            col_res1, col_res2 = st.columns(2)
            
            col_res1.metric("Estimated New EMI", f"₹{emi:,.0f}", delta_color="off")
            col_res2.metric("Debt-to-Income (DTI) Ratio", f"{dti_ratio:,.1f}%")
            
            st.markdown("---")
            max_dti = 40.0
            
            # --- Logic to combine/clarify rejection reasons ---
            is_dti_ok = dti_ratio <= max_dti
            is_credit_ok = credit_score >= 650
            
            if is_dti_ok and is_credit_ok:
                st.success(f"✅ **You are Eligible!** DTI: {dti_ratio:,.1f}% | Credit Score: {credit_score}")
            else:
                reasons = []
                if not is_dti_ok:
                    reasons.append(f"High DTI ({dti_ratio:,.1f}%) — exceeds {max_dti}% limit")
                if not is_credit_ok:
                    reasons.append(f"Low Credit Score ({credit_score}) — minimum required is 650")
                
                # Display single combined error or targeted warning
                if len(reasons) == 2:
                    st.error(f"❌ **Not Eligible.** Primary Blockers: {reasons[0]} and {reasons[1]}.")
                elif len(reasons) == 1 and not is_credit_ok and is_dti_ok:
                    st.warning(f"⚠️ **Conditional Approval.** DTI is good, but {reasons[0]} might lead to rejection or higher rate.")
                elif len(reasons) == 1 and not is_dti_ok:
                    st.error(f"❌ **Not Eligible.** Primary Blocker: {reasons[0]}.")
            # --- END Logic ---

            # --- FIX: Removed the conflicting 'kwargs' and 'type' arguments ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("🧠 Explain the Decision (SHAP)", 
                     key="explain_decision_btn", # This key is now used for CSS styling
                     on_click=go_to, 
                     args=("shap",),
                     help="Go to the Explainability tab with current inputs pre-filled.")
            # --- END FIX ---

        else:
            st.error("Please fill valid positive values for all fields.")

# ====== FINANCIAL RISK SECTION ======
elif st.session_state.page == "risk":
    st.markdown("---")
    st.markdown("<h2 style='color:white;'>📊 Financial Risk Calculator</h2>", unsafe_allow_html=True)
    st.write("Analyze your current financial standing to determine your overall risk profile.")

    with st.form(key='risk_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            # Income and Debt
            annual_income = st.slider("Annual Income (₹)", min_value=240000, max_value=24000000, step=10000, value=600000)
            existing_debt = st.slider("Existing Monthly Debt (EMIs / Credit Cards) (₹)", min_value=0, max_value=500000, step=5000, value=30000)
            
        with col2:
            # Credit Score and Expenses
            credit_score_risk = st.slider("Credit Score (CIBIL)", min_value=300, max_value=900, value=750)
            fixed_expenses = st.slider("Monthly Fixed Expenses (Rent, Utilities, etc.) (₹)", min_value=0, max_value=200000, step=1000, value=15000)

        # Collateral Input - Styled to look like a label using markdown
        st.markdown("Is Collateral (Secured Assets like property, gold, or investments) being offered?", unsafe_allow_html=True)
        collateral_presence = st.radio(
            "", # Empty label, we used markdown above
            options=['No', 'Yes'], 
            index=0, 
            horizontal=True,
            key='collateral_radio',
            label_visibility="collapsed" # Added to remove extra vertical space
        )

        submit_risk_button = st.form_submit_button(label="📈 Calculate Risk Score")

    if submit_risk_button:
        # Convert annual to monthly for calculations
        monthly_income = annual_income / 12
        
        # 1. Debt-to-Income Ratio (DTI) 
        dti = (existing_debt / monthly_income) if monthly_income > 0 else 100 
        
        # 2. Expense-to-Income Ratio (ETI) - Ratio of all mandatory payments (debt + expenses)
        eti = ((existing_debt + fixed_expenses) / monthly_income) if monthly_income > 0 else 100

        # --- Simple Risk Score Logic (0 = Low Risk, 100 = High Risk) ---
        base_risk = (dti * 50) + (eti * 20)
        credit_modifier = ((credit_score_risk - 600) / 300) * 30 
        collateral_reduction = 20 if collateral_presence == 'Yes' else 0
        
        adjusted_risk = base_risk - credit_modifier - collateral_reduction
        final_risk_score = np.clip(adjusted_risk, 0, 100) 

        # --- Display Results ---
        st.markdown("---")
        st.markdown("<h3 style='color:#2BB3FF;'>Financial Risk Assessment</h3>", unsafe_allow_html=True)

        col_risk1, col_risk2, col_risk3 = st.columns(3)
        
        col_risk1.metric("Current Debt-to-Income (DTI)", f"{dti*100:,.1f}%", delta_color="off")
        col_risk2.metric("Total Obligation-to-Income (ETI)", f"{eti*100:,.1f}%", delta_color="off")
        col_risk3.metric("Overall Financial Risk Score", f"{final_risk_score:,.0f}/100")

        st.markdown("---")

        # Risk Interpretation
        if final_risk_score < 25:
            st.success("🟢 **LOW RISK:** Excellent financial health, especially if collateral is provided.")
        elif final_risk_score < 50:
            st.info("🟡 **MODERATE RISK:** Good standing. Your obligations are manageable.")
        elif final_risk_score < 75:
            st.warning("🟠 **ELEVATED RISK:** Your financial profile shows potential stress. The presence of collateral helps, but focus on debt reduction.")
        else:
            st.error("🔴 **HIGH RISK:** Significant portion of your income is consumed by debt and expenses, and/or your credit score is low.")

# ====== EMI CALCULATOR SECTION (NEW) ======
elif st.session_state.page == "emi":
    st.markdown("---")
    st.markdown("<h2 style='color:white;'>💰 Detailed EMI Calculator</h2>", unsafe_allow_html=True)
    st.write("Calculate your exact monthly payment, total interest cost, and visualize the repayment schedule.")

    with st.form(key='emi_calculator_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            loan_amount = st.slider("Loan Principal (₹)", min_value=100000, max_value=10000000, step=10000, value=2500000)
            interest_rate = st.slider("Annual Interest Rate (%)", min_value=1.0, max_value=25.0, step=0.1, value=10.5)

        with col2:
            tenure_years = st.slider("Loan Tenure (Years)", min_value=1, max_value=30, step=1, value=15)
            st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)
            

        calculate_emi_button = st.form_submit_button(label="💵 Calculate Full Repayment")

    if calculate_emi_button:
        if loan_amount > 0 and interest_rate >= 0 and tenure_years > 0:
            
            # 1. Calculate EMI
            emi = calculate_emi(loan_amount, interest_rate, tenure_years)
            
            # 2. Create Amortization Summary & get totals
            df_summary, total_interest, total_payable = create_amortization_summary(
                loan_amount, interest_rate, emi, tenure_years
            )

            st.markdown("---")
            st.markdown("<h3 style='color:#2BB3FF;'>Summary of Loan Cost</h3>", unsafe_allow_html=True)
            
            col_sum1, col_sum2, col_sum3 = st.columns(3)
            
            # Display key metrics
            col_sum1.metric("Monthly EMI", f"₹{emi:,.0f}", delta_color="off")
            col_sum2.metric("Total Interest Paid", f"₹{total_interest:,.0f}", delta_color="off")
            col_sum3.metric("Total Amount Payable (P + I)", f"₹{total_payable:,.0f}", delta_color="off")

            st.markdown("---")

            # 3. Visualization
            st.markdown("<h3 style='color:#FFFFFF;'>Repayment Breakdown Over Time</h3>", unsafe_allow_html=True)

            if df_summary is not None and not df_summary.empty:
                df_plot = df_summary.rename(columns={
                    'Principal Component': 'Principal',
                    'Interest Component': 'Interest'
                })
                
                # Melt the DataFrame for Plotly stacked bar chart
                df_melted = df_plot.melt(
                    id_vars=['Year', 'Month', 'Remaining Balance'],
                    value_vars=['Principal', 'Interest'],
                    var_name='Payment Type',
                    value_name='Amount'
                )
                
                # Generate Plotly chart
                fig = px.bar(
                    df_melted, 
                    x='Month', 
                    y='Amount', 
                    color='Payment Type',
                    title='EMI Components Over Repayment Period (Quarterly Snapshot)',
                    color_discrete_map={'Principal': '#6AA7A3', 'Interest': '#B69B75'}
                )
                
                fig.update_layout(
                    xaxis_title="Month of Repayment",
                    yaxis_title="Amount (₹)",
                    plot_bgcolor='#1C1C1A', 
                    paper_bgcolor='#151E28', 
                    font_color='#F9F9F9',   
                    title_font_size=18
                )
                
                st.plotly_chart(fig, use_container_width=True)

                
                if st.checkbox('Show Full Amortization Data Table (Quarterly View)'):
                    df_display = df_summary.copy()
                    df_display['Principal Component'] = df_display['Principal Component'].apply(lambda x: f"₹{x:,.0f}")
                    df_display['Interest Component'] = df_display['Interest Component'].apply(lambda x: f"₹{x:,.0f}")
                    df_display['Remaining Balance'] = df_display['Remaining Balance'].apply(lambda x: f"₹{x:,.0f}")
                    st.dataframe(df_display.set_index('Month'))
                else:
                    st.info("Notice how the **Interest** component of the payment is largest at the beginning and the **Principal** component grows over time.")
            
        else:
            st.error("Please enter valid positive loan details.")

# ====== SHAP PAGE (NEWLY IMPLEMENTED) ======
elif st.session_state.page == "shap":
    st.markdown("---")
    st.markdown("<h2 style='color:white;'>🧠 Explainability (SHAP)</h2>", unsafe_allow_html=True)
    
    st.write("""
    **SHAP (SHapley Additive exPlanations)** shows how an AI model made a loan decision for a specific profile. 
    It tells you exactly which factors pushed the final loan approval probability up (Green) 
    and which factors pulled it down (Red) compared to a generic baseline.
    """)
    
    with st.form(key='shap_explanation_form', clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        # Pre-fill inputs from the last successful eligibility check
        inputs = st.session_state.eligibility_inputs
        
        with col1:
            shap_loan_amount = st.slider("Loan Amount (₹) for Explanation", min_value=100000, max_value=4000000, step=5000, 
                                         value=inputs['loan_amount'])
            shap_interest_rate = st.slider("Interest Rate (%) for Explanation", min_value=5.0, max_value=20.0, step=0.1, 
                                            value=inputs['interest_rate'])
            shap_tenure = st.slider("Loan Tenure (Years) for Explanation", min_value=1, max_value=30, step=1, 
                                     value=inputs['tenure'])

        with col2:
            shap_income = st.slider("Monthly Income (₹) for Explanation", min_value=20000,max_value=200000,     step=1000, 
                                     value=inputs['income'])
            shap_credit_score = st.slider("Credit Score (CIBIL) for Explanation", min_value=300, max_value=900, 
                                             value=inputs['credit_score'])
            st.markdown("<div style='height: 38px;'></div>", unsafe_allow_html=True)

        analyze_shap_button = st.form_submit_button(label="💡 Re-Analyze Explanation")

    # Run the simulation immediately if the page loads or the user clicks Re-Analyze
    if 'shap_last_run' not in st.session_state:
        st.session_state.shap_last_run = False

    if analyze_shap_button or not st.session_state.shap_last_run:
        
        base_prob, final_prob, df_shap = simulate_shap_explanation(
            credit_score=shap_credit_score,
            monthly_income=shap_income,
            desired_loan_amount=shap_loan_amount,
            loan_tenure_years=shap_tenure,
            annual_rate=shap_interest_rate
        )
        st.session_state.shap_last_run = True # Mark as run

        st.markdown("---")
        
        # Display Results
        col_base, col_final, _ = st.columns([1, 1, 1])
        col_base.metric("Baseline Approval Probability", f"{base_prob*100:,.0f}%", delta_color="off")
        col_final.metric("Final Predicted Probability", f"{final_prob*100:,.0f}%", 
                         delta=f"{((final_prob - base_prob)*100):+,.0f} pp (vs. Baseline)")
        
        if final_prob >= 0.5:
            st.success(f"Outcome: LIKELY APPROVED (Probability: {final_prob*100:,.0f}%)")
        else:
            st.error(f"Outcome: LIKELY REJECTED (Probability: {final_prob*100:,.0f}%)")
        
        st.markdown("---")
        
        st.markdown("<h3 style='color:#FFFFFF;'>Feature Contribution Plot (Simulated)</h3>", unsafe_allow_html=True)

        # Create the Horizontal Bar Chart (SHAP Force Plot style)
        fig = px.bar(
            df_shap.sort_values(by='SHAP_Value', ascending=True), # Sort for visual clarity
            x='SHAP_Value',
            y='Feature',
            color='Group', # Use the Group (Positive/Negative) for color
            orientation='h',
            title="How Each Factor Pushed the Approval Probability",
            color_discrete_map={'Positive': '#6AA7A3', 'Negative': '#B69B75'}
        )

        fig.update_layout(
            xaxis_title="Contribution to Prediction (Percentage Points)",
            yaxis_title="Financial Feature",
            plot_bgcolor='#1C1C1A', 
            paper_bgcolor='#151E28',
            font_color='#F9F9F9',
            title_font_size=18
        )
        
        # Add a vertical line at x=0 for visual reference
        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#F9F9F9")

        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("Detailed Feature Descriptions:")
        for index, row in df_shap.iterrows():
            icon = "⬆️" if row['Group'] == 'Positive' else "⬇️"
            st.markdown(f"**{icon} {row['Feature']} ({row['SHAP_Value']*100:+.0f} pp):** {row['Description']}", unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown("<div class='footer'> LoanEase | Simplifying finance, one click at a time💸</div>", unsafe_allow_html=True)


