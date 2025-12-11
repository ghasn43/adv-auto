import streamlit as st
import hashlib
import json
import os
import pandas as pd
from datetime import datetime
import re

# -----------------------------------------------------------
# USER DATABASE MANAGEMENT
# -----------------------------------------------------------
class UserDatabase:
    """Simple file-based user database"""
    
    def __init__(self, db_file="users.json"):
        self.db_file = db_file
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.db_file, "w") as f:
            json.dump(self.users, f, indent=4)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email, role="user"):
        """Create a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        # Validate email format
        if not self._validate_email(email):
            return False, "Invalid email format"
        
        # Validate username (alphanumeric only)
        if not re.match("^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        self.users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "active": True
        }
        self._save_users()
        return True, "User created successfully"
    
    def update_user(self, username, email=None, role=None, active=None, new_password=None):
        """Update user information"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        if email is not None:
            if not self._validate_email(email):
                return False, "Invalid email format"
            user["email"] = email
        
        if role is not None:
            user["role"] = role
        
        if active is not None:
            user["active"] = active
        
        if new_password is not None:
            if len(new_password) < 6:
                return False, "Password must be at least 6 characters"
            user["password"] = self.hash_password(new_password)
        
        self._save_users()
        return True, "User updated successfully"
    
    def delete_user(self, username):
        """Delete a user (admin only)"""
        if username in self.users:
            del self.users[username]
            self._save_users()
            return True, f"User '{username}' deleted"
        return False, "User not found"
    
    def authenticate(self, username, password):
        """Authenticate a user"""
        if username not in self.users:
            return False, "User not found", None
        
        user = self.users[username]
        
        # Check if account is active
        if not user.get("active", True):
            return False, "Account is deactivated", None
        
        if user["password"] == self.hash_password(password):
            # Update last login time
            user["last_login"] = datetime.now().isoformat()
            self._save_users()
            return True, "Login successful", user["role"]
        else:
            return False, "Invalid password", None
    
    def get_all_users(self):
        """Get all users (admin only)"""
        return self.users
    
    def get_user(self, username):
        """Get specific user details"""
        return self.users.get(username)
    
    def _validate_email(self, email):
        """Simple email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


# -----------------------------------------------------------
# CREATE DEFAULT USERS
# -----------------------------------------------------------
def create_default_users():
    """Create default admin and user accounts"""
    user_db = UserDatabase()
    
    # Create default admin if it doesn't exist
    if "admin" not in user_db.users:
        user_db.create_user("admin", "admin123", "admin@example.com", "admin")
        print("✓ Created default admin account: admin / admin123")
    
    # Create default user if it doesn't exist
    if "user" not in user_db.users:
        user_db.create_user("user", "user123", "user@example.com", "user")
        print("✓ Created default user account: user / user123")
    
    return user_db


# -----------------------------------------------------------
# ADMIN USER MANAGEMENT INTERFACE
# -----------------------------------------------------------
def show_user_management():
    """Comprehensive user management interface for admins"""
    
    st.title("👥 User Management")
    st.markdown("Manage user accounts, roles, and permissions.")
    
    user_db = st.session_state.user_db
    users = user_db.get_all_users()
    
    # Create tabs for different management functions
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Users", "➕ Add User", "✏️ Edit User", "📊 Statistics"])
    
    # -----------------------------
    # TAB 1: View All Users (FIXED VERSION)
    # -----------------------------
    with tab1:
        if users:
            # Display user statistics
            col1, col2, col3, col4 = st.columns(4)
            
            total_users = len(users)
            active_users = sum(1 for u in users.values() if u.get("active", True))
            admin_count = sum(1 for u in users.values() if u["role"] == "admin")
            user_count = sum(1 for u in users.values() if u["role"] == "user")
            
            with col1:
                st.metric("Total Users", total_users)
            with col2:
                st.metric("Active Users", active_users)
            with col3:
                st.metric("Admins", admin_count)
            with col4:
                st.metric("Regular Users", user_count)
            
            st.markdown("---")
            
            # Search and filter
            col_search, col_filter = st.columns([2, 1])
            
            with col_search:
                search_term = st.text_input("🔍 Search users", placeholder="Search by username or email")
            
            with col_filter:
                filter_role = st.selectbox("Filter by role", ["All", "admin", "user"])
            
            # Prepare user data for display (FIXED VERSION)
            user_data = []
            for username, user_info in users.items():
                # Apply filters
                if search_term and search_term.lower() not in username.lower() and search_term.lower() not in user_info["email"].lower():
                    continue
                
                if filter_role != "All" and user_info["role"] != filter_role:
                    continue
                
                # FIXED: Handle None values for last_login
                last_login = user_info.get("last_login")
                if last_login is None:
                    last_login = "Never"
                elif last_login != "Never":
                    try:
                        last_login = last_login[:19]  # Show date and time only
                    except:
                        last_login = "Invalid date"
                
                # FIXED: Handle None values for created_at
                created_at = user_info.get("created_at", "N/A")
                if created_at and created_at != "N/A":
                    created_at = created_at[:10]
                
                user_data.append({
                    "Username": username,
                    "Email": user_info["email"],
                    "Role": user_info["role"],
                    "Status": "✅ Active" if user_info.get("active", True) else "❌ Inactive",
                    "Created": created_at,
                    "Last Login": last_login,
                    "Actions": username  # For action buttons
                })
            
            if user_data:
                # Convert to DataFrame for display
                df = pd.DataFrame(user_data)
                
                # Display as an interactive table
                st.dataframe(
                    df,
                    column_config={
                        "Actions": st.column_config.Column(
                            "Actions",
                            width="small",
                            help="Click to manage user"
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Quick actions for selected user
                if len(user_data) > 0:
                    st.markdown("### Quick Actions")
                    
                    selected_user = st.selectbox(
                        "Select user for quick action",
                        [u["Username"] for u in user_data],
                        key="quick_action_select"
                    )
                    
                    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
                    
                    with col_act1:
                        if st.button("🔄 Toggle Active", use_container_width=True):
                            current_status = users[selected_user].get("active", True)
                            success, message = user_db.update_user(selected_user, active=not current_status)
                            if success:
                                st.success(f"User {selected_user} is now {'active' if not current_status else 'inactive'}")
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col_act2:
                        if st.button("👑 Make Admin", use_container_width=True):
                            success, message = user_db.update_user(selected_user, role="admin")
                            if success:
                                st.success(f"User {selected_user} is now an admin")
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col_act3:
                        if st.button("👤 Make User", use_container_width=True, disabled=selected_user=="admin"):
                            success, message = user_db.update_user(selected_user, role="user")
                            if success:
                                st.success(f"User {selected_user} is now a regular user")
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with col_act4:
                        if st.button("🗑️ Delete", use_container_width=True, disabled=selected_user=="admin"):
                            success, message = user_db.delete_user(selected_user)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
            else:
                st.info("No users match your search criteria.")
        else:
            st.info("No users found in the database.")
    
    # -----------------------------
    # TAB 2: Add New User
    # -----------------------------
    with tab2:
        st.subheader("➕ Add New User")
        
        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username*", help="3-20 characters, letters/numbers/underscores only")
                new_email = st.text_input("Email Address*", placeholder="user@example.com")
            
            with col2:
                new_password = st.text_input("Password*", type="password", help="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password*", type="password")
                new_role = st.selectbox("Role*", ["user", "admin"])
            
            # Additional options
            col3, col4 = st.columns(2)
            with col3:
                send_welcome = st.checkbox("Send welcome email (if configured)", value=False)
            with col4:
                require_password_change = st.checkbox("Require password change on first login", value=False)
            
            submit_button = st.form_submit_button("Create User", type="primary", use_container_width=True)
        
        if submit_button:
            # Validate inputs
            errors = []
            
            if not new_username or len(new_username) < 3:
                errors.append("Username must be at least 3 characters")
            elif not re.match("^[a-zA-Z0-9_]+$", new_username):
                errors.append("Username can only contain letters, numbers, and underscores")
            
            if not new_email:
                errors.append("Email is required")
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                errors.append("Invalid email format")
            
            if not new_password or len(new_password) < 6:
                errors.append("Password must be at least 6 characters")
            elif new_password != confirm_password:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create the user
                success, message = user_db.create_user(new_username, new_password, new_email, new_role)
                
                if success:
                    st.success(f"✅ User '{new_username}' created successfully!")
                    
                    # Additional options processing
                    if require_password_change:
                        st.info("User will be prompted to change password on first login")
                    
                    if send_welcome:
                        st.info("Welcome email would be sent (email service not configured)")
                    
                    # Show user details
                    with st.expander("View User Details", expanded=True):
                        st.json({
                            "username": new_username,
                            "email": new_email,
                            "role": new_role,
                            "status": "active",
                            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                else:
                    st.error(f"❌ {message}")
    
    # -----------------------------
    # TAB 3: Edit Existing User
    # -----------------------------
    with tab3:
        st.subheader("✏️ Edit Existing User")
        
        if users:
            # User selection
            edit_user = st.selectbox(
                "Select user to edit",
                list(users.keys()),
                key="edit_user_select"
            )
            
            if edit_user:
                user_info = users[edit_user]
                
                with st.form(f"edit_form_{edit_user}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Username:** {edit_user}")
                        new_email = st.text_input("Email", value=user_info["email"])
                        new_role = st.selectbox("Role", ["user", "admin"], 
                                              index=0 if user_info["role"] == "user" else 1)
                    
                    with col2:
                        account_status = st.selectbox(
                            "Account Status",
                            ["Active", "Inactive"],
                            index=0 if user_info.get("active", True) else 1
                        )
                        
                        st.markdown("---")
                        st.markdown("**Change Password** (optional)")
                        new_password = st.text_input("New Password", type="password", 
                                                   help="Leave empty to keep current password")
                        confirm_password = st.text_input("Confirm New Password", type="password")
                    
                    # User statistics
                    with st.expander("User Statistics", expanded=False):
                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            created_at = user_info.get('created_at', 'N/A')
                            if created_at != 'N/A':
                                created_at = created_at[:19]
                            st.write(f"**Created:** {created_at}")
                        with col_stat2:
                            last_login = user_info.get('last_login', 'Never')
                            if last_login != 'Never':
                                last_login = last_login[:19]
                            st.write(f"**Last Login:** {last_login}")
                    
                    # Form actions
                    col_save, col_reset, col_delete = st.columns([2, 1, 1])
                    
                    with col_save:
                        save_button = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                    
                    with col_reset:
                        reset_button = st.form_submit_button("🔄 Reset", type="secondary", use_container_width=True)
                    
                    with col_delete:
                        if edit_user != "admin":  # Prevent deleting main admin
                            delete_button = st.form_submit_button("🗑️ Delete User", type="secondary", use_container_width=True)
                    
                    if save_button:
                        # Validate password if provided
                        password_update = None
                        if new_password:
                            if len(new_password) < 6:
                                st.error("Password must be at least 6 characters")
                                st.stop()
                            if new_password != confirm_password:
                                st.error("Passwords do not match")
                                st.stop()
                            password_update = new_password
                        
                        # Update user
                        success, message = user_db.update_user(
                            edit_user,
                            email=new_email,
                            role=new_role,
                            active=(account_status == "Active"),
                            new_password=password_update
                        )
                        
                        if success:
                            st.success("✅ User updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    
                    if delete_button and edit_user != "admin":
                        success, message = user_db.delete_user(edit_user)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No users available to edit.")
    
    # -----------------------------
    # TAB 4: Statistics
    # -----------------------------
    with tab4:
        st.subheader("📊 User Statistics")
        
        if users:
            # Calculate statistics
            total_users = len(users)
            active_users = sum(1 for u in users.values() if u.get("active", True))
            inactive_users = total_users - active_users
            
            # Role distribution
            admin_count = sum(1 for u in users.values() if u["role"] == "admin")
            user_count = total_users - admin_count
            
            # Activity analysis
            users_with_login = sum(1 for u in users.values() if u.get("last_login"))
            never_logged_in = total_users - users_with_login
            
            # Recent signups (last 30 days)
            recent_signups = 0
            thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
            
            for user_info in users.values():
                created_at = user_info.get("created_at")
                if created_at:
                    try:
                        created_time = datetime.fromisoformat(created_at).timestamp()
                        if created_time > thirty_days_ago:
                            recent_signups += 1
                    except:
                        pass
            
            # Display metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Users", total_users)
                st.metric("Active Users", active_users, f"{inactive_users} inactive")
                st.metric("Admins", admin_count, f"{user_count} regular users")
            
            with col2:
                st.metric("Have Logged In", users_with_login, f"{never_logged_in} never logged in")
                st.metric("Recent Signups (30d)", recent_signups)
                # Check if users.json exists before getting size
                if os.path.exists("users.json"):
                    file_size = os.path.getsize("users.json") / 1024
                    st.metric("Database Size", f"{file_size:.1f} KB")
                else:
                    st.metric("Database Size", "0 KB")
            
            # Charts
            st.markdown("---")
            st.subheader("Charts")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Role distribution pie chart
                role_data = pd.DataFrame({
                    'Role': ['Admins', 'Regular Users'],
                    'Count': [admin_count, user_count]
                })
                st.bar_chart(role_data.set_index('Role'))
                st.caption("User Role Distribution")
            
            with chart_col2:
                # Activity status
                status_data = pd.DataFrame({
                    'Status': ['Active', 'Inactive'],
                    'Count': [active_users, inactive_users]
                })
                st.bar_chart(status_data.set_index('Status'))
                st.caption("Account Status Distribution")
            
            # Recent activity table
            st.markdown("---")
            st.subheader("Recent Activity")
            
            recent_activity = []
            for username, user_info in users.items():
                last_login = user_info.get("last_login")
                if last_login:
                    recent_activity.append({
                        "Username": username,
                        "Last Login": last_login[:19] if len(last_login) >= 19 else last_login,
                        "Role": user_info["role"],
                        "Status": "Active" if user_info.get("active", True) else "Inactive"
                    })
            
            if recent_activity:
                # Sort by last login (most recent first)
                recent_activity.sort(key=lambda x: x["Last Login"], reverse=True)
                recent_df = pd.DataFrame(recent_activity[:10])  # Top 10
                st.dataframe(recent_df, use_container_width=True, hide_index=True)
            else:
                st.info("No recent login activity.")
        else:
            st.info("No user data available for statistics.")


# -----------------------------------------------------------
# SESSION MANAGEMENT
# -----------------------------------------------------------
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_db' not in st.session_state:
        st.session_state.user_db = create_default_users()


# -----------------------------------------------------------
# LOGIN PAGE
# -----------------------------------------------------------
def show_login_page():
    """Display login page"""
    
    init_session_state()
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            padding: 10px;
            font-weight: bold;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #FF4B4B;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-header"><h1>Welcome Back</h1></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if login_button:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, message, role = st.session_state.user_db.authenticate(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = role
                    st.success(f"Welcome {username}! ({role})")
                    st.rerun()
                else:
                    st.error(message)
        
        # Demo credentials
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.code("Admin: admin / admin123\nUser: user / user123")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-header"><h1>Create Account</h1></div>', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username", placeholder="Minimum 3 characters")
            new_email = st.text_input("Email Address", placeholder="your@email.com")
            new_password = st.text_input("Choose Password", type="password", placeholder="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            user_role = st.selectbox("Account Type", ["user"], 
                                    help="Regular users have limited access. Admins can only be created by existing admins.")
            
            terms = st.checkbox("I agree to the Terms & Conditions")
            
            signup_button = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if signup_button:
            if not all([new_username, new_email, new_password, confirm_password]):
                st.error("Please fill in all fields")
            elif len(new_username) < 3:
                st.error("Username must be at least 3 characters")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif not terms:
                st.error("You must agree to the Terms & Conditions")
            else:
                success, message = st.session_state.user_db.create_user(
                    new_username, new_password, new_email, user_role
                )
                if success:
                    st.success(message + f" You can now login as {user_role}.")
                else:
                    st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------
# PROTECTED ROUTE DECORATOR
# -----------------------------------------------------------
def require_auth(required_role=None):
    """Decorator to protect routes requiring authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            init_session_state()
            
            if not st.session_state.authenticated:
                show_login_page()
                st.stop()
            
            if required_role and st.session_state.user_role != required_role:
                st.error(f"⚠️ Access Denied. This page requires {required_role} privileges.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# -----------------------------------------------------------
# LOGOUT FUNCTION
# -----------------------------------------------------------
def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_role = None
    st.success("Logged out successfully!")
    st.rerun()


# -----------------------------------------------------------
# MAIN DASHBOARD WITH NAVIGATION
# -----------------------------------------------------------
def main_with_auth():
    """Main app with authentication"""
    
    # If not authenticated, show login page
    if not st.session_state.get('authenticated', False):
        show_login_page()
        return
    
    # User is authenticated - show navigation
    show_navigation()


# -----------------------------------------------------------
# NAVIGATION SYSTEM
# -----------------------------------------------------------
def show_navigation():
    """Show navigation system with sidebar"""
    
    # Initialize session state for page tracking
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📢 Social Media Agent")
        
        # User info
        role_badge = "👑" if st.session_state.user_role == "admin" else "👤"
        st.markdown(f"""
        **Logged in as:**  
        {role_badge} **{st.session_state.username}**  
        *({st.session_state.user_role})*
        """)
        
        st.markdown("---")
        
        # Navigation menu
        st.subheader("Navigation")
        
        # Define menu options based on role
        if st.session_state.user_role == "admin":
            menu_options = {
                "🏠 Dashboard": "dashboard",
                "👥 User Management": "user_management",
                "📝 Campaigns": "campaigns",
                "📊 Analytics": "analytics",
                "⚙️ Settings": "settings"
            }
        else:
            menu_options = {
                "🏠 Dashboard": "dashboard",
                "📝 Campaigns": "campaigns",
                "👤 Profile": "profile"
            }
        
        # Create navigation buttons
        for display_name, page_id in menu_options.items():
            if st.button(display_name, use_container_width=True, 
                        type="primary" if st.session_state.current_page == page_id else "secondary"):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Quick stats for admin
        if st.session_state.user_role == "admin":
            users = st.session_state.user_db.get_all_users()
            total_users = len(users)
            active_users = sum(1 for u in users.values() if u.get("active", True))
            
            st.caption(f"👥 {total_users} users ({active_users} active)")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
    
    # Main content area based on selected page
    if st.session_state.current_page == "dashboard":
        show_dashboard_page()
    
    elif st.session_state.current_page == "user_management" and st.session_state.user_role == "admin":
        show_user_management()
    
    elif st.session_state.current_page == "campaigns":
        show_campaigns_page()
    
    elif st.session_state.current_page == "analytics" and st.session_state.user_role == "admin":
        show_analytics_page()
    
    elif st.session_state.current_page == "settings" and st.session_state.user_role == "admin":
        show_settings_page()
    
    elif st.session_state.current_page == "profile":
        show_profile_page()


# -----------------------------------------------------------
# PAGE COMPONENTS
# -----------------------------------------------------------
def show_dashboard_page():
    """Dashboard page"""
    st.title("🏠 Admin Dashboard" if st.session_state.user_role == "admin" else "🏠 User Dashboard")
    
    if st.session_state.user_role == "admin":
        st.success("👑 You have administrator privileges")
        
        # Admin quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        users = st.session_state.user_db.get_all_users()
        total_users = len(users)
        active_users = sum(1 for u in users.values() if u.get("active", True))
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Active Users", active_users)
        with col3:
            st.metric("Admins", sum(1 for u in users.values() if u["role"] == "admin"))
        with col4:
            st.metric("Campaigns", "8", "+2")
        
        st.markdown("---")
        
        # Quick actions for admin
        st.subheader("Quick Actions")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if st.button("👥 Manage Users", use_container_width=True):
                st.session_state.current_page = "user_management"
                st.rerun()
        
        with col_act2:
            if st.button("📝 Create Campaign", use_container_width=True):
                st.session_state.current_page = "campaigns"
                st.rerun()
        
        with col_act3:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.current_page = "analytics"
                st.rerun()
    
    # Welcome message for all users
    st.markdown(f"""
    ### Welcome back, {st.session_state.username}!
    
    **What you can do:**
    - 📝 Create social media campaigns
    - 🎨 Generate AI-powered images
    - 🎬 Create video reel scripts
    - 📤 Publish to Instagram (admin only)
    
    **Your role:** {st.session_state.user_role}
    """)
    
    # Recent activity placeholder
    with st.expander("📋 Recent Activity", expanded=False):
        st.info("Your recent activity will appear here")


def show_campaigns_page():
    """Campaigns page - loads the main dashboard content"""
    from dashboard import main_authenticated
    main_authenticated()


def show_analytics_page():
    """Analytics page"""
    st.title("📊 Analytics Dashboard")
    
    if st.session_state.user_role == "admin":
        st.info("Analytics features are under development")
        
        # Placeholder charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Campaign Performance")
            st.bar_chart({
                'Campaigns': ['AI Education', 'Tech UAE', 'Business Growth'],
                'Engagement': [1200, 850, 950]
            })
        
        with col2:
            st.subheader("User Activity")
            st.line_chart({
                'Days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                'Logins': [45, 52, 48, 61, 55]
            })
    else:
        st.warning("Analytics dashboard is only available for administrators")


def show_settings_page():
    """Settings page"""
    st.title("⚙️ System Settings")
    
    if st.session_state.user_role == "admin":
        st.info("System configuration options")
        
        # API Settings
        with st.expander("🔑 API Configuration", expanded=True):
            st.text_input("OpenAI API Key", type="password", value="••••••••••••••")
            st.text_input("Replicate API Token", type="password", value="••••••••••••••")
            st.text_input("Zapier Webhook URL", value="https://hooks.zapier.com/...")
            st.text_input("ImgBB API Key", type="password", value="••••••••••••••")
            
            if st.button("Save API Settings", type="primary"):
                st.success("API settings saved!")
        
        # System Settings
        with st.expander("🖥️ System Preferences", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Enable email notifications", value=True)
                st.checkbox("Auto-save campaigns", value=True)
                st.checkbox("Enable image watermark", value=False)
            
            with col2:
                st.selectbox("Default image quality", ["High", "Medium", "Low"])
                st.selectbox("Timezone", ["GMT+4 (UAE)", "GMT+0", "GMT-5"])
                st.number_input("Max campaigns per user", min_value=1, max_value=100, value=10)
            
            if st.button("Save System Preferences"):
                st.success("Preferences saved!")
        
        # Maintenance
        with st.expander("🔧 Maintenance Tools", expanded=False):
            st.warning("⚠️ Advanced tools - use with caution")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear Cache", use_container_width=True):
                    st.info("Cache cleared")
                if st.button("Backup Database", use_container_width=True):
                    st.info("Database backup created")
            
            with col2:
                if st.button("Reset Settings", use_container_width=True):
                    st.warning("Settings reset to defaults")
                if st.button("System Diagnostics", use_container_width=True):
                    st.info("Diagnostics complete")
    else:
        st.error("Access denied. Settings page is for administrators only.")


def show_profile_page():
    """User profile page"""
    st.title("👤 User Profile")
    
    user_db = st.session_state.user_db
    username = st.session_state.username
    
    if username in user_db.users:
        user_info = user_db.users[username]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Profile avatar
            initials = username[:2].upper()
            st.markdown(f"""
                <div style="text-align: center; padding: 20px;">
                    <div style="width: 100px; height: 100px; background: #FF4B4B; 
                                border-radius: 50%; display: flex; align-items: center; 
                                justify-content: center; margin: 0 auto; color: white; 
                                font-size: 36px; font-weight: bold;">
                        {initials}
                    </div>
                    <h3>{username}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Role badge
            st.markdown(f"""
                <div style="text-align: center;">
                    <span style="background: {'#FF4B4B' if user_info['role'] == 'admin' else '#4CAF50'}; 
                                color: white; padding: 3px 10px; border-radius: 15px; 
                                font-size: 12px; font-weight: bold;">
                        {user_info['role'].upper()}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Account Information")
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.text_input("Email", value=user_info['email'], disabled=True)
                st.text_input("Role", value=user_info['role'], disabled=True)
            
            with info_col2:
                created = user_info.get('created_at', 'N/A')
                if created != 'N/A':
                    created = created[:10]
                st.text_input("Member Since", value=created, disabled=True)
                
                last_login = user_info.get('last_login', 'Never')
                if last_login != 'Never':
                    last_login = last_login[:19]
                st.text_input("Last Login", value=last_login, disabled=True)
        
        # Password change section
        st.markdown("---")
        st.subheader("Change Password")
        
        with st.form("change_password"):
            current_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if not current_pass or not new_pass or not confirm_pass:
                    st.error("Please fill in all fields")
                elif len(new_pass) < 6:
                    st.error("New password must be at least 6 characters")
                elif new_pass != confirm_pass:
                    st.error("New passwords do not match")
                elif user_db.hash_password(current_pass) != user_info["password"]:
                    st.error("Current password is incorrect")
                else:
                    success, message = user_db.update_user(username, new_password=new_pass)
                    if success:
                        st.success("Password updated successfully!")
                    else:
                        st.error(message)
    else:
        st.error("User information not found")