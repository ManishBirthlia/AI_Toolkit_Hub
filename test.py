import sys
sys.path.insert(0, "System Modules")
from system_modules import get_all_tool_schemas

schemas = get_all_tool_schemas()
print(f"[OK] Loaded {len(schemas)} tool schemas.")
for s in schemas:
    print(f" - {s['name']}")
