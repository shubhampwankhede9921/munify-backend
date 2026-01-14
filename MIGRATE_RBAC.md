# 🚀 RBAC Migration - Quick Command

## Single Command to Migrate All RBAC Data

After pulling the code, run:

```bash
alembic upgrade head
```

This will:
- ✅ Delete all existing data from the 3 RBAC tables
- ✅ Insert 9 menus
- ✅ Insert all submenus/routes
- ✅ Insert all role-org-submenu mappings

---

## Full Command Sequence

```bash
# 1. Activate virtual environment (if not already active)
.venv\Scripts\activate    # Windows
# OR
source .venv/bin/activate  # Linux/Mac

# 2. Run migration
alembic upgrade head
```

---

## ✅ Verify Migration

```bash
# Check current migration state
alembic current

# Should show: 9b075b82063f (head)
```

---

## 📝 Notes

- Migration **deletes all existing data** first (clean slate)
- Then inserts fresh data from SQL file
- Safe to run multiple times (will delete and re-insert)
- No manual SQL needed - everything is automated

---

**That's it! One command: `alembic upgrade head`** 🎉
