# PromptLM

## Start
```sh
git clone ...
cd PromptLM
```

## SCoT model
**Running locally**
```sh
chmod +x ./scripts/<script_name>
./scripts/<script_name>
```

**Running with slurm**
```sh
chmod +x ./scripts/slurm/<script_name>
./scripts/slurm/<script_name>
```


```txt
def file_modify(file_path, startline, endline, content):
    '''...'''


pythoncode (root, code)

name: file_modify
file_path
startline
endline
content

-- system prompt 
generate thinking,
those tool to use:
tool1
tool2
your output format is
<html>
..


before generating tool use, please specify your step-by step think, so you output will be like
why this tool
???

- thinking ......................................

<html>
</html>

if u dont use tool, output 

answer ....


-- env
your code succesfully run

-- <bot>
I think
<tool>
<name>
pythoncode
</name>
<root>
path/to/folder
</root>
<code>
print('ehllo')
</code>
</tool>


- [ ] prompt con bot (3 con)
- [ ] answer cua bot -> chay tool
- [ ] answer ko co tool -> dua answer vao con bot tiep theo -> 
```