# RBAC Data Migration Guide - Complete Overview

## 📋 Overview

This guide explains the **3 RBAC tables** and all the **routes/data** that were inserted for role-based access control.

---

## 🗂️ The 3 Tables Structure

### 1. `perdix_mp_menu_master` (Main Menus)
**Purpose:** Stores top-level menu items (e.g., Dashboard, Projects, Admin)

**Columns:**
- `id` - Auto-increment primary key
- `menu_name` - Display name (e.g., "Dashboard", "Projects")
- `menu_icon` - Icon identifier for frontend
- `description` - Optional description
- `display_order` - Order in sidebar (1, 2, 3...)
- `status` - 'A' (Active) or 'I' (Inactive)

### 2. `perdix_mp_submenu_master` (Submenus/Routes)
**Purpose:** Stores individual pages/routes that belong to menus

**Columns:**
- `id` - Auto-increment primary key
- `submenu_name` - Display name (e.g., "Live Projects", "Create Project")
- `submenu_icon` - Icon identifier
- `route` - **Frontend route path** (e.g., "/main/projects/live")
- `menu_id` - Foreign key to `perdix_mp_menu_master.id`
- `display_order` - Order within menu
- `status` - 'A' (Active) or 'I' (Inactive)

### 3. `perdix_mp_role_org_submenu_mapping` (Access Control)
**Purpose:** Maps which roles + org_types can access which submenus

**Columns:**
- `id` - Auto-increment primary key
- `role_id` - Role ID from Perdix system (145, 146, 147, 148)
- `org_type` - Organization type ('municipality', 'lender', 'munify', 'government')
- `submenu_id` - Foreign key to `perdix_mp_submenu_master.id`
- `status` - 'A' (Active) or 'I' (Inactive)

---

## 📊 Complete Data Inserted

### Table 1: Menu Master (9 Menus)

| ID | Menu Name | Icon | Display Order | Description |
|----|-----------|------|---------------|-------------|
| 1 | Dashboard | dashboard | 1 | Main dashboard menu |
| 2 | Projects | projects | 2 | Projects management menu |
| 3 | Municipalities | municipalities | 3 | Municipalities management menu |
| 4 | Lender | lender | 4 | Lender features menu |
| 5 | Reports | reports | 5 | Reports menu |
| 6 | Admin | admin | 6 | Admin management menu |
| 7 | Trackings | trackings | 7 | Monitoring and tracking menu |
| 8 | Master | master | 8 | Master data management menu |
| 9 | Components | components | 9 | Component showcase (dev) |

---

### Table 2: Submenu Master (All Routes)

#### **Dashboard Menu** (Menu ID: 1)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Overview | `/main` | overview | 1 |
| Municipality Dashboard | `/main/dashboard/municipality` | municipality | 2 |
| Master Dashboard | `/main/admin/monitoring` | monitoring | 3 |
| Lender Dashboard | `/main/lender/dashboard` | lender | 4 |

#### **Projects Menu** (Menu ID: 2)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Live Projects | `/main/projects/live` | live | 1 |
| Funded Projects | `/main/projects/funded` | funded | 2 |
| My Projects | `/main/projects/my` | my-projects | 3 |
| Favorites | `/main/projects/favorites` | favorites | 4 |
| Card Designs | `/main/designs/cards` | card | 5 |

#### **Municipalities Menu** (Menu ID: 3)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| All Municipalities | `/main/municipalities` | municipalities | 1 |
| Credit Ratings | `/main/municipal/ratings` | ratings | 2 |
| Financial Analysis | `/main/municipal/analysis` | analysis | 3 |
| Q&A Management | `/main/municipal/qa` | qa | 4 |
| Project Progress | `/main/municipal/projects/progress` | progress | 5 |
| Documents and Meetings | `/main/municipal/document-requests` | documents | 6 |

#### **Lender Menu** (Menu ID: 4)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Request Documents and Meetings | `/main/lender/requested-documents` | request-documents | 1 |

#### **Reports Menu** (Menu ID: 5)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Lender Report | `/main/reports/lender-report` | lender-report | 1 |
| Project-level Commitment Report | `/main/reports/project-level-commitment` | commitment-report | 2 |
| Project Success Report | `/main/reports/project-success` | success-report | 3 |
| Current Status Report | `/main/reports/current-status` | status-report | 4 |
| Project-level Commitment Report (Admin) | `/main/reports/project-level-commitment-admin` | commitment-admin | 5 |
| Project Success Report (Admin) | `/main/reports/project-success-admin` | success-admin | 6 |

#### **Admin Menu** (Menu ID: 6)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Project Management | `/main/admin/projects` | project-management | 1 |
| Create Project | `/main/admin/projects/create` | create-project | 2 |
| My Drafts | `/main/admin/projects/drafts` | drafts | 3 |
| User Management | `/main/admin/users` | users | 4 |
| Invitations Management | `/main/admin/invitations` | invitations | 5 |
| Send Invitation | `/main/admin/invitation` | send-invitation | 6 |
| Notifications | `/main/admin/notifications` | notifications | 7 |
| Commitments Overview | `/main/admin/commitments` | commitments | 8 |
| Reports | `/main/admin/reports` | reports | 9 |

