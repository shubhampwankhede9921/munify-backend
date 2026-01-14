# Database Menu Setup Guide

## Overview
This guide provides SQL queries to populate the three tables required for role-based menu access:
1. `perdix_mp_menu_master` - Main menu items
2. `perdix_mp_submenu_master` - Submenu items (pages/routes)
3. `perdix_mp_role_org_submenu_mapping` - Maps which roles can access which submenus

## ⚠️ Important: Simplified Role Structure

**You don't need 8 separate roles!** Since the backend combines `role_id` + `org_type`, you only need **4 roles**:
- **Admin** (id: 1) - Works for lender, municipality, and munify
- **Normal User** (id: 2) - Works for lender, municipality, and munify
- **Super Admin** (id: 3) - For munify only
- **Government User** (id: 4) - For government/NIUA users

**See `SIMPLIFIED_ROLE_STRUCTURE.md` for detailed explanation.**

**How it works:**
- role_id=1 + org_type='lender' = **Lender Admin**
- role_id=2 + org_type='lender' = **Lender Normal User**
- role_id=1 + org_type='municipality' = **Municipality Admin**
- role_id=2 + org_type='municipality' = **Municipality Normal User**
- role_id=1 + org_type='munify' = **Munify Admin**
- role_id=2 + org_type='munify' = **Munify Normal User**
- role_id=3 + org_type='munify' = **System Super Admin**
- role_id=4 + org_type='government' = **Government/NIUA User**

---

## Table Structures

### 1. perdix_mp_menu_master
- `id` (BigInteger, Primary Key, Auto Increment)
- `menu_name` (String) - Display name
- `menu_icon` (String) - Icon name for frontend mapping
- `description` (String, Optional) - Menu description
- `display_order` (Integer) - Order in sidebar
- `status` (String) - 'A' for Active, 'I' for Inactive

### 2. perdix_mp_submenu_master
- `id` (BigInteger, Primary Key, Auto Increment)
- `submenu_name` (String) - Display name
- `submenu_icon` (String, Optional) - Icon name
- `route` (String) - Frontend route path
- `menu_id` (BigInteger, Foreign Key) - References menu_master.id
- `display_order` (Integer) - Order within menu
- `status` (String) - 'A' for Active, 'I' for Inactive

### 3. perdix_mp_role_org_submenu_mapping
- `id` (BigInteger, Primary Key, Auto Increment)
- `role_id` (BigInteger, Foreign Key) - References perdix_mp_roles_master.id
- `org_type` (String) - 'municipality', 'lender', 'munify', 'government'
- `submenu_id` (BigInteger, Foreign Key) - References submenu_master.id
- `status` (String) - 'A' for Active, 'I' for Inactive

---

## Step 1: Insert Menu Master Data

```sql
-- Insert Main Menu Items
INSERT INTO perdix_mp_menu_master (menu_name, menu_icon, description, display_order, status) VALUES
('Dashboard', 'dashboard', 'Main dashboard menu', 1, 'A'),
('Projects', 'projects', 'Projects management menu', 2, 'A'),
('Municipalities', 'municipalities', 'Municipalities management menu', 3, 'A'),
('Lender', 'lender', 'Lender features menu', 4, 'A'),
('Reports', 'reports', 'Reports menu', 5, 'A'),
('Admin', 'admin', 'Admin management menu', 6, 'A'),
('Trackings', 'trackings', 'Monitoring and tracking menu', 7, 'A'),
('Master', 'master', 'Master data management menu', 8, 'A'),
('Components', 'components', 'Component showcase (dev)', 9, 'A');
```

---

## Step 2: Insert Submenu Master Data

