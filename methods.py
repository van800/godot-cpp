import os
import re
import subprocess
from pathlib import Path


def get_default_include_paths(env):
    # Check if using MSVC compiler
    if env['CXX'] == 'cl' or env.get('MSVC', False) or env['PLATFORM'] == 'win32':
        return []

    compiler = env.subst("$CXX")
    target = os.path.join(env.Dir(".").abspath, "src", "godot.cpp")
    args = [compiler, target, "-x", "c++", "-v"]
    ret = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = ret.stdout
    match = re.search(r"#include <\.\.\.> search starts here:([\S\s]*)End of search list.", output)
    if not match:
        print("Failed to find the include paths in the compiler output.")
        return []
    return [x.strip() for x in match[1].strip().splitlines()]

def write_include_paths_to_props_file(env, output_path):
    proplist = [str(j) for j in get_default_include_paths(env)]
    props_text = ";".join(proplist)
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    pattern = r'^\s*<NMakeIncludeSearchPath>.*</NMakeIncludeSearchPath>\s*$'
    replacement = f'    <NMakeIncludeSearchPath>{props_text};$(NMakeIncludeSearchPath)</NMakeIncludeSearchPath>'
    updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    Path(output_path).write_text(updated_content, encoding='utf-8')
