# Quick Migration Guide - RBAC Tables

## 🚀 Quick Start (One Command)

After pulling the code, run this single command to migrate all RBAC data:

```bash
alembic upgrade head
```

That's it! This will:
1. ✅ Create the 3 RBAC tables (if not exists)
2. ✅ Insert 9 menus
3. ✅ Insert 44 submenus/routes
4. ✅ Insert all role-org-submenu mappings

---

## 📋 Step-by-Step (If Needed)

### 1. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Run Migration
```bash
alembic upgrade head
```

### 3. Verify (Optional)
```bash
alembic current
```

---

## ✅ Expected Output

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 50821e3e34c9, create_menu_management_tables
INFO  [alembic.runtime.migration] Running upgrade 50821e3e34c9 -> insert_menu_data, insert_menu_data_with_role_mappings
```

---

## 🔄 If Migration Already Ran

The migration uses `ON CONFLICT DO NOTHING`, so it's **safe to run multiple times**.

If you get "Target database is not up to date", run:
```bash
alembic upgrade head
```

---

## ❌ Troubleshooting

### Error: "No such revision"
```bash
# Check current migration state
alembic current

# If needed, stamp to latest
alembic stamp head
```

### Error: "Table already exists"
```bash
# Check if tables exist
alembic current

# If tables exist but migration not recorded, stamp it
alembic stamp head
```

---

## 📝 Summary

**Single Command:**
```bash
alembic upgrade head
```

**That's all you need!** 🎉