#### **Trackings Menu** (Menu ID: 7)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Project Lifecycle Tracker | `/main/admin/monitoring/lifecycle` | lifecycle | 1 |
| Commitment Monitoring | `/main/admin/monitoring/commitments` | commitment-monitoring | 2 |
| Q&A & Communication | `/main/admin/monitoring/qa` | qa-communication | 3 |
| Document Requests & Library | `/main/admin/monitoring/documents` | document-library | 4 |
| Allocation & Disbursement | `/main/admin/monitoring/allocation-disbursement` | allocation | 5 |

#### **Master Menu** (Menu ID: 8)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Roles Management | `/main/master/roles` | roles | 1 |
| Organizations Management | `/main/master/organizations` | organizations | 2 |
| Fee Category Exemptions | `/main/master/fee-category-exemptions` | fee-exemptions | 3 |
| Common Master Excel | `/main/master/common-excel` | excel | 4 |

#### **Components Menu** (Menu ID: 9)
| Submenu Name | Route | Icon | Order |
|--------------|-------|------|-------|
| Data Table | `/main/components/datatable` | table | 1 |

**Total: 44 Submenus/Routes**

---

### Table 3: Role-Org-Submenu Mappings

#### **Role IDs (from Perdix System)**
- **145** = Admin
- **146** = Normal User
- **147** = Super Admin
- **148** = Government User

#### **Organization Types**
- `municipality` - Municipality users
- `lender` - Lender users
- `munify` - Munify platform users
- `government` - Government/NIUA users

---

## 🔐 Access Mappings by Role + Org Type

### 1. Lender Admin (role_id=145, org_type='lender')
**Access to:**
- Overview
- Lender Dashboard
- Live Projects
- Funded Projects
- Favorites
- Card Designs
- All Municipalities
- Request Documents and Meetings
- Lender Report
- Project-level Commitment Report
- Project Success Report
- Current Status Report
- User Management
- Invitations Management
- Send Invitation
- Reports

### 2. Lender Normal User (role_id=146, org_type='lender')
**Access to:**
- Overview
- Lender Dashboard
- Live Projects
- Funded Projects
- Favorites
- All Municipalities
- Request Documents and Meetings
- Lender Report
- Project-level Commitment Report
- Project Success Report
- Current Status Report
- Reports

### 3. Municipality Admin (role_id=145, org_type='municipality')
**Access to:**
- Overview
- Municipality Dashboard
- My Projects
- Create Project
- My Drafts
- All Municipalities
- Q&A Management
- Project Progress
- Documents and Meetings
- User Management
- Invitations Management
- Send Invitation
- Reports
- Project-level Commitment Report
- Project Success Report
- Current Status Report

### 4. Municipality Normal User (role_id=146, org_type='municipality')
**Access to:**
- Overview
- Municipality Dashboard
- My Projects
- All Municipalities
- Q&A Management
- Project Progress
- Documents and Meetings
- Reports
- Project-level Commitment Report
- Project Success Report
- Current Status Report

### 5. Munify Admin (role_id=145, org_type='munify')
**Access to:** **ALL submenus EXCEPT Master menu**
- All Dashboard submenus
- All Projects submenus
- All Municipalities submenus
- All Lender submenus
- All Reports submenus
- All Admin submenus
- All Trackings submenus
- All Components submenus
- **EXCLUDES:** Master menu (Roles Management, Organizations Management, etc.)

### 6. Munify Normal User (role_id=146, org_type='munify')
**Access to:**
- Overview
- Municipality Dashboard
- Master Dashboard
- Lender Dashboard
- Live Projects
- Funded Projects
- My Projects
- All Municipalities
- Credit Ratings
- Financial Analysis
- Q&A Management
- Project Progress
- Lender Report
- Project-level Commitment Report
- Project Success Report
- Current Status Report
- Project-level Commitment Report (Admin)
- Project Success Report (Admin)
- Commitments Overview
- Reports
- Project Lifecycle Tracker
- Commitment Monitoring
- Q&A & Communication
- Document Requests & Library
- Allocation & Disbursement

### 7. System Super Admin (role_id=147, org_type='munify')
**Access to:** **EVERYTHING** (including Master menu)
- All 44 submenus/routes
- Full system access

### 8. Government/NIUA User (role_id=148, org_type='government')
**Access to:**
- Overview
- Municipality Dashboard
- Master Dashboard
- Lender Dashboard
- Live Projects
- Funded Projects
- Lender Report
- Project-level Commitment Report
- Project Success Report
- Current Status Report
- Project-level Commitment Report (Admin)
- Project Success Report (Admin)
- Reports

---

## 🚀 How to Migrate This Data

### Option 1: Using Alembic Migration (Recommended)

