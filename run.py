

from backend.app import app
from backend.db import reset
print(str(app.url_map._rules_by_endpoint).replace("],", "],\n"))
# reset()
app.run(host="0.0.0.0", debug=False, port=80)