```sql
-- Dashboard Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Overview', 'overview', '/main', 1, 1, 'A'),
('Municipality Dashboard', 'municipality', '/main/dashboard/municipality', 1, 2, 'A'),
('Master Dashboard', 'monitoring', '/main/admin/monitoring', 1, 3, 'A'),
('Lender Dashboard', 'lender', '/main/lender/dashboard', 1, 4, 'A');

-- Projects Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Live Projects', 'live', '/main/projects/live', 2, 1, 'A'),
('Funded Projects', 'funded', '/main/projects/funded', 2, 2, 'A'),
('My Projects', 'my-projects', '/main/projects/my', 2, 3, 'A'),
('Favorites', 'favorites', '/main/projects/favorites', 2, 4, 'A'),
('Card Designs', 'card', '/main/designs/cards', 2, 5, 'A');

-- Municipalities Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('All Municipalities', 'municipalities', '/main/municipalities', 3, 1, 'A'),
('Credit Ratings', 'ratings', '/main/municipal/ratings', 3, 2, 'A'),
('Financial Analysis', 'analysis', '/main/municipal/analysis', 3, 3, 'A'),
('Q&A Management', 'qa', '/main/municipal/qa', 3, 4, 'A'),
('Project Progress', 'progress', '/main/municipal/projects/progress', 3, 5, 'A'),
('Documents and Meetings', 'documents', '/main/municipal/document-requests', 3, 6, 'A');

-- Lender Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Request Documents and Meetings', 'request-documents', '/main/lender/requested-documents', 4, 1, 'A');

-- Reports Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Lender Report', 'lender-report', '/main/reports/lender-report', 5, 1, 'A'),
('Project-level Commitment Report', 'commitment-report', '/main/reports/project-level-commitment', 5, 2, 'A'),
('Project Success Report', 'success-report', '/main/reports/project-success', 5, 3, 'A'),
('Current Status Report', 'status-report', '/main/reports/current-status', 5, 4, 'A'),
('Project-level Commitment Report (Admin)', 'commitment-admin', '/main/reports/project-level-commitment-admin', 5, 5, 'A'),
('Project Success Report (Admin)', 'success-admin', '/main/reports/project-success-admin', 5, 6, 'A');

-- Admin Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Project Management', 'project-management', '/main/admin/projects', 6, 1, 'A'),
('Create Project', 'create-project', '/main/admin/projects/create', 6, 2, 'A'),
('My Drafts', 'drafts', '/main/admin/projects/drafts', 6, 3, 'A'),
('User Management', 'users', '/main/admin/users', 6, 4, 'A'),
('Invitations Management', 'invitations', '/main/admin/invitations', 6, 5, 'A'),
('Send Invitation', 'send-invitation', '/main/admin/invitation', 6, 6, 'A'),
('Notifications', 'notifications', '/main/admin/notifications', 6, 7, 'A'),
('Commitments Overview', 'commitments', '/main/admin/commitments', 6, 8, 'A'),
('Reports', 'reports', '/main/admin/reports', 6, 9, 'A');

-- Trackings Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Project Lifecycle Tracker', 'lifecycle', '/main/admin/monitoring/lifecycle', 7, 1, 'A'),
('Commitment Monitoring', 'commitment-monitoring', '/main/admin/monitoring/commitments', 7, 2, 'A'),
('Q&A & Communication', 'qa-communication', '/main/admin/monitoring/qa', 7, 3, 'A'),
('Document Requests & Library', 'document-library', '/main/admin/monitoring/documents', 7, 4, 'A'),
('Allocation & Disbursement', 'allocation', '/main/admin/monitoring/allocation-disbursement', 7, 5, 'A');

-- Master Submenus
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Roles Management', 'roles', '/main/master/roles', 8, 1, 'A'),
('Organizations Management', 'organizations', '/main/master/organizations', 8, 2, 'A'),
('Fee Category Exemptions', 'fee-exemptions', '/main/master/fee-category-exemptions', 8, 3, 'A'),
('Common Master Excel', 'excel', '/main/master/common-excel', 8, 4, 'A');

-- Components Submenus (Dev only)
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Data Table', 'table', '/main/components/datatable', 9, 1, 'A');
```

---

## Step 3: Create Roles (4 Roles Approach)

**IMPORTANT:** You don't need 8 separate roles! Since the backend combines `role_id` + `org_type`, you only need **4 roles**:

```sql
-- Insert 4 roles into perdix_mp_roles_master
INSERT INTO perdix_mp_roles_master (role_name, role_code, access_level, status) VALUES
('Admin', 'ADMIN', 2, 'A'),           -- id: 1 (used for Lender Admin, Municipality Admin, Munify Admin)
('Normal User', 'USER', 1, 'A'),      -- id: 2 (used for Lender Normal, Municipality Normal, Munify Normal)
('Super Admin', 'SUPER_ADMIN', 3, 'A'), -- id: 3 (System Super Admin - munify only)
('Government User', 'GOVT_USER', 1, 'A'); -- id: 4 (Government/NIUA User)
```

