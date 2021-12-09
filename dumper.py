# dump query results to temp file
# pretty_results = json.dumps(st.session_state.qry_result, indent=4)
# with open('./temp/search_results.txt','w') as out:
#     out.write(pretty_results)

import json

def dump(dumpee, n):
    pretty = json.dumps(dumpee, indent=4)
    with open(f'./temp/dump{n}.txt','w') as out:
        out.write(pretty)
