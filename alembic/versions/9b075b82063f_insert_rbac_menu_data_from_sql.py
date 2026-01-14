"""insert_rbac_menu_data_from_sql

Revision ID: 9b075b82063f
Revises: 
Create Date: 2026-01-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '9b075b82063f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Insert RBAC menu data from SQL file.
    This migration:
    1. Deletes all existing data from the 3 tables
    2. Inserts menus, submenus, and mappings
    3. Handles dynamic ID mapping (since IDs are auto-increment)
    """
    connection = op.get_bind()
    
    # ==================== Step 1: Delete All Existing Data ====================
    # Delete in reverse order of foreign key dependencies
    op.execute("DELETE FROM perdix_mp_role_org_submenu_mapping;")
    op.execute("DELETE FROM perdix_mp_submenu_master;")
    op.execute("DELETE FROM perdix_mp_menu_master;")
    
    # ==================== Step 2: Insert Menu Master Data ====================
    # Menu data from SQL file (ordered by display_order)
    menus_data = [
        ('Dashboard', 'dashboard', 'Main dashboard menu', 1),
        ('Projects', 'projects', 'Projects management menu', 2),
        ('Municipalities', 'municipalities', 'Municipalities management menu', 3),
        ('Lender', 'lender', 'Lender features menu', 4),
        ('Reports', 'reports', 'Reports menu', 5),
        ('Admin', 'admin', 'Admin management menu', 6),
        ('Trackings', 'trackings', 'Monitoring and tracking menu', 7),
        ('Master', 'master', 'Master data management menu', 8),
        ('Components', 'components', 'Component showcase (dev)', 9),
    ]
    
    # Map menu names to their expected old IDs (from SQL file)
    # This helps us map submenus correctly
    menu_name_to_old_id = {
        'Dashboard': 46,
        'Projects': 47,
        'Municipalities': 48,
        'Lender': 49,
        'Reports': 50,
        'Admin': 51,
        'Trackings': 52,
        'Master': 53,
        'Components': 54,
    }
    
    # Insert menus and track new IDs
    menu_old_to_new_id = {}
    for menu_name, menu_icon, description, display_order in menus_data:
        result = connection.execute(
            text("""
                INSERT INTO perdix_mp_menu_master (menu_name, menu_icon, description, display_order, status, created_at, updated_at)
                VALUES (:menu_name, :menu_icon, :description, :display_order, 'A', NOW(), NOW())
                RETURNING id;
            """),
            {
                "menu_name": menu_name,
                "menu_icon": menu_icon,
                "description": description,
                "display_order": display_order
            }
        )
        new_id = result.scalar()
        old_id = menu_name_to_old_id[menu_name]
        menu_old_to_new_id[old_id] = new_id
    
    # ==================== Step 3: Insert Submenu Master Data ====================
    # Submenu data from SQL file
    # Format: (submenu_name, submenu_icon, route, old_menu_id, display_order, status)
    submenus_data = [
        # Dashboard submenus (old menu_id: 46)
        ('Municipality Dashboard', 'municipality', '/main/dashboard/municipality', 46, 2, 'A'),
        ('Master Dashboard', 'monitoring', '/main/admin/monitoring', 46, 3, 'A'),
        ('Lender Dashboard', 'lender', '/main/lender/dashboard', 46, 4, 'A'),
        ('Overview', 'overview', '/main', 46, 1, 'I'),
        
        # Projects submenus (old menu_id: 47)
        ('Live Projects', 'live', '/main/projects/live', 47, 1, 'A'),
        ('Fully Funded Projects', 'funded', '/main/projects/funded', 47, 2, 'A'),
        ('My Funded Projects', 'my-projects', '/main/projects/my', 47, 3, 'A'),
        ('Favorites', 'favorites', '/main/projects/favorites', 47, 4, 'A'),
        ('Card Designs', 'card', '/main/designs/cards', 47, 5, 'A'),
        ('Project Details', 'project-details', '/main/projects/:id', 47, 6, 'A'),
        ('Create Project from Draft', 'create-draft', '/main/admin/projects/create/:draftId', 47, 11, 'A'),
        ('Edit Rejected Project', 'edit-rejected', '/main/admin/projects/create/rejected/:projectId', 47, 12, 'A'),
        
        # Municipalities submenus (old menu_id: 48)
        ('All Municipalities', 'municipalities', '/main/municipalities', 48, 1, 'A'),
        ('Credit Ratings', 'ratings', '/main/municipal/ratings', 48, 2, 'A'),
        ('Financial Analysis', 'analysis', '/main/municipal/analysis', 48, 3, 'A'),
        ('Q&A Management', 'qa', '/main/municipal/qa', 48, 4, 'A'),
        ('Project Progress', 'progress', '/main/municipal/projects/progress', 48, 5, 'A'),
        ('Documents and Meetings', 'documents', '/main/municipal/document-requests', 48, 6, 'A'),
        ('Progress Update', 'progress-update', '/main/municipal/projects/:id/progress/update', 48, 8, 'A'),
        ('Document Upload', 'document-upload', '/main/municipal/document-requests/:id/upload', 48, 9, 'A'),
        
        # Lender submenus (old menu_id: 49)
        ('Request Documents and Meetings', 'request-documents', '/main/lender/requested-documents', 49, 1, 'A'),
        
        # Reports submenus (old menu_id: 50)
        ('Lender Report', 'lender-report', '/main/reports/lender-report', 50, 1, 'A'),
        ('Project-level Commitment Report', 'commitment-report', '/main/reports/project-level-commitment', 50, 2, 'A'),
        ('Project Success Report', 'success-report', '/main/reports/project-success', 50, 3, 'A'),
        ('Current Status Report', 'status-report', '/main/reports/current-status', 50, 4, 'A'),
        ('Project-level Commitment Report (Admin)', 'commitment-admin', '/main/reports/project-level-commitment-admin', 50, 5, 'A'),
        ('Project Success Report (Admin)', 'success-admin', '/main/reports/project-success-admin', 50, 6, 'A'),
        
        # Admin submenus (old menu_id: 51)
        ('Project Management', 'project-management', '/main/admin/projects', 51, 1, 'A'),
        ('Create Project', 'create-project', '/main/admin/projects/create', 51, 2, 'A'),
        ('My Projects', 'drafts', '/main/admin/projects/drafts', 51, 3, 'A'),
        ('User Management', 'users', '/main/admin/users', 51, 4, 'A'),
        ('Invitations Management', 'invitations', '/main/admin/invitations', 51, 5, 'A'),
        ('Send Invitation', 'send-invitation', '/main/admin/invitation', 51, 6, 'A'),
        ('Notifications', 'notifications', '/main/admin/notifications', 51, 7, 'A'),
        ('Commitments Overview', 'commitments', '/main/admin/commitments', 51, 8, 'A'),
        ('Reports', 'reports', '/main/admin/reports', 51, 9, 'A'),
        ('Project Review', 'project-review', '/main/admin/projects/validate/:id', 51, 10, 'A'),
        ('Commitment Details', 'commitment-details', '/main/admin/commitments/:projectReferenceId', 51, 13, 'A'),
        
        # Trackings submenus (old menu_id: 52)
        ('Project Lifecycle Tracker', 'lifecycle', '/main/admin/monitoring/lifecycle', 52, 1, 'A'),
        ('Commitment Monitoring', 'commitment-monitoring', '/main/admin/monitoring/commitments', 52, 2, 'A'),
        ('Q&A & Communication', 'qa-communication', '/main/admin/monitoring/qa', 52, 3, 'A'),
        ('Document Requests & Library', 'document-library', '/main/admin/monitoring/documents', 52, 4, 'A'),
        ('Allocation & Disbursement', 'allocation', '/main/admin/monitoring/allocation-disbursement', 52, 5, 'A'),
        
        # Master submenus (old menu_id: 53)
        ('Roles Management', 'roles', '/main/master/roles', 53, 1, 'A'),
        ('Organizations Management', 'organizations', '/main/master/organizations', 53, 2, 'A'),
        ('Fee Category Exemptions', 'fee-exemptions', '/main/master/fee-category-exemptions', 53, 3, 'A'),
        ('Common Master Excel', 'excel', '/main/master/common-excel', 53, 4, 'A'),
        
        # Components submenus (old menu_id: 54)
        ('Data Table', 'table', '/main/components/datatable', 54, 1, 'A'),
    ]
    
    # Map submenu names to their old IDs (from SQL file analysis)
    # This mapping is based on the order and content of the SQL file
    submenu_name_to_old_id = {
        # Dashboard (menu_id 46)
        'Overview': 91, 'Municipality Dashboard': 92, 'Master Dashboard': 93, 'Lender Dashboard': 94,
        # Projects (menu_id 47)
        'Live Projects': 95, 'Fully Funded Projects': 96, 'My Funded Projects': 97, 'Favorites': 98,
        'Card Designs': 99, 'Project Details': 100, 'Create Project from Draft': 101, 'Edit Rejected Project': 102,
        # Municipalities (menu_id 48)
        'All Municipalities': 103, 'Credit Ratings': 104, 'Financial Analysis': 105, 'Q&A Management': 106,
        'Project Progress': 107, 'Documents and Meetings': 108, 'Progress Update': 109, 'Document Upload': 110,
        # Lender (menu_id 49)
        'Request Documents and Meetings': 111,
        # Reports (menu_id 50)
        'Lender Report': 112, 'Project-level Commitment Report': 113, 'Project Success Report': 114,
        'Current Status Report': 115, 'Project-level Commitment Report (Admin)': 116, 'Project Success Report (Admin)': 117,
        # Admin (menu_id 51)
        'Project Management': 118, 'Create Project': 119, 'My Projects': 120, 'User Management': 121,
        'Invitations Management': 122, 'Send Invitation': 123, 'Notifications': 124, 'Commitments Overview': 125,
        'Reports': 126, 'Project Review': 127, 'Commitment Details': 128,
        # Trackings (menu_id 52)
        'Project Lifecycle Tracker': 129, 'Commitment Monitoring': 130, 'Q&A & Communication': 131,
        'Document Requests & Library': 132, 'Allocation & Disbursement': 133,
        # Master (menu_id 53)
        'Roles Management': 134, 'Organizations Management': 135, 'Fee Category Exemptions': 136,
        'Common Master Excel': 137,
        # Components (menu_id 54)
        'Data Table': 138,
    }
    
    # Insert submenus and track new IDs by name
    submenu_name_to_new_id = {}
    submenu_old_to_new_id = {}
    
    for submenu_name, submenu_icon, route, old_menu_id, display_order, status in submenus_data:
        new_menu_id = menu_old_to_new_id[old_menu_id]
        
        result = connection.execute(
            text("""
                INSERT INTO perdix_mp_submenu_master (submenu_name, submenu_icon, route, menu_id, display_order, status, created_at, updated_at)
                VALUES (:submenu_name, :submenu_icon, :route, :menu_id, :display_order, :status, NOW(), NOW())
                RETURNING id;
            """),
            {
                "submenu_name": submenu_name,
                "submenu_icon": submenu_icon,
                "route": route,
                "menu_id": new_menu_id,
                "display_order": display_order,
                "status": status
            }
        )
        new_id = result.scalar()
        submenu_name_to_new_id[submenu_name] = new_id
        
        # Map old ID to new ID
        if submenu_name in submenu_name_to_old_id:
            old_id = submenu_name_to_old_id[submenu_name]
            submenu_old_to_new_id[old_id] = new_id
    
    # ==================== Step 4: Insert Role-Org-Submenu Mappings ====================
    # Mapping data from SQL file
    # Format: (role_id, org_type, old_submenu_id, status)
    mappings_data = [
        # Lender Admin (145, 'lender')
        (145, 'lender', 94, 'A'), (145, 'lender', 95, 'A'), (145, 'lender', 96, 'A'),
        (145, 'lender', 98, 'A'), (145, 'lender', 106, 'A'), (145, 'lender', 107, 'A'),
        (145, 'lender', 116, 'A'), (145, 'lender', 117, 'A'), (145, 'lender', 118, 'A'),
        (145, 'lender', 97, 'A'), (145, 'lender', 133, 'A'),
        (145, 'lender', 99, 'I'), (145, 'lender', 100, 'I'), (145, 'lender', 108, 'I'),
        (145, 'lender', 109, 'I'), (145, 'lender', 110, 'I'), (145, 'lender', 121, 'I'),
        (145, 'lender', 91, 'I'),
        
        # Lender Normal User (146, 'lender')
        (146, 'lender', 94, 'A'), (146, 'lender', 95, 'A'), (146, 'lender', 96, 'A'),
        (146, 'lender', 98, 'A'), (146, 'lender', 107, 'A'), (146, 'lender', 106, 'A'),
        (146, 'lender', 97, 'A'), (146, 'lender', 133, 'A'),
        (146, 'lender', 91, 'I'), (146, 'lender', 100, 'I'), (146, 'lender', 108, 'I'),
        (146, 'lender', 110, 'I'), (146, 'lender', 121, 'I'), (146, 'lender', 109, 'I'),
        
        # Municipality Admin (145, 'municipality')
        (145, 'municipality', 92, 'A'), (145, 'municipality', 114, 'A'), (145, 'municipality', 115, 'A'),
        (145, 'municipality', 103, 'A'), (145, 'municipality', 104, 'A'), (145, 'municipality', 105, 'A'),
        (145, 'municipality', 116, 'A'), (145, 'municipality', 117, 'A'), (145, 'municipality', 118, 'A'),
        (145, 'municipality', 108, 'A'), (145, 'municipality', 109, 'A'), (145, 'municipality', 95, 'A'),
        (145, 'municipality', 120, 'A'), (145, 'municipality', 133, 'A'), (145, 'municipality', 134, 'A'),
        (145, 'municipality', 135, 'A'), (145, 'municipality', 137, 'A'), (145, 'municipality', 138, 'A'),
        (145, 'municipality', 139, 'A'),
        (145, 'municipality', 91, 'I'), (145, 'municipality', 97, 'I'), (145, 'municipality', 100, 'I'),
        (145, 'municipality', 121, 'I'), (145, 'municipality', 110, 'I'),
        
        # Municipality Normal User (146, 'municipality')
        (146, 'municipality', 92, 'A'), (146, 'municipality', 103, 'A'), (146, 'municipality', 104, 'A'),
        (146, 'municipality', 105, 'A'), (146, 'municipality', 108, 'A'), (146, 'municipality', 109, 'A'),
        (146, 'municipality', 95, 'A'), (146, 'municipality', 120, 'A'), (146, 'municipality', 133, 'A'),
        (146, 'municipality', 134, 'A'), (146, 'municipality', 135, 'A'), (146, 'municipality', 139, 'A'),
        (146, 'municipality', 91, 'I'), (146, 'municipality', 97, 'I'), (146, 'municipality', 100, 'I'),
        (146, 'municipality', 121, 'I'), (146, 'municipality', 110, 'I'),
        
        # Munify Admin (145, 'munify')
        (145, 'munify', 93, 'A'), (145, 'munify', 95, 'A'), (145, 'munify', 96, 'A'),
        (145, 'munify', 105, 'A'), (145, 'munify', 110, 'A'), (145, 'munify', 111, 'A'),
        (145, 'munify', 112, 'A'), (145, 'munify', 113, 'A'), (145, 'munify', 114, 'A'),
        (145, 'munify', 115, 'A'), (145, 'munify', 116, 'A'), (145, 'munify', 117, 'A'),
        (145, 'munify', 118, 'A'), (145, 'munify', 119, 'A'), (145, 'munify', 122, 'A'),
        (145, 'munify', 123, 'A'), (145, 'munify', 124, 'A'), (145, 'munify', 125, 'A'),
        (145, 'munify', 126, 'A'), (145, 'munify', 133, 'A'), (145, 'munify', 134, 'A'),
        (145, 'munify', 135, 'A'), (145, 'munify', 136, 'A'), (145, 'munify', 137, 'A'),
        (145, 'munify', 91, 'I'), (145, 'munify', 92, 'I'), (145, 'munify', 94, 'I'),
        (145, 'munify', 97, 'I'), (145, 'munify', 98, 'I'), (145, 'munify', 99, 'I'),
        (145, 'munify', 100, 'I'), (145, 'munify', 101, 'I'), (145, 'munify', 102, 'I'),
        (145, 'munify', 103, 'I'), (145, 'munify', 106, 'I'), (145, 'munify', 121, 'I'),
        (145, 'munify', 120, 'I'), (145, 'munify', 107, 'I'), (145, 'munify', 108, 'I'),
        (145, 'munify', 109, 'I'), (145, 'munify', 104, 'I'), (145, 'munify', 131, 'I'),
        
        # Munify Normal User (146, 'munify')
        (146, 'munify', 93, 'A'), (146, 'munify', 95, 'A'), (146, 'munify', 96, 'A'),
        (146, 'munify', 110, 'A'), (146, 'munify', 111, 'A'), (146, 'munify', 112, 'A'),
        (146, 'munify', 122, 'A'), (146, 'munify', 123, 'A'), (146, 'munify', 124, 'A'),
        (146, 'munify', 125, 'A'), (146, 'munify', 126, 'A'), (146, 'munify', 133, 'A'),
        (146, 'munify', 134, 'A'), (146, 'munify', 135, 'A'), (146, 'munify', 136, 'A'),
        (146, 'munify', 91, 'I'), (146, 'munify', 92, 'I'), (146, 'munify', 94, 'I'),
        (146, 'munify', 97, 'I'), (146, 'munify', 100, 'I'), (146, 'munify', 101, 'I'),
        (146, 'munify', 102, 'I'), (146, 'munify', 103, 'I'), (146, 'munify', 104, 'I'),
        (146, 'munify', 107, 'I'), (146, 'munify', 108, 'I'), (146, 'munify', 109, 'I'),
        (146, 'munify', 120, 'I'), (146, 'munify', 121, 'I'),
        
        # System Super Admin (147, 'munify')
        (147, 'munify', 93, 'A'), (147, 'munify', 95, 'A'), (147, 'munify', 96, 'A'),
        (147, 'munify', 105, 'A'), (147, 'munify', 110, 'A'), (147, 'munify', 111, 'A'),
        (147, 'munify', 112, 'A'), (147, 'munify', 113, 'A'), (147, 'munify', 114, 'A'),
        (147, 'munify', 115, 'A'), (147, 'munify', 116, 'A'), (147, 'munify', 117, 'A'),
        (147, 'munify', 118, 'A'), (147, 'munify', 119, 'A'), (147, 'munify', 122, 'A'),
        (147, 'munify', 123, 'A'), (147, 'munify', 124, 'A'), (147, 'munify', 125, 'A'),
        (147, 'munify', 126, 'A'), (147, 'munify', 127, 'A'), (147, 'munify', 128, 'A'),
        (147, 'munify', 129, 'A'), (147, 'munify', 130, 'A'), (147, 'munify', 133, 'A'),
        (147, 'munify', 134, 'A'), (147, 'munify', 135, 'A'), (147, 'munify', 136, 'A'),
        (147, 'munify', 137, 'A'),
        (147, 'munify', 91, 'I'), (147, 'munify', 92, 'I'), (147, 'munify', 94, 'I'),
        (147, 'munify', 97, 'I'), (147, 'munify', 98, 'I'), (147, 'munify', 99, 'I'),
        (147, 'munify', 100, 'I'), (147, 'munify', 101, 'I'), (147, 'munify', 102, 'I'),
        (147, 'munify', 103, 'I'), (147, 'munify', 104, 'I'), (147, 'munify', 106, 'I'),
        (147, 'munify', 107, 'I'), (147, 'munify', 108, 'I'), (147, 'munify', 109, 'I'),
        (147, 'munify', 120, 'I'), (147, 'munify', 121, 'I'), (147, 'munify', 131, 'I'),
        
        # Government User (148, 'government')
        (148, 'government', 93, 'A'), (148, 'government', 95, 'A'), (148, 'government', 96, 'A'),
        (148, 'government', 110, 'A'), (148, 'government', 111, 'A'), (148, 'government', 112, 'A'),
        (148, 'government', 107, 'A'), (148, 'government', 108, 'A'), (148, 'government', 109, 'A'),
        (148, 'government', 133, 'A'),
        (148, 'government', 91, 'I'), (148, 'government', 92, 'I'), (148, 'government', 94, 'I'),
        (148, 'government', 121, 'I'),
    ]
    
    # Insert mappings using new submenu IDs
    for role_id, org_type, old_submenu_id, status in mappings_data:
        if old_submenu_id in submenu_old_to_new_id:
            new_submenu_id = submenu_old_to_new_id[old_submenu_id]
            connection.execute(
                text("""
                    INSERT INTO perdix_mp_role_org_submenu_mapping (role_id, org_type, submenu_id, status, created_at, updated_at)
                    VALUES (:role_id, :org_type, :submenu_id, :status, NOW(), NOW())
                    ON CONFLICT (role_id, org_type, submenu_id) DO NOTHING;
                """),
                {
                    "role_id": role_id,
                    "org_type": org_type,
                    "submenu_id": new_submenu_id,
                    "status": status
                }
            )


def downgrade() -> None:
    """Remove all RBAC menu data."""
    # Delete in reverse order of foreign key dependencies
    op.execute("DELETE FROM perdix_mp_role_org_submenu_mapping;")
    op.execute("DELETE FROM perdix_mp_submenu_master;")
    op.execute("DELETE FROM perdix_mp_menu_master;")
