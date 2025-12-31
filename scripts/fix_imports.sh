#!/bin/bash
# Fix imports in scripts to use app. prefix
for file in scripts/*.py scripts/deployment/*.py 2>/dev/null; do
    if [ -f "$file" ]; then
        sed -i.bak 's/^from database import/from app.database import/g' "$file"
        sed -i.bak 's/^from tagging import/from app.tagging import/g' "$file"
        sed -i.bak 's/^from views import/from app.views import/g' "$file"
        sed -i.bak 's/^import database$/import app.database as database/g' "$file"
        sed -i.bak 's/^import tagging$/import app.tagging as tagging/g' "$file"
    fi
done
rm -f scripts/*.bak scripts/deployment/*.bak 2>/dev/null
echo "Fixed imports"