**How it works:**
- **Lender Admin:** role_id=1 + org_type='lender'
- **Lender Normal User:** role_id=2 + org_type='lender'
- **Municipality Admin:** role_id=1 + org_type='municipality'
- **Municipality Normal User:** role_id=2 + org_type='municipality'
- **Munify Admin:** role_id=1 + org_type='munify'
- **Munify Normal User:** role_id=2 + org_type='munify'
- **System Super Admin:** role_id=3 + org_type='munify'
- **Government/NIUA User:** role_id=4 + org_type='government'

**Benefits:**
- ✅ Only 4 roles to manage instead of 8
- ✅ Same role works across different org_types
- ✅ Easier to understand and maintain
- ✅ Frontend code works without changes

**Note:** If you already have roles in your database, query them first:
```sql
SELECT id, role_name, role_code, access_level 
FROM perdix_mp_roles_master 
WHERE status = 'A'
ORDER BY id;
```

Then adjust the role_ids in the mappings below to match your actual role IDs.

---

## Step 4: Insert Role-Org-Submenu Mappings

### 4.1 Lender Admin Mappings

```sql
-- Using simplified approach: role_id=1 (Admin) + org_type='lender' = Lender Admin
-- If your Admin role has a different ID, replace 1 with your actual Admin role_id

-- Dashboard access
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 1, 'A'), -- Overview
(1, 'lender', 4, 'A'); -- Lender Dashboard

-- Projects access
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 5, 'A'), -- Live Projects
(1, 'lender', 6, 'A'), -- Funded Projects
(1, 'lender', 8, 'A'), -- Favorites
(1, 'lender', 9, 'A'); -- Card Designs (if needed)

-- Municipalities (View Only - but still need access)
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 10, 'A'); -- All Municipalities

-- Lender features
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 16, 'A'); -- Request Documents and Meetings

-- Reports
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 17, 'A'), -- Lender Report
(1, 'lender', 18, 'A'), -- Project-level Commitment Report
(1, 'lender', 19, 'A'), -- Project Success Report
(1, 'lender', 20, 'A'); -- Current Status Report

-- Admin (Organization Level - User Management)
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'lender', 25, 'A'), -- User Management
(1, 'lender', 26, 'A'), -- Invitations Management
(1, 'lender', 27, 'A'), -- Send Invitation
(1, 'lender', 30, 'A'); -- Reports
```

### 4.2 Lender Normal User Mappings

```sql
-- Using simplified approach: role_id=2 (Normal User) + org_type='lender' = Lender Normal User
-- Similar to Lender Admin but without user management

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(2, 'lender', 1, 'A'), -- Overview
(2, 'lender', 4, 'A'), -- Lender Dashboard
(2, 'lender', 5, 'A'), -- Live Projects
(2, 'lender', 6, 'A'), -- Funded Projects
(2, 'lender', 8, 'A'), -- Favorites
(2, 'lender', 10, 'A'), -- All Municipalities
(2, 'lender', 16, 'A'), -- Request Documents
(2, 'lender', 17, 'A'), -- Lender Report
(2, 'lender', 18, 'A'), -- Project-level Commitment Report
(2, 'lender', 19, 'A'), -- Project Success Report
(2, 'lender', 20, 'A'), -- Current Status Report
(2, 'lender', 30, 'A'); -- Reports
-- Note: No User Management, Invitations (these are Admin-only)
```

### 4.3 Municipality Admin Mappings

```sql
-- Using simplified approach: role_id=1 (Admin) + org_type='municipality' = Municipality Admin

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(1, 'municipality', 1, 'A'), -- Overview
(1, 'municipality', 2, 'A'), -- Municipality Dashboard
(1, 'municipality', 7, 'A'), -- My Projects
(1, 'municipality', 23, 'A'), -- Create Project
(1, 'municipality', 24, 'A'), -- My Drafts
(1, 'municipality', 10, 'A'), -- All Municipalities
(1, 'municipality', 13, 'A'), -- Q&A Management
(1, 'municipality', 14, 'A'), -- Project Progress
(1, 'municipality', 15, 'A'), -- Documents and Meetings
(1, 'municipality', 25, 'A'), -- User Management
(1, 'municipality', 26, 'A'), -- Invitations Management
(1, 'municipality', 27, 'A'), -- Send Invitation
(1, 'municipality', 30, 'A'), -- Reports
(1, 'municipality', 18, 'A'), -- Project-level Commitment Report
(1, 'municipality', 19, 'A'), -- Project Success Report
(1, 'municipality', 20, 'A'); -- Current Status Report
```