The data is already in the migration file:
```
alembic/versions/insert_menu_data_with_role_mappings.py
```

**To run:**
```bash
# Make sure you're in the project directory
cd E:\poc\python-code\blog-project

# Activate virtual environment (if not already active)
.venv\Scripts\activate

# Run the migration
alembic upgrade head
```

**What it does:**
1. Inserts 9 menus into `perdix_mp_menu_master`
2. Inserts 44 submenus into `perdix_mp_submenu_master`
3. Inserts role-org-submenu mappings into `perdix_mp_role_org_submenu_mapping`
4. Uses `ON CONFLICT DO NOTHING` to make it idempotent (safe to run multiple times)

---

### Option 2: Manual SQL Insert

If you want to insert manually or modify the data:

**Step 1: Insert Menus**
```sql
INSERT INTO perdix_mp_menu_master (menu_name, menu_icon, description, display_order, status) VALUES
('Dashboard', 'dashboard', 'Main dashboard menu', 1, 'A'),
('Projects', 'projects', 'Projects management menu', 2, 'A'),
('Municipalities', 'municipalities', 'Municipalities management menu', 3, 'A'),
('Lender', 'lender', 'Lender features menu', 4, 'A'),
('Reports', 'reports', 'Reports menu', 5, 'A'),
('Admin', 'admin', 'Admin management menu', 6, 'A'),
('Trackings', 'trackings', 'Monitoring and tracking menu', 7, 'A'),
('Master', 'master', 'Master data management menu', 8, 'A'),
('Components', 'components', 'Component showcase (dev)', 9, 'A')
ON CONFLICT (menu_name) DO NOTHING;
```

**Step 2: Insert Submenus** (after getting menu IDs)
```sql
-- Get menu IDs first
SELECT id, menu_name FROM perdix_mp_menu_master;

-- Then insert submenus (replace menu_id with actual IDs)
INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status) VALUES
('Overview', 'overview', '/main', 1, 1, 'A'),
('Live Projects', 'live', '/main/projects/live', 2, 1, 'A'),
-- ... (see migration file for complete list)
ON CONFLICT (submenu_name) DO NOTHING;
```

**Step 3: Insert Mappings** (after getting submenu IDs)
```sql
-- Get submenu IDs first
SELECT id, submenu_name FROM perdix_mp_submenu_master;

-- Then insert mappings (replace submenu_id with actual IDs)
INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status) VALUES
(145, 'lender', 1, 'A'),  -- Lender Admin can access Overview
(145, 'lender', 5, 'A'),  -- Lender Admin can access Live Projects
-- ... (see migration file for complete list)
ON CONFLICT (role_id, org_type, submenu_id) DO NOTHING;
```

---

### Option 3: Using Python Script

Create a script to insert data programmatically:

```python
from app.core.database import SessionLocal
from app.models.menu_master import MenuMaster
from app.models.submenu_master import SubmenuMaster
from app.models.role_org_submenu_mapping import RoleOrgSubmenuMapping

db = SessionLocal()

# Insert menus
menus = [
    MenuMaster(menu_name="Dashboard", menu_icon="dashboard", display_order=1, status="A"),
    MenuMaster(menu_name="Projects", menu_icon="projects", display_order=2, status="A"),
    # ... more menus
]

for menu in menus:
    db.merge(menu)  # Use merge to handle conflicts

db.commit()

# Insert submenus (after menus are created)
# ... similar pattern

# Insert mappings (after submenus are created)
# ... similar pattern
```

---

## 📝 Summary

### What Was Inserted:

1. **9 Menus** in `perdix_mp_menu_master`
2. **44 Submenus/Routes** in `perdix_mp_submenu_master`
3. **Role-Org-Submenu Mappings** in `perdix_mp_role_org_submenu_mapping`:
   - 8 different role+org_type combinations
   - Each with specific submenu access

### Key Routes for Backend Validation:

When implementing backend route access validation, map these routes:
- `/main/admin/projects/create` - Create project
- `/main/admin/users` - User management
- `/main/admin/invitation` - Send invitation
- `/main/admin/commitments` - Commitments
- `/main/projects/live` - View live projects
- `/main/municipal/qa` - Q&A management
- ... (all 44 routes)

### Migration File Location:

```
alembic/versions/insert_menu_data_with_role_mappings.py
```

**To run migration:**
```bash
alembic upgrade head
```

---

## ✅ Verification

After migration, verify data:

```sql
-- Check menus
SELECT COUNT(*) FROM perdix_mp_menu_master;  -- Should be 9

-- Check submenus
SELECT COUNT(*) FROM perdix_mp_submenu_master;  -- Should be 44

-- Check mappings
SELECT role_id, org_type, COUNT(*) as access_count
FROM perdix_mp_role_org_submenu_mapping
GROUP BY role_id, org_type
ORDER BY role_id, org_type;
```

---

**Status:** ✅ All data is ready in the Alembic migration file. Run `alembic upgrade head` to insert it!