### 4.4 Municipality Normal User Mappings

```sql
-- Using simplified approach: role_id=2 (Normal User) + org_type='municipality' = Municipality Normal User

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(2, 'municipality', 1, 'A'), -- Overview
(2, 'municipality', 2, 'A'), -- Municipality Dashboard
(2, 'municipality', 7, 'A'), -- My Projects (read-only)
(2, 'municipality', 10, 'A'), -- All Municipalities
(2, 'municipality', 13, 'A'), -- Q&A Management
(2, 'municipality', 14, 'A'), -- Project Progress
(2, 'municipality', 15, 'A'), -- Documents and Meetings
(2, 'municipality', 30, 'A'), -- Reports
(2, 'municipality', 18, 'A'), -- Project-level Commitment Report
(2, 'municipality', 19, 'A'), -- Project Success Report
(2, 'municipality', 20, 'A'); -- Current Status Report
-- Note: No Create Project, My Drafts, User Management (these are Admin-only)
```

### 4.5 Munify Admin Mappings

```sql
-- Using simplified approach: role_id=1 (Admin) + org_type='munify' = Munify Admin

-- All menus except Master (which is Super Admin only)
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status)
SELECT 1, 'munify', id, 'A'
FROM perdix_mp_submenu_master
WHERE menu_id NOT IN (8) -- Exclude Master menu (id: 8)
AND status = 'A';
```

### 4.6 Munify Normal User Mappings

```sql
-- Using simplified approach: role_id=2 (Normal User) + org_type='munify' = Munify Normal User
-- Read-only access to most menus

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(2, 'munify', 1, 'A'), -- Overview
(2, 'munify', 2, 'A'), -- Municipality Dashboard
(2, 'munify', 3, 'A'), -- Master Dashboard
(2, 'munify', 4, 'A'), -- Lender Dashboard
(2, 'munify', 5, 'A'), -- Live Projects
(2, 'munify', 6, 'A'), -- Funded Projects
(2, 'munify', 7, 'A'), -- My Projects
(2, 'munify', 10, 'A'), -- All Municipalities
(2, 'munify', 11, 'A'), -- Credit Ratings
(2, 'munify', 12, 'A'), -- Financial Analysis
(2, 'munify', 13, 'A'), -- Q&A Management
(2, 'munify', 14, 'A'), -- Project Progress
(2, 'munify', 17, 'A'), -- Lender Report
(2, 'munify', 18, 'A'), -- Project-level Commitment Report
(2, 'munify', 19, 'A'), -- Project Success Report
(2, 'munify', 20, 'A'), -- Current Status Report
(2, 'munify', 21, 'A'), -- Project-level Commitment Report (Admin)
(2, 'munify', 22, 'A'), -- Project Success Report (Admin)
(2, 'munify', 29, 'A'), -- Commitments Overview
(2, 'munify', 30, 'A'), -- Reports
(2, 'munify', 31, 'A'), -- Project Lifecycle Tracker
(2, 'munify', 32, 'A'), -- Commitment Monitoring
(2, 'munify', 33, 'A'), -- Q&A & Communication
(2, 'munify', 34, 'A'), -- Document Requests & Library
(2, 'munify', 35, 'A'); -- Allocation & Disbursement
-- Note: No Create Project, User Management, Project Review (these are Admin-only)
```

### 4.7 System Super Admin Mappings

```sql
-- Using simplified approach: role_id=3 (Super Admin) + org_type='munify' = System Super Admin
-- Full access to ALL menus including Master

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status)
SELECT 3, 'munify', id, 'A'
FROM perdix_mp_submenu_master
WHERE status = 'A';
```

### 4.8 Government/NIUA User Mappings

```sql
-- Using 4 roles approach: role_id=4 (Government User) + org_type='government'
-- Summary view only - limited access

INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(4, 'government', 1, 'A'), -- Overview
(4, 'government', 2, 'A'), -- Municipality Dashboard (summary)
(4, 'government', 3, 'A'), -- Master Dashboard (summary)
(4, 'government', 4, 'A'), -- Lender Dashboard (summary)
(4, 'government', 5, 'A'), -- Live Projects (summary)
(4, 'government', 6, 'A'), -- Funded Projects (summary)
(4, 'government', 17, 'A'), -- Lender Report (summary)
(4, 'government', 18, 'A'), -- Project-level Commitment Report (summary)
(4, 'government', 19, 'A'), -- Project Success Report (summary)
(4, 'government', 20, 'A'), -- Current Status Report (summary)
(4, 'government', 21, 'A'), -- Project-level Commitment Report (Admin) (summary)
(4, 'government', 22, 'A'), -- Project Success Report (Admin) (summary)
(4, 'government', 30, 'A'); -- Reports (summary)
```

---

## Step 5: Verification Queries

### Check Menu Data
```sql
SELECT * FROM perdix_mp_menu_master WHERE status = 'A' ORDER BY display_order;
```

### Check Submenu Data
```sql
SELECT sm.*, mm.menu_name 
FROM perdix_mp_submenu_master sm
JOIN perdix_mp_menu_master mm ON sm.menu_id = mm.id
WHERE sm.status = 'A'
ORDER BY mm.display_order, sm.display_order;
```

### Check Mappings for a Specific Role
```sql
SELECT 
    r.role_name,
    m.org_type,
    mm.menu_name,
    sm.submenu_name,
    sm.route
FROM perdix_mp_role_org_submenu_mapping m
JOIN perdix_mp_roles_master r ON m.role_id = r.id
JOIN perdix_mp_submenu_master sm ON m.submenu_id = sm.id
JOIN perdix_mp_menu_master mm ON sm.menu_id = mm.id
WHERE m.role_id = 1  -- Replace with your role_id (1=Admin, 2=Normal User, 3=Super Admin, 4=Government User)
AND m.org_type = 'lender'  -- Replace with your org_type
AND m.status = 'A'
ORDER BY mm.display_order, sm.display_order;
```

### Check All Mappings
```sql
SELECT 
    r.id as role_id,
    r.role_name,
    m.org_type,
    COUNT(m.submenu_id) as menu_count
FROM perdix_mp_role_org_submenu_mapping m
JOIN perdix_mp_roles_master r ON m.role_id = r.id
WHERE m.status = 'A'
GROUP BY r.id, r.role_name, m.org_type
ORDER BY r.role_name, m.org_type;
```

---

## Important Notes

1. **Role Structure (4 Roles Approach):**
   - Use **4 roles**: Admin (id:1), Normal User (id:2), Super Admin (id:3), Government User (id:4)
   - The combination of `role_id` + `org_type` determines full permissions
   - Example: role_id=1 + org_type='lender' = Lender Admin
   - Example: role_id=2 + org_type='lender' = Lender Normal User
   - See `SIMPLIFIED_ROLE_STRUCTURE.md` for detailed explanation

2. **Role IDs:** Use these role IDs:
   - Admin = role_id 1
   - Normal User = role_id 2
   - Super Admin = role_id 3
   - Government User = role_id 4
   
   If you have different role IDs in your database, replace them in the mappings above.

2. **Org Types:** Must be exactly:
   - `lender` (lowercase)
   - `municipality` (lowercase)
   - `munify` (lowercase)
   - `government` (lowercase)

3. **Routes:** All routes must start with `/main` to match frontend routes.

4. **Status:** Use `'A'` for Active, `'I'` for Inactive.

5. **Display Order:** Menus and submenus are ordered by `display_order` field.

6. **Testing:** After inserting data, test the API endpoint:
   ```bash
   GET /api/v1/menus/user-menus?role_id=1&org_type=lender
   ```

---

## Quick Setup Script

If you want to set up everything at once, you can create a script that:
1. Inserts all menus
2. Inserts all submenus
3. Gets role IDs dynamically
4. Inserts mappings based on role names

**Note:** Adjust the role IDs and names based on your actual database.

---

## Troubleshooting

### Issue: No menus returned
- Check if `status = 'A'` for menus, submenus, and mappings
- Verify `role_id` exists in `perdix_mp_roles_master`
- Verify `org_type` is exactly: `lender`, `municipality`, `munify`, or `government` (lowercase)

### Issue: Wrong menus displayed
- Check mappings for the specific `role_id` and `org_type` combination
- Verify routes match frontend routes exactly

### Issue: Missing submenus
- Check if submenu `status = 'A'`
- Verify `menu_id` foreign key is correct
- Check if mapping exists for the role and org_type

---

**Last Updated:** [Current Date]
**Status:** Ready for Database Population

